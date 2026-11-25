const preview = document.querySelector("#preview");
const placeholder = document.querySelector("#placeholder");
const snapshot = document.querySelector("#snapshot");
const toggle = document.querySelector("#toggle");
const status = document.querySelector("#status");
let paused = false;
let state = "connecting";

const labels = {
  streaming: "Live",
  unconfigured: "Set the camera URL in the app configuration",
  connecting: "Connecting to camera…",
  reconnecting: "Waiting for the camera to reconnect…",
  offline: "Bridge unavailable",
};

function update() {
  status.textContent = labels[state] ?? labels.offline;
  snapshot.hidden = state !== "streaming";
  if (!paused && state === "streaming") {
    if (!preview.hasAttribute("src")) {
      preview.src = "api/v1/stream.mjpg";
      preview.hidden = false;
      placeholder.hidden = true;
    }
  } else {
    preview.removeAttribute("src");
    preview.hidden = true;
    placeholder.hidden = false;
  }
  placeholder.textContent = paused ? "Live video paused" : "Waiting for the camera";
}

preview.addEventListener("load", () => {
  preview.hidden = false;
  placeholder.hidden = true;
});
preview.addEventListener("error", () => {
  preview.removeAttribute("src");
  preview.hidden = true;
  placeholder.hidden = false;
});
toggle.addEventListener("click", () => {
  paused = !paused;
  toggle.textContent = paused ? "Resume video" : "Pause video";
  update();
});

async function poll() {
  try {
    const response = await fetch("api/v1/status", { cache: "no-store" });
    if (!response.ok) throw new Error("Bridge unavailable");
    state = (await response.json()).state;
  } catch {
    state = "offline";
  } finally {
    update();
    setTimeout(poll, 2000);
  }
}

poll();
