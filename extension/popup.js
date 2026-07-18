// All JS lives here (not inline in popup.html) — MV3 extension pages get a
// mandatory default CSP (script-src 'self') that silently blocks inline
// <script> execution, unlike a plain web page or an Apps Script dialog.

const BACKEND = 'https://svg-to-slides-jwxfsrfexq-uc.a.run.app';

function esc(s) {
  return s.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
}

function readFilesAsBase64(files) {
  return Promise.all(files.map((file) => new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onload = (e) => resolve({ name: file.name, data: e.target.result.split(',')[1] });
    reader.onerror = () => reject(new Error('Could not read ' + file.name));
    reader.readAsDataURL(file);
  })));
}

// ── Shared: which tab, and the active tab's URL ─────────────────────────
// Queried once and shared between the auto-default-tab logic below and
// Mode B's cursor-placement logic, rather than querying chrome.tabs twice.

const SLIDES_EDIT_PREFIX = 'https://docs.google.com/presentation/d/';

const activeTabPromise = new Promise((resolve) => {
  chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => resolve(tabs[0] || null));
});

// ── Tabs ─────────────────────────────────────────────────────────────────

function activateTab(name) {
  document.querySelectorAll('.tab-btn').forEach((b) => b.classList.toggle('active', b.dataset.tab === name));
  document.querySelectorAll('.tab-panel').forEach((p) => p.classList.toggle('active', p.id === 'tab-' + name));
}

document.querySelectorAll('.tab-btn').forEach((btn) => {
  btn.addEventListener('click', () => activateTab(btn.dataset.tab));
});

// Default straight to Insert mode if the popup was opened from an actual
// Slides editor tab — that's almost certainly what the user wants there.
// Bulk Upload stays the default everywhere else (a new tab, some other
// page, etc.), since Insert mode is meaningless without a Slides tab.
activeTabPromise.then((tab) => {
  if (tab && tab.url && tab.url.startsWith(SLIDES_EDIT_PREFIX)) {
    activateTab('insert');
  }
});

// ══════════════════════════ Mode A: Bulk Upload ═══════════════════════════

(function modeUpload() {
  const dropZone = document.getElementById('upload-drop-zone');
  const fileInput = document.getElementById('upload-file-input');
  const fileList = document.getElementById('upload-file-list');
  const changeLink = document.getElementById('upload-change-link');
  const emailInput = document.getElementById('upload-email');
  const statusEl = document.getElementById('upload-status');
  const resultEl = document.getElementById('upload-result');
  const resultLink = document.getElementById('upload-result-link');
  const resultMessage = document.getElementById('upload-result-message');
  const submitBtn = document.getElementById('upload-submit-btn');
  const cancelBtn = document.getElementById('upload-cancel-btn');

  let files = [];

  // Only updates the file-list display + submit button state — does NOT
  // touch the result/status boxes. Used both for a fresh file selection
  // (where the caller also wants those cleared, via applyFiles below) and
  // for resetting the picker after a successful convert (where the result
  // box must stay visible, not get wiped the instant it's shown).
  function renderFileList() {
    dropZone.classList.toggle('has-files', files.length > 0);
    fileList.innerHTML = files.map((f) => '<div class="file-row">' + esc(f.name) + '</div>').join('');
    fileList.classList.toggle('visible', files.length > 0);
    changeLink.classList.toggle('visible', files.length > 0);
    submitBtn.disabled = files.length === 0;
  }

  function applyFiles(newFiles) {
    files = newFiles;
    renderFileList();
    resultEl.style.display = 'none';
    statusEl.textContent = '';
    statusEl.className = 'status';
  }

  dropZone.addEventListener('click', (e) => {
    if (dropZone.classList.contains('has-files')) return;
    if (e.target === changeLink) return;
    fileInput.click();
  });
  changeLink.addEventListener('click', (e) => { e.stopPropagation(); fileInput.click(); });
  dropZone.addEventListener('dragover', (e) => { e.preventDefault(); e.stopPropagation(); dropZone.classList.add('drag-over'); });
  dropZone.addEventListener('dragleave', (e) => { e.stopPropagation(); dropZone.classList.remove('drag-over'); });
  dropZone.addEventListener('drop', (e) => {
    e.preventDefault(); e.stopPropagation();
    dropZone.classList.remove('drag-over');
    const svgs = Array.from(e.dataTransfer.files).filter((f) => f.name.toLowerCase().endsWith('.svg'));
    if (svgs.length) applyFiles(svgs);
  });
  fileInput.addEventListener('change', () => {
    if (fileInput.files.length) applyFiles(Array.from(fileInput.files));
  });

  cancelBtn.addEventListener('click', () => window.close());

  submitBtn.addEventListener('click', async () => {
    if (!files.length) return;
    submitBtn.disabled = true;
    resultEl.style.display = 'none';
    statusEl.className = 'status';
    statusEl.innerHTML = '<div class="spinner"></div><span>Converting…</span>';

    const fd = new FormData();
    files.forEach((f) => fd.append('files', f));
    fd.append('email', emailInput.value.trim());

    try {
      const res = await fetch(BACKEND + '/convert', { method: 'POST', body: fd });
      const json = await res.json();
      if (!res.ok) throw new Error(json.detail || 'Server error');
      statusEl.textContent = '';
      resultLink.href = json.link;
      resultMessage.textContent = json.retention_days
        ? `✓ Done — ready. Link active for ${json.retention_days} days (use "Make a copy" in Drive to keep it permanently).`
        : '✓ Done — your file is ready in Google Drive.';
      resultEl.style.display = 'block';
      files = [];
      renderFileList();
      emailInput.value = '';
    } catch (err) {
      statusEl.className = 'status error';
      statusEl.textContent = '✗ ' + err.message;
      submitBtn.disabled = false;
    }
  });

  // Enter submits regardless of which field currently has focus (email
  // input or elsewhere in this tab) — only while the Upload tab is active,
  // so it doesn't fire while the Insert tab is showing instead.
  document.addEventListener('keydown', (e) => {
    if (e.key !== 'Enter') return;
    if (!document.getElementById('tab-upload').classList.contains('active')) return;
    if (submitBtn.disabled) return;
    e.preventDefault();
    submitBtn.click();
  });
})();

// ══════════════════════ Mode B: Insert into Slides ═════════════════════════

(function modeInsert() {
  const dropZone = document.getElementById('insert-drop-zone');
  const fileInput = document.getElementById('insert-file-input');
  const thumbGrid = document.getElementById('insert-thumb-grid');
  const changeLink = document.getElementById('insert-change-link');
  const warningEl = document.getElementById('insert-warning');
  const copyHint = document.getElementById('insert-copy-hint');
  const pasteHint = document.getElementById('insert-paste-hint');
  const statusEl = document.getElementById('insert-status');
  const actionBtn = document.getElementById('insert-action-btn');
  const cancelBtn = document.getElementById('insert-cancel-btn');
  const clipTarget = document.getElementById('insert-clip-target');

  let selectedFiles = [];
  let pendingBundle = null; // {mimeType: string} once converted, until copied
  let stage = 'idle';       // 'idle' -> 'converted' -> 'done'
  let placement = null;     // {x_pt, y_pt} resolved once at popup-open time

  // ── Resolve cursor position via the content script, once, at popup open ──
  // Mouse position here is inherently "last hover before the popup opened,"
  // not "at click time" — by the time the user clicks the toolbar icon the
  // cursor is over the toolbar/popup, not the slide canvas. Expected, not a
  // bug: content.js continuously caches mousemove for exactly this reason.

  const DEFAULT_SLIDE_W_PT = 960;
  const DEFAULT_SLIDE_H_PT = 540;

  function setWarning(msg) {
    if (!msg) { warningEl.classList.remove('visible'); warningEl.textContent = ''; return; }
    warningEl.textContent = msg;
    warningEl.classList.add('visible');
  }

  function resolvePlacement(callback) {
    activeTabPromise.then((tab) => {
      if (!tab || !tab.url || !tab.url.startsWith(SLIDES_EDIT_PREFIX)) {
        setWarning('Open a Google Slides presentation to use Insert mode.');
        actionBtn.disabled = true;
        callback(null);
        return;
      }

      chrome.tabs.sendMessage(tab.id, { type: 'GET_PLACEMENT_CONTEXT' }, (resp) => {
        if (chrome.runtime.lastError || !resp || !resp.ok) {
          // Most likely an already-open tab from before the extension was
          // loaded/reloaded — content.js only auto-injects on (re)navigation.
          setWarning('Couldn\'t detect the slide canvas — try refreshing the Slides tab. Inserting at the center of a standard-size slide for now.');
          callback({ x_pt: DEFAULT_SLIDE_W_PT / 2, y_pt: DEFAULT_SLIDE_H_PT / 2 });
          return;
        }

        const { canvasRect, mouse, zoomPercent } = resp;
        if (!zoomPercent || !canvasRect.width || !canvasRect.height) {
          setWarning('Couldn\'t read the zoom level — inserting at the center of a standard-size slide.');
          callback({ x_pt: DEFAULT_SLIDE_W_PT / 2, y_pt: DEFAULT_SLIDE_H_PT / 2 });
          return;
        }

        let fx = 0.5, fy = 0.5; // dead-center fallback if mouse is unknown/outside canvas
        if (mouse) {
          const rawFx = (mouse.x - canvasRect.left) / canvasRect.width;
          const rawFy = (mouse.y - canvasRect.top) / canvasRect.height;
          if (rawFx >= 0 && rawFx <= 1 && rawFy >= 0 && rawFy <= 1) {
            fx = rawFx; fy = rawFy;
          }
        }

        // Stage-0-validated formula: 1pt == 1 CSS px at 100% zoom.
        const pageWidthPt = canvasRect.width / (zoomPercent / 100);
        const pageHeightPt = canvasRect.height / (zoomPercent / 100);
        callback({ x_pt: fx * pageWidthPt, y_pt: fy * pageHeightPt });
      });
    });
  }

  resolvePlacement((result) => {
    placement = result;
    if (result) actionBtn.disabled = selectedFiles.length === 0;
  });

  // ── Clipboard write — identical pattern to addon/Dialog.html ──────────────
  // Must run inside the transient-activation window of a real click — never
  // from inside an async fetch's success handler (proven the hard way: that
  // window does not survive the round-trip).

  clipTarget.addEventListener('copy', (e) => {
    e.preventDefault();
    if (!pendingBundle) return;
    Object.keys(pendingBundle).forEach((mime) => e.clipboardData.setData(mime, pendingBundle[mime]));
  });

  function writeClipBundle(bundle) {
    pendingBundle = bundle;
    clipTarget.focus();
    const range = document.createRange();
    range.selectNodeContents(clipTarget);
    const sel = window.getSelection();
    sel.removeAllRanges();
    sel.addRange(range);
    const ok = document.execCommand('copy');
    pendingBundle = null;
    return ok;
  }

  // ── File selection ────────────────────────────────────────────────────

  dropZone.addEventListener('click', (e) => {
    if (dropZone.classList.contains('has-files')) return;
    if (e.target === changeLink) return;
    fileInput.click();
  });
  changeLink.addEventListener('click', (e) => { e.stopPropagation(); fileInput.click(); });
  dropZone.addEventListener('dragover', (e) => { e.preventDefault(); e.stopPropagation(); dropZone.classList.add('drag-over'); });
  dropZone.addEventListener('dragleave', (e) => { e.stopPropagation(); dropZone.classList.remove('drag-over'); });
  dropZone.addEventListener('drop', (e) => {
    e.preventDefault(); e.stopPropagation();
    dropZone.classList.remove('drag-over');
    const svgs = Array.from(e.dataTransfer.files).filter((f) => f.name.toLowerCase().endsWith('.svg'));
    if (svgs.length) applyFiles(svgs);
  });
  fileInput.addEventListener('change', () => {
    if (fileInput.files.length) applyFiles(Array.from(fileInput.files));
  });

  function applyFiles(files) {
    selectedFiles = files;
    dropZone.classList.add('has-files');
    thumbGrid.classList.add('visible');
    renderThumbnails(files);
    changeLink.classList.add('visible');

    pendingBundle = null;
    stage = 'idle';
    actionBtn.textContent = 'Convert';
    actionBtn.disabled = !placement;
    cancelBtn.textContent = 'Cancel';
    copyHint.classList.remove('visible');
    pasteHint.classList.remove('visible');
    clearStatus();

    // Conversion needs no user gesture (just a network call) — start
    // immediately. The one gesture the browser actually requires is
    // reserved for the clipboard write in copyShapes(), which can't be
    // triggered from here.
    convertFiles();
  }

  function renderThumbnails(files) {
    thumbGrid.innerHTML = '';
    files.forEach((file) => {
      const card = document.createElement('div');
      card.className = 'thumb-card';
      const imgWrap = document.createElement('div');
      imgWrap.className = 'thumb-img-wrap';
      const img = document.createElement('img');
      img.src = URL.createObjectURL(file);
      imgWrap.appendChild(img);
      const name = document.createElement('div');
      name.className = 'thumb-name';
      name.textContent = file.name;
      name.title = file.name;
      card.appendChild(imgWrap);
      card.appendChild(name);
      thumbGrid.appendChild(card);
    });
  }

  // ── Status helpers ────────────────────────────────────────────────────

  function clearStatus() { statusEl.innerHTML = ''; statusEl.className = 'status'; }
  function setStatus(msg, spinning, cls) {
    statusEl.innerHTML = (spinning ? '<div class="spinner"></div>' : '') + '<span>' + esc(msg) + '</span>';
    statusEl.className = 'status' + (cls ? ' ' + cls : '');
  }

  function onError(err) {
    setStatus('✗ ' + err.message, false, 'error');
    stage = 'idle';
    actionBtn.textContent = 'Convert';
    actionBtn.disabled = !placement;
  }

  // ── Convert -> Copy state machine (mirrors addon/Dialog.html exactly) ───

  actionBtn.addEventListener('click', () => {
    if (stage === 'idle') convertFiles();
    else if (stage === 'converted') copyShapes();
    // No 'done' branch needed: unlike the Apps Script modal, this popup
    // auto-closes natively the instant the user clicks elsewhere (e.g. the
    // Slides canvas) — nothing here needs to manage closing itself.
  });

  function convertFiles() {
    if (!selectedFiles.length || !placement) return;
    actionBtn.disabled = true;
    cancelBtn.disabled = true;
    setStatus('Converting…', true);

    readFilesAsBase64(selectedFiles).then((payload) => {
      return fetch(BACKEND + '/insert-svg-clip-at', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ files: payload, x_pt: placement.x_pt, y_pt: placement.y_pt }),
      });
    }).then(async (res) => {
      const json = await res.json();
      if (!res.ok) throw new Error(json.detail || 'Server error');
      pendingBundle = json.clip;
      stage = 'converted';
      actionBtn.disabled = false;
      cancelBtn.disabled = false;
      actionBtn.textContent = 'Copy shapes to clipboard';
      clearStatus();
      copyHint.classList.add('visible');
      actionBtn.focus();
    }).catch(onError);
  }

  function copyShapes() {
    const bundle = pendingBundle;
    const ok = writeClipBundle(bundle);

    if (!ok) {
      onError(new Error('Clipboard write failed — try clicking the button again.'));
      pendingBundle = bundle;
      stage = 'converted';
      actionBtn.textContent = 'Copy shapes to clipboard';
      actionBtn.disabled = false;
      return;
    }

    clearStatus();
    copyHint.classList.remove('visible');
    pasteHint.classList.add('visible');
    stage = 'done';
    actionBtn.disabled = true;
    cancelBtn.textContent = 'Copy again';
    cancelBtn.disabled = false;
  }

  cancelBtn.addEventListener('click', () => {
    if (stage === 'done') {
      stage = 'converted';
      actionBtn.textContent = 'Copy shapes to clipboard';
      actionBtn.disabled = false;
      cancelBtn.textContent = 'Cancel';
      pasteHint.classList.remove('visible');
      copyHint.classList.add('visible');
    } else {
      window.close();
    }
  });

  // ── Keyboard shortcuts (parity with the add-on dialog) ─────────────────
  document.addEventListener('keydown', (e) => {
    if (stage === 'converted' && (e.metaKey || e.ctrlKey) && e.key.toLowerCase() === 'c') {
      e.preventDefault();
      copyShapes();
    }
  });
})();
