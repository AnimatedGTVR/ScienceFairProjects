# Beginner Guide: What Does Any of This Do?

You do not need previous programming experience to run these projects. You need
a Windows, macOS, or Linux computer, permission to install software, and enough
free time for the experiments to run. Phones, tablets, Chromebooks without Linux,
and web browsers are not supported by these local programs.

## Five words that make the instructions less mysterious

- **Program:** instructions written for a computer. Python and C# are the two
  programming languages used here.
- **Terminal:** a window where you type commands. On Windows, use PowerShell or
  Command Prompt. On macOS, open Terminal. Linux also has a Terminal app.
- **Folder / directory:** two names for the same thing: a container of files.
- **Dependency:** code written by somebody else that this project needs. The
  setup command installs dependencies automatically.
- **Argument / option:** extra information after a command. In
  `train --episodes 100`, `--episodes 100` tells the program how many games.

## How to use a terminal

1. Open a terminal.
2. Change into the project folder. `cd` means "change directory."
3. Type a command from the project's README and press Enter.
4. Read the final lines. If a command fails, copy the complete error message.

Paths containing spaces should be inside quotes. Examples:

```powershell
# Windows PowerShell
cd "C:\path\to\ScienceFairProjects\Minesweeper"
```

```sh
# macOS or Linux
cd "/path/to/ScienceFairProjects/Minesweeper"
```

The `#` lines above are comments for people. The terminal ignores them.

## What Minesweeper does

The program creates a Minesweeper board in computer memory. An AI agent chooses
one square at a time. It receives a numerical reward or penalty, stores examples
in replay memory, and adjusts a neural network. One complete game is an
**episode**. Training means playing many episodes and updating the network.

Important files and terms:

- `.venv` is a private copy of Python's installed packages for this project. It
  prevents this project from changing other Python projects on the computer.
- `requirements.txt` lists the packages to install.
- A **checkpoint** is the AI's saved state. It lets training resume later.
- **Epsilon** is the chance that the agent explores with a random move.
- Evaluation sets epsilon to zero, plays 100 games, and reports the win rate.
- A CSV is a text table. Open it in Excel, Numbers, LibreOffice, or Google Sheets.

Training uses substantial CPU time. Closing the terminal stops a foreground run.
Sleep, shutdown, and power loss stop it too. Saved checkpoints protect most work,
but the newest unsaved episodes may be repeated.

## What Password Security does

The C# program makes candidate strings such as `000`, `001`, and `002`. It runs
each string through MD5, a mathematical hash function, and compares the result
with a local target hash. It counts guesses and measures time. It does not sign
in to websites, send network requests, or test real accounts.

Important terms:

- **Brute force:** systematically try every candidate in a defined search space.
- **Dictionary search:** try words from a prepared list because people often use
  predictable words.
- **Hash:** a one-way fingerprint of data. Hashing is not encryption.
- **Search space:** all candidates allowed by a rule. If each position has 62
  choices, length 6 contains 62^6 = 56,800,235,584 candidates.
- **Independent variable:** the condition deliberately changed, such as length.
- **Dependent variable:** the measured result, such as guesses or seconds.

The educational challenge uses fast, unsalted MD5. Modern systems should use slow,
salted password-hashing algorithms. These timings do not predict the time needed
to enter a real account, and this code should only be used with the included local
samples or other data you are authorized to test.

## Reading source code without panicking

Start at the top-level launcher and follow one command:

- Minesweeper: `project.py` explains each action and starts the larger modules.
- Password Security: `Program.cs` contains `Main`, the program's front door.

Common punctuation:

- `()` passes information to a function.
- `{}` groups C# instructions; indentation groups Python instructions.
- `=` stores a value under a name.
- `==` asks whether two values are equal.
- `if` makes a decision.
- `for` and `foreach` repeat instructions.
- `return` sends a result back to the caller.
- Lines beginning with `#` in Python/shell or `//` in C# are human comments.

Do not change ten things at once. Make one small change, run the tests, and write
down the result. That is debugging, and professional programmers do it constantly.
