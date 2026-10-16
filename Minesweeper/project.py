"""Beginner-friendly, cross-platform command center for the Minesweeper project.

You do not need to understand this file to use it. A *script* is just a file of
instructions for the computer. Run ``python project.py --help`` to see the
available commands. On macOS or Linux, ``python3`` may be the command instead.

Why this file exists:
* Windows, macOS, and Linux put Python virtual environments in different places.
* This script finds the correct place automatically.
* It runs the longer Python commands for you and stops if something fails.
"""

from __future__ import annotations

import argparse
import csv
import os
from pathlib import Path
import subprocess
import sys


# __file__ means "this file." Resolving its parent makes every command run from
# the project folder even if the user opened a terminal somewhere else.
ROOT = Path(__file__).resolve().parent
VENV = ROOT / ".venv"


def virtual_python() -> Path:
    """Return the Python executable inside .venv for the current operating system."""
    if os.name == "nt":  # nt is Python's name for Windows.
        return VENV / "Scripts" / "python.exe"
    return VENV / "bin" / "python"  # macOS and Linux use this layout.


def run(command: list[str], *, env: dict[str, str] | None = None) -> None:
    """Print and run a command; raise an error immediately if it fails."""
    print("Running:", " ".join(command), flush=True)
    subprocess.run(command, cwd=ROOT, env=env, check=True)


def setup() -> None:
    """Create an isolated Python environment and install project packages."""
    python = virtual_python()
    if not python.exists():
        print("Creating .venv (a private box for this project's Python packages)...")
        run([sys.executable, "-m", "venv", str(VENV)])
    print("Installing the packages listed in requirements.txt...")
    run([str(python), "-m", "pip", "install", "-r", "requirements.txt"])
    print("Setup complete. Next, run: python project.py test")


def require_environment() -> Path:
    """Give a useful message instead of a confusing missing-file error."""
    python = virtual_python()
    if not python.exists():
        raise SystemExit(
            "The project environment does not exist yet. Run "
            "'python project.py setup' first (or use python3 on macOS/Linux)."
        )
    return python


def project_environment() -> dict[str, str]:
    """Return environment settings used by training and evaluation."""
    env = os.environ.copy()
    env["PYTHONUTF8"] = "1"  # Makes symbols and text print consistently.
    # Two math threads keeps the computer responsive. Advanced users may change
    # these values before running the script; setdefault preserves their choice.
    env.setdefault("OMP_NUM_THREADS", "2")
    env.setdefault("MKL_NUM_THREADS", "2")
    return env


def train(episodes: int) -> None:
    """Play training games and update the neural-network checkpoint."""
    run(
        [str(require_environment()), "-m", "models.dqn_agent.dqn_agent",
         "--episodes", str(episodes)],
        env=project_environment(),
    )


def evaluate() -> None:
    """Load the saved model and measure it over 100 games."""
    checkpoint = ROOT / "models" / "saved_models" / "dqn_model.pth"
    if not checkpoint.exists():
        raise SystemExit("No trained model exists yet. Run a training command first.")
    run(
        [str(require_environment()), "-m", "evaluation.evaluate"],
        env=project_environment(),
    )


def test() -> None:
    """Run small checks that catch broken setup or game logic."""
    run([str(require_environment()), "-m", "unittest", "discover", "-s", "tests", "-v"])


def status() -> None:
    """Show the latest logged episode without starting any work."""
    data_path = ROOT / "models" / "dqn_agent" / "training_data.csv"
    if not data_path.exists():
        print("No training data yet. The model has not logged an episode.")
        return
    with data_path.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    if not rows:
        print("The training file exists but contains no episode rows.")
        return
    latest = rows[-1]
    print(f"Latest logged episode: {latest['Episode']}")
    print(f"Latest reward: {latest['Total Reward']}")
    print(f"Current exploration rate (epsilon): {latest['Epsilon']}")
    print("Note: after a power loss, logged rows can be ahead of the last saved checkpoint.")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Set up, test, train, evaluate, or inspect the Minesweeper AI."
    )
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("setup", help="Create .venv and install required packages.")
    commands.add_parser("test", help="Check that the board code works.")
    training = commands.add_parser("train", help="Train or resume the AI.")
    training.add_argument(
        "--episodes", type=int, default=100,
        help="Number of additional games to play (default: 100).",
    )
    commands.add_parser("evaluate", help="Measure the saved AI over 100 games.")
    commands.add_parser("status", help="Show the latest training data.")
    args = parser.parse_args()
    if args.command == "setup":
        setup()
    elif args.command == "test":
        test()
    elif args.command == "train":
        if args.episodes < 1:
            parser.error("--episodes must be at least 1")
        train(args.episodes)
    elif args.command == "evaluate":
        evaluate()
    elif args.command == "status":
        status()


if __name__ == "__main__":
    main()
