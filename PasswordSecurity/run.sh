#!/usr/bin/env sh
# Beginner note: this launcher works on macOS and Linux. "dotnet" compiles and
# runs the C# program. "$@" forwards your options to it. Example:
# ./run.sh --repeats 5 --max-guesses 15000000
set -eu
cd "$(dirname "$0")"

if ! command -v dotnet >/dev/null 2>&1; then
  echo ".NET 10 was not found. Install the .NET 10 SDK from https://dotnet.microsoft.com/download" >&2
  exit 1
fi
exec dotnet run --project PasswordSecurity.csproj -c Release -- "$@"
