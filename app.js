    const ui = {
      hud: document.getElementById("hud"),
      cameraStatus: document.getElementById("cameraStatus"),
      workerStatus: document.getElementById("workerStatus"),
      handStatus: document.getElementById("handStatus"),
      lastAction: document.getElementById("lastAction"),
      modeStatus: document.getElementById("modeStatus"),
      inputModeStatus: document.getElementById("inputModeStatus"),
      startBtn: document.getElementById("startBtn"),
      toggleBtn: document.getElementById("toggleBtn"),
      prevBtn: document.getElementById("prevBtn"),
      nextBtn: document.getElementById("nextBtn"),
      previewToggleBtn: document.getElementById("previewToggleBtn"),
      keyboardModeBtn: document.getElementById("keyboardModeBtn"),
      detectionToggleBtn: document.getElementById("detectionToggleBtn"),
      video: document.getElementById("camera"),
      overlay: document.getElementById("overlay"),
      flash: document.getElementById("flash"),
      cameraPlaceholder: document.getElementById("cameraPlaceholder"),
      debugPanel: document.getElementById("debugPanel"),
      saveConfigBtn: document.getElementById("saveConfigBtn"),
      resetConfigBtn: document.getElementById("resetConfigBtn"),
      testPrevBtn: document.getElementById("testPrevBtn"),
      testNextBtn: document.getElementById("testNextBtn"),
      closeDebugBtn: document.getElementById("closeDebugBtn"),
      bootOverlay: document.getElementById("bootOverlay"),
      bootStartBtn: document.getElementById("bootStartBtn"),
      bootDismissBtn: document.getElementById("bootDismissBtn"),
      bootTroubleshootingBtn: document.getElementById("bootTroubleshootingBtn"),
      bootTroubleshooting: document.getElementById("bootTroubleshooting"),
      bootError: document.getElementById("bootError"),
      ariaAnnouncements: document.getElementById("ariaAnnouncements"),
      metricDeltaX: document.getElementById("metricDeltaX"),
      metricDeltaY: document.getElementById("metricDeltaY"),
      metricDirection: document.getElementById("metricDirection"),
      metricPresence: document.getElementById("metricPresence"),
      metricInputFps: document.getElementById("metricInputFps"),
      metricDetectionFps: document.getElementById("metricDetectionFps"),
      metricLatencyAvg: document.getElementById("metricLatencyAvg"),
      metricDroppedFrames: document.getElementById("metricDroppedFrames"),
      metricTriggersPerMin: document.getElementById("metricTriggersPerMin"),
      metricConfidenceHistogram: document.getElementById("metricConfidenceHistogram"),
      exportMetricsBtn: document.getElementById("exportMetricsBtn"),
      frameSkip: document.getElementById("frameSkip"),
      cooldownMs: document.getElementById("cooldownMs"),
      historyWindowMs: document.getElementById("historyWindowMs"),
      minDeltaXRatio: document.getElementById("minDeltaXRatio"),
      maxDeltaYRatio: document.getElementById("maxDeltaYRatio"),
      readyHoldMs: document.getElementById("readyHoldMs"),
      openPalmMinExtendedFingers: document.getElementById("openPalmMinExtendedFingers"),
      minPalmWidthRatio: document.getElementById("minPalmWidthRatio"),
      zoneXMin: document.getElementById("zoneXMin"),
      zoneXMax: document.getElementById("zoneXMax"),
      zoneYMin: document.getElementById("zoneYMin"),
      zoneYMax: document.getElementById("zoneYMax")
    };

    function createNoopElement(tagName = "div") {
      // Tworzymy odłączony element DOM jako bezpieczny fallback dla opcjonalnych kontrolek UI.
      return document.createElement(tagName);
    }

    function assertUiElements(uiRegistry) {
      // Walidujemy kompletność krytycznych elementów UI, aby wcześnie wykryć regresje w HTML.
      const REQUIRED_UI_KEYS = [
        "hud",
        "cameraStatus",
        "workerStatus",
        "handStatus",
        "lastAction",
        "modeStatus",
        "inputModeStatus",
        "startBtn",
        "toggleBtn",
        "prevBtn",
        "nextBtn",
        "previewToggleBtn",
        "keyboardModeBtn",
        "detectionToggleBtn",
        "video",
        "overlay",
        "flash",
        "cameraPlaceholder",
        "bootOverlay",
        "bootStartBtn"
      ];

      const OPTIONAL_UI_FALLBACK_TAGS = {
        debugPanel: "aside",
        saveConfigBtn: "button",
        resetConfigBtn: "button",
        testPrevBtn: "button",
        testNextBtn: "button",
        closeDebugBtn: "button",
        bootDismissBtn: "button",
        bootTroubleshootingBtn: "button",
        bootTroubleshooting: "div",
        bootError: "div",
        ariaAnnouncements: "div",
        metricDeltaX: "span",
        metricDeltaY: "span",
        metricDirection: "span",
        metricPresence: "span",
        metricInputFps: "span",
        metricDetectionFps: "span",
        metricLatencyAvg: "span",
        metricDroppedFrames: "span",
        metricTriggersPerMin: "span",
        metricConfidenceHistogram: "span",
        exportMetricsBtn: "button",
        frameSkip: "input",
        cooldownMs: "input",
        historyWindowMs: "input",
        minDeltaXRatio: "input",
        maxDeltaYRatio: "input",
        readyHoldMs: "input",
        openPalmMinExtendedFingers: "input",
        minPalmWidthRatio: "input",
        zoneXMin: "input",
        zoneXMax: "input",
        zoneYMin: "input",
        zoneYMax: "input"
      };

      const missingRequired = REQUIRED_UI_KEYS.filter((key) => !uiRegistry[key]);
      if (missingRequired.length) {
        console.error(
          `[UI BOOT] Brak wymaganych elementów (${missingRequired.length}): ${missingRequired.join(", ")}. ` +
          "Przerywam inicjalizację aplikacji."
        );
        return false;
      }

      const missingOptional = [];
      for (const [key, tagName] of Object.entries(OPTIONAL_UI_FALLBACK_TAGS)) {
        if (!uiRegistry[key]) {
          uiRegistry[key] = createNoopElement(tagName);
          missingOptional.push(key);
        }
      }
      if (missingOptional.length) {
        console.warn(
          `[UI BOOT] Brak opcjonalnych elementów (${missingOptional.length}): ${missingOptional.join(", ")}. ` +
          "Włączono fallback/no-op."
        );
      }

      return true;
    }

    if (!assertUiElements(ui)) {
      throw new Error("UI validation failed: missing required DOM nodes.");
    }

    const deck = new Reveal({
      hash: true,
      controls: true,
      progress: true,
      center: true,
      transition: "slide",
      plugins: [ RevealMarkdown ]
    });
    await deck.initialize();

    let ctx = null;

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

    const CONFIG_KEY = "gestureRevealWorkerConfigV1";
    const DETECTION_DISABLED_KEY = "gestureRevealDetectionDisabledV1";
    let config = loadConfig();
    let worker = null;
    let cameraStream = null;
    let offscreen = null;
    let captureCanvas = null;
    let captureCtx = null;
    let detectionPaused = true;
    let workerReady = false;
    let cameraReady = false;
    let debugVisible = false;
    let rafId = null;
    let frameCounter = 0;
    let frameSeq = 0;
    let workerBusy = false;
    let isOffscreenMode = false;
    let keyboardOnlyMode = false;
    let detectionDisabled = loadDetectionDisabled();
    let previewVisible = true;
    const inFlightFrames = new Map();
    const performanceMetrics = createPerformanceMetrics();

    function createPerformanceMetrics() {
      // Trzymamy stan metryk runtime oraz histogram confidence dla porównań eksperymentalnych.
      return {
        startedAt: Date.now(),
        inputFrameTimes: [],
        processedFrameTimes: [],
        latencyMs: [],
        droppedFrames: 0,
        triggerTimes: [],
        confidenceHistogram: [0, 0, 0, 0, 0]
      };
    }

    function pushTimestamp(buffer, timestamp, windowMs = 1000) {
      // Bufor czasowy jest ograniczany oknem, aby obliczać FPS metodą ruchomego okna.
      buffer.push(timestamp);
      while (buffer.length && timestamp - buffer[0] > windowMs) {
        buffer.shift();
      }
    }

    function pushLatencySample(latencyMs) {
      // Przechowujemy ograniczoną liczbę próbek, by średnia latencja nie rosła bez końca.
      const LATENCY_WINDOW = 240;
      performanceMetrics.latencyMs.push(latencyMs);
      if (performanceMetrics.latencyMs.length > LATENCY_WINDOW) {
        performanceMetrics.latencyMs.shift();
      }
    }

    function getAverageLatencyMs() {
      // Średnia latencja z ostatniego okna próbek.
      if (!performanceMetrics.latencyMs.length) return 0;
      const sum = performanceMetrics.latencyMs.reduce((acc, value) => acc + value, 0);
      return sum / performanceMetrics.latencyMs.length;
    }

    function recordConfidence(confidence) {
      // Confidence mapujemy do pięciu kubełków histogramu [0-0.2), ... [0.8-1.0].
      if (!Number.isFinite(confidence)) return;
      const normalized = clamp(confidence, 0, 1);
      const index = Math.min(4, Math.floor(normalized * 5));
      performanceMetrics.confidenceHistogram[index] += 1;
    }

    function trimTriggerWindow(now) {
      // Triggery / min bazują wyłącznie na ostatnich 60 sekundach.
      const ONE_MINUTE = 60_000;
      while (performanceMetrics.triggerTimes.length && now - performanceMetrics.triggerTimes[0] > ONE_MINUTE) {
        performanceMetrics.triggerTimes.shift();
      }
    }

    function updateDebugPerformanceMetrics() {
      // Synchronizujemy metryki wydajnościowe do panelu debug.
      const now = performance.now();
      trimTriggerWindow(now);
      ui.metricInputFps.textContent = performanceMetrics.inputFrameTimes.length.toFixed(1);
      ui.metricDetectionFps.textContent = performanceMetrics.processedFrameTimes.length.toFixed(1);
      ui.metricLatencyAvg.textContent = getAverageLatencyMs().toFixed(1);
      ui.metricDroppedFrames.textContent = String(performanceMetrics.droppedFrames);
      ui.metricTriggersPerMin.textContent = performanceMetrics.triggerTimes.length.toFixed(1);
      ui.metricConfidenceHistogram.textContent = `[${performanceMetrics.confidenceHistogram.join(", ")}]`;
    }

    function buildMetricsExportPayload() {
      // Eksport JSON zawiera aktualną konfigurację i metryki wymagane do porównań eksperymentów.
      const nowIso = new Date().toISOString();
      return {
        exportedAt: nowIso,
        sessionStartedAt: new Date(performanceMetrics.startedAt).toISOString(),
        config,
        metrics: {
          inputFps: Number(ui.metricInputFps.textContent),
          detectionFpsEffective: Number(ui.metricDetectionFps.textContent),
          averageLatencyMs: Number(ui.metricLatencyAvg.textContent),
          droppedFrames: performanceMetrics.droppedFrames,
          triggersPerMin: Number(ui.metricTriggersPerMin.textContent),
          confidenceHistogram: [...performanceMetrics.confidenceHistogram],
          latencySamplesMs: [...performanceMetrics.latencyMs]
        }
      };
    }

    function exportMetricsJson() {
      // Generujemy i pobieramy snapshot metryk jako plik JSON.
      const payload = buildMetricsExportPayload();
      const blob = new Blob([JSON.stringify(payload, null, 2)], { type: "application/json" });
      const url = URL.createObjectURL(blob);
      const anchor = document.createElement("a");
      anchor.href = url;
      anchor.download = `gesture-metrics-${Date.now()}.json`;
      anchor.click();
      URL.revokeObjectURL(url);
      markAction("wyeksportowano metryki JSON");
    }

    function initializeRenderingMode() {
      // Preferujemy tryb OffscreenCanvas, aby odciążyć główny wątek UI.
      isOffscreenMode = typeof ui.overlay.transferControlToOffscreen === "function";
      if (isOffscreenMode) {
        // W trybie Offscreen nie pobieramy kontekstu 2D na głównym wątku.
        ctx = null;
      } else if (!ctx) {
        // Fallback: rysowanie pozostaje na głównym wątku.
        ctx = ui.overlay.getContext("2d");
      }
    }

    function setText(el, text, cls) {
      el.textContent = text;
      el.className = cls;
    }

    function loadDetectionDisabled() {
      // Flaga trwała pozwala całkowicie wyłączyć detekcję między restartami aplikacji.
      return localStorage.getItem(DETECTION_DISABLED_KEY) === "1";
    }

    function persistDetectionDisabled(disabled) {
      // Dla disabled=true zapisujemy flagę, a dla false usuwamy ją z localStorage.
      if (disabled) {
        localStorage.setItem(DETECTION_DISABLED_KEY, "1");
      } else {
        localStorage.removeItem(DETECTION_DISABLED_KEY);
      }
    }

    function announceStatus(message, politeness = "polite") {
      // Komunikaty ARIA informują czytniki ekranu o zmianach stanu bez przenoszenia fokusu.
      if (!ui.ariaAnnouncements) return;
      ui.ariaAnnouncements.setAttribute("aria-live", politeness);
      ui.ariaAnnouncements.textContent = "";
      requestAnimationFrame(() => {
        ui.ariaAnnouncements.textContent = message;
      });
    }

    function pulseFlash() {
      ui.flash.classList.add("visible");
      setTimeout(() => ui.flash.classList.remove("visible"), 120);
    }

    function markAction(text, cls = "value-ok") {
      setText(ui.lastAction, text, cls);
      announceStatus(`Akcja: ${text}`);
    }

    function showBootError(message) {
      ui.bootError.style.display = "block";
      ui.bootError.textContent = message;
    }

    function clearBootError() {
      ui.bootError.style.display = "none";
      ui.bootError.textContent = "";
    }

    function setOverlaySize() {
      const rect = ui.video.getBoundingClientRect();
      ui.overlay.width = rect.width || 320;
      ui.overlay.height = rect.height || 240;
      drawActiveZone();
    }

    function normalizedToCanvas(point) {
      return {
        x: point.x * ui.overlay.width,
        y: point.y * ui.overlay.height
      };
    }

    function drawActiveZone() {
      if (isOffscreenMode || !ctx) return;
      ctx.clearRect(0, 0, ui.overlay.width, ui.overlay.height);
      const { xMin, xMax, yMin, yMax } = config.activeZone;
      const x = xMin * ui.overlay.width;
      const y = yMin * ui.overlay.height;
      const w = (xMax - xMin) * ui.overlay.width;
      const h = (yMax - yMin) * ui.overlay.height;
      ctx.save();
      ctx.strokeStyle = "rgba(255,255,255,0.35)";
      ctx.lineWidth = 2;
      ctx.setLineDash([6, 6]);
      ctx.strokeRect(x, y, w, h);
      ctx.restore();
    }

    function drawLandmarks(landmarks) {
      if (isOffscreenMode || !ctx) return;
      drawActiveZone();
      if (!landmarks || !landmarks.length) return;
      ctx.save();
      ctx.fillStyle = "rgba(61, 220, 151, 0.95)";
      for (const p of landmarks) {
        const c = normalizedToCanvas(p);
        ctx.beginPath();
        ctx.arc(c.x, c.y, 3, 0, Math.PI * 2);
        ctx.fill();
      }
      ctx.restore();
    }

    function setPaused(paused) {
      detectionPaused = paused;
      setText(ui.modeStatus, paused ? "pauza" : "aktywny", paused ? "value-warn" : "value-ok");
      ui.toggleBtn.textContent = paused ? "Wznów detekcję" : "Wstrzymaj detekcję";
      announceStatus(paused ? "Detekcja wstrzymana." : "Detekcja aktywna.");
      if (worker) {
        worker.postMessage({ type: "setPaused", paused });
      }
    }

    function setKeyboardOnlyMode(enabled) {
      // Tryb keyboard-only jest równorzędną metodą sterowania i może działać z kamerą lub bez niej.
      keyboardOnlyMode = enabled;
      setText(
        ui.inputModeStatus,
        enabled ? "keyboard-only" : "gesty + klawiatura",
        enabled ? "value-warn" : "value-ok"
      );
      ui.keyboardModeBtn.textContent = enabled ? "Tryb keyboard-only: ON" : "Tryb keyboard-only: OFF";
      announceStatus(enabled ? "Włączono tryb keyboard-only." : "Włączono tryb gesty plus klawiatura.");
    }

    function updateDetectionToggleButton() {
      // Przycisk pokazuje aktualny stan globalnego wyłączenia detekcji.
      ui.detectionToggleBtn.textContent = detectionDisabled ? "Detekcja: OFF" : "Detekcja: ON";
    }

    function loadConfig() {
      try {
        const raw = localStorage.getItem(CONFIG_KEY);
        if (!raw) return JSON.parse(JSON.stringify(DEFAULT_CONFIG));
        const parsed = JSON.parse(raw);
        return {
          ...JSON.parse(JSON.stringify(DEFAULT_CONFIG)),
          ...parsed,
          activeZone: { ...DEFAULT_CONFIG.activeZone, ...(parsed.activeZone || {}) }
        };
      } catch {
        return JSON.parse(JSON.stringify(DEFAULT_CONFIG));
      }
    }

    function clamp(value, min, max) {
      return Math.min(max, Math.max(min, value));
    }

    function parseNumericBounds(inputEl, fallbackValue) {
      // Odczytujemy granice bezpośrednio z inputów, aby walidacja była spójna z UI.
      const minAttr = Number(inputEl.min);
      const maxAttr = Number(inputEl.max);
      const min = Number.isFinite(minAttr) ? minAttr : fallbackValue;
      const max = Number.isFinite(maxAttr) ? maxAttr : fallbackValue;
      return { min, max: Math.max(min, max) };
    }

    function sanitizeNumericField(inputEl, defaultValue) {
      // Każde pole liczbowe: Number(...), fallback dla NaN i clamp do bezpiecznego zakresu.
      const parsedValue = Number(inputEl.value);
      const safeValue = Number.isFinite(parsedValue) ? parsedValue : defaultValue;
      const bounds = parseNumericBounds(inputEl, defaultValue);
      return clamp(safeValue, bounds.min, bounds.max);
    }

    function sanitizeActiveZone(candidateZone) {
      // Wymuszamy poprawny porządek i zakres strefy aktywnej w normalizacji [0, 1].
      const defaultZone = DEFAULT_CONFIG.activeZone;
      let { xMin, xMax, yMin, yMax } = candidateZone;
      let corrected = false;

      xMin = clamp(xMin, 0, 1);
      xMax = clamp(xMax, 0, 1);
      yMin = clamp(yMin, 0, 1);
      yMax = clamp(yMax, 0, 1);

      if (xMin >= xMax) {
        corrected = true;
        if (xMin > xMax) {
          [xMin, xMax] = [xMax, xMin];
        }
        if (xMin === xMax) {
          xMin = defaultZone.xMin;
          xMax = defaultZone.xMax;
        }
      }

      if (yMin >= yMax) {
        corrected = true;
        if (yMin > yMax) {
          [yMin, yMax] = [yMax, yMin];
        }
        if (yMin === yMax) {
          yMin = defaultZone.yMin;
          yMax = defaultZone.yMax;
        }
      }

      return {
        zone: { xMin, xMax, yMin, yMax },
        corrected
      };
    }

    function sanitizeConfig() {
      // Budujemy wyłącznie poprawny obiekt konfiguracji możliwy do zapisania i wysłania do workera.
      const sanitized = {
        frameSkip: sanitizeNumericField(ui.frameSkip, DEFAULT_CONFIG.frameSkip),
        cooldownMs: sanitizeNumericField(ui.cooldownMs, DEFAULT_CONFIG.cooldownMs),
        historyWindowMs: sanitizeNumericField(ui.historyWindowMs, DEFAULT_CONFIG.historyWindowMs),
        minDeltaXRatio: sanitizeNumericField(ui.minDeltaXRatio, DEFAULT_CONFIG.minDeltaXRatio),
        maxDeltaYRatio: sanitizeNumericField(ui.maxDeltaYRatio, DEFAULT_CONFIG.maxDeltaYRatio),
        readyHoldMs: sanitizeNumericField(ui.readyHoldMs, DEFAULT_CONFIG.readyHoldMs),
        openPalmMinExtendedFingers: sanitizeNumericField(ui.openPalmMinExtendedFingers, DEFAULT_CONFIG.openPalmMinExtendedFingers),
        minPalmWidthRatio: sanitizeNumericField(ui.minPalmWidthRatio, DEFAULT_CONFIG.minPalmWidthRatio),
        activeZone: { ...DEFAULT_CONFIG.activeZone }
      };

      const zoneCandidate = {
        xMin: sanitizeNumericField(ui.zoneXMin, DEFAULT_CONFIG.activeZone.xMin),
        xMax: sanitizeNumericField(ui.zoneXMax, DEFAULT_CONFIG.activeZone.xMax),
        yMin: sanitizeNumericField(ui.zoneYMin, DEFAULT_CONFIG.activeZone.yMin),
        yMax: sanitizeNumericField(ui.zoneYMax, DEFAULT_CONFIG.activeZone.yMax)
      };

      const zoneResult = sanitizeActiveZone(zoneCandidate);
      sanitized.activeZone = zoneResult.zone;
      return {
        config: sanitized,
        correctedZone: zoneResult.corrected
      };
    }

    function saveConfig() {
      const { config: sanitizedConfig, correctedZone } = sanitizeConfig();
      config = sanitizedConfig;
      localStorage.setItem(CONFIG_KEY, JSON.stringify(sanitizedConfig));
      if (correctedZone) {
        markAction("skorygowano nieprawidłowe ustawienia strefy", "value-warn");
      }
    }

    function updateConfigInputs() {
      ui.frameSkip.value = config.frameSkip;
      ui.cooldownMs.value = config.cooldownMs;
      ui.historyWindowMs.value = config.historyWindowMs;
      ui.minDeltaXRatio.value = config.minDeltaXRatio;
      ui.maxDeltaYRatio.value = config.maxDeltaYRatio;
      ui.readyHoldMs.value = config.readyHoldMs;
      ui.openPalmMinExtendedFingers.value = config.openPalmMinExtendedFingers;
      ui.minPalmWidthRatio.value = config.minPalmWidthRatio;
      ui.zoneXMin.value = config.activeZone.xMin;
      ui.zoneXMax.value = config.activeZone.xMax;
      ui.zoneYMin.value = config.activeZone.yMin;
      ui.zoneYMax.value = config.activeZone.yMax;
    }

    function readConfigInputs() {
      const { config: sanitizedConfig, correctedZone } = sanitizeConfig();
      config = sanitizedConfig;
      updateConfigInputs();
      if (correctedZone) {
        markAction("skorygowano nieprawidłowe ustawienia strefy", "value-warn");
      }
    }

    function syncConfigToWorker() {
      if (!worker) return;
      worker.postMessage({ type: "setConfig", config });
      drawActiveZone();
    }

    function setPreviewVisibility(visible) {
      // Spójnie przełączamy widoczność okna podglądu i etykietę przycisku w panelu HUD.
      previewVisible = visible;
      ui.hud.classList.toggle("camera-hidden", !visible);
      ui.previewToggleBtn.textContent = visible ? "Ukryj podgląd" : "Pokaż podgląd";
    }

    function togglePreviewVisibility() {
      // Udostępniamy szybkie przełączanie podglądu kamerki bez wyłączania detekcji.
      setPreviewVisibility(!previewVisible);
      markAction(previewVisible ? "podgląd kamery widoczny" : "podgląd kamery ukryty", "value-muted");
    }

    function clearLocalGestureConfiguration() {
      // Czyścimy całą lokalną konfigurację związaną z modułem gestów i wracamy do domyślnych wartości.
      localStorage.removeItem(CONFIG_KEY);
      config = JSON.parse(JSON.stringify(DEFAULT_CONFIG));
      updateConfigInputs();
      syncConfigToWorker();
    }

    function isTypingContext(eventTarget) {
      // Nie przechwytujemy skrótów klawiaturowych podczas wpisywania wartości w formularzach.
      const activeElement = eventTarget instanceof Element ? eventTarget : document.activeElement;
      if (!(activeElement instanceof HTMLElement)) return false;
      return activeElement.isContentEditable || ["INPUT", "TEXTAREA", "SELECT"].includes(activeElement.tagName);
    }

    function isInteractiveControlElement(eventTarget) {
      // Dla elementów interaktywnych zostawiamy natywną obsługę klawiatury (Enter/Space, aktywacja linków, itp.).
      const activeElement = eventTarget instanceof Element ? eventTarget : document.activeElement;
      if (!(activeElement instanceof Element)) return false;
      return Boolean(activeElement.closest("button, a, [role='button']"));
    }

    function isHudControlFocused() {
      // Skróty globalne blokujemy, jeśli fokus jest na kontrolkach HUD/debug, aby nie zaburzać dostępności UI.
      if (!(document.activeElement instanceof Element)) return false;
      const controlSelectors = "button, a, [role='button'], input, select, textarea, [contenteditable='true']";
      return Boolean(document.activeElement.closest(`#hud ${controlSelectors}, #debugPanel ${controlSelectors}, #bootOverlay ${controlSelectors}`));
    }

    function handleGlobalKeyboard(event) {
      // Skróty działają tylko w obszarze prezentacji lub gdy fokus nie jest na kontrolkach HUD/debug.
      if (isTypingContext(event.target) || isInteractiveControlElement(event.target)) return;
      const eventTarget = event.target instanceof Element ? event.target : document.activeElement;
      const isInsidePresentation = eventTarget instanceof Element && Boolean(eventTarget.closest(".reveal"));
      if (!isInsidePresentation && isHudControlFocused()) return;
      const key = event.key.toLowerCase();

      if (key === "d") {
        event.preventDefault();
        toggleDebug();
      } else if (key === "f") {
        event.preventDefault();
        toggleFullscreen();
      } else if (key === "h") {
        event.preventDefault();
        togglePreviewVisibility();
      } else if (key === "k") {
        event.preventDefault();
        setKeyboardOnlyMode(!keyboardOnlyMode);
      } else if (["arrowright", "pagedown", " "].includes(key)) {
        event.preventDefault();
        deck.next();
        markAction("klawiatura: następny slajd", "value-muted");
      } else if (["arrowleft", "pageup"].includes(key)) {
        event.preventDefault();
        deck.prev();
        markAction("klawiatura: poprzedni slajd", "value-muted");
      }
    }

    function toggleDebug() {
      debugVisible = !debugVisible;
      ui.debugPanel.classList.toggle("visible", debugVisible);
    }

    function toggleFullscreen() {
      if (!document.fullscreenElement) {
        document.documentElement.requestFullscreen?.();
      } else {
        document.exitFullscreen?.();
      }
    }

    function bindSafeClick(element, handler) {
      if (!element) return;
      element.addEventListener("click", (event) => {
        event.preventDefault();
        event.stopPropagation();
        handler(event);
      });
      element.addEventListener("pointerdown", (event) => event.stopPropagation());
      element.addEventListener("mousedown", (event) => event.stopPropagation());
      element.addEventListener("touchstart", (event) => event.stopPropagation(), { passive: true });
    }

    function explainMediaError(error) {
      const name = error?.name || "Error";
      const message = error?.message || "Nieznany błąd.";
      if (name === "NotAllowedError") return "Brak zgody na użycie kamery. Zezwól na dostęp do kamery dla tej strony i spróbuj ponownie.";
      if (name === "NotFoundError") return "Nie znaleziono kamery w systemie.";
      if (name === "NotReadableError") return "Kamera jest zajęta przez inną aplikację albo system blokuje jej odczyt.";
      if (name === "OverconstrainedError") return "Nie udało się dobrać parametrów kamery.";
      if (name === "SecurityError") return "Przeglądarka zablokowała dostęp do kamery z powodów bezpieczeństwa.";
      return `${name}: ${message}`;
    }

    function createWorker() {
      if (worker || detectionDisabled) return;
      worker = new Worker("./gesture-worker.js", { type: "module" });

      worker.addEventListener("message", (event) => {
        const msg = event.data || {};
        if (msg.type === "ready") {
          workerReady = true;
          setText(ui.workerStatus, "gotowy", "value-ok");
          announceStatus("Worker detekcji jest gotowy.");
          syncConfigToWorker();
          if (isOffscreenMode && offscreen) {
            worker.postMessage({ type: "attachCanvas", canvas: offscreen }, [offscreen]);
            offscreen = null;
          }
        } else if (msg.type === "status") {
          if (msg.workerStatus) setText(ui.workerStatus, msg.workerStatus.text, msg.workerStatus.className);
          if (msg.handStatus) setText(ui.handStatus, msg.handStatus.text, msg.handStatus.className);
          if (msg.metrics) {
            ui.metricDeltaX.textContent = Number(msg.metrics.deltaX || 0).toFixed(3);
            ui.metricDeltaY.textContent = Number(msg.metrics.deltaY || 0).toFixed(3);
            ui.metricDirection.textContent = msg.metrics.direction || "brak";
            ui.metricPresence.textContent = Number(msg.metrics.presence || 0).toFixed(3);
            recordConfidence(Number(msg.metrics.presence || 0));
            updateDebugPerformanceMetrics();
          }
          if (!isOffscreenMode) {
            if (msg.landmarks) drawLandmarks(msg.landmarks);
            else drawActiveZone();
          }
        } else if (msg.type === "gesture") {
          if (keyboardOnlyMode) return;
          const now = performance.now();
          performanceMetrics.triggerTimes.push(now);
          trimTriggerWindow(now);
          if (msg.action === "next") {
            deck.next();
            markAction(`następny slajd · ${new Date().toLocaleTimeString()}`);
            pulseFlash();
          } else if (msg.action === "prev") {
            deck.prev();
            markAction(`poprzedni slajd · ${new Date().toLocaleTimeString()}`);
            pulseFlash();
          }
        } else if (msg.type === "processed") {
          const processedAt = performance.now();
          pushTimestamp(performanceMetrics.processedFrameTimes, processedAt);
          if (Number.isFinite(msg.frameId) && inFlightFrames.has(msg.frameId)) {
            const frameStart = inFlightFrames.get(msg.frameId);
            inFlightFrames.delete(msg.frameId);
            pushLatencySample(processedAt - frameStart);
          }
          updateDebugPerformanceMetrics();
          workerBusy = false;
          if (!isOffscreenMode) {
            if (msg.landmarks) drawLandmarks(msg.landmarks);
            else drawActiveZone();
          }
        } else if (msg.type === "error") {
          setText(ui.workerStatus, "błąd", "value-err");
          announceStatus("Wystąpił błąd workera detekcji.", "assertive");
          markAction(`błąd workera: ${msg.message}`, "value-err");
          showBootError(`Worker: ${msg.message}`);
          workerBusy = false;
        }
      });

      worker.addEventListener("error", (error) => {
        setText(ui.workerStatus, "błąd", "value-err");
        markAction(`worker error: ${error.message}`, "value-err");
        showBootError(`Worker script error: ${error.message}`);
      });
    }

    async function startCamera() {
      if (!navigator.mediaDevices?.getUserMedia) {
        throw new Error("Przeglądarka nie obsługuje getUserMedia().");
      }

      cameraStream = await navigator.mediaDevices.getUserMedia({
        video: {
          width: { ideal: 640 },
          height: { ideal: 480 },
          facingMode: "user"
        },
        audio: false
      });

      ui.video.srcObject = cameraStream;
      await ui.video.play();
      ui.cameraPlaceholder.style.display = "none";
      cameraReady = true;
      setText(ui.cameraStatus, "aktywna", "value-ok");
      announceStatus("Kamera została uruchomiona.");
      setOverlaySize();
      ui.toggleBtn.disabled = false;
    }

    async function startSystem() {
      if (detectionDisabled) {
        markAction("detekcja jest globalnie wyłączona", "value-warn");
        announceStatus("Najpierw włącz detekcję przyciskiem Detekcja OFF/ON.", "assertive");
        return;
      }
      clearBootError();
      ui.startBtn.disabled = true;
      ui.bootStartBtn.disabled = true;
      try {
        // Przy każdym nowym starcie resetujemy metryki sesji, aby eksport miał spójne dane.
        Object.assign(performanceMetrics, createPerformanceMetrics());
        inFlightFrames.clear();
        updateDebugPerformanceMetrics();
        createWorker();
        if (!cameraStream) await startCamera();

        captureCanvas = document.createElement("canvas");
        captureCanvas.width = 320;
        captureCanvas.height = 240;
        captureCtx = captureCanvas.getContext("2d", { willReadFrequently: false });

        // Inicjalizacja ścieżki renderowania: Offscreen (preferowany) albo fallback na głównym wątku.
        initializeRenderingMode();
        if (isOffscreenMode && !offscreen) {
          offscreen = ui.overlay.transferControlToOffscreen();
        }

        if (isOffscreenMode && workerReady && offscreen) {
          worker.postMessage({ type: "attachCanvas", canvas: offscreen }, [offscreen]);
          offscreen = null;
        }

        setPaused(false);
        setKeyboardOnlyMode(false);
        ui.bootOverlay.style.display = "none";
        markAction("system uruchomiony");
        stopLoop();
        renderLoop();
      } catch (error) {
        const message = explainMediaError(error);
        setText(ui.cameraStatus, "błąd", "value-err");
        announceStatus("Błąd uruchamiania kamery.", "assertive");
        markAction(`błąd uruchomienia: ${message}`, "value-err");
        showBootError(message);
        ui.startBtn.disabled = false;
        ui.bootStartBtn.disabled = false;
      }
    }

    function stopLoop() {
      if (rafId) cancelAnimationFrame(rafId);
      rafId = null;
    }

    function shutdownSystem() {
      // Zatrzymujemy pętlę renderowania i przywracamy flagi sterujące do stanu początkowego.
      stopLoop();
      workerBusy = false;
      cameraReady = false;
      detectionPaused = true;
      frameCounter = 0;
      frameSeq = 0;
      inFlightFrames.clear();

      // Zwalniamy wszystkie ścieżki kamery, aby urządzenie nie pozostawało zajęte po zamknięciu.
      cameraStream?.getTracks().forEach((track) => track.stop());
      cameraStream = null;
      ui.video.srcObject = null;
      ui.cameraPlaceholder.style.display = "grid";

      // Kończymy worker i czyścimy stan inicjalizacji, by możliwy był bezpieczny restart systemu.
      worker?.terminate();
      worker = null;
      workerReady = false;

      // Czyścimy zasoby pomocnicze używane do przechwytywania klatek.
      captureCanvas = null;
      captureCtx = null;
      offscreen = null;

      // Aktualizujemy statusy interfejsu, aby użytkownik widział jednoznacznie stan zatrzymania.
      setText(ui.cameraStatus, "zatrzymana", "value-muted");
      setText(ui.workerStatus, "zatrzymany", "value-muted");
      setText(ui.modeStatus, "zatrzymane", "value-muted");
      setText(ui.handStatus, "brak", "value-muted");
      announceStatus("System został zatrzymany.");
      ui.toggleBtn.disabled = true;
      ui.toggleBtn.textContent = "Wznów detekcję";
      markAction(`system zatrzymany · ${new Date().toLocaleTimeString()}`, "value-warn");

      if (!isOffscreenMode) {
        drawActiveZone();
      }
    }

    function setDetectionDisabled(disabled) {
      // Ta operacja daje użytkownikowi „twardy” tryb prywatności: brak detekcji i wyczyszczone dane lokalne.
      detectionDisabled = disabled;
      persistDetectionDisabled(disabled);
      updateDetectionToggleButton();

      if (disabled) {
        clearBootError();
        shutdownSystem();
        clearLocalGestureConfiguration();
        setKeyboardOnlyMode(true);
        ui.bootOverlay.style.display = "none";
        ui.startBtn.disabled = true;
        ui.bootStartBtn.disabled = true;
        setText(ui.workerStatus, "wyłączona", "value-muted");
        setText(ui.modeStatus, "wyłączone", "value-muted");
        markAction("detekcja wyłączona i konfiguracja wyczyszczona", "value-warn");
        announceStatus("Detekcja została całkowicie wyłączona.", "assertive");
      } else {
        ui.startBtn.disabled = false;
        ui.bootStartBtn.disabled = false;
        setText(ui.workerStatus, "ładowanie...", "value-warn");
        markAction("detekcja włączona — uruchom kamerę", "value-ok");
        announceStatus("Detekcja została ponownie włączona.");
        createWorker();
      }
    }

    function renderLoop() {
      rafId = requestAnimationFrame(renderLoop);
      if (detectionPaused || !cameraReady || !worker || !workerReady) return;
      if (ui.video.readyState < 2) return;

      if (workerBusy) {
        // Worker jest zajęty, więc bieżąca klatka nie trafia do detekcji.
        performanceMetrics.droppedFrames += 1;
        updateDebugPerformanceMetrics();
        return;
      }

      frameCounter++;
      if (frameCounter % Math.max(1, config.frameSkip) !== 0) return;
      pushTimestamp(performanceMetrics.inputFrameTimes, performance.now());

      captureCtx.drawImage(ui.video, 0, 0, captureCanvas.width, captureCanvas.height);
      const bitmapPromise = createImageBitmap(captureCanvas);

      workerBusy = true;
      const frameId = ++frameSeq;
      const frameCapturedAt = performance.now();
      inFlightFrames.set(frameId, frameCapturedAt);
      bitmapPromise.then((bitmap) => {
        worker.postMessage({
          type: "processFrame",
          frameId,
          timestamp: performance.now(),
          capturedAt: frameCapturedAt,
          bitmap,
          width: captureCanvas.width,
          height: captureCanvas.height
        }, [bitmap]);
      }).catch((error) => {
        inFlightFrames.delete(frameId);
        workerBusy = false;
        markAction(`błąd obrazu: ${error.message}`, "value-err");
      });
    }

    bindSafeClick(ui.startBtn, startSystem);
    bindSafeClick(ui.bootStartBtn, startSystem);
    bindSafeClick(ui.bootDismissBtn, () => {
      ui.bootOverlay.style.display = "none";
      setKeyboardOnlyMode(true);
      markAction("uruchomiono bez kamery");
    });
    bindSafeClick(ui.bootTroubleshootingBtn, () => {
      const visible = ui.bootTroubleshooting.style.display === "block";
      ui.bootTroubleshooting.style.display = visible ? "none" : "block";
      announceStatus(visible ? "Ukryto sekcję troubleshooting." : "Pokazano sekcję troubleshooting.");
    });
    bindSafeClick(ui.closeDebugBtn, () => {
      debugVisible = true;
      toggleDebug();
    });
    bindSafeClick(ui.exportMetricsBtn, exportMetricsJson);
    bindSafeClick(ui.toggleBtn, () => {
      setPaused(!detectionPaused);
      drawActiveZone();
    });
    bindSafeClick(ui.prevBtn, () => deck.prev());
    bindSafeClick(ui.nextBtn, () => deck.next());
    bindSafeClick(ui.previewToggleBtn, togglePreviewVisibility);
    bindSafeClick(ui.keyboardModeBtn, () => {
      setKeyboardOnlyMode(!keyboardOnlyMode);
    });
    bindSafeClick(ui.detectionToggleBtn, () => {
      setDetectionDisabled(!detectionDisabled);
    });
    bindSafeClick(ui.testPrevBtn, () => {
      deck.prev();
      markAction("test: poprzedni slajd");
    });
    bindSafeClick(ui.testNextBtn, () => {
      deck.next();
      markAction("test: następny slajd");
    });
    bindSafeClick(ui.saveConfigBtn, () => {
      readConfigInputs();
      saveConfig();
      syncConfigToWorker();
      markAction("ustawienia zapisane");
    });
    bindSafeClick(ui.resetConfigBtn, () => {
      config = JSON.parse(JSON.stringify(DEFAULT_CONFIG));
      updateConfigInputs();
      saveConfig();
      syncConfigToWorker();
      markAction("ustawienia zresetowane");
    });

    window.addEventListener("keydown", handleGlobalKeyboard, { capture: true });

    document.addEventListener("visibilitychange", () => {
      if (document.hidden) setPaused(true);
    });

    window.addEventListener("resize", () => {
      setOverlaySize();
      drawActiveZone();
    });
    window.addEventListener("beforeunload", shutdownSystem);

    initializeRenderingMode();
    updateConfigInputs();
    updateDetectionToggleButton();
    setPaused(true);
    setText(ui.cameraStatus, "nieuruchomiona", "value-muted");
    setText(ui.workerStatus, detectionDisabled ? "wyłączona" : "ładowanie...", detectionDisabled ? "value-muted" : "value-warn");
    setText(ui.handStatus, "brak", "value-muted");
    drawActiveZone();
    setPreviewVisibility(true);
    if (detectionDisabled) {
      setKeyboardOnlyMode(true);
      ui.startBtn.disabled = true;
      ui.bootStartBtn.disabled = true;
      ui.bootOverlay.style.display = "none";
      setText(ui.modeStatus, "wyłączone", "value-muted");
      markAction("detekcja jest globalnie wyłączona", "value-warn");
    } else {
      createWorker();
    }
  
