// PROGRAM OVERVIEW FOR FIRST-TIME CODERS
// --------------------------------------
// A program is a precise recipe for a computer. This one creates possible
// password strings, hashes each one with MD5, and compares the resulting bytes
// with a target hash. It NEVER signs in to a website or contacts an account.
//
// Main() is the front door. It reads command-line options and chooses a task.
// Methods such as BruteForce() and Dictionary() generate guesses. Guess() tests
// those guesses while counting attempts and measuring time. Run() saves CSV
// files, which are plain text tables that Excel and spreadsheet apps can open.
//
// C# syntax cheatsheet:
//   string = text; int/long = whole number; double = decimal number
//   if = make a decision; for/foreach = repeat work; return = send a result back
//   // begins a comment for humans; the computer ignores comments

using System.Diagnostics;
using System.Globalization;
using System.Numerics;
using System.Security.Cryptography;
using System.Text;

namespace PasswordSecurity;

internal static partial class Program
{
    private static readonly string[] Words = ["apple", "river", "cloud", "tiger", "moon", "robot"];
    private const string Lower = "abcdefghijklmnopqrstuvwxyz";
    private const string Letters = Lower + "ABCDEFGHIJKLMNOPQRSTUVWXYZ";
    private sealed record GuessResult(string Status, int Guesses, double Seconds);

    private static int Main(string[] args)
    {
        try
        {
            return RunCommand(args);
        }
        catch (Exception error)
        {
            Console.Error.WriteLine(error.Message);
            return 1;
        }
    }

    private static int RunCommand(string[] args)
    {
        if (args is ["--resume-six"])
            return ResumeSix();

        if (args is ["--challenge", .. var challengeArgs])
            return RunChallenge(challengeArgs);

        if (args is ["--test-import"])
        {
            TestImport();
            return 0;
        }

        if (args is ["--self-test"])
        {
            SelfTest();
            return 0;
        }

        if (args.Contains("--help"))
        {
            PrintHelp();
            return 0;
        }

        (int repeats, int maxGuesses, string outputFolder) =
            ParseExperimentOptions(args);

        Run(repeats, maxGuesses, outputFolder);
        return 0;
    }

    private static (int Repeats, int MaxGuesses, string OutputFolder)
        ParseExperimentOptions(string[] args)
    {
        int repeats = 3;
        int maxGuesses = 200_000;
        string outputFolder = "results";

        for (int index = 0; index < args.Length; index += 2)
        {
            string option = args[index];
            if (index + 1 >= args.Length)
                throw new ArgumentException($"Missing value for {option}.");

            string value = args[index + 1];
            switch (option)
            {
                case "--repeats":
                    repeats = ParsePositiveInt(value);
                    break;
                case "--max-guesses":
                    maxGuesses = ParsePositiveInt(value);
                    break;
                case "--output":
                    outputFolder = value;
                    break;
                default:
                    throw new ArgumentException($"Unknown option: {option}");
            }
        }

        return (repeats, maxGuesses, outputFolder);
    }

    private static void PrintHelp()
    {
        Console.WriteLine("Password Security classroom experiment");
        Console.WriteLine();
        Console.WriteLine("Run a baseline experiment:");
        Console.WriteLine("  dotnet run -c Release -- --repeats 5 --max-guesses 15000000");
        Console.WriteLine("Check that the program works:");
        Console.WriteLine("  dotnet run -c Release -- --self-test");
        Console.WriteLine("Run a Science Buddies challenge (0 through 6):");
        Console.WriteLine("  dotnet run -c Release -- --challenge 1");
        Console.WriteLine("Resume the six-character challenge search:");
        Console.WriteLine("  dotnet run -c Release -- --resume-six");
        Console.WriteLine();
        Console.WriteLine("--repeats N runs each measurement N times.");
        Console.WriteLine("--max-guesses N stops a baseline trial after N guesses.");
        Console.WriteLine("--output FOLDER chooses where result folders are created.");
        Console.WriteLine("These searches compare local classroom hashes; they do not access accounts.");
    }

    private static int ParsePositiveInt(string value)
    {
        return int.TryParse(value, out int number) && number > 0
            ? number
            : throw new ArgumentException(
                "Numeric options must be positive integers.");
    }

    // Fast unsalted MD5 is used only as the classroom project's comparison model.
    private static byte[] Digest(string text) => MD5.HashData(Encoding.UTF8.GetBytes(text));

    private static IEnumerable<string> BruteForce(string alphabet, int length)
    {
        if (alphabet.Length == 0 || length < 1) throw new ArgumentException("Invalid alphabet or length.");
        var indices = new int[length];
        var chars = new char[length];
        while (true)
        {
            for (int i = 0; i < length; i++) chars[i] = alphabet[indices[i]];
            yield return new string(chars);
            int position = length - 1;
            while (position >= 0 && ++indices[position] == alphabet.Length)
                indices[position--] = 0;
            if (position < 0) yield break;
        }
    }

    private static string Capitalize(string word) => char.ToUpperInvariant(word[0]) + word[1..];

    private static IEnumerable<string> Dictionary()
    {
        foreach (string word in Words) { yield return word; yield return Capitalize(word); }
    }

    private static IEnumerable<string> WordPairs()
    {
        foreach (string first in Words)
        foreach (string second in Words)
        foreach (string separator in new[] { "", "+", "7" })
        foreach (string a in new[] { first, Capitalize(first) })
        foreach (string b in new[] { second, Capitalize(second) })
            yield return a + separator + b;
    }

    private static GuessResult Guess(byte[] target, IEnumerable<string> candidates, int limit)
    {
        // Stopwatch measures elapsed time. "attempts" is the dependent variable
        // we care about: how many candidates were tested before a match or limit.
        var timer = Stopwatch.StartNew();
        int attempts = 0;
        foreach (string candidate in candidates.Take(limit))
        {
            attempts++;
            if (Digest(candidate).AsSpan().SequenceEqual(target))
                return new("found", attempts, timer.Elapsed.TotalSeconds);
        }
        return new("not_found_within_search", attempts, timer.Elapsed.TotalSeconds);
    }

    private static void Csv(TextWriter writer, params object[] fields)
    {
        // CSV means comma-separated values. Quotes keep commas inside a value
        // from accidentally creating an extra spreadsheet column.
        writer.WriteLine(string.Join(",", fields.Select(field =>
        {
            string value = Convert.ToString(field, CultureInfo.InvariantCulture) ?? "";
            return "\"" + value.Replace("\"", "\"\"") + "\"";
        })));
    }

    private static void Run(int repeats, int limit, string root)
    {
        string output = Path.GetFullPath(Path.Combine(root, $"csharp-{DateTime.Now:yyyyMMdd-HHmmss}-{Guid.NewGuid():N}"));
        Directory.CreateDirectory(output);
        var alphabets = new[] { ("digits", "0123456789"), ("lowercase", Lower),
            ("mixed_letters", Letters), ("letters_digits", Letters + "0123456789") };
        using (var theory = new StreamWriter(Path.Combine(output, "theoretical.csv")))
        {
            Csv(theory, "alphabet", "alphabet_size", "length", "possibilities",
                "worst_seconds_at_one_guess_per_second", "expected_guesses_uniform_random");
            foreach (var (name, alphabet) in alphabets)
            for (int length = 1; length <= 8; length++)
            {
                BigInteger size = BigInteger.Pow(alphabet.Length, length);
                Csv(theory, name, alphabet.Length, length, size, size, ((decimal)size + 1) / 2);
            }
        }
        // Warm up hashing and both candidate generators before measured trials.
        Guess(Digest("99"), BruteForce("0123456789", 2), 100);
        Guess(Digest("Moon"), Dictionary(), 12);
        Guess(Digest("Robot+River"), WordPairs(), 432);
        using var measurements = new StreamWriter(Path.Combine(output, "measurements.csv"));
        Csv(measurements, "method", "sample", "alphabet", "length", "trial", "search_space", "status", "guesses", "seconds");
        int count = 0;
        var report = new StringBuilder("# Password Security: measured password experiment\n\n" +
            $"{repeats} repetitions per condition; {limit:N0} guesses allowed per trial.\n\n" +
            "| Method | Alphabet | Sample | Found / trials | Guesses per trial | Mean seconds | Min seconds | Max seconds |\n" +
            "|---|---|---|---:|---:|---:|---:|---:|\n");
        using var summary = new StreamWriter(Path.Combine(output, "summary.csv"));
        Csv(summary, "method", "alphabet", "sample", "length", "found_trials", "trials", "guesses", "mean_seconds", "min_seconds", "max_seconds");
        void Measure(string method, string target, string alphabet, BigInteger size, Func<IEnumerable<string>> candidates)
        {
            byte[] hash = Digest(target);
            var trials = new List<GuessResult>();
            for (int trial = 1; trial <= repeats; trial++)
            {
                GuessResult result = Guess(hash, candidates(), limit);
                trials.Add(result);
                Csv(measurements, method, target, alphabet, target.Length, trial, size, result.Status, result.Guesses, result.Seconds);
                count++;
                if (trial == 1) Console.WriteLine($"{method} / {alphabet} / length {target.Length}: {result.Status}, {result.Guesses:N0} guesses, {result.Seconds:F6}s");
            }
            int found = trials.Count(r => r.Status == "found");
            double mean = trials.Average(r => r.Seconds), min = trials.Min(r => r.Seconds), max = trials.Max(r => r.Seconds);
            Csv(summary, method, alphabet, target, target.Length, found, repeats, trials[0].Guesses, mean, min, max);
            report.AppendLine(FormattableString.Invariant($"| {method} | {alphabet} | `{target}` | {found}/{repeats} | {trials[0].Guesses} | {mean:F6} | {min:F6} | {max:F6} |"));
        }
        foreach (var (name, alphabet) in alphabets)
        for (int length = 1; length <= 4; length++)
            Measure("brute_force", new string(alphabet[^1], length), name,
                BigInteger.Pow(alphabet.Length, length), () => BruteForce(alphabet, length));
        foreach (string target in new[] { "tiger", "Moon", "Robot+River", "x9Q!m2" })
        {
            Measure("dictionary", target, "toy_dictionary", 12, Dictionary);
            Measure("word_pairs", target, "toy_dictionary", 432, WordPairs);
        }
        report.Append("\n## Interpretation\n\n" +
            "Brute-force samples occupy the last position in a fixed-length search. " +
            "For completed searches, the guess count equals alphabet size raised to password length. " +
            "Adding a character multiplies this worst-case count by the alphabet size.\n\n" +
            "Dictionary results depend on the supplied words and enumeration order. " +
            "A longer predictable combination can be found in fewer guesses than a short exhaustive-search target. " +
            "A failed dictionary search only means the sample was not among the tested candidates.\n\n" +
            "## Limits\n\n" +
            "These are repeated timing measurements of the same synthetic samples, not a population study. " +
            "Incomplete searches report time spent testing, not time to crack. " +
            "Tiny durations are noisy; .NET warmup, CPU load, and garbage collection affect timing. " +
            "Minesweeper training ran concurrently during this experiment. " +
            "Fast unsalted MD5 results do not predict the time to access real accounts.\n");
        File.WriteAllText(Path.Combine(output, "REPORT.md"), report.ToString());
        File.WriteAllText(Path.Combine(output, "notes.txt"),
            $"C# / {System.Runtime.InteropServices.RuntimeInformation.FrameworkDescription}\n" +
            $"Repeats: {repeats}; maximum guesses per trial: {limit}\n" +
            "Synthetic samples, fixed-length brute force, last-candidate targets.\n" +
            "Not-found trials are limited searches, not measured crack times.\n" +
            "Record background CPU load when comparing runs. Initial setup ran alongside Minesweeper.\n" +
            "Fast unsalted MD5 is an educational model, not modern password storage.\n");
        Console.WriteLine($"Saved {count} measured trials and 32 theoretical rows to {output}");
    }

    private static void SelfTest()
    {
        int passed = 0;
        void Check(bool condition, string name)
        {
            if (!condition) throw new Exception($"FAIL: {name}");
            Console.WriteLine($"PASS: {name}"); passed++;
        }
        Check(BruteForce("01", 2).SequenceEqual(new[] { "00", "01", "10", "11" }), "Leading zeros and candidate order");
        GuessResult known = Guess(Digest("09"), BruteForce("0123456789", 2), 100);
        Check(known.Status == "found" && known.Guesses == 10, "Known guess count");
        GuessResult limited = Guess(Digest("99"), BruteForce("0123456789", 2), 10);
        Check(limited.Status == "not_found_within_search" && limited.Guesses == 10, "Search limit");
        Check(Guess(Digest("Moon"), Dictionary(), 100).Guesses == 10, "Dictionary capitalization");
        GuessResult pair = Guess(Digest("Robot+River"), WordPairs(), 1000);
        Check(pair.Status == "found" && pair.Guesses == 380 && WordPairs().Count() == 432, "Word-pair search");
        Check(BigInteger.Pow(62, 8) == BigInteger.Parse("218340105584896"), "Search-space calculation");
        Check(
            CandidateAt(0) == "aaaaaa" &&
            CandidateAt(61) == "aaaaa9" &&
            CandidateAt(62) == "aaaaba" &&
            CandidateAt(TotalCandidates - 1) == "999999",
            "Six-character candidate order");
        Console.WriteLine($"{passed} checks passed.");
    }
}
