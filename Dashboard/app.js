// Ask the Python server for progress and put it on the page.
const projectsElement = document.querySelector("#projects");
const statusElement = document.querySelector("#status");
const isPublishedSite = location.hostname.endsWith("github.io");
const apiUrl = new URLSearchParams(location.search).get("api") ||
  (isPublishedSite ? "status.json" : "/api/status");
const number = new Intl.NumberFormat();
let refreshMilliseconds = 10_000;

function readableState(state) {
  return { running: "Running", complete: "Complete", stale: "Paused", missing: "No data", error: "Error" }[state] || state;
}

function formatTime(seconds) {
  if (seconds === 0) return "Done";
  if (!Number.isFinite(seconds)) return "Calculating...";
  const days = Math.floor(seconds / 86400);
  const hours = Math.floor((seconds % 86400) / 3600);
  const minutes = Math.max(1, Math.floor((seconds % 3600) / 60));
  if (days) return `About ${days}d ${hours}h`;
  if (hours) return `About ${hours}h ${minutes}m`;
  return `About ${minutes}m`;
}

function projectHtml(project) {
  const percent = Math.max(0, Math.min(100, project.percent));
  return `
    <article class="project">
      <div class="heading"><h2>${project.name}</h2><span class="state">${readableState(project.state)}</span></div>
      <p class="percent">${project.percent.toFixed(2)}%</p>
      <progress class="track" aria-label="${project.name} progress" max="100" value="${percent}">${percent}%</progress>
      <div class="details">
        <p><span class="label">Completed</span><strong>${number.format(project.completed)}</strong></p>
        <p><span class="label">Still needed</span><strong>${number.format(project.remaining)}</strong></p>
        <p><span class="label">Time left</span><strong>${formatTime(project.estimatedSecondsRemaining)}</strong></p>
      </div>
    </article>`;
}

async function update() {
  try {
    const response = await fetch(apiUrl, { cache: "no-store" });
    if (!response.ok) throw new Error(`API error: ${response.status}`);
    const data = await response.json();
    refreshMilliseconds = (data.refreshSeconds || 10) * 1000;
    projectsElement.innerHTML = data.projects.map(projectHtml).join("");
    statusElement.className = "";
    statusElement.textContent = isPublishedSite
      ? `Progress snapshot: ${data.generatedAt}`
      : `Updated ${new Date(data.generatedAt).toLocaleTimeString()}`;
  } catch (error) {
    statusElement.className = "error";
    statusElement.textContent = `Could not load progress: ${error.message}`;
  } finally {
    setTimeout(update, refreshMilliseconds);
  }
}

update();
