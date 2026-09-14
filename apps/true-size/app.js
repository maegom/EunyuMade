(function () {
  "use strict";

  const DEFAULT_PX_PER_MM = 96 / 25.4;
  const BOARD_WIDTH_MM = 600;
  const BOARD_HEIGHT_MM = 400;
  const MIN_PX_PER_MM = 2;
  const MAX_PX_PER_MM = 15;
  const storageKey = "true-size-studio:v1";

  const $ = (id) => document.getElementById(id);
  const elements = {
    app: $("app"),
    workspace: document.querySelector(".workspace"),
    scaleStatus: $("scaleStatus"),
    scaleStatusText: $("scaleStatusText"),
    scaleReadout: $("scaleReadout"),
    calibrationPercent: $("calibrationPercent"),
    targetControl: $("targetLengthControl"),
    measuredLength: $("measuredLength"),
    applyMeasured: $("applyMeasured"),
    saveCalibration: $("saveCalibration"),
    resetCalibration: $("resetCalibration"),
    toggleCalibration: $("toggleCalibration"),
    closeCalibration: $("closeCalibration"),
    calibrationBench: $("calibrationBench"),
    calibrationLineWrap: $("calibrationLineWrap"),
    calibrationLine: $("calibrationLine"),
    calibrationHandle: $("calibrationHandle"),
    benchTargetLabel: $("benchTargetLabel"),
    benchTargetHint: $("benchTargetHint"),
    fullscreenButton: $("fullscreenButton"),
    fileInput: $("fileInput"),
    sidebarUpload: $("sidebarUpload"),
    toolbarUpload: $("toolbarUpload"),
    boardEmpty: $("boardEmpty"),
    replaceImage: $("replaceImage"),
    removeImage: $("removeImage"),
    emptyImageControls: $("emptyImageControls"),
    loadedImageControls: $("loadedImageControls"),
    filePreview: $("filePreview"),
    fileName: $("fileName"),
    fileMeta: $("fileMeta"),
    imageWidth: $("imageWidth"),
    imageHeight: $("imageHeight"),
    imageX: $("imageX"),
    imageY: $("imageY"),
    lockRatio: $("lockRatio"),
    centerImage: $("centerImage"),
    minorGridToggle: $("minorGridToggle"),
    majorGridToggle: $("majorGridToggle"),
    rulerToggle: $("rulerToggle"),
    boardViewport: $("boardViewport"),
    boardShell: $("boardShell"),
    measurementBoard: $("measurementBoard"),
    horizontalRuler: $("horizontalRuler"),
    verticalRuler: $("verticalRuler"),
    dropOverlay: $("dropOverlay"),
    imageObject: $("imageObject"),
    stageImage: $("stageImage"),
    sizeBadge: $("sizeBadge"),
    toast: $("toast")
  };

  const stored = readStoredState();
  const state = {
    pxPerMm: clamp(Number(stored.pxPerMm) || DEFAULT_PX_PER_MM, MIN_PX_PER_MM, MAX_PX_PER_MM),
    calibrated: Boolean(stored.calibrated),
    targetMm: [50, 100, 150].includes(Number(stored.targetMm)) ? Number(stored.targetMm) : 100,
    calibrationOpen: stored.calibrationOpen !== false,
    minorGrid: stored.minorGrid !== false,
    majorGrid: stored.majorGrid !== false,
    rulers: stored.rulers !== false,
    imageUrl: null,
    fileName: "",
    naturalWidth: 0,
    naturalHeight: 0,
    ratio: 1,
    widthMm: 100,
    heightMm: 100,
    xMm: 30,
    yMm: 30
  };

  let toastTimer;
  let dragDepth = 0;

  function clamp(value, min, max) {
    return Math.min(max, Math.max(min, value));
  }

  function round(value, places = 1) {
    const scale = 10 ** places;
    return Math.round((value + Number.EPSILON) * scale) / scale;
  }

  function readStoredState() {
    try { return JSON.parse(localStorage.getItem(storageKey) || "{}"); }
    catch { return {}; }
  }

  function persist() {
    try {
      localStorage.setItem(storageKey, JSON.stringify({
        pxPerMm: state.pxPerMm,
        calibrated: state.calibrated,
        targetMm: state.targetMm,
        calibrationOpen: state.calibrationOpen,
        minorGrid: state.minorGrid,
        majorGrid: state.majorGrid,
        rulers: state.rulers
      }));
    } catch { /* Storage is optional. */ }
  }

  function showToast(message, kind = "success") {
    window.clearTimeout(toastTimer);
    elements.toast.textContent = message;
    elements.toast.classList.toggle("is-error", kind === "error");
    elements.toast.hidden = false;
    toastTimer = window.setTimeout(() => { elements.toast.hidden = true; }, 2800);
  }

  function setPxPerMm(next, markUncalibrated = true) {
    state.pxPerMm = clamp(Number(next) || DEFAULT_PX_PER_MM, MIN_PX_PER_MM, MAX_PX_PER_MM);
    if (markUncalibrated) state.calibrated = false;
    renderScale();
  }

  function renderScale() {
    document.documentElement.style.setProperty("--px-per-mm", `${state.pxPerMm}px`);
    document.documentElement.style.setProperty("--grid-5mm", `${state.pxPerMm * 5}px`);
    document.documentElement.style.setProperty("--grid-10mm", `${state.pxPerMm * 10}px`);
    document.documentElement.style.setProperty("--board-width", `${state.pxPerMm * BOARD_WIDTH_MM}px`);
    document.documentElement.style.setProperty("--board-height", `${state.pxPerMm * BOARD_HEIGHT_MM}px`);
    elements.calibrationLine.style.width = `${state.targetMm * state.pxPerMm}px`;
    elements.calibrationLineWrap.style.width = `${Math.max(state.targetMm * state.pxPerMm + 36, 240)}px`;
    elements.scaleReadout.textContent = `${state.pxPerMm.toFixed(4)} px/mm`;
    elements.calibrationPercent.textContent = `${(state.pxPerMm / DEFAULT_PX_PER_MM * 100).toFixed(2)}%`;
    elements.scaleStatus.classList.toggle("is-calibrated", state.calibrated);
    elements.scaleStatusText.textContent = state.calibrated ? "보정 완료 · 실제 스케일" : "조정 중 · 확정 필요";
    elements.benchTargetLabel.textContent = String(state.targetMm);
    elements.benchTargetHint.textContent = `${state.targetMm} mm`;
    elements.measuredLength.value = String(state.targetMm);
    for (const button of elements.targetControl.querySelectorAll("button")) {
      const active = Number(button.dataset.target) === state.targetMm;
      button.classList.toggle("is-active", active);
      button.setAttribute("aria-checked", String(active));
    }
    renderImage();
    rebuildRulerLabels();
    persist();
  }

  function renderCalibrationOpen() {
    elements.workspace.classList.toggle("calibration-collapsed", !state.calibrationOpen);
    elements.toggleCalibration.setAttribute("aria-expanded", String(state.calibrationOpen));
    persist();
  }

  function renderViewOptions() {
    elements.minorGridToggle.checked = state.minorGrid;
    elements.majorGridToggle.checked = state.majorGrid;
    elements.rulerToggle.checked = state.rulers;
    elements.measurementBoard.classList.toggle("hide-minor-grid", !state.minorGrid);
    elements.measurementBoard.classList.toggle("hide-major-grid", !state.majorGrid);
    elements.boardShell.classList.toggle("hide-rulers", !state.rulers);
    persist();
  }

  function rebuildRulerLabels() {
    elements.horizontalRuler.replaceChildren();
    elements.verticalRuler.replaceChildren();
    for (let mm = 10; mm < BOARD_WIDTH_MM; mm += 10) {
      const label = document.createElement("span");
      label.className = "ruler-label";
      label.style.left = `${mm * state.pxPerMm}px`;
      label.textContent = String(mm / 10);
      elements.horizontalRuler.append(label);
    }
    for (let mm = 10; mm < BOARD_HEIGHT_MM; mm += 10) {
      const label = document.createElement("span");
      label.className = "ruler-label";
      label.style.top = `${mm * state.pxPerMm}px`;
      label.textContent = String(mm / 10);
      elements.verticalRuler.append(label);
    }
  }

  function renderImage() {
    const loaded = Boolean(state.imageUrl);
    elements.imageObject.hidden = !loaded;
    elements.boardEmpty.hidden = loaded;
    elements.emptyImageControls.hidden = loaded;
    elements.loadedImageControls.hidden = !loaded;
    elements.removeImage.hidden = !loaded;
    if (!loaded) return;

    state.widthMm = clamp(state.widthMm, 1, BOARD_WIDTH_MM);
    state.heightMm = clamp(state.heightMm, 1, BOARD_HEIGHT_MM);
    state.xMm = clamp(state.xMm, 0, Math.max(0, BOARD_WIDTH_MM - state.widthMm));
    state.yMm = clamp(state.yMm, 0, Math.max(0, BOARD_HEIGHT_MM - state.heightMm));

    Object.assign(elements.imageObject.style, {
      left: `${state.xMm * state.pxPerMm}px`,
      top: `${state.yMm * state.pxPerMm}px`,
      width: `${state.widthMm * state.pxPerMm}px`,
      height: `${state.heightMm * state.pxPerMm}px`
    });
    elements.imageWidth.value = state.widthMm.toFixed(1);
    elements.imageHeight.value = state.heightMm.toFixed(1);
    elements.imageX.value = state.xMm.toFixed(1);
    elements.imageY.value = state.yMm.toFixed(1);
    elements.sizeBadge.textContent = `${state.widthMm.toFixed(1)} × ${state.heightMm.toFixed(1)} mm`;
  }

  function chooseImage() {
    elements.fileInput.value = "";
    elements.fileInput.click();
  }

  function loadFile(file) {
    if (!file || !file.type.startsWith("image/")) {
      showToast("PNG, JPG, WebP 같은 이미지 파일을 선택해 주세요.", "error");
      return;
    }
    if (file.size > 50 * 1024 * 1024) {
      showToast("이미지는 50MB 이하로 선택해 주세요.", "error");
      return;
    }

    const url = URL.createObjectURL(file);
    const probe = new Image();
    probe.onload = () => {
      if (state.imageUrl) URL.revokeObjectURL(state.imageUrl);
      state.imageUrl = url;
      state.fileName = file.name;
      state.naturalWidth = probe.naturalWidth;
      state.naturalHeight = probe.naturalHeight;
      state.ratio = probe.naturalWidth / probe.naturalHeight || 1;
      state.widthMm = clamp(probe.naturalWidth / 96 * 25.4, 30, 200);
      state.heightMm = state.widthMm / state.ratio;
      if (state.heightMm > 260) {
        state.heightMm = 260;
        state.widthMm = state.heightMm * state.ratio;
      }
      state.xMm = 30;
      state.yMm = 30;
      elements.stageImage.src = url;
      elements.filePreview.src = url;
      elements.fileName.textContent = file.name;
      elements.fileMeta.textContent = `${probe.naturalWidth} × ${probe.naturalHeight} px`;
      renderImage();
      elements.imageObject.focus({ preventScroll: true });
      showToast("이미지를 불러왔어요. mm 단위로 크기를 조절할 수 있습니다.");
    };
    probe.onerror = () => {
      URL.revokeObjectURL(url);
      showToast("이미지를 읽지 못했습니다.", "error");
    };
    probe.src = url;
  }

  function removeImage() {
    if (state.imageUrl) URL.revokeObjectURL(state.imageUrl);
    state.imageUrl = null;
    elements.stageImage.removeAttribute("src");
    elements.filePreview.removeAttribute("src");
    renderImage();
  }

  function updateSize(axis, raw) {
    const value = Number(raw);
    if (!Number.isFinite(value) || value <= 0) return renderImage();
    if (axis === "width") {
      state.widthMm = clamp(value, 1, BOARD_WIDTH_MM);
      if (elements.lockRatio.checked) state.heightMm = state.widthMm / state.ratio;
    } else {
      state.heightMm = clamp(value, 1, BOARD_HEIGHT_MM);
      if (elements.lockRatio.checked) state.widthMm = state.heightMm * state.ratio;
    }
    renderImage();
  }

  function updatePosition(axis, raw) {
    const value = Number(raw);
    if (!Number.isFinite(value)) return renderImage();
    if (axis === "x") state.xMm = value;
    else state.yMm = value;
    renderImage();
  }

  function beginCalibrationDrag(event) {
    event.preventDefault();
    elements.calibrationHandle.setPointerCapture(event.pointerId);
    const origin = elements.calibrationLine.getBoundingClientRect().left;
    const onMove = (moveEvent) => {
      const width = moveEvent.clientX - origin;
      setPxPerMm(width / state.targetMm, true);
    };
    const onEnd = () => {
      elements.calibrationHandle.removeEventListener("pointermove", onMove);
      elements.calibrationHandle.removeEventListener("pointerup", onEnd);
      elements.calibrationHandle.removeEventListener("pointercancel", onEnd);
    };
    elements.calibrationHandle.addEventListener("pointermove", onMove);
    elements.calibrationHandle.addEventListener("pointerup", onEnd);
    elements.calibrationHandle.addEventListener("pointercancel", onEnd);
  }

  function beginImagePointer(event) {
    if (!state.imageUrl) return;
    const handle = event.target.closest(".resize-handle");
    const mode = handle ? "resize" : "move";
    const corner = handle?.dataset.handle || "se";
    event.preventDefault();
    elements.imageObject.setPointerCapture(event.pointerId);
    elements.imageObject.focus({ preventScroll: true });

    const start = {
      clientX: event.clientX,
      clientY: event.clientY,
      x: state.xMm,
      y: state.yMm,
      width: state.widthMm,
      height: state.heightMm
    };

    const onMove = (moveEvent) => {
      const dx = (moveEvent.clientX - start.clientX) / state.pxPerMm;
      const dy = (moveEvent.clientY - start.clientY) / state.pxPerMm;
      if (mode === "move") {
        state.xMm = start.x + dx;
        state.yMm = start.y + dy;
      } else {
        const leftSide = corner.includes("w");
        const topSide = corner.includes("n");
        let width = Math.max(1, start.width + (leftSide ? -dx : dx));
        let height = Math.max(1, start.height + (topSide ? -dy : dy));
        if (elements.lockRatio.checked) {
          const fromHorizontal = Math.abs(dx) >= Math.abs(dy);
          if (fromHorizontal) height = width / state.ratio;
          else width = height * state.ratio;
        }
        if (leftSide) state.xMm = start.x + start.width - width;
        if (topSide) state.yMm = start.y + start.height - height;
        state.widthMm = width;
        state.heightMm = height;
      }
      renderImage();
    };
    const onEnd = () => {
      elements.imageObject.removeEventListener("pointermove", onMove);
      elements.imageObject.removeEventListener("pointerup", onEnd);
      elements.imageObject.removeEventListener("pointercancel", onEnd);
    };
    elements.imageObject.addEventListener("pointermove", onMove);
    elements.imageObject.addEventListener("pointerup", onEnd);
    elements.imageObject.addEventListener("pointercancel", onEnd);
  }

  function registerWebMcpTools() {
    const context = document.modelContext;
    if (!context?.registerTool) return;
    const register = (definition) => {
      try { void Promise.resolve(context.registerTool(definition)).catch(() => {}); }
      catch { /* Experimental API can reject registration. */ }
    };
    register({
      name: "set_monitor_calibration",
      title: "모니터 스케일 보정",
      description: "선택한 기준선이 실제 자에서 측정된 길이를 사용해 화면의 mm 스케일을 보정합니다.",
      inputSchema: {
        type: "object",
        properties: {
          targetMm: { type: "number", enum: [50, 100, 150] },
          measuredMm: { type: "number", minimum: 10, maximum: 500 }
        },
        required: ["targetMm", "measuredMm"],
        additionalProperties: false
      },
      annotations: { readOnlyHint: false, untrustedContentHint: false },
      execute(input) {
        const targetMm = Number(input?.targetMm);
        const measuredMm = Number(input?.measuredMm);
        if (![50, 100, 150].includes(targetMm) || !Number.isFinite(measuredMm) || measuredMm < 10 || measuredMm > 500) throw new Error("유효한 기준 길이와 측정 길이가 필요합니다.");
        state.targetMm = targetMm;
        setPxPerMm(state.pxPerMm * targetMm / measuredMm, false);
        state.calibrated = true;
        renderScale();
        return { calibrated: true, pxPerMm: round(state.pxPerMm, 5) };
      }
    });
    register({
      name: "set_loaded_image_size",
      title: "이미지 실물 크기 설정",
      description: "현재 불러온 이미지의 실물 표시 크기를 mm 단위로 설정합니다.",
      inputSchema: {
        type: "object",
        properties: {
          widthMm: { type: "number", minimum: 1, maximum: 600 },
          heightMm: { type: "number", minimum: 1, maximum: 400 }
        },
        required: ["widthMm"],
        additionalProperties: false
      },
      annotations: { readOnlyHint: false, untrustedContentHint: false },
      execute(input) {
        if (!state.imageUrl) throw new Error("먼저 이미지를 불러와야 합니다.");
        const width = Number(input?.widthMm);
        const height = input?.heightMm == null ? width / state.ratio : Number(input.heightMm);
        if (!Number.isFinite(width) || !Number.isFinite(height) || width < 1 || height < 1) throw new Error("유효한 이미지 크기가 필요합니다.");
        state.widthMm = width;
        state.heightMm = height;
        renderImage();
        return { widthMm: round(state.widthMm), heightMm: round(state.heightMm) };
      }
    });
  }

  elements.targetControl.addEventListener("click", (event) => {
    const button = event.target.closest("button[data-target]");
    if (!button) return;
    state.targetMm = Number(button.dataset.target);
    renderScale();
  });

  for (const button of document.querySelectorAll("[data-adjust]")) {
    button.addEventListener("click", () => setPxPerMm(state.pxPerMm * (1 + Number(button.dataset.adjust)), true));
  }

  elements.applyMeasured.addEventListener("click", () => {
    const measured = Number(elements.measuredLength.value);
    if (!Number.isFinite(measured) || measured <= 0) return showToast("실제 자에서 읽은 길이를 입력해 주세요.", "error");
    setPxPerMm(state.pxPerMm * state.targetMm / measured, true);
    showToast("측정값을 반영했어요. 실제 자로 한 번 더 확인해 주세요.");
  });

  elements.saveCalibration.addEventListener("click", () => {
    state.calibrated = true;
    state.calibrationOpen = false;
    renderScale();
    renderCalibrationOpen();
    showToast("스케일을 저장했어요. 이제 이미지가 실제 크기로 표시됩니다.");
  });

  elements.resetCalibration.addEventListener("click", () => {
    state.pxPerMm = DEFAULT_PX_PER_MM;
    state.calibrated = false;
    renderScale();
    showToast("기본 96 PPI 스케일로 초기화했습니다.");
  });

  const toggleCalibration = () => {
    state.calibrationOpen = !state.calibrationOpen;
    renderCalibrationOpen();
  };
  elements.toggleCalibration.addEventListener("click", toggleCalibration);
  elements.closeCalibration.addEventListener("click", toggleCalibration);
  elements.calibrationHandle.addEventListener("pointerdown", beginCalibrationDrag);

  elements.fullscreenButton.addEventListener("click", async () => {
    try {
      if (document.fullscreenElement) await document.exitFullscreen();
      else await document.documentElement.requestFullscreen();
    } catch { showToast("이 브라우저에서는 전체 화면을 열 수 없습니다.", "error"); }
  });

  for (const button of [elements.sidebarUpload, elements.toolbarUpload, elements.boardEmpty, elements.replaceImage]) {
    button.addEventListener("click", chooseImage);
  }
  elements.fileInput.addEventListener("change", () => loadFile(elements.fileInput.files?.[0]));
  elements.removeImage.addEventListener("click", removeImage);

  elements.imageWidth.addEventListener("change", () => updateSize("width", elements.imageWidth.value));
  elements.imageHeight.addEventListener("change", () => updateSize("height", elements.imageHeight.value));
  elements.imageX.addEventListener("change", () => updatePosition("x", elements.imageX.value));
  elements.imageY.addEventListener("change", () => updatePosition("y", elements.imageY.value));
  elements.imageObject.addEventListener("pointerdown", beginImagePointer);

  for (const button of document.querySelectorAll("[data-width]")) {
    button.addEventListener("click", () => updateSize("width", button.dataset.width));
  }
  elements.centerImage.addEventListener("click", () => {
    state.xMm = (BOARD_WIDTH_MM - state.widthMm) / 2;
    state.yMm = (BOARD_HEIGHT_MM - state.heightMm) / 2;
    renderImage();
    window.requestAnimationFrame(() => elements.imageObject.scrollIntoView({ block: "center", inline: "center", behavior: "smooth" }));
  });

  elements.imageObject.addEventListener("keydown", (event) => {
    if (!["ArrowLeft", "ArrowRight", "ArrowUp", "ArrowDown"].includes(event.key)) return;
    event.preventDefault();
    const step = event.altKey ? 0.1 : event.shiftKey ? 10 : 1;
    if (event.key === "ArrowLeft") state.xMm -= step;
    if (event.key === "ArrowRight") state.xMm += step;
    if (event.key === "ArrowUp") state.yMm -= step;
    if (event.key === "ArrowDown") state.yMm += step;
    renderImage();
  });

  elements.minorGridToggle.addEventListener("change", () => { state.minorGrid = elements.minorGridToggle.checked; renderViewOptions(); });
  elements.majorGridToggle.addEventListener("change", () => { state.majorGrid = elements.majorGridToggle.checked; renderViewOptions(); });
  elements.rulerToggle.addEventListener("change", () => { state.rulers = elements.rulerToggle.checked; renderViewOptions(); });

  window.addEventListener("dragenter", (event) => {
    if (!Array.from(event.dataTransfer?.types || []).includes("Files")) return;
    event.preventDefault();
    dragDepth += 1;
    elements.dropOverlay.classList.add("is-visible");
  });
  window.addEventListener("dragover", (event) => {
    if (!Array.from(event.dataTransfer?.types || []).includes("Files")) return;
    event.preventDefault();
  });
  window.addEventListener("dragleave", (event) => {
    if (!Array.from(event.dataTransfer?.types || []).includes("Files")) return;
    dragDepth = Math.max(0, dragDepth - 1);
    if (dragDepth === 0) elements.dropOverlay.classList.remove("is-visible");
  });
  window.addEventListener("drop", (event) => {
    event.preventDefault();
    dragDepth = 0;
    elements.dropOverlay.classList.remove("is-visible");
    loadFile(event.dataTransfer?.files?.[0]);
  });

  renderViewOptions();
  renderCalibrationOpen();
  renderScale();
  registerWebMcpTools();
})();
