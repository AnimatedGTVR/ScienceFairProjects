"""Regenerate and bundle the completed password-security project."""

import subprocess
import sys
import zipfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
PROJECT = HERE.parent.parent


def run(script):
    subprocess.run([sys.executable, str(HERE / script)], check=True, cwd=HERE)


def main():
    run("create_graphs.py")
    run("create_workbook.py")
    run("create_report.py")
    files = [
        HERE / "Password-Security-Final.xlsx",
        HERE / "Password-Security-Final-Report.docx",
        HERE / "Password-Security-Display-Board.docx",
        PROJECT / "FINAL-REPORT.md",
        PROJECT / "DISPLAY-BOARD.md",
        HERE / "challenge-summary.csv",
        HERE / "final-summary.csv",
        HERE / "challenge-attempts.png",
        HERE / "challenge-attempts.svg",
        HERE / "measured-cracking-time.png",
        HERE / "measured-cracking-time.svg",
        HERE / "search-space-growth.png",
        HERE / "search-space-growth.svg",
        HERE / "completed-search.png",
        HERE / "completed-search.svg",
        HERE.parent / "baseline" / "measurements.csv",
        HERE.parent / "baseline" / "summary.csv",
        HERE.parent / "baseline" / "theoretical.csv",
    ]
    package = HERE / "Password-Security-Science-Fair-Package.zip"
    with zipfile.ZipFile(package, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for path in files:
            archive.write(path, path.name)
    print(f"Created {package}")


if __name__ == "__main__":
    main()
