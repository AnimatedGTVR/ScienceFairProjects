"""Create poster-ready SVG graphs using only Python's standard library."""

import csv
import html
import math
from pathlib import Path

HERE = Path(__file__).resolve().parent
BASELINE = HERE.parent / "baseline"
W, H = 1100, 650
LEFT, RIGHT, TOP, BOTTOM = 105, 45, 105, 95
PLOT_W, PLOT_H = W - LEFT - RIGHT, H - TOP - BOTTOM
COLORS = ["#2563eb", "#16a34a", "#dc2626", "#9333ea"]


def label(x, y, value, size=16, anchor="start", weight="normal", color="#172033"):
    return (
        f'<text x="{x}" y="{y}" font-family="Arial, sans-serif" '
        f'font-size="{size}" text-anchor="{anchor}" font-weight="{weight}" '
        f'fill="{color}">{html.escape(str(value))}</text>'
    )


def start(title, subtitle):
    return [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">',
        '<rect width="100%" height="100%" fill="#fff"/>',
        label(LEFT, 44, title, 28, weight="bold"),
        label(LEFT, 74, subtitle, 15, color="#596579"),
    ]


def short(value):
    for size, suffix in [(1e12, "T"), (1e9, "B"), (1e6, "M"), (1e3, "K")]:
        if value >= size:
            return f"{value / size:g}{suffix}"
    return f"{value:g}"


def log_y(value, low, high):
    position = (math.log10(max(value, 10**low)) - low) / (high - low)
    return TOP + PLOT_H * (1 - position)


def axes(parts, low, high, title):
    for power in range(low, high + 1):
        y = log_y(10**power, low, high)
        parts.append(f'<line x1="{LEFT}" y1="{y}" x2="{W-RIGHT}" y2="{y}" stroke="#dfe4ec"/>')
        parts.append(label(LEFT - 14, y + 5, f"10^{power}", 13, "end", color="#596579"))
    middle = TOP + PLOT_H / 2
    parts.append(
        f'<text x="{-middle}" y="28" transform="rotate(-90)" '
        f'font-family="Arial, sans-serif" font-size="15" text-anchor="middle" '
        f'font-weight="bold" fill="#172033">{html.escape(title)}</text>'
    )
    parts.append(f'<line x1="{LEFT}" y1="{TOP}" x2="{LEFT}" y2="{TOP+PLOT_H}" stroke="#172033"/>')
    parts.append(f'<line x1="{LEFT}" y1="{TOP+PLOT_H}" x2="{W-RIGHT}" y2="{TOP+PLOT_H}" stroke="#172033"/>')


def bar_chart(path, names, values):
    parts = start("Password Challenge Attempts",
                  "Total guesses used for each Science Buddies challenge (logarithmic scale)")
    axes(parts, 1, 11, "Total guesses (log scale)")
    slot, baseline = PLOT_W / len(names), TOP + PLOT_H
    for index, (name, value) in enumerate(zip(names, values)):
        width = slot * .58
        x = LEFT + slot * index + (slot - width) / 2
        y = log_y(value, 1, 11)
        parts.append(f'<rect x="{x}" y="{y}" width="{width}" height="{baseline-y}" rx="5" fill="#2563eb"/>')
        parts.append(label(x + width / 2, y - 10, short(value), 13, "middle", "bold"))
        parts.append(label(x + width / 2, baseline + 27, f"Challenge {name}", 14, "middle"))
    parts.append(label(LEFT, H - 25,
        "Challenge 6 exhausted 56.8 billion six-character alphanumeric candidates without a match.",
        14, color="#596579"))
    parts.append("</svg>")
    path.write_text("\n".join(parts), encoding="utf-8")


def line_chart(path, title, subtitle, series, low, high, y_title):
    parts = start(title, subtitle)
    axes(parts, low, high, y_title)
    lengths = sorted({x for values in series.values() for x, _ in values})
    minimum, maximum = min(lengths), max(lengths)
    for length in lengths:
        x = LEFT + (length - minimum) / (maximum - minimum) * PLOT_W
        parts.append(label(x, TOP + PLOT_H + 27, length, 14, "middle"))
    parts.append(label(LEFT + PLOT_W / 2, H - 28,
                       "Password length (characters)", 15, "middle", "bold"))
    for color, (name, points) in zip(COLORS, series.items()):
        coords = []
        for length, value in points:
            x = LEFT + (length - minimum) / (maximum - minimum) * PLOT_W
            coords.append((x, log_y(value, low, high)))
        point_string = " ".join(f"{x},{y}" for x, y in coords)
        parts.append(f'<polyline points="{point_string}" fill="none" stroke="{color}" stroke-width="4"/>')
        for x, y in coords:
            parts.append(f'<circle cx="{x}" cy="{y}" r="6" fill="{color}" stroke="#fff" stroke-width="2"/>')
    for index, (color, name) in enumerate(zip(COLORS, series)):
        x = LEFT + 12 + index * 215
        parts.append(f'<rect x="{x}" y="{TOP+12}" width="18" height="18" rx="3" fill="{color}"/>')
        parts.append(label(x + 27, TOP + 27, name, 14))
    parts.append("</svg>")
    path.write_text("\n".join(parts), encoding="utf-8")


def completion_card(path):
    parts = start("Completed Six-Character Search",
                  "Full alphanumeric search: lowercase + uppercase + digits")
    parts += [
        '<rect x="105" y="125" width="890" height="375" rx="18" fill="#f5f7fb" stroke="#dce1ea"/>',
        label(550, 215, "56,800,235,584", 54, "middle", "bold", "#2563eb"),
        label(550, 252, "password candidates tested", 20, "middle", color="#596579"),
        '<rect x="180" y="300" width="740" height="28" rx="14" fill="#16a34a"/>',
        label(550, 321, "100% of the planned search space", 15, "middle", "bold", "#fff"),
        label(330, 395, "≈ 8.13 hours", 30, "middle", "bold"),
        label(330, 426, "approximate active wall time", 15, "middle", color="#596579"),
        label(770, 395, "No match", 30, "middle", "bold", "#dc2626"),
        label(770, 426, "Challenge 6 result", 15, "middle", color="#596579"),
        label(105, 550,
              "Conclusion: the target was not six characters made only from A–Z, a–z, and 0–9.",
              17, weight="bold"),
        label(105, 580,
              "This rules out only the tested search space; it does not prove the password is unguessable.",
              15, color="#596579"),
        "</svg>",
    ]
    path.write_text("\n".join(parts), encoding="utf-8")


def rows(path):
    with path.open(newline="", encoding="utf-8-sig") as source:
        return list(csv.DictReader(source))


def main():
    challenges = rows(HERE / "challenge-summary.csv")
    bar_chart(HERE / "challenge-attempts.svg",
              [row["challenge"] for row in challenges],
              [float(row["total_guesses"]) for row in challenges])

    names = {
        "digits": "Digits (10)",
        "lowercase": "Lowercase (26)",
        "mixed_letters": "Letters (52)",
        "letters_digits": "Letters + digits (62)",
    }
    measured = {}
    for row in rows(BASELINE / "summary.csv"):
        if row["method"] == "brute_force":
            measured.setdefault(row["alphabet"], []).append(
                (int(row["length"]), float(row["mean_seconds"])))
    line_chart(HERE / "measured-cracking-time.svg", "Measured Brute-Force Time",
               "Mean of five C# trials per condition; worst-position sample (logarithmic scale)",
               {names[key]: measured[key] for key in names}, -6, 2,
               "Mean seconds (log scale)")

    theoretical = {}
    for row in rows(BASELINE / "theoretical.csv"):
        theoretical.setdefault(row["alphabet"], []).append(
            (int(row["length"]), float(row["possibilities"])))
    line_chart(HERE / "search-space-growth.svg", "Password Search Space Growth",
               "Every extra character multiplies possible passwords (logarithmic scale)",
               {names[key]: theoretical[key] for key in names}, 1, 15,
               "Possible passwords (log scale)")
    completion_card(HERE / "completed-search.svg")


if __name__ == "__main__":
    main()
