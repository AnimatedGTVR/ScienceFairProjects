# Password Security: measured password experiment

5 repetitions per condition; 15,000,000 guesses allowed per trial.

| Method | Alphabet | Sample | Found / trials | Guesses per trial | Mean seconds | Min seconds | Max seconds |
|---|---|---|---:|---:|---:|---:|---:|
| brute_force | digits | `9` | 5/5 | 10 | 0.000010 | 0.000004 | 0.000016 |
| brute_force | digits | `99` | 5/5 | 100 | 0.000055 | 0.000049 | 0.000069 |
| brute_force | digits | `999` | 5/5 | 1000 | 0.000517 | 0.000478 | 0.000573 |
| brute_force | digits | `9999` | 5/5 | 10000 | 0.006347 | 0.004760 | 0.011639 |
| brute_force | lowercase | `z` | 5/5 | 26 | 0.000015 | 0.000013 | 0.000018 |
| brute_force | lowercase | `zz` | 5/5 | 676 | 0.000383 | 0.000369 | 0.000402 |
| brute_force | lowercase | `zzz` | 5/5 | 17576 | 0.008427 | 0.008061 | 0.009136 |
| brute_force | lowercase | `zzzz` | 5/5 | 456976 | 0.158177 | 0.148259 | 0.171077 |
| brute_force | mixed_letters | `Z` | 5/5 | 52 | 0.000020 | 0.000018 | 0.000022 |
| brute_force | mixed_letters | `ZZ` | 5/5 | 2704 | 0.000896 | 0.000879 | 0.000923 |
| brute_force | mixed_letters | `ZZZ` | 5/5 | 140608 | 0.049650 | 0.045617 | 0.053332 |
| brute_force | mixed_letters | `ZZZZ` | 5/5 | 7311616 | 3.633987 | 2.931068 | 3.896488 |
| brute_force | letters_digits | `9` | 5/5 | 62 | 0.000037 | 0.000033 | 0.000044 |
| brute_force | letters_digits | `99` | 5/5 | 3844 | 0.001990 | 0.001901 | 0.002133 |
| brute_force | letters_digits | `999` | 5/5 | 238328 | 0.124207 | 0.118292 | 0.129184 |
| brute_force | letters_digits | `9999` | 5/5 | 14776336 | 8.026581 | 7.801447 | 8.299444 |
| dictionary | toy_dictionary | `tiger` | 5/5 | 7 | 0.000010 | 0.000004 | 0.000029 |
| word_pairs | toy_dictionary | `tiger` | 0/5 | 432 | 0.000252 | 0.000245 | 0.000263 |
| dictionary | toy_dictionary | `Moon` | 5/5 | 10 | 0.000006 | 0.000006 | 0.000007 |
| word_pairs | toy_dictionary | `Moon` | 0/5 | 432 | 0.000254 | 0.000247 | 0.000263 |
| dictionary | toy_dictionary | `Robot+River` | 0/5 | 12 | 0.000008 | 0.000007 | 0.000011 |
| word_pairs | toy_dictionary | `Robot+River` | 5/5 | 380 | 0.000225 | 0.000218 | 0.000234 |
| dictionary | toy_dictionary | `x9Q!m2` | 0/5 | 12 | 0.000008 | 0.000007 | 0.000008 |
| word_pairs | toy_dictionary | `x9Q!m2` | 0/5 | 432 | 0.000292 | 0.000248 | 0.000429 |

## Interpretation

Brute-force samples occupy the last position in a fixed-length search. For completed searches, the guess count equals alphabet size raised to password length. Adding a character multiplies this worst-case count by the alphabet size.

Dictionary results depend on the supplied words and enumeration order. A longer predictable combination can be found in fewer guesses than a short exhaustive-search target. A failed dictionary search only means the sample was not among the tested candidates.

## Limits

These are repeated timing measurements of the same synthetic samples, not a population study. Incomplete searches report time spent testing, not time to crack. Tiny durations are noisy; .NET warmup, CPU load, and garbage collection affect timing. Minesweeper training ran concurrently during this experiment. Fast unsalted MD5 results do not predict the time to access real accounts.
