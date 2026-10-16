# Windows compatibility shortcut. New users should use run.ps1, which explains
# every command. This wrapper remains so older instructions still work.
param([ValidateRange(1, 1000000)][int]$Episodes = 100)
$ErrorActionPreference = 'Stop'
& "$PSScriptRoot\run.ps1" train --episodes $Episodes
exit $LASTEXITCODE
