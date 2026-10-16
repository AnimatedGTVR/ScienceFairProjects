# Start Here: Minesweeper

The main [README](README.md) has complete Windows, macOS, and Linux instructions.
If programming is new to you, read the repository's
[beginner guide](../BEGINNER-GUIDE.md) first.

Quick start from this folder:

```text
Windows Command Prompt:  run.cmd setup
Windows PowerShell:      .\run.ps1 setup
macOS or Linux:          ./run.sh setup
```

After setup, use the same launcher with one of these commands:

- `test` checks the game code.
- `train --episodes 100` plays 100 additional training games.
- `evaluate` tests the saved AI over 100 games.
- `status` prints the most recent training row.
- `--help` displays the available commands.

Training resumes saved state and can take a long time. Evaluation requires a
checkpoint created by training. Setup checks prove the software runs; they do
not prove the AI has learned a strong strategy.
