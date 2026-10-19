"""Run the final trained-versus-random Minesweeper comparison."""

import argparse
import csv
import os
import random
import time

import numpy as np
import torch

from environment.minesweeper_env import MinesweeperEnv
from models.dqn_agent.dqn_agent import DQNAgent


def build_agent(kind):
    if kind == "trained_dqn":
        agent = DQNAgent(config_name="minesweeper_1")
        agent.load("models/saved_models/dqn_model.pth")
        agent.policy_net.eval()
        agent.target_net.eval()
        agent.epsilon = 0.0
        return agent
    return None


def choose_action(agent, kind, observation, action_rng):
    if kind == "trained_dqn":
        return agent.act(observation)
    board = np.asarray(observation["board"])
    candidates = np.argwhere(board == -3)
    if len(candidates) == 0:
        return (0, 0, 0)
    row, column = candidates[action_rng.randrange(len(candidates))]
    # A reveal-only random player is an easy-to-explain baseline.
    return (int(row), int(column), 0)


def evaluate(kind, games, seed):
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    agent = build_agent(kind)
    action_rng = random.Random(seed + (1 if kind == "trained_dqn" else 2))
    rows = []
    started = time.perf_counter()

    for game_number in range(1, games + 1):
        env = MinesweeperEnv(board_size=(6, 6), num_mines=3, reward_scale=50)
        observation, _ = env.reset(seed=seed + game_number)
        moves = 0
        terminated = truncated = False
        while not (terminated or truncated):
            action = choose_action(agent, kind, observation, action_rng)
            if moves == 0:
                # The board places mines lazily after the first click. Reset the
                # mine generator here so move-selection randomness cannot alter it.
                random.seed(seed + game_number)
            observation, reward, terminated, truncated, _ = env.step(action)
            moves += 1
        rows.append({
            "agent": kind,
            "game": game_number,
            "won": int(env.game.won),
            "moves": moves,
            "score": env.game.get_score(),
        })
        if game_number % 250 == 0:
            print(f"{kind}: {game_number}/{games}", flush=True)

    wins = sum(row["won"] for row in rows)
    print(f"{kind}: {wins}/{games} wins ({wins / games:.1%}) in {time.perf_counter() - started:.1f}s")
    return rows


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--games", type=int, default=2000)
    parser.add_argument("--output", default="results/final/final-evaluation-games.csv")
    args = parser.parse_args()
    if args.games < 1:
        parser.error("--games must be positive")

    all_rows = evaluate("trained_dqn", args.games, 20261019)
    all_rows.extend(evaluate("random_agent", args.games, 20261019))
    os.makedirs(os.path.dirname(args.output), exist_ok=True)
    with open(args.output, "w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=["agent", "game", "won", "moves", "score"])
        writer.writeheader()
        writer.writerows(all_rows)
    print(f"Saved {args.output}")


if __name__ == "__main__":
    main()
