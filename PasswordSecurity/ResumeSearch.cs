// Searches every six-character value made from a-z, A-Z, and 0-9.
//
// The search space contains 62^6 = 56,800,235,584 candidates. Progress is
// checkpointed every million guesses, so an interrupted run can resume instead
// of starting over.

using System.Text.Json;

namespace PasswordSecurity;

internal static partial class Program
{
    private const string SearchAlphabet =
        "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789";

    private const int SearchAlphabetSize = 62;
    private const int SearchPasswordLength = 6;
    private const long TotalCandidates = 56_800_235_584L;
    private const long CheckpointInterval = 1_000_000L;
    private const string CheckpointPath = "password-search-state.json";
    private const string ChallengeSourcePath = "original/crack_password.py";

    private sealed record SearchState(
        long Next,
        long Total,
        string Status,
        string? Password);

    private static int ResumeSix()
    {
        // A named mutex prevents two copies from updating the same checkpoint.
        using var searchLock = new Mutex(false, "ScienceFairPasswordSearch");

        if (!TryAcquire(searchLock))
        {
            Console.WriteLine("The six-character search is already running.");
            return 0;
        }

        try
        {
            SearchState state = LoadCheckpoint();
            ValidateCheckpoint(state);

            if (state.Status is "found" or "exhausted")
            {
                Console.WriteLine($"The search is already {state.Status}.");
                return 0;
            }

            byte[] targetHash =
                ImportChallenges(File.ReadAllText(ChallengeSourcePath))[6];

            SaveCheckpoint(state);
            Console.WriteLine(
                $"Resuming six-character search at {state.Next:N0}/{TotalCandidates:N0}.");

            return SearchCandidates(state.Next, targetHash);
        }
        finally
        {
            searchLock.ReleaseMutex();
        }
    }

    private static bool TryAcquire(Mutex searchLock)
    {
        try
        {
            return searchLock.WaitOne(0);
        }
        catch (AbandonedMutexException)
        {
            // The previous process ended without releasing its lock. The OS has
            // transferred ownership to this process, so resuming is safe.
            return true;
        }
    }

    private static SearchState LoadCheckpoint()
    {
        if (!File.Exists(CheckpointPath))
        {
            return new SearchState(0, TotalCandidates, "running", null);
        }

        string json = File.ReadAllText(CheckpointPath);
        return JsonSerializer.Deserialize<SearchState>(json)
            ?? throw new InvalidDataException("The search checkpoint is empty.");
    }

    private static void ValidateCheckpoint(SearchState state)
    {
        bool invalid =
            state.Total != TotalCandidates ||
            state.Next < 0 ||
            state.Next > TotalCandidates ||
            state.Status is not ("running" or "found" or "exhausted");

        if (invalid)
        {
            throw new InvalidDataException("The search checkpoint is invalid.");
        }
    }

    private static int SearchCandidates(long startingIndex, byte[] targetHash)
    {
        for (long index = startingIndex; index < TotalCandidates; index++)
        {
            string candidate = CandidateAt(index);

            if (Digest(candidate).AsSpan().SequenceEqual(targetHash))
            {
                var completed = new SearchState(
                    index + 1,
                    TotalCandidates,
                    "found",
                    candidate);

                SaveCheckpoint(completed);
                Console.WriteLine(
                    $"FOUND challenge 6: {candidate}; position {index + 1:N0}.");
                return 0;
            }

            long nextIndex = index + 1;
            if (nextIndex % CheckpointInterval == 0)
            {
                SaveCheckpoint(new SearchState(
                    nextIndex,
                    TotalCandidates,
                    "running",
                    null));

                Console.WriteLine(
                    $"Progress: {nextIndex:N0}/{TotalCandidates:N0}");
            }
        }

        SaveCheckpoint(new SearchState(
            TotalCandidates,
            TotalCandidates,
            "exhausted",
            null));

        Console.WriteLine("The six-character search exhausted every candidate.");
        return 0;
    }

    private static string CandidateAt(long index)
    {
        Span<char> characters = stackalloc char[SearchPasswordLength];

        for (int position = SearchPasswordLength - 1; position >= 0; position--)
        {
            characters[position] =
                SearchAlphabet[(int)(index % SearchAlphabetSize)];

            index /= SearchAlphabetSize;
        }

        return new string(characters);
    }

    private static void SaveCheckpoint(SearchState state)
    {
        string temporaryPath = CheckpointPath + ".tmp";
        string json = JsonSerializer.Serialize(state);

        // The notification watcher may briefly have the checkpoint open.
        // Retry that harmless file-sharing race instead of ending a long search.
        for (int attempt = 1; attempt <= 20; attempt++)
        {
            try
            {
                File.WriteAllText(temporaryPath, json);
                File.Move(temporaryPath, CheckpointPath, overwrite: true);
                return;
            }
            catch (Exception error) when (
                attempt < 20 &&
                error is IOException or UnauthorizedAccessException)
            {
                Thread.Sleep(100);
            }
        }
    }
}
