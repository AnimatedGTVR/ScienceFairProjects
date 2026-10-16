// This file contains the Science Buddies challenge searches. It reads the seven
// local target values from original/crack_password.py AS TEXT. It does not run
// that Python file. Each method generates a different, documented kind of guess.
// Search limits prevent an accidental endless run. "Unsolved" only means none of
// the candidates tested by that method matched; it does not prove impossibility.

using System.Diagnostics;
using System.Text.RegularExpressions;

namespace PasswordSecurity;

internal static partial class Program
{
    private static Dictionary<int, byte[]> ImportChallenges(string source)
    {
        // Read literal assignments as data. Never execute downloaded Python.
        var values = new Dictionary<int, string>();
        foreach (Match match in Regex.Matches(source,
            "(?m)^[ \\t]*password([0-6])[ \\t]*=[ \\t]*([\"'])([^\"'\\r\\n]*)\\2[ \\t]*(?:#.*)?\\r?$"))
            values[int.Parse(match.Groups[1].Value)] = match.Groups[3].Value;
        var hashes = new Dictionary<int, byte[]>();
        for (int id = 0; id <= 6; id++)
        {
            if (!values.TryGetValue(id, out string? value) || value.Length == 0)
                throw new InvalidDataException($"Missing password{id} literal assignment in the supplied source.");
            if (id == 0)
            {
                if (value.Contains('\\')) throw new InvalidDataException("Password 0 contains escapes; use a simple literal for this importer.");
                hashes[id] = Digest(value);
            }
            else
            {
                if (!Regex.IsMatch(value, "\\A[0-9a-fA-F]{32}\\z"))
                    throw new InvalidDataException($"Password {id} is not a 32-character MD5 hash.");
                hashes[id] = Convert.FromHexString(value);
            }
        }
        return hashes;
    }

    private static IEnumerable<string> Lengths(string alphabet, int maxLength)
    {
        for (int length = 1; length <= maxLength; length++)
            foreach (string candidate in BruteForce(alphabet, length)) yield return candidate;
    }

    private static IEnumerable<string> OfficialWords(string[] words)
    {
        foreach (string word in words) { yield return word; yield return Capitalize(word); }
    }

    private static IEnumerable<string> OfficialPairs(string[] words)
    {
        foreach (string first in words)
        foreach (string second in words)
        foreach (string separator in new[] { "" }.Concat("~!@#$%^&*()_-+={}[]:<>,./".Select(c => c.ToString())))
        foreach (string a in new[] { first, Capitalize(first) })
        foreach (string b in new[] { second, Capitalize(second) })
            yield return a + separator + b;
    }

    private static int RunChallenge(string[] args)
    {
        bool patterns = args.Length == 2 && args[1] == "--patterns";
        bool leet = args.Length == 2 && args[1] == "--leet";
        bool longSearch = args.Length == 2 && args[1] == "--long";
        bool extended = args.Length == 2 && (args[1] == "--extended" || patterns || leet || longSearch);
        if ((!extended && args.Length != 1) || !int.TryParse(args[0], out int id) || id < 0 || id > 6)
            throw new ArgumentException("Use: dotnet run -c Release -- --challenge 0 (choose 0-6).");
        string sourcePath = Path.Combine("original", "crack_password.py");
        string wordsPath = Path.Combine("original", "passwords.txt");
        if (!File.Exists(sourcePath) || !File.Exists(wordsPath))
            throw new FileNotFoundException("Place Science Buddies' crack_password.py and passwords.txt in Password Security/original first. No challenge has been run.");
        byte[] target = ImportChallenges(File.ReadAllText(sourcePath))[id];
        string[] words = File.ReadAllLines(wordsPath).Select(w => w.Trim()).Where(w => w.Length > 0).ToArray();
        if (words.Length == 0 || words.Any(w => w.Contains('<') || w.Contains('>')))
            throw new InvalidDataException("The word list is empty or appears to contain HTML instead of passwords.");
        string output = Path.Combine("results", $"challenge-{id}-{DateTime.Now:yyyyMMdd-HHmmss}-{Guid.NewGuid():N}");
        Directory.CreateDirectory(output);
        long guessLimit = longSearch ? 20_000_000_000L : extended ? 150_000_000 : 15_000_000;
        int timeLimit = longSearch ? 7200 : extended ? 120 : 30;
        File.WriteAllText(Path.Combine(output, "provenance.txt"),
            "Source: Science Buddies official downloads supplied locally.\n" +
            $"Python SHA256: {Convert.ToHexString(System.Security.Cryptography.SHA256.HashData(File.ReadAllBytes(sourcePath)))}\n" +
            $"Word list SHA256: {Convert.ToHexString(System.Security.Cryptography.SHA256.HashData(File.ReadAllBytes(wordsPath)))}\n" +
            "C# methods follow the project concepts; enumeration order may differ from the Python starter.\n" +
            $"Limits: {guessLimit} guesses or {timeLimit} seconds per method. Extended: {extended}. Unsolved does not mean uncrackable.\n");
        using var csv = new StreamWriter(Path.Combine(output, "challenge-results.csv")) { AutoFlush = true };
        Csv(csv, "challenge", "method", "status", "guesses", "seconds", "recovered_sample");
        var methods = new (string Name, Func<IEnumerable<string>> Candidates)[] {
            ("dictionary", () => OfficialWords(words)),
            ("numeric_1_to_4", () => Lengths("0123456789", 4)),
            ("word_pairs", () => OfficialPairs(words)),
            ("modified_dictionary", () => ModifiedWords(words)),
            ("alphanumeric_1_to_8", () => Lengths(Letters + "0123456789", 8))
        };
        if (extended) methods = [
            ("all_word_capitalizations", () => words.SelectMany(CaseVariants)),
            ("modified_dictionary_complete", () => ModifiedWords(words)),
            ("uppercase_word_pairs", () => UpperPairs(words)),
            ("three_words", () => ThreeWords(words))
        ];
        if (patterns) methods = [
            ("transformed_word_pairs", () => TransformedPairs(words)),
            ("printable_ascii_1_to_4", () => Lengths(new string(Enumerable.Range(32, 95).Select(i => (char)i).ToArray()), 4))
        ];
        if (leet) methods = [("dictionary_character_substitutions", () => words.SelectMany(LeetVariants))];
        if (longSearch) methods = [
            ("numeric_lengths_5_to_8", () => Enumerable.Range(5, 4).SelectMany(length => BruteForce("0123456789", length))),
            ("three_words_case_and_separators", () => ThreeWordPatterns(words)),
            ("printable_ascii_length_5", () => BruteForce(new string(Enumerable.Range(32, 95).Select(i => (char)i).ToArray()), 5))
        ];
        foreach (var (method, candidates) in methods)
        {
            Console.WriteLine($"Challenge {id}: {method}...");
            var timer = Stopwatch.StartNew();
            long guesses = 0;
            string status = "exhausted", recovered = "";
            foreach (string candidate in candidates())
            {
                if (guesses >= guessLimit || timer.Elapsed.TotalSeconds >= timeLimit) { status = "limit_reached"; break; }
                guesses++;
                if (longSearch && guesses % 5_000_000 == 0)
                    Console.WriteLine($"Progress: {method}, {guesses:N0} guesses, {timer.Elapsed.TotalSeconds:F1}s");
                if (Digest(candidate).AsSpan().SequenceEqual(target))
                { status = "found"; recovered = candidate; break; }
            }
            double seconds = timer.Elapsed.TotalSeconds;
            Csv(csv, id, method, status, guesses, seconds, recovered);
            Console.WriteLine($"{status}: {guesses:N0} guesses in {seconds:F3}s" + (status == "found" ? $"; sample = {recovered}" : ""));
            if (status == "found") break;
        }
        Console.WriteLine($"Results: {Path.GetFullPath(output)}");
        return 0;
    }

    private static IEnumerable<string> ThreeWordPatterns(string[] words)
    {
        foreach (string a in words)
        foreach (string b in words)
        foreach (string c in words)
        foreach (string separator in new[] { "", "+", "_", "-", " " })
        {
            if (separator.Length > 0) yield return a + separator + b + separator + c;
            yield return Capitalize(a) + separator + Capitalize(b) + separator + Capitalize(c);
            yield return Capitalize(a) + separator + b + separator + c;
        }
    }

    private static IEnumerable<string> CaseVariants(string word)
    {
        int[] positions = Enumerable.Range(0, word.Length).Where(i => char.IsLetter(word[i])).ToArray();
        if (positions.Length > 20) yield break;
        for (int mask = 0; mask < (1 << positions.Length); mask++)
        {
            char[] chars = word.ToLowerInvariant().ToCharArray();
            for (int bit = 0; bit < positions.Length; bit++)
                if ((mask & (1 << bit)) != 0) chars[positions[bit]] = char.ToUpperInvariant(chars[positions[bit]]);
            yield return new string(chars);
        }
    }

    private static IEnumerable<string> TransformedPairs(string[] words)
    {
        foreach (string a in words)
        foreach (string b in words)
        foreach (string combined in new[] { a + b, Capitalize(a) + b, a + Capitalize(b), Capitalize(a) + Capitalize(b), (a + b).ToUpperInvariant() })
        {
            yield return new string(combined.Reverse().ToArray());
            yield return combined.Replace('a', '@').Replace('o', '0').Replace('i', '1').Replace('s', '$');
            foreach (string suffix in new[] { "!", "?", ".", "@", "#", "$", "1", "12", "123", "1234", "2026", "2025", "2024", "2014" })
                yield return combined + suffix;
        }
    }

    private static IEnumerable<string> LeetVariants(string word)
    {
        if (word.Length == 0) { yield return ""; yield break; }
        char c = char.ToLowerInvariant(word[0]);
        string replacements = c switch { 'a' => "aA@4", 'e' => "eE3", 'i' => "iI1!", 'l' => "lL1",
            'o' => "oO0", 's' => "sS$5", 't' => "tT7", 'b' => "bB8", 'g' => "gG9", 'z' => "zZ2",
            _ => char.IsLetter(c) ? $"{c}{char.ToUpperInvariant(c)}" : c.ToString() };
        foreach (string tail in LeetVariants(word[1..]))
        foreach (char replacement in replacements) yield return replacement + tail;
    }

    private static IEnumerable<string> UpperPairs(string[] words)
    {
        foreach (string a in words)
        foreach (string b in words)
        foreach (string separator in new[] { "", "!", "+", "-", "_", "@", "#", "$", "%", "&", "*", ".", " ", "1", "123" })
        {
            yield return a.ToUpperInvariant() + separator + b.ToUpperInvariant();
            yield return a.ToUpperInvariant() + separator + b;
            yield return a + separator + b.ToUpperInvariant();
        }
    }

    private static IEnumerable<string> ThreeWords(string[] words)
    {
        foreach (string a in words)
        foreach (string b in words)
        foreach (string c in words)
            yield return a + b + c;
    }

    private static IEnumerable<string> ModifiedWords(string[] words)
    {
        foreach (string word in words)
        {
            var variants = new[] { word, Capitalize(word), word.ToUpperInvariant(),
                new string(word.Reverse().ToArray()),
                new string(word.Select((c, i) => i % 2 == 0 ? char.ToUpperInvariant(c) : char.ToLowerInvariant(c)).ToArray()),
                word.Replace('a', '@').Replace('o', '0').Replace('i', '1').Replace('s', '$') }.Distinct();
            foreach (string variant in variants)
            {
                yield return variant;
                foreach (char punctuation in "!@#$%^&*?._-+") yield return variant + punctuation;
                for (int number = 0; number <= 9999; number++)
                {
                    yield return variant + number.ToString(System.Globalization.CultureInfo.InvariantCulture);
                    yield return number.ToString(System.Globalization.CultureInfo.InvariantCulture) + variant;
                }
            }
        }
    }

    private static void TestImport()
    {
        if (!CaseVariants("a1b").Order().SequenceEqual(new[] { "a1b", "A1b", "a1B", "A1B" }.Order()))
            throw new Exception("Capitalization enumeration failed.");
        if (ThreeWords(["a", "b"]).Count() != 8 || !LeetVariants("secret").Contains("s3cr3t"))
            throw new Exception("Extended search generator failed.");
        if (Lengths("ab", 4).Count() != 30)
            throw new Exception("Variable-length search enumeration failed.");
        string hash = Convert.ToHexString(Digest("123"));
        string source = "password0 = \"\"\npassword0 = \"314\"\n" +
            string.Join("\n", Enumerable.Range(1, 6).Select(id => $"    password{id} = '{hash}' # fixture"));
        var imported = ImportChallenges(source);
        if (!imported[0].SequenceEqual(Digest("314")) || !imported[6].SequenceEqual(Digest("123")))
            throw new Exception("Importer fixture failed.");
        try { ImportChallenges(source.Replace(hash, "invalid")); }
        catch (InvalidDataException) { Console.WriteLine("PASS: literal import, practice password, and invalid-hash rejection (synthetic fixtures)."); return; }
        throw new Exception("Invalid hashes were accepted.");
    }
}
