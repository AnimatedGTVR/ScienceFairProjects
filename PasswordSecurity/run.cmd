@echo off
rem Beginner note: this Windows Command Prompt launcher starts the C# program.
rem %* means "pass along every option I typed after run.cmd".
cd /d "%~dp0"
dotnet --version >nul 2>nul
if errorlevel 1 (
  echo .NET 10 was not found. Install the .NET 10 SDK from https://dotnet.microsoft.com/download
  exit /b 1
)
dotnet run --project PasswordSecurity.csproj -c Release -- %*
