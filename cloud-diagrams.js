(function () {
  'use strict';

  const runtime = window.PETAKERJA_EXPLORER_RUNTIME || {};
  const DB_NAME = 'petakerja-architecture-cloud-v1';
  const DB_VERSION = 1;
  const DOCUMENT_STORE = 'documents';
  const META_STORE = 'meta';
  const AUTOSAVE_DELAY = 1400;
  const sessionId = (() => {
    try {
      const key = 'petakerja-architecture-writer-session';
      const existing = sessionStorage.getItem(key);
      if (existing) return existing;
      const created = `${crypto.randomUUID?.() || `${Date.now()}-${Math.random()}`}`;
      sessionStorage.setItem(key, created);
      return created;
    } catch (_error) {
      return `${Date.now()}-${Math.random().toString(36).slice(2)}`;
    }
  })();

  function apiBase() {
    return `${String(runtime.cloudApiBase || '/api/architecture-explorer').replace(/\/$/, '')}/diagrams`;
  }

  function escapeHTML(value) {
    return String(value ?? '').replace(/[&<>'"]/g, (character) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', "'": '&#39;', '"': '&quot;' }[character]));
  }

  function openDatabase() {
    if (!('indexedDB' in window)) return Promise.resolve(null);
    return new Promise((resolve, reject) => {
      const request = indexedDB.open(DB_NAME, DB_VERSION);
      request.onupgradeneeded = () => {
        const database = request.result;
        if (!database.objectStoreNames.contains(DOCUMENT_STORE)) database.createObjectStore(DOCUMENT_STORE, { keyPath: 'id' });
        if (!database.objectStoreNames.contains(META_STORE)) database.createObjectStore(META_STORE, { keyPath: 'key' });
      };
      request.onsuccess = () => resolve(request.result);
      request.onerror = () => reject(request.error);
    });
  }

  async function dbOperation(store, mode, callback) {
    const database = await openDatabase();
    if (!database) return null;
    return new Promise((resolve, reject) => {
      const transaction = database.transaction(store, mode);
      const objectStore = transaction.objectStore(store);
      let result;
      try { result = callback(objectStore); } catch (error) { reject(error); return; }
      transaction.oncomplete = () => resolve(result?.result ?? result ?? null);
      transaction.onerror = () => reject(transaction.error);
    }).finally(() => database.close());
  }

  const dbGet = (store, key) => dbOperation(store, 'readonly', (objectStore) => objectStore.get(key));
  const dbPut = (store, value) => dbOperation(store, 'readwrite', (objectStore) => objectStore.put(value));

  async function request(path = '', options = {}) {
    const response = await fetch(`${apiBase()}${path}`, {
      ...options,
      credentials: 'same-origin',
      headers: { ...(options.body ? { 'Content-Type': 'application/json' } : {}), ...(options.headers || {}) },
    });
    const payload = response.status === 204 ? {} : await response.json().catch(() => ({}));
    if (!response.ok) {
      const error = new Error(payload.error || `Cloud request failed (${response.status}).`);
      error.status = response.status;
      error.payload = payload;
      throw error;
    }
    return payload;
  }

  function bytesToBase64(bytes) {
    let binary = '';
    const chunk = 0x8000;
    for (let offset = 0; offset < bytes.length; offset += chunk) binary += String.fromCharCode(...bytes.subarray(offset, offset + chunk));
    return btoa(binary);
  }

  function yUpdateFromXml(xml) {
    if (!window.Y?.Doc) return null;
    const ydoc = new window.Y.Doc();
    const documentMap = ydoc.getMap('document');
    const pages = ydoc.getMap('pages');
    const parsed = new DOMParser().parseFromString(String(xml || ''), 'application/xml');
    documentMap.set('format', 'drawio-mxgraph-v1');
    documentMap.set('updatedAt', new Date().toISOString());
    for (const diagram of parsed.querySelectorAll('mxfile > diagram')) {
      const pageId = diagram.getAttribute('id') || diagram.getAttribute('name') || crypto.randomUUID?.() || `${Date.now()}`;
      const page = new window.Y.Map();
      const cells = new window.Y.Map();
      page.set('name', diagram.getAttribute('name') || 'Page');
      for (const cell of diagram.querySelectorAll('mxCell')) {
        const id = cell.getAttribute('petakerjaKey') || cell.getAttribute('id');
        if (!id) continue;
        const record = new window.Y.Map();
        ['id', 'value', 'style', 'parent', 'source', 'target', 'vertex', 'edge', 'petakerjaKey'].forEach((name) => {
          const value = cell.getAttribute(name);
          if (value != null) record.set(name, value);
        });
        const geometry = cell.querySelector(':scope > mxGeometry');
        if (geometry) {
          const geometryRecord = {};
          for (const name of ['x', 'y', 'width', 'height', 'relative']) {
            const value = geometry.getAttribute(name);
            if (value != null) geometryRecord[name] = value;
          }
          record.set('geometry', geometryRecord);
        }
        cells.set(id, record);
      }
      page.set('cells', cells);
      pages.set(pageId, page);
    }
    return window.Y.encodeStateAsUpdate(ydoc);
  }

  function createManager(options = {}) {
    const elements = {
      library: document.getElementById('cloud-diagram-library'),
      create: document.getElementById('cloud-diagram-new'),
      save: document.getElementById('cloud-diagram-save'),
      version: document.getElementById('cloud-diagram-version'),
      share: document.getElementById('cloud-diagram-share'),
      dialog: document.getElementById('cloud-diagram-dialog'),
      close: document.getElementById('cloud-diagram-close'),
      closeFooter: document.getElementById('cloud-diagram-close-footer'),
      refresh: document.getElementById('cloud-diagram-refresh'),
      search: document.getElementById('cloud-diagram-search'),
      list: document.getElementById('cloud-diagram-list'),
      status: document.getElementById('cloud-diagram-status'),
      title: document.getElementById('cloud-diagram-title'),
      subtitle: document.getElementById('cloud-diagram-subtitle'),
    };
    let active = null;
    let autosaveTimer = null;
    let saving = false;
    let list = [];

    const language = () => options.getLanguage?.() === 'ms' ? 'ms' : 'en';
    const label = (en, ms) => language() === 'ms' ? ms : en;
    const setStatus = (message, kind = 'info') => {
      if (elements.status) { elements.status.textContent = message; elements.status.dataset.state = kind; }
      options.onStatus?.(message, kind);
    };

    function updateControls() {
      const enabled = Boolean(runtime.capabilities?.cloudDiagrams);
      for (const element of [elements.library, elements.create]) if (element) element.hidden = !enabled;
      const cloudOpen = Boolean(active);
      if (elements.save) elements.save.hidden = !enabled || !options.isEditorAvailable?.();
      if (elements.version) elements.version.hidden = !cloudOpen || !active.diagram?.can_edit;
      if (elements.share) elements.share.hidden = !cloudOpen || !active.diagram?.can_manage;
      if (elements.save) {
        const text = active
          ? (active.dirty ? label('Save to cloud *', 'Simpan ke awan *') : label('Saved to cloud', 'Disimpan ke awan'))
          : label('Save to cloud', 'Simpan ke awan');
        elements.save.querySelector('span').textContent = text;
        elements.save.disabled = saving || (active && !active.diagram?.can_edit);
      }
    }

    function renderLibrary() {
      if (!elements.list) return;
      const query = elements.search?.value.trim().toLocaleLowerCase() || '';
      const rows = list.filter((diagram) => !query || `${diagram.title} ${diagram.diagram_type}`.toLocaleLowerCase().includes(query));
      elements.list.innerHTML = rows.length ? rows.map((diagram) => {
        const shared = diagram.access_role === 'editor' || diagram.access_role === 'viewer';
        const canonical = diagram.visibility === 'canonical';
        return `<article class="cloud-diagram-card" data-cloud-id="${escapeHTML(diagram.id)}"><div><strong>${escapeHTML(diagram.title)}</strong><span>${escapeHTML(diagram.diagram_type)} · ${canonical ? label('Canonical', 'Kanonikal') : shared ? label('Shared', 'Dikongsi') : label('Private', 'Peribadi')}</span><small>${new Date(diagram.updated_at).toLocaleString()}</small></div><div><button type="button" data-cloud-open="${escapeHTML(diagram.id)}">${diagram.can_edit ? label('Open', 'Buka') : label('View', 'Lihat')}</button>${canonical ? `<button type="button" class="secondary-button" data-cloud-copy="${escapeHTML(diagram.id)}">${label('Make a copy', 'Buat salinan')}</button>` : ''}</div></article>`;
      }).join('') : `<p class="cloud-diagram-empty">${label('No cloud diagrams match this view.', 'Tiada rajah awan sepadan dengan paparan ini.')}</p>`;
    }

    async function loadList(showDialog = false) {
      if (!runtime.capabilities?.cloudDiagrams) return [];
      if (showDialog && elements.dialog && !elements.dialog.open) elements.dialog.showModal();
      setStatus(label('Loading cloud diagrams…', 'Memuatkan rajah awan…'));
      try {
        const payload = await request();
        list = payload.diagrams || [];
        await dbPut(META_STORE, { key: 'diagram-list', diagrams: list, updatedAt: Date.now() });
        renderLibrary();
        setStatus(label(`${list.length} cloud diagram(s) available.`, `${list.length} rajah awan tersedia.`), 'success');
        return list;
      } catch (error) {
        const cached = await dbGet(META_STORE, 'diagram-list').catch(() => null);
        if (cached?.diagrams) { list = cached.diagrams; renderLibrary(); }
        setStatus(`${label('Cloud library unavailable', 'Pustaka awan tidak tersedia')}: ${error.message}`, 'error');
        return list;
      }
    }

    async function openRecord(record, source = 'cloud') {
      active = { ...record, id: record.diagram.id, source, dirty: Boolean(record.dirty), openedAt: Date.now() };
      await dbPut(DOCUMENT_STORE, active);
      options.openDocument?.(active);
      updateControls();
      setStatus(source === 'cache' ? label('Opened the offline copy. Checking the cloud…', 'Salinan luar talian dibuka. Menyemak awan…') : label('Cloud diagram loaded.', 'Rajah awan dimuatkan.'), 'success');
      return active;
    }

    async function open(id) {
      const cached = await dbGet(DOCUMENT_STORE, id).catch(() => null);
      if (cached?.xml) await openRecord(cached, 'cache');
      try {
        const remote = await request(`/${encodeURIComponent(id)}`);
        const localChanged = cached?.dirty && cached.xml !== remote.xml;
        if (localChanged) {
          active = cached;
          updateControls();
          setStatus(label('Offline changes are pending. Save them or create a branch before replacing this copy.', 'Perubahan luar talian belum disimpan. Simpan atau cipta cabang sebelum menggantikan salinan ini.'), 'warning');
          return active;
        }
        return await openRecord({ ...remote, id, dirty: false }, 'cloud');
      } catch (error) {
        if (cached?.xml) return cached;
        setStatus(`${label('Unable to open the diagram', 'Rajah tidak dapat dibuka')}: ${error.message}`, 'error');
        throw error;
      }
    }

    async function persistYUpdate(xml) {
      if (!active?.diagram?.can_edit || !active.branch?.id) return;
      const update = yUpdateFromXml(xml);
      if (!update?.length || update.length > 1024 * 1024) return;
      try {
        await request(`/${encodeURIComponent(active.id)}/sync/updates`, {
          method: 'POST',
          body: JSON.stringify({ branchId: active.branch.id, clientId: sessionId, update: bytesToBase64(update) }),
        });
      } catch (_error) { /* Snapshot autosave remains authoritative during the single-writer phase. */ }
    }

    async function recoverSaveConflict(error, snapshot) {
      if (error.status === 409) {
        setStatus(label('A newer cloud revision exists. Your browser copy is safe.', 'Semakan awan yang lebih baharu wujud. Salinan pelayar anda selamat.'), 'conflict');
        const shouldBranch = window.confirm(label(
          'Save this work on a new branch? Choose Cancel to keep it offline and review the newer cloud revision first.',
          'Simpan kerja ini pada cabang baharu? Pilih Batal untuk menyimpannya di luar talian dan semak semakan awan yang lebih baharu dahulu.',
        ));
        if (!shouldBranch) return false;
        const name = window.prompt(label('New branch name', 'Nama cabang baharu'), `offline-recovery-${new Date().toISOString().slice(0, 10)}`);
        if (!name) return false;
        const payload = await request(`/${encodeURIComponent(active.id)}/branches`, {
          method: 'POST',
          body: JSON.stringify({ name, sourceBranchId: active.branch.id }),
        });
        active = { ...active, branch: payload.branch, xml: snapshot.xml, dirty: true };
        await dbPut(DOCUMENT_STORE, active);
        setStatus(label('Recovery branch created. Saving the pending work...', 'Cabang pemulihan dicipta. Menyimpan kerja tertangguh...'), 'warning');
        window.setTimeout(() => saveNow(), 0);
        return true;
      }

      if (error.status === 423) {
        setStatus(label('Another session currently owns the edit lease.', 'Sesi lain sedang memegang pajakan suntingan.'), 'locked');
        const shouldTakeOver = window.confirm(label(
          'Request takeover of this branch? The other session will become read-only on its next save.',
          'Ambil alih cabang ini? Sesi lain akan menjadi baca sahaja pada simpanan seterusnya.',
        ));
        if (!shouldTakeOver) return false;
        const payload = await request(`/${encodeURIComponent(active.id)}/branches/${encodeURIComponent(active.branch.id)}/takeover`, {
          method: 'POST',
          body: JSON.stringify({ sessionId }),
        });
        active = { ...active, branch: payload.branch, xml: snapshot.xml, dirty: true };
        await dbPut(DOCUMENT_STORE, active);
        setStatus(label('Edit lease acquired. Saving the pending work...', 'Pajakan suntingan diperoleh. Menyimpan kerja tertangguh...'), 'warning');
        window.setTimeout(() => saveNow(), 0);
        return true;
      }

      return false;
    }

    async function saveNow() {
      if (saving || !options.isEditorAvailable?.()) return false;
      const snapshot = options.getSnapshot?.();
      if (!snapshot?.xml) { setStatus(label('Open a diagram in Edit mode before saving.', 'Buka rajah dalam mod Edit sebelum menyimpan.'), 'warning'); return false; }
      if (!active) return createFromCurrent();
      if (!active.diagram?.can_edit) { setStatus(label('This diagram is read-only. Make a private copy to edit it.', 'Rajah ini hanya untuk bacaan. Buat salinan peribadi untuk mengubahnya.'), 'warning'); return false; }
      saving = true; updateControls();
      try {
        let preview = null;
        try { preview = await options.exportPreview?.(); } catch (_error) { /* XML still saves when SVG export is temporarily unavailable. */ }
        const xml = preview?.xml || snapshot.xml;
        const payload = await request(`/${encodeURIComponent(active.id)}`, {
          method: 'PUT',
          body: JSON.stringify({ branchId: active.branch.id, expectedRevision: active.branch.revision, sessionId, xml, svg: preview?.svg || active.svg || null, title: active.diagram.title, diagramType: snapshot.analysis?.selectedPage?.detection?.diagramType || active.diagram.diagram_type }),
        });
        active = { ...active, ...payload, diagram: payload.diagram || active.diagram, branch: payload.branch || active.branch, xml, svg: preview?.svg || active.svg || null, dirty: false, source: 'cloud' };
        await dbPut(DOCUMENT_STORE, active);
        await persistYUpdate(xml);
        options.markClean?.();
        setStatus(label('Saved to the cloud.', 'Disimpan ke awan.'), 'success');
        await loadList(false);
        return true;
      } catch (error) {
        active = { ...active, xml: snapshot.xml, dirty: true };
        await dbPut(DOCUMENT_STORE, active);
        let recoveryStarted = false;
        try { recoveryStarted = await recoverSaveConflict(error, snapshot); } catch (recoveryError) {
          setStatus(`${label('Recovery could not start', 'Pemulihan tidak dapat dimulakan')}: ${recoveryError.message}`, 'error');
        }
        if (!recoveryStarted && error.status !== 409 && error.status !== 423) {
          setStatus(`${label('Cloud save failed; the browser copy is safe', 'Simpanan awan gagal; salinan pelayar masih selamat')}: ${error.message}`, 'error');
        }
        return false;
      } finally { saving = false; updateControls(); }
    }

    async function createFromCurrent() {
      const snapshot = options.getSnapshot?.();
      if (!snapshot?.xml) return false;
      const title = window.prompt(label('Diagram title', 'Tajuk rajah'), snapshot.filename?.replace(/\.(?:drawio|xml)$/i, '') || label('Untitled Diagram', 'Rajah Tanpa Tajuk'));
      if (!title) return false;
      saving = true; updateControls();
      try {
        let preview = null;
        try { preview = await options.exportPreview?.(); } catch (_error) { /* preview is optional */ }
        const payload = await request('', { method: 'POST', body: JSON.stringify({ title, diagramType: snapshot.analysis?.selectedPage?.detection?.diagramType || 'unknown', xml: preview?.xml || snapshot.xml, svg: preview?.svg || null }) });
        await openRecord({ ...payload, id: payload.diagram.id, dirty: false }, 'cloud');
        options.markClean?.();
        await loadList(false);
        return true;
      } catch (error) { setStatus(`${label('Unable to create the cloud diagram', 'Rajah awan tidak dapat dicipta')}: ${error.message}`, 'error'); return false; }
      finally { saving = false; updateControls(); }
    }

    async function createBlank() {
      const title = window.prompt(label('New diagram title', 'Tajuk rajah baharu'), label('Untitled Diagram', 'Rajah Tanpa Tajuk'));
      if (!title) return;
      try {
        const payload = await request('', { method: 'POST', body: JSON.stringify({ title, diagramType: 'unknown' }) });
        await openRecord({ ...payload, id: payload.diagram.id, dirty: false }, 'cloud');
        await loadList(false);
      } catch (error) { setStatus(`${label('Unable to create the diagram', 'Rajah tidak dapat dicipta')}: ${error.message}`, 'error'); }
    }

    async function copyCanonical(id) {
      try {
        const source = await request(`/${encodeURIComponent(id)}`);
        const payload = await request('', { method: 'POST', body: JSON.stringify({ title: `${source.diagram.title} — Copy`, diagramType: source.diagram.diagram_type, sourceDiagramId: source.diagram.source_diagram_id || source.diagram.id, xml: source.xml, svg: source.svg }) });
        await openRecord({ ...payload, id: payload.diagram.id, dirty: false }, 'cloud');
        elements.dialog?.close();
        await loadList(false);
      } catch (error) { setStatus(`${label('Unable to copy the diagram', 'Rajah tidak dapat disalin')}: ${error.message}`, 'error'); }
    }

    async function createVersion() {
      if (!active?.diagram?.can_edit) return;
      if (active.dirty && !(await saveNow())) return;
      const versionLabel = window.prompt(label('Version label', 'Label versi'), label('Checkpoint', 'Titik semak'));
      if (!versionLabel) return;
      const note = window.prompt(label('Optional version note', 'Nota versi pilihan'), '') || '';
      try {
        await request(`/${encodeURIComponent(active.id)}/versions`, { method: 'POST', body: JSON.stringify({ branchId: active.branch.id, label: versionLabel, note }) });
        setStatus(label('Version created.', 'Versi dicipta.'), 'success');
      } catch (error) { setStatus(`${label('Unable to create the version', 'Versi tidak dapat dicipta')}: ${error.message}`, 'error'); }
    }

    async function share() {
      if (!active?.diagram?.can_manage) return;
      const email = window.prompt(label('Existing PetaKerja user email', 'E-mel pengguna PetaKerja sedia ada'));
      if (!email) return;
      const role = window.confirm(label('Allow editing? Choose Cancel for view-only access.', 'Benarkan suntingan? Pilih Batal untuk akses lihat sahaja.')) ? 'editor' : 'viewer';
      try {
        await request(`/${encodeURIComponent(active.id)}/members`, { method: 'POST', body: JSON.stringify({ email, role }) });
        setStatus(label('Collaborator added.', 'Rakan kerjasama ditambah.'), 'success');
      } catch (error) { setStatus(`${label('Unable to add the collaborator', 'Rakan kerjasama tidak dapat ditambah')}: ${error.message}`, 'error'); }
    }

    function notifyWorking(snapshot) {
      if (!active || !snapshot?.xml || saving) return;
      active = { ...active, xml: snapshot.xml, dirty: Boolean(snapshot.dirty), updatedAt: Date.now() };
      dbPut(DOCUMENT_STORE, active).catch(() => {});
      updateControls();
      window.clearTimeout(autosaveTimer);
      if (active.diagram?.can_edit && snapshot.dirty) autosaveTimer = window.setTimeout(saveNow, AUTOSAVE_DELAY);
    }

    function setActiveFromDocumentKey(key) {
      if (!String(key || '').startsWith('cloud-')) { active = null; updateControls(); return; }
      const id = String(key).slice(6);
      dbGet(DOCUMENT_STORE, id).then((record) => { if (record) { active = record; updateControls(); } }).catch(() => {});
    }

    function applyLanguage() {
      if (!elements.title) return;
      elements.title.textContent = label('Cloud diagrams', 'Rajah awan');
      elements.subtitle.textContent = label('Private diagrams and canonical PetaKerja references available to this account.', 'Rajah peribadi dan rujukan PetaKerja kanonikal yang tersedia untuk akaun ini.');
      if (elements.search) elements.search.placeholder = label('Search diagrams', 'Cari rajah');
      elements.library?.querySelector('span') && (elements.library.querySelector('span').textContent = label('Cloud', 'Awan'));
      elements.create?.querySelector('span') && (elements.create.querySelector('span').textContent = label('New', 'Baharu'));
      updateControls(); renderLibrary();
    }

    elements.library?.addEventListener('click', () => loadList(true));
    elements.create?.addEventListener('click', createBlank);
    elements.save?.addEventListener('click', saveNow);
    elements.version?.addEventListener('click', createVersion);
    elements.share?.addEventListener('click', share);
    elements.close?.addEventListener('click', () => elements.dialog?.close());
    elements.closeFooter?.addEventListener('click', () => elements.dialog?.close());
    elements.refresh?.addEventListener('click', () => loadList(false));
    elements.search?.addEventListener('input', renderLibrary);
    elements.list?.addEventListener('click', (event) => {
      const openButton = event.target.closest('[data-cloud-open]');
      const copyButton = event.target.closest('[data-cloud-copy]');
      if (openButton) { elements.dialog?.close(); open(openButton.dataset.cloudOpen); }
      else if (copyButton) copyCanonical(copyButton.dataset.cloudCopy);
    });
    window.addEventListener('online', () => { if (active?.dirty) saveNow(); else loadList(false); });
    applyLanguage();

    return Object.freeze({
      loadList, open, saveNow, createFromCurrent, notifyWorking, setActiveFromDocumentKey,
      updateControls, applyLanguage, active: () => active,
    });
  }

  window.PETAKERJA_CLOUD = Object.freeze({ createManager });
}());
