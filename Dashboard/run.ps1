# Starts the progress website on Windows.
# Open http://127.0.0.1:8080 after this script prints that it is ready.
# Press Ctrl+C in this window when you want to stop the website.
$ErrorActionPreference = 'Stop'
Set-Location $PSScriptRoot

if (Get-Command python -ErrorAction SilentlyContinue) {
    & python .\server.py
}
elseif (Get-Command py -ErrorAction SilentlyContinue) {
    & py -3 .\server.py
}
else {
    throw 'Python 3 was not found. Install Python 3.10 or newer.'
}

exit $LASTEXITCODE

