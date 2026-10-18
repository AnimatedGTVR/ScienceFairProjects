// Small browser version of the classroom password experiment.
// It compares generated guesses with text entered on this page. Nothing is uploaded.
const guesserForm = document.querySelector("#guesser-form");
const passwordInput = document.querySelector("#demo-password");
const resultElement = document.querySelector("#guesser-result");
const testButton = guesserForm.querySelector("button");

const MAX_GUESSES = 500_000;
const ALPHANUMERIC = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789";
let commonPasswords;

// Give the browser a chance to repaint between large batches of guesses.
function pauseForBrowser() {
  return new Promise(resolve => setTimeout(resolve, 0));
}

async function loadCommonPasswords() {
  if (commonPasswords) return commonPasswords;
  const response = await fetch("passwords.txt");
  if (!response.ok) throw new Error("The classroom word list could not be loaded.");
  commonPasswords = (await response.text()).split(/\r?\n/).map(word => word.trim()).filter(Boolean);
  return commonPasswords;
}

async function runDemo(target) {
  let guesses = 0;
  const started = performance.now();

  function check(candidate, method) {
    guesses += 1;
    return candidate === target ? method : null;
  }

  // Method 1: PIN-style numbers from 0 through 9999.
  for (let value = 0; value <= 9999 && guesses < MAX_GUESSES; value += 1) {
    const foundBy = check(String(value), "number search");
    if (foundBy) return { foundBy, guesses, milliseconds: performance.now() - started };
  }

  const words = await loadCommonPasswords();

  // Method 2: each entry in the supplied common-password list.
  for (const word of words) {
    if (guesses >= MAX_GUESSES) break;
    const foundBy = check(word, "common-password list");
    if (foundBy) return { foundBy, guesses, milliseconds: performance.now() - started };
  }

  // Method 3: two common words joined together, such as secretpassword.
  for (let first = 0; first < words.length && guesses < MAX_GUESSES; first += 1) {
    for (let second = 0; second < words.length && guesses < MAX_GUESSES; second += 1) {
      const foundBy = check(words[first] + words[second], "two-word search");
      if (foundBy) return { foundBy, guesses, milliseconds: performance.now() - started };
    }
    if (first % 25 === 0) await pauseForBrowser();
  }

  // Method 4: every letter-and-number string up to three characters long.
  for (let length = 1; length <= 3 && guesses < MAX_GUESSES; length += 1) {
    const indexes = Array(length).fill(0);
    const combinations = ALPHANUMERIC.length ** length;
    for (let count = 0; count < combinations && guesses < MAX_GUESSES; count += 1) {
      let candidate = "";
      for (const index of indexes) candidate += ALPHANUMERIC[index];
      const foundBy = check(candidate, "short letter-and-number brute force");
      if (foundBy) return { foundBy, guesses, milliseconds: performance.now() - started };

      for (let position = length - 1; position >= 0; position -= 1) {
        indexes[position] += 1;
        if (indexes[position] < ALPHANUMERIC.length) break;
        indexes[position] = 0;
      }
      if (count % 25_000 === 0) await pauseForBrowser();
    }
  }

  return { foundBy: null, guesses, milliseconds: performance.now() - started };
}

guesserForm.addEventListener("submit", async event => {
  event.preventDefault();
  const target = passwordInput.value;
  if (!target) return;

  testButton.disabled = true;
  resultElement.className = "guesser-result";
  resultElement.textContent = "Testing guesses on this device...";

  try {
    const result = await runDemo(target);
    const elapsed = result.milliseconds < 1 ? "less than 1 millisecond" : `${Math.round(result.milliseconds).toLocaleString()} milliseconds`;
    resultElement.className = `guesser-result ${result.foundBy ? "found" : "not-found"}`;
    resultElement.innerHTML = result.foundBy
      ? `<strong>Found by the ${result.foundBy}.</strong>${result.guesses.toLocaleString()} guesses in ${elapsed}.`
      : `<strong>Not found within this demo's limits.</strong>${result.guesses.toLocaleString()} guesses were tested in ${elapsed}. This does not mean the password is unguessable.`;
  } catch (error) {
    resultElement.className = "guesser-result error";
    resultElement.textContent = error.message;
  } finally {
    // Clear the entered value as soon as the test finishes.
    passwordInput.value = "";
    testButton.disabled = false;
    passwordInput.focus();
  }
});
