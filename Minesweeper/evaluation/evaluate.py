# evaluation/evaluate.py

import os
import json
import csv
import time
from typing import Type, Dict, List
from backend.game import GameSession
from models.base_agent import BaseAgent
from models.dqn_agent.dqn_agent import DQNAgent
from environment.minesweeper_env import MinesweeperEnv


def evaluate_agent(
    agent_class: Type[BaseAgent],
    num_episodes: int,
    width: int,
    height: int,
    num_mines: int,
    agent_config: Dict = None,
    verbose: bool = False,
    save_dir: str = None
):
    """
    Evaluate the agent and optionally log results and save replays.
    """
    os.makedirs(save_dir, exist_ok=True) if save_dir else None
    agent_config = agent_config or {}

    # Create agent depending on class type
    if agent_class is DQNAgent or agent_class.__name__ in ("DQNAgent", "DQN_Agent"):
        agent = agent_class(
            config_name=agent_config.get("config_name", "minesweeper_1"),
            config_path=agent_config.get(
                "config_path",
                os.path.join("models", "dqn_agent", "config.yaml"),
            ),
        )
        agent.load(agent_config.get("checkpoint", "models/saved_models/dqn_model.pth"))
        agent.policy_net.eval()
        agent.target_net.eval()
    else:
        agent = agent_class(config=agent_config)

    # For evaluation - set epsilon to 0
    if hasattr(agent, "epsilon"):
        agent.epsilon = 0.0
    summary = []
    replays = []

    wins = 0
    total_moves = 0

    for ep in range(1, num_episodes + 1):
        env = MinesweeperEnv(
            board_size=(width, height),
            num_mines=num_mines,
            reward_scale=50   # match training
        )

        obs, _info = env.reset()
        moves = 0
        replay = []

        terminated = False
        truncated = False

        while not (terminated or truncated):

            # Agent chooses action based on encoded observation
            action = agent.act(obs)

            replay.append({
                "step": moves,
                "state": obs,
                "action": action
            })

            # Step environment
            obs, reward, terminated, truncated, _info = env.step(action)
            moves += 1

        # Extract results
        won = int(env.game.won)
        wins += won
        total_moves += moves

        summary.append({
            "episode": ep,
            "moves": moves,
            "won": bool(won),
            "score": env.game.get_score()
        })

        if save_dir:
            replays.append({
                "episode": ep,
                "won": bool(won),
                "replay": replay
            })

        if verbose:
            print(f"Episode {ep}: {'WIN' if won else 'loss'} in {moves} moves "
                  f"(score: {env.game.get_score():.2f})")
        elif ep % max(1, num_episodes // 10) == 0:
            print(
                f"Evaluation progress: {ep}/{num_episodes} games, "
                f"{wins} wins so far",
                flush=True,
            )

    # Final stats
    win_rate = wins / num_episodes
    avg_moves = total_moves / num_episodes

    print(f"\n{agent_class.__name__} - Win rate: {win_rate:.2%}, "
          f"Avg moves: {avg_moves:.1f}")

    # Save logs
    if save_dir:
        timestamp = int(time.time())

        # Save summary CSV
        with open(f"{save_dir}/summary_{timestamp}.csv", "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=["episode", "moves", "won", "score"])
            writer.writeheader()
            writer.writerows(summary)

        # Save replay JSON
        with open(f"{save_dir}/replays_{timestamp}.json", "w") as f:
            # json.dump(replays, f, indent=2)
            pass # Pass to avoid saving JSON for now


def evaluate_multiple_difficulties(agent_class: Type[BaseAgent], agent_config: Dict = None):
    difficulties = [
        {"width": 6, "height": 6, "num_mines": 3, "label": "easy"},
    ]
    for setting in difficulties:
        print(f"\n== Difficulty: {setting['label']} ==")
        evaluate_agent(
            agent_class=agent_class,
            num_episodes=50,
            width=setting["width"],
            height=setting["height"],
            num_mines=setting["num_mines"],
            agent_config=agent_config,
            save_dir=f"evaluation/logs/{agent_class.__name__.lower()}_{setting['label']}",
            verbose=False
        )



if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Measure the trained Minesweeper AI on fresh games."
    )
    parser.add_argument(
        "--episodes",
        type=int,
        default=1000,
        help="number of fresh games to evaluate (default: 1000)",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="print the result of every game",
    )
    arguments = parser.parse_args()

    if arguments.episodes < 1:
        parser.error("--episodes must be at least 1")

    evaluate_agent(
        agent_class=DQNAgent,
        num_episodes=arguments.episodes,
        width=6,
        height=6,
        num_mines=3,
        agent_config={
            "config_name": "minesweeper_1",
            "config_path": "models/dqn_agent/config.yaml"
        },
        verbose=arguments.verbose,
        save_dir="evaluation/logs/dqn_agent"
    )

