# Minesweeper Reinforcement Learning: Final Report

## Question

Does reinforcement learning improve a computer agent's Minesweeper win rate compared with random play on a 6×6 board containing three mines?

## Hypothesis

I predicted that if the agent trained through many games, then it would win more often than a program choosing unrevealed squares randomly.

## Background

Minesweeper is partially observable because the mines are hidden. A reinforcement-learning agent repeatedly observes the visible board, chooses an action, and receives a reward. This project used a Deep Q-Network (DQN), which uses a neural network to estimate the future value of possible actions.

## Variables

- **Independent variable:** agent type and amount of training.
- **Dependent variable:** win rate on fresh Minesweeper boards.
- **Controls:** 6×6 board, three mines, game rules, evaluation seed, and 2,000 final games per agent.

## Procedure

1. I configured a 6×6 board with three mines.
2. I trained the DQN for 249,830 games while recording reward, loss, epsilon, and game length.
3. I saved the trained model.
4. I disabled random exploration for evaluation.
5. I tested the trained model on 2,000 fresh boards.
6. I tested a reveal-only random baseline on 2,000 fresh boards generated with the same seed sequence.
7. I compared wins, win rates, average moves, training trends, and 95% confidence intervals.

## Results

| Agent | Games | Wins | Win rate | Average moves | 95% confidence interval |
|---|---:|---:|---:|---:|---:|
| Trained DQN | 2,000 | 901 | 45.05% | 6.27 | 42.88%–47.24% |
| Random baseline | 2,000 | 260 | 13.00% | 3.10 | 11.60%–14.55% |

The trained DQN won **3.47 times as often** as random play. During training, its observed win rate increased from **1.48%** in the first 10,000 games to **15.53%** in the final 9,830 games. Mean game length increased from **4.07** to **5.01** moves, meaning the agent generally survived longer.

## Conclusion

The results support my hypothesis for this model and board setup. The trained agent won 45.05% of its final games, compared with 13.00% for the random baseline. Training produced a large practical improvement, although the model still lost more games than it won. This is expected because Minesweeper includes hidden information and some board states require uncertain choices.

## Limitations

- Training stopped at 249,830 games because of available computer time, below Science Buddies' suggested starting point of 300,000.
- Only one final trained model was measured, so repeated independent training runs would better separate learning from luck during training.
- The conclusion applies to this 6×6, three-mine environment and reward system.
- The random baseline only reveals random unopened squares; other rule-based strategies could be stronger comparisons.
- A win-rate estimate has sampling uncertainty even with 2,000 test games.

## Future Work

Train several fresh models with different learning rates and epsilon-decay settings, evaluate each on the same seeded boards, and compare DQN with a logic-based Minesweeper solver, Double DQN, or Dueling DQN.

## Sources

1. Tracey Ngo, “Train a Reinforcement Learning AI to Play Minesweeper,” Science Buddies, updated February 27, 2026. https://www.sciencebuddies.org/science-fair-projects/project-ideas/ArtificialIntelligence_p034/artificial-intelligence/rl_minesweeper
2. Volodymyr Mnih et al., “Human-level control through deep reinforcement learning,” *Nature* 518, 529–533 (2015). https://doi.org/10.1038/nature14236
3. Gymnasium Documentation, “Basic Usage” and “Training an Agent.” https://gymnasium.farama.org/main/introduction/basic_usage/
4. Richard S. Sutton and Andrew G. Barto, *Reinforcement Learning: An Introduction*, second edition. http://incompleteideas.net/book/the-book-2nd.html
