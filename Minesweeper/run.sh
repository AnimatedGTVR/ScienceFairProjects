#!/usr/bin/env sh
# Beginner note: this is a tiny launcher for macOS and Linux. A shell script is
# simply a list of terminal instructions. "$@" passes everything you typed after
# this filename to project.py. Example: ./run.sh train --episodes 100
set -eu
cd "$(dirname "$0")"

# Some systems call Python "python3" and others call it "python".
if command -v python3 >/dev/null 2>&1; then
  exec python3 project.py "$@"
elif command -v python >/dev/null 2>&1; then
  exec python project.py "$@"
else
  echo "Python 3 was not found. Install Python 3.10 or newer, then try again." >&2
  exit 1
fi
