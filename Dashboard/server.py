"""Tiny read-only API and web server for the science fair dashboard.

The browser cannot read arbitrary files from a computer. This server is the
small bridge: it reads the two progress files, converts them to safe JSON, and
serves the HTML/CSS/JavaScript dashboard. It uses only Python's standard library.
"""

from __future__ import annotations

import argparse
import csv
import json
import os
import sys
from datetime import datetime, timezone
from http import HTTPStatus
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

# Training was intentionally finalized at the actual completed count on
# October 19, 2026. The dashboard now treats that preserved run as complete.
MINE_TARGET = 249_830
PASSWORD_TARGET = 62**6
DEFAULT_RATES = {
    "minesweeper": 1.0,
    "password-security": 1_800_000.0,
}
ACTIVE_WITHIN_SECONDS = 5 * 60
DASHBOARD_DIRECTORY = Path(__file__).resolve().parent
REPOSITORY_DIRECTORY = DASHBOARD_DIRECTORY.parent


def first_existing_path(environment_name: str, candidates: list[Path]) -> Path:
    """Use an environment override first, then the first existing default."""

    custom_path = os.environ.get(environment_name)
    if custom_path:
        return Path(custom_path).expanduser().resolve()

    for candidate in candidates:
        if candidate.exists():
            return candidate

    # Return the first default even when it is missing. The API can then explain
    # exactly which file it expected instead of crashing.
    return candidates[0]


def progress_paths() -> tuple[Path, Path]:
    """Find progress files in this repository or in the active local projects."""

    work_directory = REPOSITORY_DIRECTORY.parents[1]

    mine_path = first_existing_path(
        "SCIENCE_FAIR_MINE_DATA",
        [
            work_directory
            / "ScienceFairProjects"
            / "minesweeper-ai"
            / "models"
            / "dqn_agent"
            / "training_data.csv",
            REPOSITORY_DIRECTORY
            / "Minesweeper"
            / "models"
            / "dqn_agent"
            / "training_data.csv",
        ],
    )

    password_path = first_existing_path(
        "SCIENCE_FAIR_PASSWORD_STATE",
        [
            work_directory / "Animated" / "password-search-state.json",
            REPOSITORY_DIRECTORY
            / "PasswordSecurity"
            / "password-search-state.json",
        ],
    )

    return mine_path, password_path


def timestamp_for(path: Path) -> str | None:
    """Return a browser-friendly UTC timestamp for a file."""

    if not path.exists():
        return None

    modified = datetime.fromtimestamp(path.stat().st_mtime, tz=timezone.utc)
    return modified.isoformat()


def recently_updated(path: Path) -> bool:
    """Treat a frequently changing progress file as evidence the job is active."""

    if not path.exists():
        return False

    age = datetime.now(tz=timezone.utc).timestamp() - path.stat().st_mtime
    return age <= ACTIVE_WITHIN_SECONDS


def read_last_csv_row(path: Path) -> list[str]:
    """Read the last non-empty CSV row without loading the full history file."""

    last_row: list[str] | None = None
    with path.open("r", encoding="utf-8", newline="") as source:
        for row in csv.reader(source):
            if row:
                last_row = row

    if last_row is None:
        raise ValueError("The training CSV is empty.")

    return last_row


def minesweeper_status(path: Path) -> dict[str, Any]:
    """Build the safe public status object for Minesweeper training."""

    if not path.exists():
        return missing_project(
            "minesweeper",
            "Minesweeper",
            "games",
            MINE_TARGET,
            path,
        )

    completed = int(read_last_csv_row(path)[0])
    completed = max(0, min(completed, MINE_TARGET))

    if completed >= MINE_TARGET:
        state = "complete"
    elif recently_updated(path):
        state = "running"
    else:
        state = "stale"

    return project_status(
        "minesweeper",
        "Minesweeper",
        "games",
        completed,
        MINE_TARGET,
        state,
        path,
    )


def password_status(path: Path) -> dict[str, Any]:
    """Build password-search status without exposing a recovered password."""

    if not path.exists():
        return missing_project(
            "password-security",
            "Password Security",
            "guesses",
            PASSWORD_TARGET,
            path,
        )

    with path.open("r", encoding="utf-8") as source:
        checkpoint = json.load(source)

    completed = int(checkpoint.get("Next", 0))
    target = int(checkpoint.get("Total", PASSWORD_TARGET))
    search_state = str(checkpoint.get("Status", "unknown")).lower()
    completed = max(0, min(completed, target))

    # Finding the sample satisfies the experiment even if the remaining search
    # space was never tested.
    goal_reached = search_state == "found"
    if search_state in {"found", "exhausted"}:
        state = "complete"
    elif recently_updated(path):
        state = "running"
    else:
        state = "stale"

    result = project_status(
        "password-security",
        "Password Security",
        "guesses",
        completed,
        target,
        state,
        path,
    )
    result["remaining"] = 0 if goal_reached else target - completed
    result["goalReached"] = goal_reached
    result["searchStatus"] = search_state
    return result


def project_status(
    project_id: str,
    name: str,
    unit: str,
    completed: int,
    target: int,
    state: str,
    path: Path,
) -> dict[str, Any]:
    """Create the common JSON shape used by both project cards."""

    remaining = max(0, target - completed)
    rate = DEFAULT_RATES.get(project_id)
    estimated_seconds = round(remaining / rate) if rate and state == "running" else None
    if remaining == 0:
        estimated_seconds = 0

    return {
        "id": project_id,
        "name": name,
        "unit": unit,
        "completed": completed,
        "target": target,
        "remaining": remaining,
        "percent": round((completed / target) * 100, 2) if target else 0,
        "state": state,
        "lastUpdated": timestamp_for(path),
        # Approximate runtime based on the measured speed of each experiment.
        "estimatedSecondsRemaining": estimated_seconds,
        "error": None,
    }


def missing_project(
    project_id: str,
    name: str,
    unit: str,
    target: int,
    path: Path,
) -> dict[str, Any]:
    """Return useful JSON when a progress file has not been created yet."""

    result = project_status(
        project_id,
        name,
        unit,
        0,
        target,
        "missing",
        path,
    )
    # Never publish the computer's local username or folder structure.
    result["error"] = "Progress data is not available yet."
    return result


def status_snapshot() -> dict[str, Any]:
    """Read both experiments and isolate errors to the affected card."""

    mine_path, password_path = progress_paths()
    projects: list[dict[str, Any]] = []

    for reader, path, project_id, name, unit, target in [
        (
            minesweeper_status,
            mine_path,
            "minesweeper",
            "Minesweeper",
            "games",
            MINE_TARGET,
        ),
        (
            password_status,
            password_path,
            "password-security",
            "Password Security",
            "guesses",
            PASSWORD_TARGET,
        ),
    ]:
        try:
            projects.append(reader(path))
        except (OSError, ValueError, KeyError, json.JSONDecodeError) as error:
            failed = missing_project(project_id, name, unit, target, path)
            failed["state"] = "error"
            failed["error"] = str(error)
            projects.append(failed)

    return {
        "generatedAt": datetime.now(tz=timezone.utc).isoformat(),
        "refreshSeconds": 10,
        "projects": projects,
    }


def public_status_snapshot() -> dict[str, Any]:
    """Return rounded progress without machine paths or exact activity times."""

    snapshot = status_snapshot()
    for project in snapshot["projects"]:
        rounding = 100 if project["id"] == "minesweeper" else 10_000_000
        completed = (project["completed"] // rounding) * rounding
        target = project["target"]
        project["completed"] = completed
        if project["state"] == "complete":
            project["target"] = completed
            project["remaining"] = 0
            project["percent"] = 100.0
        else:
            project["remaining"] = max(0, target - completed)
            project["percent"] = round((completed / target) * 100, 2) if target else 0
        estimate = project.get("estimatedSecondsRemaining")
        if isinstance(estimate, int) and estimate > 0:
            project["estimatedSecondsRemaining"] = round(estimate / 900) * 900
        project.pop("lastUpdated", None)
        project.pop("error", None)
        project.pop("searchStatus", None)
    snapshot["generatedAt"] = datetime.now(tz=timezone.utc).date().isoformat()
    snapshot["refreshSeconds"] = 3600
    return snapshot


class DashboardHandler(SimpleHTTPRequestHandler):
    """Serve dashboard files plus one read-only JSON endpoint."""

    # Avoid advertising the Python version in public HTTP response headers.
    server_version = "ScienceFairDashboard"
    sys_version = ""

    def end_headers(self) -> None:
        """Apply privacy and browser-safety headers to every response."""

        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Referrer-Policy", "no-referrer")
        self.send_header("Permissions-Policy", "camera=(), microphone=(), geolocation=()")
        super().end_headers()

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(
            *args,
            directory=str(DASHBOARD_DIRECTORY),
            **kwargs,
        )

    def log_message(self, message_format: str, *arguments: Any) -> None:
        # SimpleHTTPRequestHandler normally writes ordinary HTTP access lines to
        # stderr. Put them on stdout so the health watchdog does not mistake a
        # successful page request for an application error.
        message = message_format % arguments
        print(f"{self.address_string()} - {message}", flush=True)

    def do_GET(self) -> None:  # noqa: N802 - required by BaseHTTPRequestHandler
        route = urlparse(self.path).path
        if route == "/api/status":
            self.send_json(status_snapshot())
            return

        # Friendly aliases make both / and /dashboard open the same page.
        if route in {"/", "/dashboard"}:
            self.path = "/index.html"

        super().do_GET()

    def send_json(self, value: dict[str, Any]) -> None:
        payload = json.dumps(value, indent=2).encode("utf-8")
        self.send_response(HTTPStatus.OK)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(payload)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(payload)


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Serve the science fair progress dashboard."
    )
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", default=8080, type=int)
    parser.add_argument(
        "--snapshot",
        action="store_true",
        help="Print one JSON status response and exit.",
    )
    parser.add_argument(
        "--public-snapshot",
        type=Path,
        help="Write a rounded, privacy-safe status JSON file and exit.",
    )
    return parser.parse_args()


def main() -> int:
    arguments = parse_arguments()

    if arguments.snapshot:
        print(json.dumps(status_snapshot(), indent=2))
        return 0

    if arguments.public_snapshot:
        arguments.public_snapshot.write_text(
            json.dumps(public_status_snapshot(), indent=2) + "\n",
            encoding="utf-8",
        )
        return 0

    server = ThreadingHTTPServer(
        (arguments.host, arguments.port),
        DashboardHandler,
    )
    print(
        f"Science fair dashboard: http://{arguments.host}:{arguments.port}",
        flush=True,
    )

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nDashboard stopped.")
    finally:
        server.server_close()

    return 0


if __name__ == "__main__":
    sys.exit(main())

