# Minesweeper

Train a Deep Q-Network on a 6 by 6 board with three mines. Compare learning rate,
exploration decay, and training duration while measuring evaluation win rate.

## Compatibility

The `project.py` launcher works on Windows, macOS, and Linux. Install Python 3.10
or newer first. This is a desktop command-line project; phones and ordinary web
browsers cannot run it directly. CPU training works everywhere supported by the
packages in `requirements.txt`; speed varies greatly by computer.

New to code? Read the repository's [beginner guide](../BEGINNER-GUIDE.md), then
run `--help`:

```text
Windows:       run.cmd --help
PowerShell:    .\run.ps1 --help
macOS/Linux:   ./run.sh --help
Direct Python: python project.py --help
```

On macOS/Linux, use `chmod +x run.sh` once if the downloaded file is not executable.

## Setup

Python 3.12 was used for the recorded runs. From this folder, use the command for
your operating system:

```text
Windows:      run.cmd setup
PowerShell:   .\run.ps1 setup
macOS/Linux:  ./run.sh setup
```

Setup creates `.venv`, the project's private package environment, and installs
the dependencies. It can take several minutes because the AI package is large.
Then replace `setup` with `test` to run three quick game-logic checks.

## Train and evaluate

```text
Windows:      run.cmd train --episodes 100
PowerShell:   .\run.ps1 train --episodes 100
macOS/Linux:  ./run.sh train --episodes 100
```

Replace `train --episodes 100` with `evaluate` to test the saved AI, or `status`
to inspect the latest training row without starting work. The `train.ps1` and
`evaluate.ps1` files remain as Windows compatibility shortcuts.

Training adds episodes to the saved model. Evaluation loads that model, disables
random exploration, and plays 1,000 games for a repeatable measurement. Train
before evaluating.

Training was finalized on October 19, 2026 after **249,830 games**. In the final
evaluation, the trained model won **901 of 2,000 fresh games (45.05%)**, while a
random baseline won **260 of 2,000 (13.0%)**. The trained model therefore won
about **3.47 times as often**. See the complete spreadsheet, report, graphs, raw
data, and downloadable archive in [`results/final`](results/final/).

The earlier [60,500-game interim evaluation](INTERIM-RESULTS.md) measured 303
wins in 1,000 fresh games, or 30.3%.

Settings: `models/dqn_agent/config.yaml`. Weights are saved in
`models/saved_models/`. Training data is in `models/dqn_agent/training_data.csv`;
plots are generated in `models/dqn_agent/plots/` when training exits. Evaluation
CSVs are written to `evaluation/logs/`.

Archive existing outputs and start from fresh weights for independent comparisons.
Keep board size and training budget fixed when testing a learning parameter.

## Validation

All three board tests passed. Training, saving, resuming, and evaluation were
verified. A 100-game benchmark took 56.76 seconds in training and 62.46 seconds
overall on the original CPU setup; see `benchmark.json`. Runtime varies with
hardware, game length, and background load. This is not evidence of learned skill.

Checkpoints are saved every 100 episodes and on normal exit. Checkpoint and CSV
writes are separate, so after a sudden shutdown the logged count may be ahead
of the model's persisted training state.

## Attribution

- [Science Buddies instructions](https://www.sciencebuddies.org/science-fair-projects/project-ideas/ArtificialIntelligence_p034/artificial-intelligence/rl_minesweeper)
- [Science Buddies source](https://github.com/science-buddies/reinforcement_learning_minesweeper)
- [Original environment](https://github.com/markov-labs/RL-Minesweeper)

Local changes correct the configuration name, load weights for evaluation, use
neural-network evaluation mode, match reward scaling, update the mine-placement
test, and provide cross-platform launchers.
