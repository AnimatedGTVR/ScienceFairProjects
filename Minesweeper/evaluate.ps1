# Windows compatibility shortcut. "Evaluate" means load the trained AI, let it
# play 100 games without random exploration, and calculate its win rate.
$ErrorActionPreference = 'Stop'
& "$PSScriptRoot\run.ps1" evaluate
exit $LASTEXITCODE
