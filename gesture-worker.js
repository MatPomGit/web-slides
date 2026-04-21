import { FilesetResolver, HandLandmarker } from "https://cdn.jsdelivr.net/npm/@mediapipe/tasks-vision@0.10.22/+esm";

const DEFAULT_CONFIG = {
  frameSkip: 2,
  cooldownMs: 1200,
  historyWindowMs: 380,
  minDeltaXRatio: 0.22,
  maxDeltaYRatio: 0.18,
  readyHoldMs: 140,
  openPalmMinExtendedFingers: 3,
  minPalmWidthRatio: 0.12,
  activeZone: { xMin: 0.10, xMax: 0.90, yMin: 0.10, yMax: 0.90 }
};

let config = structuredClone(DEFAULT_CONFIG);
let handLandmarker = null;
let paused = true;
let lastTriggerAt = 0;
let readySince = null;
let xHistory = [];
let overlayCanvas = null;
let overlayCtx = null;

function postStatus(handText, handClass, metrics = {}, landmarks = null) {
  self.postMessage({
    type: "status",
    handStatus: { text: handText, className: handClass },
    metrics,
    landmarks
  });
}

function distance(a, b) {
  const dx = a.x - b.x;
  const dy = a.y - b.y;
  return Math.sqrt(dx * dx + dy * dy);
}

function countExtendedFingers(landmarks) {
  const tips = [8, 12, 16, 20];
  const pips = [6, 10, 14, 18];
  let count = 0;
  for (let i = 0; i < tips.length; i++) {
    if (landmarks[tips[i]].y < landmarks[pips[i]].y) count++;
  }
  const thumbTip = landmarks[4];
  const thumbIp = landmarks[3];
  if (Math.abs(thumbTip.x - thumbIp.x) > 0.04) count++;
  return count;
}

function getPalmCenter(landmarks) {
  const ids = [0, 5, 9, 13, 17];
  const sum = ids.reduce((acc, idx) => {
    acc.x += landmarks[idx].x;
    acc.y += landmarks[idx].y;
    return acc;
  }, { x: 0, y: 0 });
  return { x: sum.x / ids.length, y: sum.y / ids.length };
}

function getPalmWidth(landmarks) {
  return distance(landmarks[5], landmarks[17]);
}

function isOpenPalm(landmarks) {
  const extended = countExtendedFingers(landmarks);
  const palmWidth = getPalmWidth(landmarks);
  return extended >= config.openPalmMinExtendedFingers && palmWidth >= config.minPalmWidthRatio;
}

function isPointInActiveZone(p) {
  const z = config.activeZone;
  return p.x >= z.xMin && p.x <= z.xMax && p.y >= z.yMin && p.y <= z.yMax;
}

function canTrigger(now) {
  return now - lastTriggerAt >= config.cooldownMs;
}

function resetTracking() {
  readySince = null;
  xHistory = [];
}

async function init() {
  try {
    self.postMessage({
      type: "status",
      workerStatus: { text: "ładowanie...", className: "value-warn" },
      handStatus: { text: "brak", className: "value-muted" },
      metrics: { deltaX: 0, deltaY: 0, direction: "brak", presence: 0 }
    });

    const vision = await FilesetResolver.forVisionTasks(
      "https://cdn.jsdelivr.net/npm/@mediapipe/tasks-vision@0.10.22/wasm"
    );

    handLandmarker = await HandLandmarker.createFromOptions(vision, {
      baseOptions: {
        modelAssetPath: "https://storage.googleapis.com/mediapipe-models/hand_landmarker/hand_landmarker/float16/1/hand_landmarker.task"
      },
      runningMode: "VIDEO",
      numHands: 1,
      minHandDetectionConfidence: 0.6,
      minHandPresenceConfidence: 0.6,
      minTrackingConfidence: 0.6
    });

    self.postMessage({ type: "ready" });
  } catch (error) {
    self.postMessage({ type: "error", message: error.message || String(error) });
  }
}

function drawActiveZone() {
  if (!overlayCtx || !overlayCanvas) return;
  overlayCtx.clearRect(0, 0, overlayCanvas.width, overlayCanvas.height);
  const { xMin, xMax, yMin, yMax } = config.activeZone;
  const x = xMin * overlayCanvas.width;
  const y = yMin * overlayCanvas.height;
  const w = (xMax - xMin) * overlayCanvas.width;
  const h = (yMax - yMin) * overlayCanvas.height;
  overlayCtx.save();
  overlayCtx.strokeStyle = "rgba(255,255,255,0.35)";
  overlayCtx.lineWidth = 2;
  overlayCtx.setLineDash([6, 6]);
  overlayCtx.strokeRect(x, y, w, h);
  overlayCtx.restore();
}

function drawLandmarks(landmarks) {
  if (!overlayCtx || !overlayCanvas) return;
  drawActiveZone();
  if (!landmarks || !landmarks.length) return;
  overlayCtx.save();
  overlayCtx.fillStyle = "rgba(61, 220, 151, 0.95)";
  for (const p of landmarks) {
    const x = p.x * overlayCanvas.width;
    const y = p.y * overlayCanvas.height;
    overlayCtx.beginPath();
    overlayCtx.arc(x, y, 3, 0, Math.PI * 2);
    overlayCtx.fill();
  }
  overlayCtx.restore();
}

function processGesture(landmarks, now, presence = 1) {
  const center = getPalmCenter(landmarks);
  const openPalm = isOpenPalm(landmarks);
  const inZone = isPointInActiveZone(center);

  if (!openPalm || !inZone) {
    resetTracking();
    postStatus(openPalm ? "poza strefą" : "dłoń niegotowa", "value-warn", {
      deltaX: 0,
      deltaY: 0,
      direction: "brak",
      presence
    }, landmarks);
    return;
  }

  if (readySince === null) readySince = now;
  if (now - readySince < config.readyHoldMs) {
    postStatus("gotowa", "value-ok", {
      deltaX: 0,
      deltaY: 0,
      direction: "czekanie",
      presence
    }, landmarks);
    return;
  }

  xHistory.push({ t: now, x: center.x, y: center.y });
  xHistory = xHistory.filter(p => now - p.t <= config.historyWindowMs);

  if (xHistory.length < 4) {
    postStatus("gotowa", "value-ok", {
      deltaX: 0,
      deltaY: 0,
      direction: "zbieranie",
      presence
    }, landmarks);
    return;
  }

  const xs = xHistory.map(p => p.x);
  const ys = xHistory.map(p => p.y);
  const deltaX = Math.max(...xs) - Math.min(...xs);
  const deltaY = Math.max(...ys) - Math.min(...ys);
  const first = xHistory[0];
  const last = xHistory[xHistory.length - 1];
  const diff = last.x - first.x;
  const direction = diff > 0.02 ? "prawo" : diff < -0.02 ? "lewo" : "brak";

  postStatus("gotowa", "value-ok", { deltaX, deltaY, direction, presence }, landmarks);

  if (!canTrigger(now)) return;

  if (diff > 0.12 && deltaX >= config.minDeltaXRatio && deltaY <= config.maxDeltaYRatio) {
    lastTriggerAt = now;
    resetTracking();
    self.postMessage({ type: "gesture", action: "next" });
  } else if (diff < -0.12 && deltaX >= config.minDeltaXRatio && deltaY <= config.maxDeltaYRatio) {
    lastTriggerAt = now;
    resetTracking();
    self.postMessage({ type: "gesture", action: "prev" });
  }
}

self.addEventListener("message", async (event) => {
  const msg = event.data || {};
  try {
    if (msg.type === "attachCanvas") {
      overlayCanvas = msg.canvas;
      overlayCtx = overlayCanvas.getContext("2d");
      drawActiveZone();
    } else if (msg.type === "setConfig") {
      config = {
        ...structuredClone(DEFAULT_CONFIG),
        ...msg.config,
        activeZone: { ...DEFAULT_CONFIG.activeZone, ...(msg.config?.activeZone || {}) }
      };
      drawActiveZone();
    } else if (msg.type === "setPaused") {
      paused = !!msg.paused;
      if (paused) {
        resetTracking();
        drawActiveZone();
      }
    } else if (msg.type === "processFrame") {
      if (paused || !handLandmarker || !msg.bitmap) {
        msg.bitmap?.close?.();
        self.postMessage({ type: "processed" });
        return;
      }

      const result = handLandmarker.detectForVideo(msg.bitmap, msg.timestamp);
      msg.bitmap.close?.();

      if (result.landmarks && result.landmarks.length > 0) {
        const landmarks = result.landmarks[0];
        drawLandmarks(landmarks);
        processGesture(landmarks, msg.timestamp, result.handednesses?.[0]?.[0]?.score ?? 1);
        self.postMessage({ type: "processed", landmarks });
      } else {
        resetTracking();
        drawActiveZone();
        postStatus("brak", "value-muted", {
          deltaX: 0,
          deltaY: 0,
          direction: "brak",
          presence: 0
        }, null);
        self.postMessage({ type: "processed" });
      }
    }
  } catch (error) {
    try { msg.bitmap?.close?.(); } catch {}
    self.postMessage({ type: "error", message: error.message || String(error) });
    self.postMessage({ type: "processed" });
  }
});

init();
