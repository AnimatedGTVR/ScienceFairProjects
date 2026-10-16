#!/usr/bin/env sh
# Starts the progress website on macOS or Linux.
# Open http://127.0.0.1:8080 and press Ctrl+C here to stop the server.
set -eu
cd "$(dirname "$0")"
exec python3 server.py

