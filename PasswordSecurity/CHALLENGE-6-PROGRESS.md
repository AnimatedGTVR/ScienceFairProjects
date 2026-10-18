# Challenge 6: expanded searches

October 10, 2026. All expanded searches below exhausted their candidate lists without a match. Challenge 6 remains unsolved. Counts are attempts, not necessarily unique passwords.

| Method | Guesses | Seconds |
|---|---:|---:|
| all_word_capitalizations | 34269 | 0.035 |
| modified_dictionary_complete | 48473908 | 27.561 |
| uppercase_word_pairs | 8515125 | 5.488 |
| three_words | 82312875 | 49.693 |
| transformed_word_pairs | 15138000 | 7.781 |
| printable_ascii_1_to_4 | 82317120 | 46.718 |
| dictionary_character_substitutions | 321125 | 0.16 |

Total additional attempts: 237112422.

The complete ASCII search covered 95 printable characters (space through tilde) at lengths 1-4. No matching hash was found. The three-word search covered lowercase concatenations of the supplied 435 words. Other capitalization or separator combinations were not included in that three-word search. This does not establish the actual password length or pattern beyond the searched spaces.

Next options: expand the vocabulary, test further word combinations and separators, or run a longer search with a measured time budget. Preserve earlier failed searches as experimental evidence. No web password-lookup service was used.

## Completed six-character alphanumeric search

The resumed C# search later exhausted all 56,800,235,584 combinations made from
lowercase letters, uppercase letters, and digits. No matching password was
found. The two active process-log intervals totaled approximately 8.13 hours,
for an average of about 1.94 million guesses per second.

This result rules out only six-character passwords from the tested 62-character
alphabet. It does not rule out other lengths, symbols, phrases, or patterns.
Final graphs and spreadsheet-ready tables are in [results/final](results/final/README.md).
