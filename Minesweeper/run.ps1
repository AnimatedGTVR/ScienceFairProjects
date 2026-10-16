# Beginner note: this is the Windows launcher. A PowerShell script is just a file
# of terminal instructions. Everything after this filename is passed to project.py.
# Example: .\run.ps1 train --episodes 100
param([Parameter(ValueFromRemainingArguments = $true)][string[]]$ProjectArguments)
$ErrorActionPreference = 'Stop' # Stop immediately instead of hiding an error.
Set-Location $PSScriptRoot      # Work from the folder containing this script.

if (Get-Command python -ErrorAction SilentlyContinue) {
    & python .\project.py @ProjectArguments
} elseif (Get-Command py -ErrorAction SilentlyContinue) {
    & py -3 .\project.py @ProjectArguments
} else {
    throw 'Python 3 was not found. Install Python 3.10 or newer, then try again.'
}
exit $LASTEXITCODE
