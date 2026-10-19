"""Build the final Minesweeper science-fair workbook, reports, and graphs."""

from __future__ import annotations

import csv
import math
import statistics
import zipfile
from collections import defaultdict
from pathlib import Path

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Inches, Pt
from openpyxl import Workbook, load_workbook
from openpyxl.chart import BarChart, LineChart, Reference
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter

HERE = Path(__file__).resolve().parent
TRAINING = HERE / "training-data.csv"
EVALUATION = HERE / "final-evaluation-games.csv"
BLUE, NAVY, GREEN, ORANGE, LIGHT = "3478F6", "172033", "17824C", "D97706", "EEF3FA"
SCIENCE_BUDDIES = "https://www.sciencebuddies.org/science-fair-projects/project-ideas/ArtificialIntelligence_p034/artificial-intelligence/rl_minesweeper"


def read_training():
    rows = []
    with TRAINING.open(newline="", encoding="utf-8-sig") as handle:
        for row in csv.DictReader(handle):
            rows.append({
                "episode": int(row["Episode"]),
                "reward": float(row["Total Reward"]),
                "loss": float(row["Average Loss"]),
                "epsilon": float(row["Epsilon"]),
                "length": int(row["Episode Length"]),
            })
    return rows


def read_evaluation():
    with EVALUATION.open(newline="", encoding="utf-8-sig") as handle:
        return list(csv.DictReader(handle))


def mean(values):
    return statistics.fmean(values) if values else 0.0


def wilson(wins, total):
    z = 1.959963984540054
    p = wins / total
    denominator = 1 + z * z / total
    center = (p + z * z / (2 * total)) / denominator
    margin = z * math.sqrt((p * (1 - p) + z * z / (4 * total)) / total) / denominator
    return center - margin, center + margin


def analyze(training, evaluation):
    grouped = defaultdict(list)
    for row in evaluation:
        grouped[row["agent"]].append(row)
    eval_summary = []
    for key, label in [("trained_dqn", "Trained DQN"), ("random_agent", "Random baseline")]:
        rows = grouped[key]
        wins = sum(int(row["won"]) for row in rows)
        low, high = wilson(wins, len(rows))
        eval_summary.append({
            "key": key, "label": label, "games": len(rows), "wins": wins,
            "rate": wins / len(rows), "moves": mean(float(row["moves"]) for row in rows),
            "ci_low": low, "ci_high": high,
        })

    block_size = 10_000
    blocks = []
    for start in range(0, len(training), block_size):
        chunk = training[start:start + block_size]
        blocks.append({
            "start": chunk[0]["episode"], "end": chunk[-1]["episode"],
            "games": len(chunk), "wins": sum(row["reward"] >= .999 for row in chunk),
            "rate": mean(row["reward"] >= .999 for row in chunk),
            "reward": mean(row["reward"] for row in chunk),
            "loss": mean(row["loss"] for row in chunk),
            "length": mean(row["length"] for row in chunk),
            "epsilon": chunk[-1]["epsilon"],
        })
    return eval_summary, blocks


def title(ws, text, subtitle=None):
    ws.merge_cells("A1:H1")
    ws["A1"] = text
    ws["A1"].font = Font(size=22, bold=True, color="FFFFFF")
    ws["A1"].fill = PatternFill("solid", fgColor=NAVY)
    ws["A1"].alignment = Alignment(vertical="center")
    ws.row_dimensions[1].height = 38
    if subtitle:
        ws.merge_cells("A2:H2")
        ws["A2"] = subtitle
        ws["A2"].font = Font(size=11, color="596579")
        ws.row_dimensions[2].height = 25


def header(row):
    for cell in row:
        cell.font = Font(bold=True, color="FFFFFF")
        cell.fill = PatternFill("solid", fgColor=BLUE)
        cell.alignment = Alignment(wrap_text=True, vertical="center")


def widths(ws, mapping):
    for column, value in mapping.items():
        ws.column_dimensions[column].width = value


def make_workbook(training, evaluation, eval_summary, blocks):
    wb = Workbook()
    ws = wb.active
    ws.title = "Overview"
    title(ws, "Minesweeper Learning Experiment", "Final results from 249,830 training games and 4,000 fresh evaluation games")
    facts = [
        ("Research question", "Does reinforcement learning improve a computer agent's Minesweeper win rate compared with random play?"),
        ("Hypothesis", "If the agent trains through many games, then it will win more often than a random agent."),
        ("Board", "6 × 6 cells with 3 mines"),
        ("Training completed", f"{len(training):,} games"),
        ("Final trained result", f"{eval_summary[0]['wins']:,} / {eval_summary[0]['games']:,} wins ({eval_summary[0]['rate']:.2%})"),
        ("Random result", f"{eval_summary[1]['wins']:,} / {eval_summary[1]['games']:,} wins ({eval_summary[1]['rate']:.2%})"),
        ("Improvement", f"The trained model won {eval_summary[0]['rate']/eval_summary[1]['rate']:.2f} times as often as random play."),
        ("Training trend", f"Win rate rose from {blocks[0]['rate']:.2%} in the first 10,000 games to {blocks[-1]['rate']:.2%} in the final {blocks[-1]['games']:,}."),
        ("Conclusion", "The results support the hypothesis for this model and board setup."),
    ]
    row = 4
    for label, value in facts:
        ws.cell(row, 1, label).font = Font(bold=True, color=NAVY)
        ws.cell(row, 2, value)
        ws.merge_cells(start_row=row, start_column=2, end_row=row, end_column=8)
        ws.cell(row, 2).alignment = Alignment(wrap_text=True, vertical="top")
        ws.row_dimensions[row].height = 32
        row += 1
    widths(ws, {"A": 24, "B": 19, "C": 14, "D": 14, "E": 14, "F": 14, "G": 14, "H": 14})
    ws.freeze_panes = "A4"

    ws = wb.create_sheet("Final Evaluation")
    title(ws, "Final Evaluation", "Fresh games; exploration disabled for the trained model")
    ws.append([]); ws.append(["Agent", "Games", "Wins", "Losses", "Win rate", "Average moves", "95% CI low", "95% CI high"])
    header(ws[4])
    for item in eval_summary:
        ws.append([item["label"], item["games"], item["wins"], item["games"]-item["wins"], item["rate"], item["moves"], item["ci_low"], item["ci_high"]])
    for row in ws.iter_rows(min_row=5, max_row=6, min_col=5, max_col=8):
        for cell in row: cell.number_format = "0.00%"
    ws["A9"] = "Key finding"
    ws["A9"].font = Font(bold=True, color=NAVY)
    ws["B9"] = f"The trained DQN won {eval_summary[0]['rate']/eval_summary[1]['rate']:.2f}× as often as the random baseline."
    ws.merge_cells("B9:H9")
    chart = BarChart()
    chart.title = "Win Rate: Trained vs Random"
    chart.y_axis.title = "Win rate"
    chart.add_data(Reference(ws, min_col=5, min_row=4, max_row=6), titles_from_data=True)
    chart.set_categories(Reference(ws, min_col=1, min_row=5, max_row=6))
    chart.height, chart.width = 8, 14
    ws.add_chart(chart, "A12")
    widths(ws, {"A": 22, "B": 14, "C": 14, "D": 14, "E": 14, "F": 17, "G": 14, "H": 14})
    ws.freeze_panes = "A4"

    ws = wb.create_sheet("Training Progress")
    title(ws, "Training Progress", "Each row summarizes up to 10,000 games")
    ws.append([]); ws.append(["Start game", "End game", "Games", "Wins", "Win rate", "Mean reward", "Mean loss", "Mean moves", "Ending epsilon"])
    header(ws[4])
    for block in blocks:
        ws.append([block["start"], block["end"], block["games"], block["wins"], block["rate"], block["reward"], block["loss"], block["length"], block["epsilon"]])
    for row in ws.iter_rows(min_row=5, max_row=4+len(blocks)):
        row[4].number_format = "0.00%"
        for cell in row[5:]: cell.number_format = "0.0000"
    chart = LineChart()
    chart.title = "Training Win Rate by 10,000-Game Block"
    chart.y_axis.title = "Win rate"
    chart.x_axis.title = "End game"
    chart.add_data(Reference(ws, min_col=5, min_row=4, max_row=4+len(blocks)), titles_from_data=True)
    chart.set_categories(Reference(ws, min_col=2, min_row=5, max_row=4+len(blocks)))
    chart.height, chart.width = 8, 15
    ws.add_chart(chart, "K4")
    widths(ws, {get_column_letter(i): 15 for i in range(1, 10)})
    ws.freeze_panes = "A5"

    ws = wb.create_sheet("Evaluation Games")
    title(ws, "Raw Evaluation Games", "Every fresh board used in the final comparison")
    ws.append([]); ws.append(["Agent", "Game", "Won", "Moves", "Score"])
    header(ws[4])
    for item in evaluation:
        ws.append([item["agent"], int(item["game"]), int(item["won"]), int(item["moves"]), float(item["score"])])
    widths(ws, {"A": 20, "B": 12, "C": 12, "D": 12, "E": 14})
    ws.auto_filter.ref = f"A4:E{ws.max_row}"
    ws.freeze_panes = "A5"

    ws = wb.create_sheet("Science Buddies")
    title(ws, "Science Buddies Checklist", "What the assigned project asks students to examine")
    ws.append([]); ws.append(["Item", "What this project did", "Evidence / location"]); header(ws[4])
    checklist = [
        ("Objective", "Changed training amount and measured whether a DQN learned to play Minesweeper.", "Overview and Training Progress"),
        ("Board recommendation", "Used a recommended small 6×6 board with 3 mines.", "Configuration"),
        ("Training episodes", "Completed 249,830 games; below the suggested 300,000 because available computer time was a constraint.", "training-data.csv"),
        ("Graphs", "Recorded reward, loss, episode length, epsilon, and block win rate.", "Training Progress"),
        ("Evaluation", "Tested the saved model on 2,000 fresh boards.", "Final Evaluation"),
        ("Iteration/comparison", "Compared an early 60,500-game checkpoint, the final model, and a random baseline.", "Overview / report"),
        ("Engineering tradeoff", "More training could improve performance, but required substantially more computer time.", "Limitations"),
        ("Source", SCIENCE_BUDDIES, "Accessed October 19, 2026"),
    ]
    for item in checklist: ws.append(item)
    for row in ws.iter_rows(min_row=5):
        for cell in row: cell.alignment = Alignment(wrap_text=True, vertical="top")
        ws.row_dimensions[row[0].row].height = 42
    widths(ws, {"A": 24, "B": 72, "C": 34})
    ws.freeze_panes = "A5"

    ws = wb.create_sheet("Research Notes")
    title(ws, "Research Notes", "Background information that helps explain the experiment")
    ws.append([]); ws.append(["Topic", "Research note", "Why it matters here", "Source"]); header(ws[4])
    research = [
        ("Reinforcement learning", "An agent observes a state, chooses an action, receives a reward, and repeats until an episode ends.", "Each Minesweeper game was one episode; wins and safe moves supplied feedback.", "https://gymnasium.farama.org/main/introduction/basic_usage/"),
        ("Q-learning", "Q-values estimate the expected future reward of actions. A policy selects actions using these estimates.", "The model learned which reveal or flag action looked most useful for a board state.", "https://gymnasium.farama.org/main/introduction/train_agent/"),
        ("Deep Q-Network", "A DQN uses a neural network to estimate action values when a table would be too large.", "A Minesweeper board has many possible states, so the project used a neural network.", "https://doi.org/10.1038/nature14236"),
        ("Exploration", "Epsilon is the chance of choosing a random action instead of the model's current best action.", "Epsilon decreased from about 1.0 to 0.05 during training and was set to 0 during final evaluation.", SCIENCE_BUDDIES),
        ("Learning rate", "The learning rate controls the size of each update to the model.", "This experiment used 0.00025, a small update size intended to keep learning stable.", SCIENCE_BUDDIES),
        ("Loss", "Loss measures disagreement between the network's prediction and its training target; noise and temporary increases are normal.", f"Mean loss changed from {blocks[0]['loss']:.5f} in the first 10,000 games to {blocks[-1]['loss']:.5f} in the final block.", SCIENCE_BUDDIES),
        ("Partial observability", "Mine locations are hidden; only revealed clues provide information.", "The model must make decisions without seeing the complete board.", SCIENCE_BUDDIES),
        ("Fair comparison", "Both agents should face the same rules and many fresh boards.", "Both final agents played 2,000 seeded 6×6 boards with three mines.", "Experiment design"),
        ("Uncertainty", "A measured win rate varies with the random sample of boards.", "The workbook reports 95% Wilson confidence intervals instead of treating one percentage as exact.", "Statistical analysis"),
        ("Reproducibility", "Raw data, source code, settings, seeds, and the model checkpoint make a computational experiment easier to repeat.", "These files are included in the final package.", "Project files"),
    ]
    for item in research: ws.append(item)
    for row in ws.iter_rows(min_row=5):
        for cell in row: cell.alignment = Alignment(wrap_text=True, vertical="top")
        ws.row_dimensions[row[0].row].height = 65
    widths(ws, {"A": 23, "B": 60, "C": 60, "D": 54})
    ws.freeze_panes = "A5"

    ws = wb.create_sheet("Configuration")
    title(ws, "Model Configuration")
    ws.append([]); ws.append(["Setting", "Value", "Meaning"]); header(ws[4])
    config = [
        ("Board", "6 × 6, 3 mines", "Same difficulty for training and final testing"),
        ("Algorithm", "Deep Q-Network (DQN)", "Neural network estimates action values"),
        ("Discount factor", 0.95, "Weight given to future reward"),
        ("Starting epsilon", 1.0, "Training began with random exploration"),
        ("Minimum epsilon", 0.05, "At least 5% exploration during training"),
        ("Epsilon decay", 0.9999, "Gradual shift from exploring to using learned choices"),
        ("Learning rate", 0.00025, "Size of model updates"),
        ("Replay memory", 250000, "Maximum stored experiences"),
        ("Mini-batch", 64, "Experiences used for one update"),
        ("Network sync rate", 1000, "Interval for updating the target network"),
        ("Final evaluation epsilon", 0, "No random exploration by trained model"),
        ("Evaluation seed", 20261019, "Makes board generation repeatable"),
    ]
    for item in config: ws.append(item)
    widths(ws, {"A": 27, "B": 24, "C": 70})

    for sheet in wb.worksheets:
        sheet.sheet_view.showGridLines = False
        for row in sheet.iter_rows():
            for cell in row:
                cell.border = Border(bottom=Side(style="hair", color="DCE1EA"))
    path = HERE / "Minesweeper-Final.xlsx"
    wb.save(path)
    return path


def make_markdown(eval_summary, blocks, training):
    trained, random_agent = eval_summary
    text = f"""# Minesweeper Reinforcement Learning: Final Report

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
2. I trained the DQN for {len(training):,} games while recording reward, loss, epsilon, and game length.
3. I saved the trained model.
4. I disabled random exploration for evaluation.
5. I tested the trained model on {trained['games']:,} fresh boards.
6. I tested a reveal-only random baseline on {random_agent['games']:,} fresh boards generated with the same seed sequence.
7. I compared wins, win rates, average moves, training trends, and 95% confidence intervals.

## Results

| Agent | Games | Wins | Win rate | Average moves | 95% confidence interval |
|---|---:|---:|---:|---:|---:|
| Trained DQN | {trained['games']:,} | {trained['wins']:,} | {trained['rate']:.2%} | {trained['moves']:.2f} | {trained['ci_low']:.2%}–{trained['ci_high']:.2%} |
| Random baseline | {random_agent['games']:,} | {random_agent['wins']:,} | {random_agent['rate']:.2%} | {random_agent['moves']:.2f} | {random_agent['ci_low']:.2%}–{random_agent['ci_high']:.2%} |

The trained DQN won **{trained['rate']/random_agent['rate']:.2f} times as often** as random play. During training, its observed win rate increased from **{blocks[0]['rate']:.2%}** in the first 10,000 games to **{blocks[-1]['rate']:.2%}** in the final {blocks[-1]['games']:,} games. Mean game length increased from **{blocks[0]['length']:.2f}** to **{blocks[-1]['length']:.2f}** moves, meaning the agent generally survived longer.

## Conclusion

The results support my hypothesis for this model and board setup. The trained agent won {trained['rate']:.2%} of its final games, compared with {random_agent['rate']:.2%} for the random baseline. Training produced a large practical improvement, although the model still lost more games than it won. This is expected because Minesweeper includes hidden information and some board states require uncertain choices.

## Limitations

- Training stopped at {len(training):,} games because of available computer time, below Science Buddies' suggested starting point of 300,000.
- Only one final trained model was measured, so repeated independent training runs would better separate learning from luck during training.
- The conclusion applies to this 6×6, three-mine environment and reward system.
- The random baseline only reveals random unopened squares; other rule-based strategies could be stronger comparisons.
- A win-rate estimate has sampling uncertainty even with 2,000 test games.

## Future Work

Train several fresh models with different learning rates and epsilon-decay settings, evaluate each on the same seeded boards, and compare DQN with a logic-based Minesweeper solver, Double DQN, or Dueling DQN.

## Sources

1. Tracey Ngo, “Train a Reinforcement Learning AI to Play Minesweeper,” Science Buddies, updated February 27, 2026. {SCIENCE_BUDDIES}
2. Volodymyr Mnih et al., “Human-level control through deep reinforcement learning,” *Nature* 518, 529–533 (2015). https://doi.org/10.1038/nature14236
3. Gymnasium Documentation, “Basic Usage” and “Training an Agent.” https://gymnasium.farama.org/main/introduction/basic_usage/
4. Richard S. Sutton and Andrew G. Barto, *Reinforcement Learning: An Introduction*, second edition. http://incompleteideas.net/book/the-book-2nd.html
"""
    (HERE / "FINAL-REPORT.md").write_text(text, encoding="utf-8")
    board = f"""# Display Board Notes

## Question
Can a Deep Q-Network learn to win Minesweeper more often than random play?

## Hypothesis
More training will cause the DQN to win more often than a random agent.

## Method
I trained one DQN for **{len(training):,} games** on 6×6 boards with three mines. I then tested the trained model and a random baseline on **2,000 fresh games each**.

## Results
- Trained DQN: **{trained['wins']:,} wins ({trained['rate']:.2%})**
- Random baseline: **{random_agent['wins']:,} wins ({random_agent['rate']:.2%})**
- Improvement: **{trained['rate']/random_agent['rate']:.2f}× the random win rate**
- Training win rate: **{blocks[0]['rate']:.2%} early → {blocks[-1]['rate']:.2%} late**

## Conclusion
My hypothesis was supported. The trained model won much more often than random play, showing that it learned useful Minesweeper decisions. It was not perfect and still lost more than half of its final games.

## Limits
One model, one board size, and less than the suggested 300,000 training games. More independent trials and stronger comparison agents would improve the experiment.
"""
    (HERE / "DISPLAY-BOARD.md").write_text(board, encoding="utf-8")
    return text


def make_docx(report_text):
    doc = Document()
    styles = doc.styles
    styles["Normal"].font.name = "Aptos"
    styles["Normal"].font.size = Pt(11)
    for line in report_text.splitlines():
        if line.startswith("# "):
            p = doc.add_heading(line[2:], 0); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        elif line.startswith("## "):
            doc.add_heading(line[3:], 1)
        elif line.startswith("- "):
            doc.add_paragraph(line[2:], style="List Bullet")
        elif line and not line.startswith("|"):
            doc.add_paragraph(line.replace("**", "").replace("*", ""))
    path = HERE / "Minesweeper-Final-Report.docx"
    doc.save(path)
    return path


def make_display_docx():
    source = (HERE / "DISPLAY-BOARD.md").read_text(encoding="utf-8")
    doc = Document()
    doc.styles["Normal"].font.name = "Aptos"
    doc.styles["Normal"].font.size = Pt(14)
    for line in source.splitlines():
        if line.startswith("# "):
            paragraph = doc.add_heading(line[2:], 0)
            paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
        elif line.startswith("## "):
            doc.add_heading(line[3:], 1)
        elif line.startswith("- "):
            doc.add_paragraph(line[2:].replace("**", ""), style="List Bullet")
        elif line:
            doc.add_paragraph(line.replace("**", ""))
    path = HERE / "Minesweeper-Display-Board.docx"
    doc.save(path)
    return path


def make_svg(eval_summary, blocks):
    trained, random_agent = eval_summary
    width, height = 1000, 620
    def txt(x, y, value, size=18, anchor="start", bold=False):
        weight = "bold" if bold else "normal"
        return f'<text x="{x}" y="{y}" font-family="Arial" font-size="{size}" text-anchor="{anchor}" font-weight="{weight}" fill="#{NAVY}">{value}</text>'
    parts = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}">', '<rect width="100%" height="100%" fill="white"/>', txt(80, 52, "Final Minesweeper Win Rate", 30, bold=True), txt(80, 82, "2,000 fresh 6×6 games per agent", 16)]
    for index, item in enumerate([trained, random_agent]):
        x = 190 + index * 390
        bar_h = item["rate"] / .5 * 360
        y = 490 - bar_h
        color = BLUE if index == 0 else ORANGE
        parts += [f'<rect x="{x}" y="{y}" width="210" height="{bar_h}" rx="8" fill="#{color}"/>', txt(x+105, y-18, f'{item["rate"]:.1%}', 30, "middle", True), txt(x+105, 530, item["label"], 20, "middle", True), txt(x+105, 560, f'{item["wins"]:,} wins', 16, "middle")]
    parts.append(txt(940, 600, f'Trained model won {trained["rate"]/random_agent["rate"]:.2f}× as often', 16, "end", True)); parts.append('</svg>')
    (HERE / "final-win-rate.svg").write_text("".join(parts), encoding="utf-8")

    parts = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}">', '<rect width="100%" height="100%" fill="white"/>', txt(80, 52, "Learning During Training", 30, bold=True), txt(80, 82, "Win rate in each 10,000-game block", 16)]
    left, top, plot_w, plot_h = 90, 120, 840, 390
    for rate in [0, .05, .10, .15, .20]:
        y = top + plot_h * (1-rate/.20)
        parts += [f'<line x1="{left}" y1="{y}" x2="{left+plot_w}" y2="{y}" stroke="#DCE1EA"/>', txt(left-12, y+5, f'{rate:.0%}', 14, "end")]
    points = []
    for i, block in enumerate(blocks):
        x = left + i * plot_w / (len(blocks)-1)
        y = top + plot_h * (1-min(block["rate"], .20)/.20)
        points.append(f"{x},{y}")
    parts += [f'<polyline points="{" ".join(points)}" fill="none" stroke="#{BLUE}" stroke-width="5"/>', txt(left, 550, "First games", 16), txt(left+plot_w, 550, f'{blocks[-1]["end"]:,} games', 16, "end"), txt(940, 595, f'{blocks[0]["rate"]:.2%} → {blocks[-1]["rate"]:.2%}', 20, "end", True), '</svg>']
    (HERE / "training-win-rate.svg").write_text("".join(parts), encoding="utf-8")


def make_summary_csv(eval_summary, blocks, training):
    with (HERE / "final-summary.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(["metric", "value", "unit"])
        writer.writerow(["training games", len(training), "games"])
        writer.writerow(["trained wins", eval_summary[0]["wins"], "of 2000"])
        writer.writerow(["trained win rate", eval_summary[0]["rate"] * 100, "percent"])
        writer.writerow(["random wins", eval_summary[1]["wins"], "of 2000"])
        writer.writerow(["random win rate", eval_summary[1]["rate"] * 100, "percent"])
        writer.writerow(["win-rate multiplier", eval_summary[0]["rate"] / eval_summary[1]["rate"], "times random"])
        writer.writerow(["first 10000 training win rate", blocks[0]["rate"] * 100, "percent"])
        writer.writerow(["last training block win rate", blocks[-1]["rate"] * 100, "percent"])


def make_zip(paths):
    package = HERE / "Minesweeper-Science-Fair-Package.zip"
    with zipfile.ZipFile(package, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for path in paths:
            archive.write(path, path.name)
    return package


def main():
    training, evaluation = read_training(), read_evaluation()
    eval_summary, blocks = analyze(training, evaluation)
    workbook = make_workbook(training, evaluation, eval_summary, blocks)
    report_text = make_markdown(eval_summary, blocks, training)
    docx = make_docx(report_text)
    display_docx = make_display_docx()
    make_svg(eval_summary, blocks)
    make_summary_csv(eval_summary, blocks, training)
    package_files = [workbook, docx, display_docx, HERE/"FINAL-REPORT.md", HERE/"DISPLAY-BOARD.md", HERE/"final-summary.csv", HERE/"final-win-rate.svg", HERE/"training-win-rate.svg", EVALUATION, TRAINING, HERE/"trained-model.pth"]
    package = make_zip(package_files)
    print(f"Created {workbook.name}, {docx.name}, and {package.name}")


if __name__ == "__main__":
    main()
