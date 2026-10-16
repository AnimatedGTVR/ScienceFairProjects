# Password Security

C# experiments comparing password length, character sets, and guessing methods.
The program checks classroom sample hashes locally.

## Compatibility

The .NET program works on Windows, macOS, and Linux wherever the .NET 10 SDK is
available, including common Intel/AMD and ARM computers. It does not need Python.
It is not a phone app or browser page. New programmers should first read the
repository's [beginner guide](../BEGINNER-GUIDE.md).

Launchers:

```text
Windows:      run.cmd --help
PowerShell:   .\run.ps1 --help
macOS/Linux:  ./run.sh --help
Direct .NET:  dotnet run -c Release -- --help
```

On macOS/Linux, use `chmod +x run.sh` once if needed.

## Setup and validation

Install the [.NET 10 SDK](https://dotnet.microsoft.com/download). No third-party
NuGet packages are needed. From this folder:

```powershell
dotnet build -c Release
dotnet run -c Release -- --self-test
dotnet run -c Release -- --test-import
```

`build` translates human-readable C# into a runnable program. `--self-test` checks
guess order and counts. `--test-import` checks that challenge data is read safely.

## Run the experiment

```powershell
dotnet run -c Release -- --repeats 5 --max-guesses 15000000
```

This produces 120 trials, raw CSVs, summary statistics, theoretical calculations,
and a report in a new results folder. See the [recorded baseline](results/baseline/REPORT.md).
Brute-force targets are last in the enumeration order, measuring worst-case
effort for a known length. Incomplete searches are not measured crack times.
Minesweeper ran concurrently during the recorded trials, affecting timing.

## Science Buddies challenges

```powershell
dotnet run -c Release -- --challenge 0
dotnet run -c Release -- --challenge 6 --extended
dotnet run -c Release -- --challenge 6 --patterns
dotnet run -c Release -- --challenge 6 --leet
```

Choose a challenge from 0-6. The supplied Python file is read as data, while
guessing runs in C#. The supplied dictionary contains 435 words. Default methods
stop at 15 million guesses or 30 seconds; extended modes allow 150 million or
120 seconds per method. Enumeration order differs from the Python starter.

- [Challenge results](CHALLENGE-RESULTS.md): passwords 0-5 solved.
- [Challenge 6 progress](CHALLENGE-6-PROGRESS.md): additional unsuccessful searches.

## Resume a longer search

```powershell
dotnet run -c Release -- --resume-six
```

Tests six alphanumeric characters: 56,800,235,584 possibilities. Saves the next
position every million attempts in `password-search-state.json`. Rerunning resumes;
an abrupt interruption can repeat up to a million unsaved attempts. Stops on a
match or exhaustion. Keep the checkpoint with the same challenge source file.

## Attribution and limitations

[Science Buddies project instructions](https://www.sciencebuddies.org/science-fair-projects/project-ideas/CompSci_p046/computer-science/password-security-how-easily-can-your-password-be-hacked)

Files in `original/` are Science Buddies materials supplied by the user and retain
their original attribution. The C# implementation was written with AI assistance.
Fast unsalted MD5 matches the educational challenge, not modern password storage
or real account protections. Hashing is not encryption; collisions are possible.
