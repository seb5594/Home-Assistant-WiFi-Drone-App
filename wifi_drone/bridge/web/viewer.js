const preview = document.querySelector("#preview");
const placeholder = document.querySelector("#placeholder");
const snapshot = document.querySelector("#snapshot");
const toggle = document.querySelector("#toggle");
const status = document.querySelector("#status");
let paused = false;
let state = "connecting";
let wifiState;

const labels = {
  streaming: "Live",
  unconfigured: "Set the camera URL in the app configuration",
  connecting: "Connecting to camera…",
  reconnecting: "Waiting for the camera to reconnect…",
  offline: "Bridge unavailable",
};

const wifiLabels = {
  waiting_helper: "Waiting for WiFi App Helper",
  pairing_required: "Set the same pairing secret in both apps",
  helper_protocol: "WiFi App Helper protocol is incompatible",
  adapter_unavailable: "Choose an available adapter in the app configuration",
  joining: "Joining the drone WiFi…",
  dhcp: "Waiting for the drone network address…",
  joining_failed: "WiFi setup failed. Check the app logs.",
};

function update() {
  status.textContent = wifiLabels[wifiState] ?? labels[state] ?? labels.offline;
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
    const result = await response.json();
    state = result.state;
    wifiState = result.wifi_state;
  } catch {
    state = "offline";
    wifiState = undefined;
  } finally {
    update();
    setTimeout(poll, 2000);
  }
}

poll();
