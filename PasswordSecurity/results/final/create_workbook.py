"""Build a polished Excel workbook that imports cleanly into Google Sheets."""

from __future__ import annotations

import csv
from pathlib import Path

from openpyxl import Workbook, load_workbook
from openpyxl.chart import BarChart, LineChart, Reference
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.worksheet.table import Table, TableStyleInfo

HERE = Path(__file__).resolve().parent
BASELINE = HERE.parent / "baseline"
OUTPUT = HERE / "Password-Security-Final.xlsx"

NAVY = "14213D"
BLUE = "2563EB"
CYAN = "06B6D4"
GREEN = "16A34A"
RED = "DC2626"
AMBER = "F59E0B"
PURPLE = "9333EA"
PALE = "F4F7FC"
WHITE = "FFFFFF"
MUTED = "5B6577"
GRID = "DCE3EE"
SERIES_COLORS = [BLUE, GREEN, RED, PURPLE]


def read_rows(path):
    with path.open(newline="", encoding="utf-8-sig") as source:
        return list(csv.DictReader(source))


def title(ws, text, subtitle, last_column=8):
    ws.sheet_view.showGridLines = False
    ws.merge_cells(start_row=1, start_column=1, end_row=1, end_column=last_column)
    ws["A1"] = text
    ws["A1"].font = Font(size=24, bold=True, color=WHITE)
    ws["A1"].fill = PatternFill("solid", fgColor=NAVY)
    ws["A1"].alignment = Alignment(vertical="center")
    ws.row_dimensions[1].height = 42
    ws.merge_cells(start_row=2, start_column=1, end_row=2, end_column=last_column)
    ws["A2"] = subtitle
    ws["A2"].font = Font(size=11, color=MUTED)
    ws.row_dimensions[2].height = 25


def card(ws, cell_range, heading, value, color):
    ws.merge_cells(cell_range)
    top_left = ws[cell_range.split(":")[0]]
    top_left.value = f"{heading}\n{value}"
    top_left.fill = PatternFill("solid", fgColor=color)
    top_left.font = Font(size=15, bold=True, color=WHITE)
    top_left.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
    top_left.border = Border(
        left=Side(color=WHITE), right=Side(color=WHITE),
        top=Side(color=WHITE), bottom=Side(color=WHITE)
    )


def style_table(ws, start_row, end_row, end_column, name):
    for cell in ws[start_row]:
        if cell.column <= end_column:
            cell.fill = PatternFill("solid", fgColor=NAVY)
            cell.font = Font(bold=True, color=WHITE)
            cell.alignment = Alignment(horizontal="center")
    ref = f"A{start_row}:{ws.cell(end_row, end_column).coordinate}"
    table = Table(displayName=name, ref=ref)
    table.tableStyleInfo = TableStyleInfo(
        name="TableStyleMedium2", showRowStripes=True, showColumnStripes=False
    )
    ws.add_table(table)
    ws.freeze_panes = f"A{start_row + 1}"


def add_overview(wb):
    ws = wb.active
    ws.title = "Overview"
    ws.sheet_properties.tabColor = BLUE
    title(ws, "PASSWORD SECURITY EXPERIMENT",
          "Completed results • six challenges solved • 56.8 billion candidates tested")
    card(ws, "A4:B6", "COMBINATIONS TESTED", "56,800,235,584", BLUE)
    card(ws, "C4:D6", "CHALLENGE 6", "NO MATCH", RED)
    card(ws, "E4:F6", "ACTIVE TIME", "≈ 8.13 HOURS", PURPLE)
    card(ws, "G4:H6", "THROUGHPUT", "≈ 1.94M / SEC", GREEN)
    for row in range(4, 7):
        ws.row_dimensions[row].height = 26

    headers = ["Challenge", "Result", "Method", "Successful guesses", "Total guesses", "Seconds"]
    for column, value in enumerate(headers, 1):
        ws.cell(9, column, value)
    challenges = read_rows(HERE / "challenge-summary.csv")
    for row_number, row in enumerate(challenges, 10):
        values = [
            int(row["challenge"]), row["result"].replace("_", " ").title(),
            row["successful_method"].replace("_", " ").title(),
            int(row["successful_method_guesses"]) if row["successful_method_guesses"] else None,
            int(row["total_guesses"]), float(row["seconds"]),
        ]
        for column, value in enumerate(values, 1):
            ws.cell(row_number, column, value)
        ws.cell(row_number, 2).font = Font(
            bold=True, color=GREEN if row["result"] == "found" else RED
        )
    style_table(ws, 9, 9 + len(challenges), 6, "ChallengeResults")
    for row in range(10, 10 + len(challenges)):
        ws.cell(row, 4).number_format = "#,##0"
        ws.cell(row, 5).number_format = "#,##0"
        ws.cell(row, 6).number_format = "0.000"

    chart = BarChart()
    chart.title = "Guesses Used by Challenge"
    chart.y_axis.title = "Total guesses (log scale)"
    chart.x_axis.title = "Challenge"
    chart.y_axis.scaling.logBase = 10
    chart.height, chart.width = 9, 16
    chart.add_data(Reference(ws, min_col=5, min_row=9, max_row=16), titles_from_data=True)
    chart.set_categories(Reference(ws, min_col=1, min_row=10, max_row=16))
    chart.series[0].graphicalProperties.solidFill = BLUE
    chart.legend = None
    ws.add_chart(chart, "A19")

    ws.merge_cells("A37:H38")
    ws["A37"] = (
        "Conclusion: Challenge 6 was not a six-character password made only from "
        "A–Z, a–z, and 0–9. This rules out only that tested search space."
    )
    ws["A37"].fill = PatternFill("solid", fgColor="E8F0FE")
    ws["A37"].font = Font(size=12, bold=True, color=NAVY)
    ws["A37"].alignment = Alignment(wrap_text=True, vertical="center")
    for column, width in {"A": 13, "B": 16, "C": 28, "D": 19, "E": 20, "F": 14, "G": 18, "H": 18}.items():
        ws.column_dimensions[column].width = width


def add_measured(wb):
    ws = wb.create_sheet("Measured Time")
    ws.sheet_properties.tabColor = CYAN
    title(ws, "MEASURED BRUTE-FORCE TIME",
          "Mean of five C# trials for the worst-position password", 6)
    data = read_rows(BASELINE / "summary.csv")
    keys = ["digits", "lowercase", "mixed_letters", "letters_digits"]
    names = ["Digits (10)", "Lowercase (26)", "Letters (52)", "Letters + digits (62)"]
    ws.append([])
    headers = ["Length"] + names
    for column, value in enumerate(headers, 1):
        ws.cell(4, column, value)
    lookup = {(row["alphabet"], int(row["length"])): float(row["mean_seconds"])
              for row in data if row["method"] == "brute_force"}
    for length in range(1, 5):
        ws.append([length] + [lookup[(key, length)] for key in keys])
    style_table(ws, 4, 8, 5, "MeasuredTimes")
    for row in range(5, 9):
        for column in range(2, 6):
            ws.cell(row, column).number_format = "0.000000"

    chart = LineChart()
    chart.title = "Time Rises Rapidly with Length"
    chart.y_axis.title = "Mean seconds (log scale)"
    chart.x_axis.title = "Password length"
    chart.y_axis.scaling.logBase = 10
    chart.height, chart.width = 12, 20
    chart.add_data(Reference(ws, min_col=2, max_col=5, min_row=4, max_row=8), titles_from_data=True)
    chart.set_categories(Reference(ws, min_col=1, min_row=5, max_row=8))
    for series, color in zip(chart.series, SERIES_COLORS):
        series.graphicalProperties.line.solidFill = color
        series.graphicalProperties.line.width = 26000
    ws.add_chart(chart, "A11")
    for column in "ABCDE":
        ws.column_dimensions[column].width = 22


def add_search_space(wb):
    ws = wb.create_sheet("Search Space")
    ws.sheet_properties.tabColor = PURPLE
    title(ws, "PASSWORD SEARCH SPACE GROWTH",
          "Every additional character multiplies the number of candidates", 6)
    data = read_rows(BASELINE / "theoretical.csv")
    keys = ["digits", "lowercase", "mixed_letters", "letters_digits"]
    names = ["Digits (10)", "Lowercase (26)", "Letters (52)", "Letters + digits (62)"]
    for column, value in enumerate(["Length"] + names, 1):
        ws.cell(4, column, value)
    lookup = {(row["alphabet"], int(row["length"])): int(row["possibilities"])
              for row in data}
    for length in range(1, 9):
        ws.append([length] + [lookup[(key, length)] for key in keys])
    style_table(ws, 4, 12, 5, "SearchSpaces")
    for row in range(5, 13):
        for column in range(2, 6):
            ws.cell(row, column).number_format = "#,##0"

    chart = LineChart()
    chart.title = "Possible Passwords by Length"
    chart.y_axis.title = "Possible passwords (log scale)"
    chart.x_axis.title = "Password length"
    chart.y_axis.scaling.logBase = 10
    chart.height, chart.width = 12, 20
    chart.add_data(Reference(ws, min_col=2, max_col=5, min_row=4, max_row=12), titles_from_data=True)
    chart.set_categories(Reference(ws, min_col=1, min_row=5, max_row=12))
    for series, color in zip(chart.series, SERIES_COLORS):
        series.graphicalProperties.line.solidFill = color
        series.graphicalProperties.line.width = 26000
    ws.add_chart(chart, "A15")
    for column in "ABCDE":
        ws.column_dimensions[column].width = 24


def add_notes(wb):
    ws = wb.create_sheet("Notes")
    ws.sheet_properties.tabColor = AMBER
    title(ws, "METHODS AND LIMITATIONS",
          "Context needed to interpret the experiment correctly", 6)
    notes = [
        ("Question", "How do password length, character set, and guessing method affect cracking difficulty?"),
        ("Repeated trials", "Five timing trials were run for each measured benchmark condition."),
        ("Worst case", "Brute-force benchmark samples were last in the enumeration order."),
        ("Challenge 6", "All 56,800,235,584 six-character alphanumeric candidates were tested."),
        ("Result", "No match was found for Challenge 6."),
        ("Important limit", "The result rules out only the tested length and alphabet."),
        ("Runtime", "8.13 hours is approximate active wall time from two process-log intervals."),
        ("Ethics", "The project used educational sample hashes, not real accounts or stolen credentials."),
        ("Hashing", "Fast unsalted MD5 is educational and does not represent modern password storage."),
    ]
    ws["A4"], ws["B4"] = "Topic", "Explanation"
    for row_number, (topic, explanation) in enumerate(notes, 5):
        ws.cell(row_number, 1, topic)
        ws.cell(row_number, 2, explanation)
        ws.cell(row_number, 1).font = Font(bold=True, color=NAVY)
        ws.cell(row_number, 2).alignment = Alignment(wrap_text=True, vertical="top")
        ws.row_dimensions[row_number].height = 36
    style_table(ws, 4, 4 + len(notes), 2, "ExperimentNotes")
    ws.column_dimensions["A"].width = 22
    ws.column_dimensions["B"].width = 95


def main():
    wb = Workbook()
    add_overview(wb)
    add_measured(wb)
    add_search_space(wb)
    add_notes(wb)
    wb.save(OUTPUT)
    # Reopen immediately so a corrupt file fails here instead of after upload.
    load_workbook(OUTPUT, read_only=True).close()
    print(OUTPUT)


if __name__ == "__main__":
    main()
