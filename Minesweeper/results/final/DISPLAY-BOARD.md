# Display Board Notes

## Question
Can a Deep Q-Network learn to win Minesweeper more often than random play?

## Hypothesis
More training will cause the DQN to win more often than a random agent.

## Method
I trained one DQN for **249,830 games** on 6×6 boards with three mines. I then tested the trained model and a random baseline on **2,000 fresh games each**.

## Results
- Trained DQN: **901 wins (45.05%)**
- Random baseline: **260 wins (13.00%)**
- Improvement: **3.47× the random win rate**
- Training win rate: **1.48% early → 15.53% late**

## Conclusion
My hypothesis was supported. The trained model won much more often than random play, showing that it learned useful Minesweeper decisions. It was not perfect and still lost more than half of its final games.

## Limits
One model, one board size, and less than the suggested 300,000 training games. More independent trials and stronger comparison agents would improve the experiment.
