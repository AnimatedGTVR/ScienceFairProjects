# Password Security

## Subtitle

How do length, character set, and guessing method affect cracking difficulty?

## Left Panel — Question and Method

### Question

How do password length, available characters, and guessing strategy change the
number of guesses and time needed to recover a classroom sample password?

### Hypothesis

Longer passwords and larger character sets will require exponentially more
brute-force guesses. Dictionary attacks will be faster for predictable words
but will fail when the target is missing from their candidate list.

### Variables

- Independent: length, character set, and guessing method
- Dependent: guesses, elapsed time, and success or failure
- Controlled: computer, C# program, MD5 comparison, enumeration order, and repetitions

### Method

1. Wrote a C# password guesser.
2. Tested four character sets at lengths one through four.
3. Repeated every baseline condition five times.
4. Compared brute force, dictionary, word-pair, and pattern methods.
5. Tested seven authorized Science Buddies challenge hashes.
6. Exhausted all 62^6 candidates for Challenge 6.
7. Exported CSV data and graphed the results.

### Safety

Only supplied educational hashes and synthetic passwords were tested. No real
account, login page, or private password was accessed.

## Center Panel — Results

### Headline Result

**56,800,235,584 six-character alphanumeric candidates tested**

**Challenge 6 result: no match**

Approximate active wall time: **8.13 hours**

Average speed: **1.94 million guesses per second**

![Completed search](results/final/completed-search.png)

![Measured brute-force time](results/final/measured-cracking-time.png)

![Search-space growth](results/final/search-space-growth.png)

![Challenge attempts](results/final/challenge-attempts.png)

### Key Measured Comparison

| Four-character alphabet | Candidates | Mean time |
|---|---:|---:|
| Digits | 10,000 | 0.006347 s |
| Lowercase | 456,976 | 0.158177 s |
| Letters | 7,311,616 | 3.633987 s |
| Letters + digits | 14,776,336 | 8.026581 s |

## Right Panel — Analysis and Conclusion

### Analysis

- Search spaces grew exponentially instead of linearly.
- The length-four alphanumeric search had about 1,478 times more candidates
  than the length-four digit search.
- Dictionary attacks found predictable samples in fewer than 500 guesses.
- Word-pair attacks found longer samples without testing every possible string.
- A failed search proves only that the target was absent from the tested space.

### Conclusion

The hypothesis was supported. Longer, less predictable passwords resisted the
tested guessing methods better than short passwords and dictionary words.
Length was especially powerful because every new character multiplied the
number of candidates. Six of seven challenge passwords were recovered, while
Challenge 6 was not found after the complete six-character alphanumeric search.

### Limitations

- Educational fast MD5, not modern password storage
- One computer and five baseline repetitions
- Background CPU load affected timing
- A 435-word dictionary cannot represent every likely password
- Online accounts normally rate-limit failed attempts

### Practical Lesson

Use long, unique passwords or passphrases, avoid common patterns, use a password
manager, and enable multi-factor authentication.

### Credits

Science Buddies supplied the project idea, original Python materials, sample
hashes, and word list. The experiment used a commented C# implementation.
AI assistance was used for programming, graphs, and report drafting.
