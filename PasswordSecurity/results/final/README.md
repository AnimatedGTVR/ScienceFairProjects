# Final password-security graphs

These files turn the completed experiment into poster-ready vector graphs and
spreadsheet-ready CSV tables.

- Password-Security-Final.xlsx is a polished, one-file workbook for Google Sheets.
- challenge-attempts.svg compares Science Buddies Challenges 0–6.
- measured-cracking-time.svg shows measured C# time by password length.
- search-space-growth.svg shows theoretical growth for four alphabets.
- completed-search.svg summarizes the 56.8-billion-guess search.
- challenge-summary.csv opens in Excel or Google Sheets.
- final-summary.csv contains the headline measurements and conclusions.

The vertical axes use logarithmic scales because the results span many orders
of magnitude. The 8.13-hour runtime is an approximate active wall-clock
measurement from the two process-log intervals. It is not CPU time.

Regenerate the SVG files by running python create_graphs.py in this folder.
Regenerate the workbook by running python create_workbook.py in this folder.
