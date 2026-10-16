# Interim Minesweeper Evaluation

This measurement was taken after 60,500 training games. Training continued
toward the 300,000-game target afterward, so this is a checkpoint rather than
the finished experiment.

## Experiment

The trained Deep Q-Network played fresh 6 by 6 Minesweeper boards containing
three mines. Random exploration was disabled during evaluation, so every action
came from the saved model.

- **Independent variable:** amount of AI training
- **Dependent variable:** evaluation win rate
- **Controlled settings:** board size, mine count, model structure, reward rules,
  and zero evaluation exploration

## Results

| Model stage | Evaluation games | Wins | Win rate | Average moves |
|---|---:|---:|---:|---:|
| Earlier saved model | 100 | 13 | 13.0% | 3.36 |
| Model after 60,500 training games | 1,000 | 303 | 30.3% | 6.12 |

The 1,000-game result has a 95% Wilson confidence interval of approximately
**27.53% to 33.22%**. This interval describes sampling uncertainty for fresh
boards under the same evaluation settings.

The raw evaluation is stored locally as
`evaluation/logs/dqn_agent/summary_1792108873.csv`. Its SHA-256 checksum is:

```text
D842A6C0C6103495A6D548272CAE1E48C33EA3EEB17EECE8BE04308CFC7F8047
```

## Interim conclusion

The later model had a substantially higher observed win rate than the earlier
saved model. This supports the idea that additional training improved performance
for this AI and board configuration. A new evaluation after 300,000 games will
provide the final comparison.

The comparison is not a perfect controlled replication because the earlier
evaluation used only 100 games while the later evaluation used 1,000. More
independent training runs would be needed to separate the effect of training
duration from random variation between model runs.
