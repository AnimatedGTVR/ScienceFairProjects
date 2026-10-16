# Beginner note: this is the Windows launcher. "dotnet" compiles and runs the
# C# program. Everything after the script name is passed to the program.
# Example: .\run.ps1 --repeats 5 --max-guesses 15000000
param([Parameter(ValueFromRemainingArguments = $true)][string[]]$ProgramArguments)
$ErrorActionPreference = 'Stop'
Set-Location $PSScriptRoot

if (-not (Get-Command dotnet -ErrorAction SilentlyContinue)) {
    throw '.NET 10 was not found. Install the .NET 10 SDK from https://dotnet.microsoft.com/download'
}
& dotnet run --project .\PasswordSecurity.csproj -c Release -- @ProgramArguments
exit $LASTEXITCODE
