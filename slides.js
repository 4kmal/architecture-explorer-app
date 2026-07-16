(function () {
  'use strict';

  const Fabric = window.fabric;
  const CONFIG = window.PETAKERJA_SLIDES;
  const ARCH = window.PETAKERJA_ARCHITECTURE || {};
  const DIAGRAMS = window.PETAKERJA_DIAGRAM_ASSETS || {};
  const RUNTIME = window.PETAKERJA_EXPLORER_RUNTIME || { integrated: false, api: (path) => `/api/${path}` };
  if (!Fabric || !CONFIG) return;

  const el = (id) => document.getElementById(id);
  const shell = el('slides-shell');
  const editor = shell?.querySelector('.slides-editor');
  const state = {
    active: false,
    previousHash: '#explorer',
    deck: null,
    currentSlideId: null,
    canvas: null,
    workspaceToken: '',
    localRevision: null,
    cloud: null,
    suppressHistory: false,
    history: [],
    historyIndex: -1,
    saveTimer: 0,
    checkerTimer: 0,
    diagramObjectURLs: [],
    mobilePanel: 'canvas',
    slideWheelDelta: 0,
    slideWheelDirection: 0,
    slideWheelResetTimer: 0,
    slideWheelLockedUntil: 0,
  };

  const SLIDE_WHEEL_THRESHOLD = 64;
  const SLIDE_WHEEL_COOLDOWN_MS = 260;
  const SLIDE_WHEEL_IDLE_RESET_MS = 180;

  const customProps = ['elementId', 'elementType', 'assetId', 'diagramId', 'diagramHash', 'diagramVariant', 'diagramLanguage', 'diagramLabelMode', 'sourceRevision', 'sourceSvg', 'altText', 'caption', 'linkHash'];
  // Fabric 7 no longer reliably forwards Canvas#toJSON(propertiesToInclude)
  // to every object subclass (notably SVG groups). Register the presentation
  // metadata globally so linked-diagram identity and accessibility fields
  // survive local saves, cloud sync, imports and browser reloads.
  Fabric.FabricObject.customProperties = Array.from(new Set([
    ...(Fabric.FabricObject.customProperties || []),
    ...customProps,
  ]));
  // The editor's layout coordinates are authored from each object's top-left
  // corner. Fabric 7 defaults to centre origins, which otherwise shifts wide
  // text boxes and imported SVG groups outside the slide after creation.
  Fabric.FabricObject.ownDefaults.originX = 'left';
  Fabric.FabricObject.ownDefaults.originY = 'top';
  const localized = (value, language = interfaceLanguage()) => typeof value === 'string' ? value : (value?.[language] || value?.en || value?.ms || '');
  const ui = (en, ms) => interfaceLanguage() === 'ms' ? ms : en;
  const nowISO = () => new Date().toISOString();
  const uid = (prefix) => `${prefix}-${crypto.randomUUID()}`;
  const interfaceLanguage = () => {
    try { return localStorage.getItem('petakerja-explorer-language') === 'ms' ? 'ms' : 'en'; } catch (_error) { return 'en'; }
  };
  const safeName = (value) => String(value || 'petakerja-slides').trim().replace(/[<>:"/\\|?*]+/g, '-').slice(0, 96) || 'petakerja-slides';
  const download = (blob, name) => { const href = URL.createObjectURL(blob); const a = document.createElement('a'); a.href = href; a.download = name; a.click(); setTimeout(() => URL.revokeObjectURL(href), 1500); };
  const svgData = (svg) => `data:image/svg+xml;base64,${btoa(unescape(encodeURIComponent(svg)))}`;
  const hashText = async (text) => Array.from(new Uint8Array(await crypto.subtle.digest('SHA-256', new TextEncoder().encode(text)))).map((byte) => byte.toString(16).padStart(2, '0')).join('');
  const announce = (message) => { const node = el('slides-live'); if (node) node.textContent = message; };
  const formatTime = (seconds) => `${Math.floor(seconds / 60)}:${String(seconds % 60).padStart(2, '0')}`;

  async function loadCanvasJSON(canvas, json) {
    await canvas.loadFromJSON(json || emptyCanvasJSON());
    canvas.requestRenderAll();
    return canvas;
  }

  function resolveLightDarkCSS(source, useDark = document.documentElement.dataset.theme === 'dark') {
    let output = '';
    let cursor = 0;
    while (cursor < source.length) {
      const start = source.indexOf('light-dark(', cursor);
      if (start < 0) { output += source.slice(cursor); break; }
      output += source.slice(cursor, start);
      let depth = 1;
      let separator = -1;
      let end = -1;
      for (let index = start + 11; index < source.length; index += 1) {
        const character = source[index];
        if (character === '(') depth += 1;
        else if (character === ')') {
          depth -= 1;
          if (depth === 0) { end = index; break; }
        } else if (character === ',' && depth === 1 && separator < 0) separator = index;
      }
      if (separator < 0 || end < 0) { output += source.slice(start); break; }
      const light = source.slice(start + 11, separator).trim();
      const dark = source.slice(separator + 1, end).trim();
      output += useDark ? dark : light;
      cursor = end + 1;
    }
    return output;
  }

  async function groupSVG(svg) {
    // Browsers understand CSS light-dark(), but Fabric's SVG parser does not.
    // Resolve the current presentation theme for the editable canvas while
    // retaining the original theme-aware SVG snapshot in the deck asset.
    const parsed = await Fabric.loadSVGFromString(resolveLightDarkCSS(svg));
    return Fabric.util.groupSVGElements((parsed.objects || []).filter(Boolean), parsed.options || {});
  }

  function addAndSelect(object) {
    state.canvas.add(object);
    state.canvas.setActiveObject(object);
    state.canvas.requestRenderAll();
    return object;
  }

  function replaceButtonText(selector, en, ms) {
    const node = document.querySelector(selector);
    if (!node) return;
    const label = ui(en, ms);
    const span = node.querySelector(':scope > span');
    if (span) span.textContent = label;
    else {
      const textNode = [...node.childNodes].find((child) => child.nodeType === Node.TEXT_NODE && child.nodeValue.trim());
      if (textNode) textNode.nodeValue = label;
      else node.append(document.createTextNode(label));
    }
  }

  function translateSlidesUI() {
    replaceButtonText('#slides-link', 'Slides', 'Slaid');
    replaceButtonText('#slides-back', 'Explorer', 'Explorer');
    replaceButtonText('#slides-undo', 'Undo', 'Undur');
    replaceButtonText('#slides-redo', 'Redo', 'Buat semula');
    replaceButtonText('#slides-add', 'Add slide', 'Tambah slaid');
    replaceButtonText('#slides-present', 'Present', 'Bentang');
    replaceButtonText('#slides-save', 'Save', 'Simpan');
    replaceButtonText('#slides-save-copy', 'Save as copy', 'Simpan sebagai salinan');
    replaceButtonText('#slides-cloud', 'Sync', 'Segerak');
    replaceButtonText('#slides-export', 'Export', 'Eksport');
    const setText = (selector, en, ms) => { const node = document.querySelector(selector); if (node) node.textContent = ui(en, ms); };
    setText('.slides-filmstrip__heading strong', 'Slides', 'Slaid');
    setText('#slides-preset', 'New UKM deck', 'Dek UKM baharu');
    [['layouts', 'Layouts', 'Susun atur'], ['elements', 'Elements', 'Elemen'], ['diagrams', 'Diagrams', 'Rajah'], ['properties', 'Properties', 'Sifat']].forEach(([id, en, ms]) => setText(`[data-slides-panel="${id}"]`, en, ms));
    setText('#slides-panel-layouts h3', 'Layouts', 'Susun atur');
    setText('#slides-panel-elements h3:first-child', 'Elements', 'Elemen');
    setText('#slides-panel-diagrams h3', 'Explorer diagrams', 'Rajah Explorer');
    setText('#slides-panel-properties h3', 'Properties', 'Sifat');
    [['heading', 'Heading', 'Tajuk'], ['body', 'Body text', 'Teks isi'], ['rectangle', 'Rectangle', 'Segi empat'], ['ellipse', 'Ellipse', 'Elips'], ['image', 'Image', 'Imej']].forEach(([id, en, ms]) => replaceButtonText(`[data-add-element="${id}"]`, en, ms));
    [['front', 'Bring forward', 'Bawa ke hadapan'], ['back', 'Send backward', 'Hantar ke belakang'], ['duplicate', 'Duplicate', 'Gandakan'], ['delete', 'Delete', 'Padam']].forEach(([id, en, ms]) => setText(`[data-layer-action="${id}"]`, en, ms));
    setText('[data-slides-bottom="notes"]', 'Speaker notes', 'Nota pembentang');
    const checkerButton = document.querySelector('[data-slides-bottom="checker"]');
    if (checkerButton?.firstChild) checkerButton.firstChild.nodeValue = `${ui('Presentation checker', 'Pemeriksa pembentangan')} `;
    const notes = el('slides-speaker-notes');
    if (notes) notes.placeholder = ui('Speaker notes are exported to PowerPoint and are not shown to the audience.', 'Nota pembentang dieksport ke PowerPoint dan tidak dipaparkan kepada penonton.');
    const search = el('slides-diagram-search'); if (search) search.placeholder = ui('Search diagrams', 'Cari rajah');
    const optionLabels = {
      'slides-diagram-family': { all: ui('All families', 'Semua keluarga') },
      'slides-diagram-audience': { all: ui('All audiences', 'Semua pengguna'), user: ui('User', 'Pengguna'), administrator: ui('Administrator', 'Pentadbir') },
      'slides-diagram-variant': { all: ui('All variants', 'Semua varian'), polished: ui('Polished', 'Dikemas'), original: ui('Original', 'Asal') },
    };
    Object.entries(optionLabels).forEach(([id, labels]) => [...(el(id)?.options || [])].forEach((option) => { if (labels[option.value]) option.textContent = labels[option.value]; }));
    setText('#slides-insert-current-diagram', 'Insert current Explorer diagram', 'Masukkan rajah Explorer semasa');
    [['slides', 'Slides', 'Slaid'], ['canvas', 'Canvas', 'Kanvas'], ['tools', 'Tools', 'Alat'], ['notes', 'Notes', 'Nota']].forEach(([id, en, ms]) => setText(`[data-slides-mobile="${id}"]`, en, ms));
    document.documentElement.lang = interfaceLanguage();
  }

  function theme() {
    const configured = CONFIG.themes[0];
    return document.documentElement.dataset.theme === 'dark' ? configured.dark : configured.light;
  }

  function emptyCanvasJSON(background) {
    return { version: Fabric.version, objects: [], background: background || theme().background };
  }

  function createSlide(definition, language, index) {
    const id = uid('slide');
    const palette = theme();
    const title = localized(definition?.title || { en: `Slide ${index + 1}`, ms: `Slaid ${index + 1}` }, language);
    const subtitle = localized(definition?.subtitle || '', language);
    const objects = [
      new Fabric.Textbox(title, { left: 110, top: 92, width: 1380, fontFamily: 'Aptos', fontSize: index === 0 ? 60 : 46, fontWeight: 700, fill: palette.text, lineHeight: 1.08, elementId: uid('text'), elementType: 'title' }),
      new Fabric.Textbox(subtitle, { left: 112, top: index === 0 ? 205 : 178, width: 1240, fontFamily: 'Aptos', fontSize: index === 0 ? 28 : 23, fill: palette.muted, lineHeight: 1.25, elementId: uid('text'), elementType: 'subtitle' }),
    ];
    if (index > 0) objects.push(new Fabric.Textbox(language === 'ms' ? 'Tambah isi utama, bukti atau rajah di sini.' : 'Add the main evidence, key points or diagram here.', { left: 112, top: 282, width: 1050, fontFamily: 'Aptos', fontSize: 25, fill: palette.text, lineHeight: 1.3, elementId: uid('text'), elementType: 'body' }));
    const temporary = new Fabric.StaticCanvas(null, { width: 1600, height: 900, backgroundColor: palette.background });
    objects.forEach((object) => temporary.add(object));
    const canvasJson = temporary.toJSON(customProps);
    temporary.dispose();
    return {
      id,
      name: title,
      hidden: false,
      layoutId: index === 0 ? 'title' : 'title-body',
      section: definition?.section || 'custom',
      durationSeconds: Number(definition?.durationSeconds || 45),
      speakerNotes: language === 'ms' ? `Terangkan tujuan slaid “${title}” dengan ringkas dan kaitkan dengan slaid seterusnya.` : `Explain the purpose of “${title}” briefly and connect it to the next slide.`,
      canvasJson,
      preview: '',
    };
  }

  function createDeck() {
    const preset = CONFIG.presets[0];
    const language = CONFIG.defaultLanguage;
    const createdAt = nowISO();
    return {
      schemaVersion: CONFIG.schemaVersion,
      id: uid('deck'),
      title: language === 'ms' ? 'Pembentangan FYP PetaKerja' : 'PetaKerja FYP Presentation',
      language,
      aspectRatio: '16:9',
      presetId: preset.id,
      themeId: CONFIG.defaultTheme,
      slides: preset.slides.map((slide, index) => createSlide(slide, language, index)),
      assets: {},
      createdAt,
      updatedAt: createdAt,
    };
  }

  function currentSlide() { return state.deck?.slides.find((slide) => slide.id === state.currentSlideId) || state.deck?.slides[0] || null; }

  function serializeCanvas() { return state.canvas?.toJSON(customProps) || emptyCanvasJSON(); }

  function captureCurrentSlide({ history = false, persist = true, check = true } = {}) {
    const slide = currentSlide();
    if (!slide || !state.canvas) return;
    slide.canvasJson = serializeCanvas();
    slide.preview = state.canvas.toDataURL({ format: 'png', multiplier: 0.18, enableRetinaScaling: false });
    slide.updatedAt = nowISO();
    state.deck.updatedAt = nowISO();
    if (history) pushHistory();
    renderThumbnails();
    if (persist) scheduleSave();
    if (check) scheduleChecker();
  }

  function pushHistory() {
    if (state.suppressHistory || !state.canvas) return;
    const snapshot = JSON.stringify(serializeCanvas());
    if (state.history[state.historyIndex] === snapshot) return;
    state.history = state.history.slice(0, state.historyIndex + 1);
    state.history.push(snapshot);
    if (state.history.length > 60) state.history.shift();
    state.historyIndex = state.history.length - 1;
    updateHistoryButtons();
  }

  function updateHistoryButtons() {
    el('slides-undo').disabled = state.historyIndex <= 0;
    el('slides-redo').disabled = state.historyIndex < 0 || state.historyIndex >= state.history.length - 1;
  }

  async function restoreHistory(index) {
    if (index < 0 || index >= state.history.length) return;
    state.historyIndex = index;
    state.suppressHistory = true;
    await loadCanvasJSON(state.canvas, JSON.parse(state.history[index]));
    state.suppressHistory = false;
    captureCurrentSlide();
    updateHistoryButtons();
  }

  async function loadSlide(slideId, { savePrevious = true } = {}) {
    if (savePrevious) captureCurrentSlide();
    const slide = state.deck.slides.find((item) => item.id === slideId) || state.deck.slides[0];
    if (!slide) return;
    state.currentSlideId = slide.id;
    state.suppressHistory = true;
    await loadCanvasJSON(state.canvas, slide.canvasJson || emptyCanvasJSON());
    state.suppressHistory = false;
    state.history = [JSON.stringify(serializeCanvas())];
    state.historyIndex = 0;
    el('slides-speaker-notes').value = slide.speakerNotes || '';
    el('slides-duration').value = slide.durationSeconds || 45;
    updateHistoryButtons();
    renderThumbnails();
    syncActiveThumbnail(slide);
    renderProperties();
    updateTotalTime();
  }

  function syncActiveThumbnail(slide) {
    if (!slide) return;
    requestAnimationFrame(() => {
      const active = document.querySelector(`.slides-thumb[data-slide-id="${CSS.escape(slide.id)}"]`);
      active?.scrollIntoView({
        block: 'nearest',
        inline: 'nearest',
        behavior: window.matchMedia?.('(prefers-reduced-motion: reduce)').matches ? 'auto' : 'smooth',
      });
    });
    const index = state.deck.slides.findIndex((item) => item.id === slide.id);
    announce(ui(`Slide ${index + 1} of ${state.deck.slides.length}: ${slide.name}`, `Slaid ${index + 1} daripada ${state.deck.slides.length}: ${slide.name}`));
  }

  function renderThumbnails() {
    const list = el('slides-thumbnails');
    if (!list || !state.deck) return;
    list.replaceChildren(...state.deck.slides.map((slide) => {
      const item = document.createElement('li');
      item.className = `slides-thumb${slide.id === state.currentSlideId ? ' is-active' : ''}${slide.hidden ? ' is-hidden' : ''}`;
      item.draggable = true;
      item.dataset.slideId = slide.id;
      const button = document.createElement('button');
      button.className = 'slides-thumb__button';
      button.type = 'button';
      button.setAttribute('aria-label', `Open ${slide.name}`);
      const image = document.createElement('img');
      image.alt = '';
      image.src = slide.preview || renderSlidePreview(slide);
      button.append(image);
      button.addEventListener('click', () => loadSlide(slide.id));
      const menu = document.createElement('div');
      menu.className = 'slides-thumb__menu';
      [['duplicate', 'Duplicate'], ['hide', slide.hidden ? 'Show' : 'Hide'], ['delete', 'Delete']].forEach(([action, label]) => {
        const actionButton = document.createElement('button'); actionButton.type = 'button'; actionButton.textContent = label; actionButton.dataset.slideAction = action;
        actionButton.addEventListener('click', () => slideAction(slide.id, action)); menu.append(actionButton);
      });
      item.addEventListener('dragstart', (event) => event.dataTransfer.setData('text/slide-id', slide.id));
      item.addEventListener('dragover', (event) => event.preventDefault());
      item.addEventListener('drop', (event) => { event.preventDefault(); reorderSlides(event.dataTransfer.getData('text/slide-id'), slide.id); });
      item.append(button, menu);
      return item;
    }));
  }

  function renderSlidePreview(slide) {
    const canvas = document.createElement('canvas'); canvas.width = 320; canvas.height = 180;
    const preview = new Fabric.StaticCanvas(canvas, { width: 1600, height: 900, enableRetinaScaling: false });
    loadCanvasJSON(preview, slide.canvasJson || emptyCanvasJSON()).then(() => {
      slide.preview = preview.toDataURL({ format: 'png', multiplier: 0.2, enableRetinaScaling: false });
      preview.dispose();
      const image = document.querySelector(`.slides-thumb[data-slide-id="${CSS.escape(slide.id)}"] img`); if (image) image.src = slide.preview;
    }).catch(() => preview.dispose());
    return slide.preview || 'data:image/gif;base64,R0lGODlhAQABAAD/ACwAAAAAAQABAAACADs=';
  }

  function slideAction(slideId, action) {
    const index = state.deck.slides.findIndex((slide) => slide.id === slideId);
    if (index < 0) return;
    captureCurrentSlide();
    if (action === 'duplicate') {
      const copy = structuredClone(state.deck.slides[index]); copy.id = uid('slide'); copy.name = `${copy.name} copy`; copy.preview = '';
      state.deck.slides.splice(index + 1, 0, copy); loadSlide(copy.id, { savePrevious: false });
    } else if (action === 'hide') {
      state.deck.slides[index].hidden = !state.deck.slides[index].hidden; renderThumbnails(); scheduleSave(); scheduleChecker();
    } else if (action === 'delete' && state.deck.slides.length > 1) {
      state.deck.slides.splice(index, 1); loadSlide(state.deck.slides[Math.max(0, index - 1)].id, { savePrevious: false });
    }
  }

  function reorderSlides(sourceId, targetId) {
    if (!sourceId || sourceId === targetId) return;
    captureCurrentSlide();
    const source = state.deck.slides.findIndex((slide) => slide.id === sourceId);
    const target = state.deck.slides.findIndex((slide) => slide.id === targetId);
    if (source < 0 || target < 0) return;
    const [slide] = state.deck.slides.splice(source, 1); state.deck.slides.splice(target, 0, slide);
    renderThumbnails(); scheduleSave(); scheduleChecker();
  }

  function addSlide(layout = 'title-body') {
    captureCurrentSlide();
    const definition = { title: { en: 'New slide', ms: 'Slaid baharu' }, subtitle: { en: '', ms: '' }, durationSeconds: 45, section: 'custom' };
    const slide = createSlide(definition, state.deck.language, state.deck.slides.length); slide.layoutId = layout;
    const currentIndex = state.deck.slides.findIndex((item) => item.id === state.currentSlideId);
    state.deck.slides.splice(currentIndex + 1, 0, slide); loadSlide(slide.id, { savePrevious: false });
  }

  function addText(kind) {
    const palette = theme();
    const isHeading = kind === 'heading';
    const object = new Fabric.IText(isHeading ? (state.deck.language === 'ms' ? 'Tajuk' : 'Heading') : (state.deck.language === 'ms' ? 'Tambah teks' : 'Add text'), {
      left: 180, top: isHeading ? 150 : 300, width: isHeading ? 900 : 720, fontFamily: 'Aptos', fontSize: isHeading ? 42 : 25, fontWeight: isHeading ? 700 : 400, fill: palette.text,
      elementId: uid('text'), elementType: isHeading ? 'heading' : 'body',
    });
    addAndSelect(object); captureCurrentSlide({ history: true });
  }

  function addShape(kind) {
    const palette = theme();
    const common = { left: 280, top: 260, width: 340, height: 180, fill: palette.secondary, stroke: palette.primary, strokeWidth: 2, elementId: uid('shape'), elementType: kind };
    const object = kind === 'ellipse' ? new Fabric.Ellipse({ ...common, rx: 170, ry: 90, width: undefined, height: undefined }) : new Fabric.Rect({ ...common, rx: 10, ry: 10 });
    addAndSelect(object); captureCurrentSlide({ history: true });
  }

  function addImageFile(file) {
    if (!file || !/^image\//.test(file.type) || file.size > 10 * 1024 * 1024) return;
    const reader = new FileReader();
    reader.onload = async () => {
      const image = await Fabric.Image.fromURL(reader.result, { crossOrigin: 'anonymous' });
      image.scaleToWidth(Math.min(720, image.width || 720)); image.set({ left: 220, top: 180, elementId: uid('image'), elementType: 'image', assetId: uid('asset'), altText: '', caption: '' });
      state.deck.assets[image.assetId] = { type: 'image', mimeType: file.type, sha256: '', source: { kind: 'embedded', name: file.name }, data: reader.result };
      addAndSelect(image); captureCurrentSlide({ history: true }); renderProperties();
    };
    reader.readAsDataURL(file);
  }

  function diagramMeta(id) {
    const exact = (ARCH.diagrams || []).find((diagram) => diagram.id === id);
    const canonical = id.endsWith('-original') ? (ARCH.diagrams || []).find((diagram) => diagram.id === id.replace(/-original$/, '')) : null;
    return exact || canonical || { id, title: id.replace(/-/g, ' '), category: 'Diagram', description: '' };
  }

  function diagramFamily(id, meta) {
    const source = `${id} ${meta.category || ''}`.toLowerCase();
    if (source.includes('sequence')) return 'Sequence';
    if (source.includes('flow')) return 'Flow Chart';
    if (source.includes('usecase') || source.includes('use case')) return 'Use Case';
    if (source.includes('domain') || source.includes('implementation') || source.includes('class')) return 'Class';
    if (source.includes('architecture') || source.includes('module')) return 'Architecture';
    if (source.includes('supabase') || source.includes('erd') || source.includes('data')) return 'ERD and data';
    return 'Other';
  }

  function diagramAudience(id) {
    if (/admin|administrator/.test(id)) return 'administrator';
    if (/user|google|job|map|sign-out/.test(id)) return 'user';
    return 'all';
  }

  function renderDiagramLibrary() {
    state.diagramObjectURLs.forEach((url) => URL.revokeObjectURL(url)); state.diagramObjectURLs = [];
    const library = el('slides-diagram-library');
    const search = el('slides-diagram-search').value.trim().toLowerCase();
    const family = el('slides-diagram-family').value;
    const audience = el('slides-diagram-audience').value;
    const variant = el('slides-diagram-variant').value;
    const entries = Object.entries(DIAGRAMS).map(([id, asset]) => ({ id, asset, meta: diagramMeta(id), family: diagramFamily(id, diagramMeta(id)), audience: diagramAudience(id), variant: id.endsWith('-original') ? 'original' : 'polished' }))
      .filter((item) => (!search || `${item.id} ${item.meta.title} ${item.family}`.toLowerCase().includes(search)) && (family === 'all' || item.family === family) && (audience === 'all' || item.audience === audience || item.audience === 'all') && (variant === 'all' || item.variant === variant));
    library.replaceChildren(...entries.slice(0, 80).map((item) => {
      const button = document.createElement('button'); button.type = 'button'; button.className = 'slides-diagram-card';
      const svg = item.asset.svg?.[state.deck.language] || item.asset.svg?.en || item.asset.svg?.ms || '';
      const url = URL.createObjectURL(new Blob([svg], { type: 'image/svg+xml' })); state.diagramObjectURLs.push(url);
      const image = document.createElement('img'); image.src = url; image.alt = '';
      const title = document.createElement('strong'); title.textContent = item.meta.title || item.id;
      const detail = document.createElement('small'); detail.textContent = `${item.family} · ${item.variant}`;
      button.append(image, title, detail); button.addEventListener('click', () => insertDiagram(item.id)); return button;
    }));
  }

  async function insertDiagram(diagramId) {
    const asset = DIAGRAMS[diagramId]; if (!asset) return;
    const language = state.deck.language;
    const svg = asset.svg?.[language] || asset.svg?.en || asset.svg?.ms;
    if (!svg) return;
    const sha256 = await hashText(svg);
    const group = await groupSVG(svg);
    group.scaleToWidth(Math.min(1120, group.width || 1120));
    if ((group.getScaledHeight?.() || 0) > 620) group.scaleToHeight(620);
    group.set({ left: 230, top: 205, elementId: uid('diagram'), elementType: 'diagram', assetId: uid('asset'), diagramId, diagramHash: sha256, diagramVariant: diagramId.endsWith('-original') ? 'original' : 'polished', diagramLanguage: language, diagramLabelMode: 'simple', sourceRevision: sha256, sourceSvg: svg, altText: `${diagramMeta(diagramId).title} diagram`, caption: diagramMeta(diagramId).title, linkHash: `#explorer?diagram=${encodeURIComponent(diagramId)}` });
    state.deck.assets[group.assetId] = { type: 'diagram', mimeType: 'image/svg+xml', sha256, source: { diagramId, variant: group.diagramVariant, language, labelMode: 'simple' }, data: svg };
    addAndSelect(group); captureCurrentSlide({ history: true }); renderProperties(); announce(`${diagramMeta(diagramId).title} inserted.`);
  }

  function renderLayouts() {
    const layouts = [
      ['title', ui('Title slide', 'Slaid tajuk')], ['title-body', ui('Title + body', 'Tajuk + isi')], ['two-column', ui('Two columns', 'Dua lajur')], ['diagram-focus', ui('Diagram focus', 'Fokus rajah')], ['blank', ui('Blank', 'Kosong')],
    ];
    el('slides-layouts').replaceChildren(...layouts.map(([id, label]) => {
      const button = document.createElement('button'); button.type = 'button'; button.textContent = label; button.addEventListener('click', () => applyLayout(id)); return button;
    }));
  }

  function applyLayout(layoutId) {
    const palette = theme();
    const title = currentSlide()?.name || (state.deck.language === 'ms' ? 'Tajuk slaid' : 'Slide title');
    state.suppressHistory = true; state.canvas.clear(); state.canvas.backgroundColor = palette.background;
    if (layoutId !== 'blank') state.canvas.add(new Fabric.Textbox(title, { left: 100, top: 70, width: 1400, fontFamily: 'Aptos', fontSize: layoutId === 'title' ? 60 : 44, fontWeight: 700, fill: palette.text, elementId: uid('text'), elementType: 'title' }));
    if (layoutId === 'title') state.canvas.add(new Fabric.Textbox(state.deck.language === 'ms' ? 'Subtajuk pembentangan' : 'Presentation subtitle', { left: 102, top: 190, width: 1200, fontFamily: 'Aptos', fontSize: 28, fill: palette.muted, elementId: uid('text'), elementType: 'subtitle' }));
    if (layoutId === 'title-body') state.canvas.add(new Fabric.Textbox(state.deck.language === 'ms' ? 'Tambah isi utama di sini.' : 'Add the main content here.', { left: 105, top: 210, width: 1180, fontFamily: 'Aptos', fontSize: 26, fill: palette.text, elementId: uid('text'), elementType: 'body' }));
    if (layoutId === 'two-column') {
      state.canvas.add(new Fabric.Textbox(state.deck.language === 'ms' ? 'Lajur kiri' : 'Left column', { left: 105, top: 210, width: 620, fontFamily: 'Aptos', fontSize: 25, fill: palette.text, elementId: uid('text'), elementType: 'body' }));
      state.canvas.add(new Fabric.Textbox(state.deck.language === 'ms' ? 'Lajur kanan' : 'Right column', { left: 850, top: 210, width: 620, fontFamily: 'Aptos', fontSize: 25, fill: palette.text, elementId: uid('text'), elementType: 'body' }));
    }
    if (layoutId === 'diagram-focus') state.canvas.add(new Fabric.Rect({ left: 155, top: 185, width: 1290, height: 610, fill: palette.surface, stroke: palette.border, strokeWidth: 2, rx: 8, ry: 8, elementId: uid('shape'), elementType: 'diagram-placeholder' }));
    currentSlide().layoutId = layoutId; state.suppressHistory = false; state.canvas.renderAll(); captureCurrentSlide({ history: true });
  }

  function renderProperties() {
    const target = el('slides-properties');
    const object = state.canvas?.getActiveObject();
    if (!object) { target.innerHTML = '<p class="slides-muted">Select an object to edit its properties.</p>'; return; }
    target.innerHTML = `<div class="slides-property-grid">
      <label for="slides-prop-x">X</label><input id="slides-prop-x" type="number" value="${Math.round(object.left || 0)}">
      <label for="slides-prop-y">Y</label><input id="slides-prop-y" type="number" value="${Math.round(object.top || 0)}">
      <label for="slides-prop-width">Width</label><input id="slides-prop-width" type="number" value="${Math.round(object.getScaledWidth?.() || object.width || 0)}">
      <label for="slides-prop-height">Height</label><input id="slides-prop-height" type="number" value="${Math.round(object.getScaledHeight?.() || object.height || 0)}">
      <label for="slides-prop-angle">Rotation</label><input id="slides-prop-angle" type="number" value="${Math.round(object.angle || 0)}">
      <label for="slides-prop-opacity">Opacity</label><input id="slides-prop-opacity" type="range" min="0.1" max="1" step="0.05" value="${object.opacity ?? 1}">
      <label for="slides-prop-alt">Description</label><textarea id="slides-prop-alt" rows="3">${escapeHTML(object.altText || '')}</textarea>
      <label for="slides-prop-caption">Caption</label><input id="slides-prop-caption" type="text" value="${escapeHTML(object.caption || '')}">
    </div>${object.diagramId ? `<p class="slides-muted">Linked to <a href="#explorer?diagram=${encodeURIComponent(object.diagramId)}">${escapeHTML(object.diagramId)}</a></p><button id="slides-refresh-diagram" type="button" class="secondary-button">Refresh from source</button><button id="slides-detach-diagram" type="button" class="secondary-button">Detach</button>` : ''}`;
    [['x', 'left'], ['y', 'top'], ['angle', 'angle'], ['opacity', 'opacity']].forEach(([id, property]) => el(`slides-prop-${id}`).addEventListener('input', (event) => { object.set(property, Number(event.target.value)); object.setCoords(); state.canvas.requestRenderAll(); captureCurrentSlide(); }));
    el('slides-prop-width').addEventListener('change', (event) => { object.scaleToWidth(Math.max(10, Number(event.target.value))); object.setCoords(); state.canvas.requestRenderAll(); captureCurrentSlide({ history: true }); });
    el('slides-prop-height').addEventListener('change', (event) => { object.scaleToHeight(Math.max(10, Number(event.target.value))); object.setCoords(); state.canvas.requestRenderAll(); captureCurrentSlide({ history: true }); });
    el('slides-prop-alt').addEventListener('input', (event) => { object.altText = event.target.value; captureCurrentSlide(); });
    el('slides-prop-caption').addEventListener('input', (event) => { object.caption = event.target.value; captureCurrentSlide(); });
    el('slides-refresh-diagram')?.addEventListener('click', () => refreshDiagramObject(object));
    el('slides-detach-diagram')?.addEventListener('click', () => { delete object.diagramId; delete object.diagramHash; delete object.sourceRevision; object.elementType = 'image'; captureCurrentSlide({ history: true }); renderProperties(); });
  }

  async function refreshDiagramObject(object) {
    const asset = DIAGRAMS[object.diagramId]; if (!asset) return;
    const svg = asset.svg?.[object.diagramLanguage || state.deck.language] || asset.svg?.en || asset.svg?.ms; if (!svg) return;
    const geometry = { left: object.left, top: object.top, scaleX: object.scaleX, scaleY: object.scaleY, angle: object.angle };
    state.canvas.remove(object);
    const group = await groupSVG(svg);
    const revision = await hashText(svg);
    group.set({ ...geometry, ...object.toObject(customProps), sourceSvg: svg, diagramHash: revision, sourceRevision: revision });
    addAndSelect(group); captureCurrentSlide({ history: true }); renderProperties();
  }

  function escapeHTML(value) { return String(value).replace(/[&<>'"]/g, (character) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', "'": '&#39;', '"': '&quot;' }[character])); }

  function updateTotalTime() {
    const total = state.deck.slides.filter((slide) => !slide.hidden).reduce((sum, slide) => sum + Number(slide.durationSeconds || 0), 0);
    el('slides-total-time').textContent = `${formatTime(total)} total`;
  }

  function contrastRatio(first, second) {
    const luminance = (hex) => {
      const normalized = /^#[0-9a-f]{6}$/i.test(hex || '') ? hex.slice(1) : '000000';
      const values = [0, 2, 4].map((index) => parseInt(normalized.slice(index, index + 2), 16) / 255).map((value) => value <= 0.03928 ? value / 12.92 : ((value + 0.055) / 1.055) ** 2.4);
      return values[0] * 0.2126 + values[1] * 0.7152 + values[2] * 0.0722;
    };
    const a = luminance(first); const b = luminance(second); return (Math.max(a, b) + 0.05) / (Math.min(a, b) + 0.05);
  }

  function validateDeck() {
    captureCurrentSlide({ persist: false, check: false });
    const issues = [];
    const visible = state.deck.slides.filter((slide) => !slide.hidden);
    const total = visible.reduce((sum, slide) => sum + Number(slide.durationSeconds || 0), 0);
    if (visible.length < 10 || visible.length > 12) issues.push({ severity: 'warning', text: `Use 10–12 main slides; this deck has ${visible.length}.` });
    if (total < 540 || total > 600) issues.push({ severity: 'warning', text: `Target 9–10 minutes; the current timing is ${formatTime(total)}.` });
    const sections = new Set(visible.map((slide) => slide.section));
    CONFIG.requiredSections.filter((section) => !sections.has(section)).forEach((section) => issues.push({ severity: 'error', text: `Missing required section: ${localized(CONFIG.sectionLabels[section])}.` }));
    if (state.deck.language !== 'ms') issues.push({ severity: 'warning', text: 'UKM guidance recommends Bahasa Melayu for the presentation.' });
    visible.forEach((slide, index) => {
      if (!String(slide.speakerNotes || '').trim()) issues.push({ severity: 'warning', text: `Slide ${index + 1} has no speaker notes.` });
      const objects = slide.canvasJson?.objects || [];
      if (objects.filter((object) => /text|i-text|textbox/.test(object.type)).reduce((sum, object) => sum + String(object.text || '').split(/\s+/).length, 0) > 90) issues.push({ severity: 'warning', text: `Slide ${index + 1} may contain too much text.` });
      objects.forEach((object) => {
        const width = Number(object.width || 0) * Number(object.scaleX || 1); const height = Number(object.height || 0) * Number(object.scaleY || 1);
        if (Number(object.left || 0) < 0 || Number(object.top || 0) < 0 || Number(object.left || 0) + width > 1600 || Number(object.top || 0) + height > 900) issues.push({ severity: 'error', text: `Slide ${index + 1} has content outside the slide bounds.` });
        if (/text|i-text|textbox/.test(object.type) && Number(object.fontSize || 0) < 18) issues.push({ severity: 'warning', text: `Slide ${index + 1} contains text smaller than 18 pt.` });
        if ((object.elementType === 'image' || object.elementType === 'diagram') && !String(object.altText || '').trim() && !String(object.caption || '').trim()) issues.push({ severity: 'warning', text: `Slide ${index + 1} has an image or diagram without a description or caption.` });
        if (object.fill && /^#[0-9a-f]{6}$/i.test(object.fill) && contrastRatio(object.fill, slide.canvasJson.background || '#ffffff') < 3) issues.push({ severity: 'warning', text: `Slide ${index + 1} may contain low-contrast content.` });
        if (object.diagramId && DIAGRAMS[object.diagramId]) {
          const currentSvg = DIAGRAMS[object.diagramId].svg?.[object.diagramLanguage || state.deck.language] || DIAGRAMS[object.diagramId].svg?.en;
          if (currentSvg) hashText(currentSvg).then((hash) => {
            const stale = hash !== object.diagramHash;
            if (stale !== Boolean(object.diagramStale)) {
              object.diagramStale = stale;
              scheduleChecker();
            }
          });
        }
        if (object.diagramStale) issues.push({ severity: 'warning', text: `Slide ${index + 1} contains a linked diagram with a newer source revision.` });
      });
    });
    el('slides-issue-count').textContent = String(issues.length);
    const results = el('slides-checker-results');
    results.innerHTML = issues.length ? `<ul class="slides-check-list">${issues.map((issue) => `<li class="slides-check-item" data-severity="${issue.severity}"><i data-lucide="${issue.severity === 'error' ? 'circle-x' : 'triangle-alert'}" aria-hidden="true"></i><span>${escapeHTML(issue.text)}</span></li>`).join('')}</ul>` : '<p class="slides-check-item"><i data-lucide="circle-check" aria-hidden="true"></i><span>No presentation issues found.</span></p>';
    window.lucide?.createIcons?.({ nodes: [results] });
    return issues;
  }

  function scheduleChecker() { clearTimeout(state.checkerTimer); state.checkerTimer = setTimeout(validateDeck, 450); }

  async function workspaceSession() {
    if (state.workspaceToken) return state.workspaceToken;
    const response = await fetch(RUNTIME.api('workspace/session'), { credentials: 'same-origin' });
    if (!response.ok) throw new Error('The local workspace host is unavailable.');
    const payload = await response.json(); state.workspaceToken = payload.token; return state.workspaceToken;
  }

  async function saveLocal({ immediate = false } = {}) {
    if (!state.deck) return;
    captureCurrentSlide({ persist: false, check: false });
    el('slides-save-status').textContent = 'Saving locally…';
    try {
      const token = await workspaceSession();
      const exists = Boolean(state.localRevision);
      const response = await fetch(RUNTIME.api(`workspace/presentations${exists ? `/${encodeURIComponent(state.deck.id)}` : ''}`), {
        method: exists ? 'PUT' : 'POST', credentials: 'same-origin', headers: { 'Content-Type': 'application/json', 'X-PetaKerja-Workspace-Token': token },
        body: JSON.stringify(exists ? { document: state.deck, revision: state.localRevision } : { document: state.deck }),
      });
      const payload = await response.json();
      if (response.status === 409) { state.localRevision = payload.revision; throw new Error('A newer local revision exists. Reload it or save a copy.'); }
      if (!response.ok) throw new Error(payload.error?.message || 'Local save failed.');
      state.localRevision = payload.revision; el('slides-save-status').textContent = 'Saved locally'; announce('Presentation saved to the local workspace.');
      if (!immediate) syncCloud({ silent: true });
      if (location.hash !== `#slides/${state.deck.id}`) history.replaceState(null, '', `#slides/${state.deck.id}`);
    } catch (error) { el('slides-save-status').textContent = error.message; }
  }

  function scheduleSave() { clearTimeout(state.saveTimer); el('slides-save-status').textContent = 'Unsaved changes'; state.saveTimer = setTimeout(() => saveLocal(), 1200); }

  async function saveAsCopy() {
    if (!state.deck) return;
    captureCurrentSlide({ persist: false, check: false });
    const copy = structuredClone(state.deck);
    copy.id = uid('deck');
    copy.title = `${copy.title} ${ui('copy', 'salinan')}`;
    copy.createdAt = nowISO();
    copy.updatedAt = copy.createdAt;
    copy.slides = copy.slides.map((slide) => ({ ...slide, id: uid('slide') }));
    state.deck = copy;
    state.currentSlideId = copy.slides[0]?.id || null;
    state.localRevision = null;
    el('slides-title').value = copy.title;
    await loadSlide(state.currentSlideId, { savePrevious: false });
    await saveLocal({ immediate: true });
    announce(ui('A separate presentation copy was saved.', 'Salinan pembentangan yang berasingan telah disimpan.'));
  }

  async function loadLocal(deckId) {
    try {
      const response = await fetch(RUNTIME.api(`workspace/presentations/${encodeURIComponent(deckId)}`), { credentials: 'same-origin' });
      if (!response.ok) return false;
      const payload = await response.json(); state.deck = payload.document; state.localRevision = payload.revision; return true;
    } catch (_error) { return false; }
  }

  async function loadMostRecentLocal() {
    try {
      const response = await fetch(RUNTIME.api('workspace/presentations'), { credentials: 'same-origin' });
      if (!response.ok) return false;
      const payload = await response.json();
      const latest = payload.presentations?.[0];
      return latest?.id ? loadLocal(latest.id) : false;
    } catch (_error) { return false; }
  }

  async function loadCloud(deckId = '') {
    if (!RUNTIME.integrated) return false;
    try {
      const listResponse = await fetch('/api/architecture-explorer/presentations', { credentials: 'include' });
      if (!listResponse.ok) return false;
      const list = await listResponse.json();
      const candidate = deckId
        ? list.presentations?.find((item) => item.document_id === deckId || item.id === deckId)
        : list.presentations?.[0];
      if (!candidate) return false;
      const response = await fetch(`/api/architecture-explorer/presentations/${encodeURIComponent(candidate.id)}`, { credentials: 'include' });
      if (!response.ok) return false;
      const payload = await response.json();
      state.deck = payload.presentation.document;
      state.localRevision = null;
      const map = readSyncMap();
      map[state.deck.id] = { cloudId: payload.presentation.id, revision: payload.presentation.revision, updatedAt: payload.presentation.updated_at };
      writeSyncMap(map);
      return true;
    } catch (_error) { return false; }
  }

  async function syncCloud({ silent = false } = {}) {
    if (!RUNTIME.integrated || !state.deck) { if (!silent) announce('Cloud sync is available through the integrated PetaKerja mini-app.'); return; }
    captureCurrentSlide({ persist: false, check: false }); el('slides-save-status').textContent = 'Syncing...';
    const syncMap = readSyncMap(); const existing = syncMap[state.deck.id];
    try {
      const response = await fetch(`/api/architecture-explorer/presentations${existing ? `/${existing.cloudId}` : ''}`, {
        method: existing ? 'PUT' : 'POST', credentials: 'include', headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(existing ? { title: state.deck.title, document: state.deck, revision: existing.revision } : { title: state.deck.title, document: state.deck }),
      });
      const payload = await response.json().catch(() => ({}));
      if (response.status === 401) { el('slides-save-status').textContent = 'Saved locally · sign in to sync'; return; }
      if (response.status === 409) {
        const conflict = existing || (payload.presentation ? { cloudId: payload.presentation.id, revision: payload.presentation.revision } : null);
        await resolveCloudConflict(conflict, payload); return;
      }
      if (!response.ok) throw new Error(payload.error || 'Cloud sync failed.');
      syncMap[state.deck.id] = { cloudId: payload.presentation.id, revision: payload.presentation.revision, updatedAt: payload.presentation.updated_at }; writeSyncMap(syncMap);
      const failedAssets = await syncCloudAssets(payload.presentation.id);
      await removeQueued(state.deck.id);
      el('slides-save-status').textContent = failedAssets ? `Synced; ${failedAssets} asset(s) pending` : 'Saved locally and synced';
      if (!silent) announce(failedAssets ? 'The presentation synced, but some assets could not be uploaded.' : 'Presentation synced privately to PetaKerja.');
    } catch (error) { await queueOffline({ deckId: state.deck.id, document: state.deck, existing }); el('slides-save-status').textContent = 'Saved locally · cloud sync queued'; if (!silent) announce(error.message); }
  }

  async function assetBlob(asset) {
    if (!asset?.data) return null;
    if (String(asset.data).startsWith('data:')) return (await fetch(asset.data)).blob();
    return new Blob([asset.data], { type: asset.mimeType || 'application/octet-stream' });
  }

  async function syncCloudAssets(cloudId) {
    let failed = 0;
    for (const [assetId, asset] of Object.entries(state.deck.assets || {})) {
      try {
        const blob = await assetBlob(asset);
        if (!blob) continue;
        const response = await fetch(`/api/architecture-explorer/presentations/${encodeURIComponent(cloudId)}/assets/${encodeURIComponent(assetId)}`, {
          method: 'PUT',
          credentials: 'include',
          headers: { 'Content-Type': asset.mimeType || blob.type || 'application/octet-stream' },
          body: blob,
        });
        if (!response.ok) failed += 1;
      } catch (_error) { failed += 1; }
    }
    return failed;
  }

  function readSyncMap() { try { return JSON.parse(localStorage.getItem('petakerja-slides-cloud-map:v1') || '{}'); } catch (_error) { return {}; } }
  function writeSyncMap(value) { localStorage.setItem('petakerja-slides-cloud-map:v1', JSON.stringify(value)); }

  async function resolveCloudConflict(existing, payload) {
    const cloud = payload.presentation;
    const choice = prompt('A newer cloud revision exists. Type LOCAL to overwrite it as a new copy, CLOUD to load it, or COPY to keep both.', 'COPY')?.toUpperCase();
    if (choice === 'CLOUD' && cloud?.document) {
      state.deck = cloud.document; state.localRevision = null; await loadSlide(state.deck.slides[0].id, { savePrevious: false }); await saveLocal({ immediate: true });
    } else if (choice === 'LOCAL' || choice === 'COPY') {
      const map = readSyncMap(); delete map[state.deck.id]; writeSyncMap(map);
      if (choice === 'COPY') { state.deck.id = uid('deck'); state.deck.title += ' copy'; state.localRevision = null; }
      await saveLocal({ immediate: true }); await syncCloud({ silent: false });
    } else if (existing && cloud?.revision) { existing.revision = cloud.revision; }
  }

  function openQueue() {
    return new Promise((resolve, reject) => {
      const request = indexedDB.open('petakerja-slides-studio', 1);
      request.onupgradeneeded = () => { if (!request.result.objectStoreNames.contains('cloudQueue')) request.result.createObjectStore('cloudQueue', { keyPath: 'id' }); };
      request.onsuccess = () => resolve(request.result); request.onerror = () => reject(request.error);
    });
  }

  async function queueOffline(operation) {
    try { const db = await openQueue(); const tx = db.transaction('cloudQueue', 'readwrite'); tx.objectStore('cloudQueue').put({ id: operation.deckId, ...operation, queuedAt: nowISO() }); await new Promise((resolve) => { tx.oncomplete = resolve; }); db.close(); } catch (_error) { /* Local workspace save remains authoritative. */ }
  }

  async function removeQueued(deckId) {
    try { const db = await openQueue(); const tx = db.transaction('cloudQueue', 'readwrite'); tx.objectStore('cloudQueue').delete(deckId); await new Promise((resolve) => { tx.oncomplete = resolve; }); db.close(); } catch (_error) { /* Queue cleanup is best effort. */ }
  }

  async function renderSlideToDataURL(slide, multiplier = 1) {
    const element = document.createElement('canvas');
    const canvas = new Fabric.StaticCanvas(element, { width: 1600, height: 900, enableRetinaScaling: false });
    await loadCanvasJSON(canvas, slide.canvasJson || emptyCanvasJSON());
    const data = canvas.toDataURL({ format: 'png', multiplier, enableRetinaScaling: false }); canvas.dispose(); return data;
  }

  async function exportJSON() { captureCurrentSlide({ persist: false, check: false }); download(new Blob([JSON.stringify(state.deck, null, 2)], { type: 'application/json' }), `${safeName(state.deck.title)}.slides.json`); }
  async function exportCurrentPNG() { captureCurrentSlide(); const data = await renderSlideToDataURL(currentSlide(), 2); download(await (await fetch(data)).blob(), `${safeName(currentSlide().name)}.png`); }
  async function exportPNGZip() {
    captureCurrentSlide(); const zip = new JSZip();
    for (let index = 0; index < state.deck.slides.length; index += 1) { const data = await renderSlideToDataURL(state.deck.slides[index], 2); zip.file(`${String(index + 1).padStart(2, '0')}-${safeName(state.deck.slides[index].name)}.png`, data.split(',')[1], { base64: true }); }
    download(await zip.generateAsync({ type: 'blob' }), `${safeName(state.deck.title)}-slides.zip`);
  }

  async function exportPPTX() {
    captureCurrentSlide();
    const pptx = new pptxgen(); pptx.layout = 'LAYOUT_WIDE'; pptx.author = 'PetaKerja Slides Studio'; pptx.subject = state.deck.title; pptx.title = state.deck.title; pptx.company = 'Universiti Kebangsaan Malaysia'; pptx.lang = state.deck.language === 'ms' ? 'ms-MY' : 'en-MY';
    const xScale = 13.333 / 1600; const yScale = 7.5 / 900;
    for (const source of state.deck.slides) {
      const slide = pptx.addSlide(); const background = source.canvasJson?.background || '#ffffff'; slide.background = { color: String(background).replace('#', '') };
      for (const object of source.canvasJson?.objects || []) {
        const x = Number(object.left || 0) * xScale; const y = Number(object.top || 0) * yScale; const w = Number(object.width || 1) * Number(object.scaleX || 1) * xScale; const h = Number(object.height || 1) * Number(object.scaleY || 1) * yScale;
        if (/text|i-text|textbox/.test(object.type)) slide.addText(String(object.text || ''), { x, y, w, h: Math.max(h, 0.25), fontFace: object.fontFamily || 'Aptos', fontSize: Math.max(8, Number(object.fontSize || 24) * 0.75), bold: Number(object.fontWeight) >= 600 || object.fontWeight === 'bold', color: String(object.fill || '#17212b').replace('#', ''), rotate: Number(object.angle || 0), margin: 0, breakLine: false, valign: 'mid', fit: 'shrink' });
        else if (object.elementType === 'diagram' && object.sourceSvg) slide.addImage({ data: svgData(resolveLightDarkCSS(object.sourceSvg, /^#(?:0b|10|11|12|13|14|15)/i.test(String(background)))), x, y, w, h, altText: object.altText || object.caption || 'PetaKerja diagram' });
        else if (object.type === 'image' && object.src) slide.addImage({ data: object.src, x, y, w, h, altText: object.altText || object.caption || 'Image' });
        else if (object.type === 'rect') slide.addShape(pptx.ShapeType.rect, { x, y, w, h, rotate: Number(object.angle || 0), fill: { color: String(object.fill || '#ffffff').replace('#', ''), transparency: Math.round((1 - Number(object.opacity ?? 1)) * 100) }, line: { color: String(object.stroke || '#cbd2d8').replace('#', ''), width: Number(object.strokeWidth || 1) } });
        else if (object.type === 'ellipse') slide.addShape(pptx.ShapeType.ellipse, { x, y, w, h, rotate: Number(object.angle || 0), fill: { color: String(object.fill || '#ffffff').replace('#', '') }, line: { color: String(object.stroke || '#cbd2d8').replace('#', ''), width: Number(object.strokeWidth || 1) } });
      }
      if (source.speakerNotes) slide.addNotes(source.speakerNotes);
    }
    await pptx.writeFile({ fileName: `${safeName(state.deck.title)}.pptx` });
  }

  async function printDeck() {
    captureCurrentSlide(); const root = document.createElement('div'); root.className = 'slides-print-root';
    for (const slide of state.deck.slides.filter((item) => !item.hidden)) { const page = document.createElement('section'); page.className = 'slides-print-page'; const image = document.createElement('img'); image.src = await renderSlideToDataURL(slide, 2); image.alt = slide.name; page.append(image); root.append(page); }
    document.body.append(root); window.print(); setTimeout(() => root.remove(), 1000);
  }

  async function presentDeck() {
    captureCurrentSlide(); const visible = state.deck.slides.filter((slide) => !slide.hidden); if (!visible.length) return;
    let index = Math.max(0, visible.findIndex((slide) => slide.id === state.currentSlideId)); let started = Date.now();
    const overlay = document.createElement('div'); overlay.className = 'slides-presentation'; overlay.tabIndex = 0;
    const stage = document.createElement('div'); stage.className = 'slides-presentation__slide';
    const image = document.createElement('img'); image.alt = ''; stage.append(image);
    const notes = document.createElement('aside'); notes.className = 'slides-presentation__notes';
    const controls = document.createElement('div'); controls.className = 'slides-presentation__controls';
    const previous = document.createElement('button'); previous.textContent = 'Previous'; const status = document.createElement('span'); const next = document.createElement('button'); next.textContent = 'Next'; const close = document.createElement('button'); close.textContent = 'Close'; controls.append(previous, status, next, close); overlay.append(stage, notes, controls); document.body.append(overlay);
    const render = async () => { image.src = await renderSlideToDataURL(visible[index], 1.25); notes.textContent = visible[index].speakerNotes || 'No speaker notes.'; status.textContent = `${index + 1}/${visible.length} · ${formatTime(Math.floor((Date.now() - started) / 1000))}`; };
    const move = (amount) => { index = Math.max(0, Math.min(visible.length - 1, index + amount)); render(); };
    previous.addEventListener('click', () => move(-1)); next.addEventListener('click', () => move(1)); close.addEventListener('click', () => overlay.remove());
    overlay.addEventListener('keydown', (event) => { if (['ArrowRight', 'PageDown', ' '].includes(event.key)) { event.preventDefault(); move(1); } if (['ArrowLeft', 'PageUp'].includes(event.key)) { event.preventDefault(); move(-1); } if (event.key === 'Escape') overlay.remove(); });
    const timer = setInterval(() => { if (!overlay.isConnected) clearInterval(timer); else status.textContent = `${index + 1}/${visible.length} · ${formatTime(Math.floor((Date.now() - started) / 1000))}`; }, 1000);
    await render(); overlay.focus(); overlay.requestFullscreen?.().catch(() => {});
  }

  async function importDeck(file) {
    try {
      const document = JSON.parse(await file.text());
      if (document.schemaVersion !== 1 || !Array.isArray(document.slides)) throw new Error('Unsupported Slides Studio document.');
      captureCurrentSlide(); state.deck = document; state.deck.id = uid('deck'); state.deck.title = `${state.deck.title} copy`; state.localRevision = null; await loadSlide(state.deck.slides[0].id, { savePrevious: false }); scheduleSave(); renderDiagramLibrary();
    } catch (error) { announce(error.message); }
  }

  function bindCanvas() {
    state.canvas = new Fabric.Canvas('slides-canvas', { width: 1600, height: 900, preserveObjectStacking: true, selection: true, backgroundColor: theme().background });
    Fabric.Object.prototype.transparentCorners = false; Fabric.Object.prototype.cornerColor = '#0b6aa2'; Fabric.Object.prototype.cornerStyle = 'circle'; Fabric.Object.prototype.borderColor = '#0b6aa2';
    ['object:modified', 'object:added', 'object:removed', 'text:changed'].forEach((eventName) => state.canvas.on(eventName, () => { if (!state.suppressHistory) captureCurrentSlide({ history: eventName !== 'text:changed' }); }));
    state.canvas.on('selection:created', renderProperties); state.canvas.on('selection:updated', renderProperties); state.canvas.on('selection:cleared', renderProperties);
  }

  function bindUI() {
    el('slides-back').addEventListener('click', () => { location.hash = state.previousHash || '#explorer'; });
    el('slides-add').addEventListener('click', () => addSlide());
    el('slides-preset').addEventListener('click', async () => { if (!confirm('Create a new 12-slide UKM FYP deck? Unsaved changes remain in the current local deck.')) return; captureCurrentSlide(); state.deck = createDeck(); state.localRevision = null; el('slides-title').value = state.deck.title; await loadSlide(state.deck.slides[0].id, { savePrevious: false }); renderDiagramLibrary(); scheduleSave(); });
    el('slides-title').addEventListener('input', (event) => { state.deck.title = event.target.value; scheduleSave(); });
    el('slides-undo').addEventListener('click', () => restoreHistory(state.historyIndex - 1)); el('slides-redo').addEventListener('click', () => restoreHistory(state.historyIndex + 1));
    el('slides-save').addEventListener('click', () => saveLocal({ immediate: true }));
    el('slides-save-copy').addEventListener('click', saveAsCopy);
    el('slides-cloud').addEventListener('click', () => syncCloud({ silent: false })); el('slides-present').addEventListener('click', presentDeck);
    el('slides-export').addEventListener('click', () => { el('slides-export-options').hidden = !el('slides-export-options').hidden; });
    el('slides-export-options').addEventListener('click', (event) => { const type = event.target.closest('[data-slides-export]')?.dataset.slidesExport; if (!type) return; el('slides-export-options').hidden = true; ({ pptx: exportPPTX, json: exportJSON, png: exportCurrentPNG, zip: exportPNGZip, print: printDeck })[type]?.(); });
    shell.querySelectorAll('[data-slides-panel]').forEach((button) => button.addEventListener('click', () => { shell.querySelectorAll('[data-slides-panel]').forEach((item) => item.setAttribute('aria-selected', String(item === button))); shell.querySelectorAll('[data-slides-tool-panel]').forEach((panel) => { panel.hidden = panel.dataset.slidesToolPanel !== button.dataset.slidesPanel; }); if (button.dataset.slidesPanel === 'diagrams') renderDiagramLibrary(); if (button.dataset.slidesPanel === 'properties') renderProperties(); }));
    shell.querySelectorAll('[data-add-element]').forEach((button) => button.addEventListener('click', () => { const kind = button.dataset.addElement; if (kind === 'heading' || kind === 'body') addText(kind); else if (kind === 'image') el('slides-image-input').click(); else addShape(kind); }));
    el('slides-image-input').addEventListener('change', (event) => { addImageFile(event.target.files?.[0]); event.target.value = ''; });
    shell.querySelectorAll('[data-layer-action]').forEach((button) => button.addEventListener('click', async () => { const object = state.canvas.getActiveObject(); if (!object) return; const action = button.dataset.layerAction; if (action === 'front') state.canvas.bringObjectForward(object); if (action === 'back') state.canvas.sendObjectBackwards(object); if (action === 'delete') state.canvas.remove(object); if (action === 'duplicate') { const copy = await object.clone(customProps); copy.set({ left: object.left + 28, top: object.top + 28, elementId: uid('element') }); addAndSelect(copy); } state.canvas.requestRenderAll(); captureCurrentSlide({ history: true }); }));
    ['slides-diagram-search', 'slides-diagram-family', 'slides-diagram-audience', 'slides-diagram-variant'].forEach((id) => el(id).addEventListener(id.includes('search') ? 'input' : 'change', renderDiagramLibrary));
    el('slides-insert-current-diagram').addEventListener('click', () => { const id = document.querySelector('.nav-item.is-active[data-diagram]')?.dataset.diagram; if (id && DIAGRAMS[id]) insertDiagram(id); else announce('Open a registered Explorer diagram first.'); });
    el('slides-speaker-notes').addEventListener('input', (event) => { currentSlide().speakerNotes = event.target.value; scheduleSave(); scheduleChecker(); });
    el('slides-duration').addEventListener('input', (event) => { currentSlide().durationSeconds = Math.max(5, Number(event.target.value || 45)); updateTotalTime(); scheduleSave(); scheduleChecker(); });
    shell.querySelectorAll('[data-slides-bottom]').forEach((button) => button.addEventListener('click', () => { shell.querySelectorAll('[data-slides-bottom]').forEach((item) => item.setAttribute('aria-pressed', String(item === button))); el('slides-notes-panel').hidden = button.dataset.slidesBottom !== 'notes'; el('slides-checker-panel').hidden = button.dataset.slidesBottom !== 'checker'; if (button.dataset.slidesBottom === 'checker') validateDeck(); }));
    shell.querySelectorAll('[data-slides-mobile]').forEach((button) => button.addEventListener('click', () => { state.mobilePanel = button.dataset.slidesMobile; editor.dataset.mobilePanel = state.mobilePanel; shell.querySelectorAll('[data-slides-mobile]').forEach((item) => item.setAttribute('aria-selected', String(item === button))); }));
    el('slides-zoom-out').addEventListener('click', () => setStageZoom(-0.1)); el('slides-zoom-in').addEventListener('click', () => setStageZoom(0.1));
    shell.querySelector('.slides-stage').addEventListener('wheel', handleSlidesStageWheel, { passive: false });
    el('slides-import-input').addEventListener('change', (event) => { importDeck(event.target.files?.[0]); event.target.value = ''; });
    window.addEventListener('keydown', (event) => {
      if (!state.active || ['INPUT', 'TEXTAREA', 'SELECT'].includes(event.target.tagName) || event.target.isContentEditable) return;
      const control = event.ctrlKey || event.metaKey;
      if (control && event.key.toLowerCase() === 'z') { event.preventDefault(); restoreHistory(state.historyIndex + (event.shiftKey ? 1 : -1)); }
      else if (control && event.key.toLowerCase() === 'y') { event.preventDefault(); restoreHistory(state.historyIndex + 1); }
      else if (control && event.key.toLowerCase() === 's') { event.preventDefault(); saveLocal({ immediate: true }); }
      else if (event.key === 'Delete' || event.key === 'Backspace') { const object = state.canvas.getActiveObject(); if (object) { state.canvas.remove(object); state.canvas.requestRenderAll(); captureCurrentSlide({ history: true }); } }
      else if (['ArrowLeft', 'ArrowRight', 'ArrowUp', 'ArrowDown'].includes(event.key)) { const object = state.canvas.getActiveObject(); if (!object) return; event.preventDefault(); const step = event.shiftKey ? 10 : 1; if (event.key === 'ArrowLeft') object.left -= step; if (event.key === 'ArrowRight') object.left += step; if (event.key === 'ArrowUp') object.top -= step; if (event.key === 'ArrowDown') object.top += step; object.setCoords(); state.canvas.requestRenderAll(); captureCurrentSlide(); }
    });
    window.addEventListener('beforeunload', () => captureCurrentSlide({ persist: false, check: false }));
    window.addEventListener('resize', fitCanvasStage);
  }

  function normalizeSlideWheelDelta(event, stage) {
    const multiplier = event.deltaMode === 1 ? 16 : event.deltaMode === 2 ? Math.max(stage.clientHeight, 1) : 1;
    return event.deltaY * multiplier;
  }

  function resetSlideWheelGesture() {
    state.slideWheelDelta = 0;
    state.slideWheelDirection = 0;
    clearTimeout(state.slideWheelResetTimer);
    state.slideWheelResetTimer = 0;
  }

  function isSlidesStageWheelNavigation(event, stage) {
    if (!state.active || !state.deck || state.deck.slides.length < 2 || event.ctrlKey || event.metaKey) return false;
    if (window.matchMedia?.('(max-width: 980px)').matches) return false;
    if (Math.abs(event.deltaY) <= Math.abs(event.deltaX) || event.deltaY === 0) return false;
    const target = event.target instanceof Element ? event.target : null;
    if (!target || !stage.contains(target)) return false;
    return !target.closest('#slides-canvas-wrap, .slides-zoom, button, input, textarea, select, [contenteditable="true"], [role="button"]');
  }

  function handleSlidesStageWheel(event) {
    const stage = event.currentTarget;
    if (!isSlidesStageWheelNavigation(event, stage)) return;
    const delta = normalizeSlideWheelDelta(event, stage);
    if (!delta) return;
    event.preventDefault();

    const now = performance.now();
    const direction = Math.sign(delta);
    if (state.slideWheelDirection && state.slideWheelDirection !== direction) state.slideWheelDelta = 0;
    state.slideWheelDirection = direction;
    clearTimeout(state.slideWheelResetTimer);
    state.slideWheelResetTimer = setTimeout(resetSlideWheelGesture, SLIDE_WHEEL_IDLE_RESET_MS);

    if (now < state.slideWheelLockedUntil) {
      state.slideWheelDelta = 0;
      return;
    }

    state.slideWheelDelta += delta;
    if (Math.abs(state.slideWheelDelta) < SLIDE_WHEEL_THRESHOLD) return;

    const currentIndex = state.deck.slides.findIndex((slide) => slide.id === state.currentSlideId);
    const nextIndex = Math.max(0, Math.min(state.deck.slides.length - 1, currentIndex + direction));
    state.slideWheelLockedUntil = now + SLIDE_WHEEL_COOLDOWN_MS;
    resetSlideWheelGesture();
    if (nextIndex === currentIndex) return;
    loadSlide(state.deck.slides[nextIndex].id);
  }

  function setStageZoom(delta) {
    const current = Number(el('slides-canvas-wrap').dataset.zoom || 1); const next = Math.max(0.5, Math.min(1.5, current + delta)); el('slides-canvas-wrap').dataset.zoom = String(next); el('slides-canvas-wrap').style.transform = `scale(${next})`; el('slides-zoom-value').textContent = `${Math.round(next * 100)}%`;
  }

  function fitCanvasStage() { el('slides-canvas-wrap').style.transform = ''; el('slides-canvas-wrap').dataset.zoom = '1'; el('slides-zoom-value').textContent = 'Fit'; }

  async function enterSlides() {
    if (!state.active) {
      state.active = true; document.body.classList.add('is-slides-mode'); shell.hidden = false;
      if (!state.canvas) { bindCanvas(); bindUI(); renderLayouts(); populateDiagramFamilies(); }
      const routeId = location.hash.match(/^#slides\/([^/?]+)/)?.[1];
      let loaded = Boolean(state.deck);
      if (routeId && (!state.deck || state.deck.id !== decodeURIComponent(routeId))) {
        const requested = decodeURIComponent(routeId);
        loaded = await loadLocal(requested) || await loadCloud(requested);
      }
      if (!routeId && !state.deck) loaded = await loadMostRecentLocal() || await loadCloud();
      if (!loaded || !state.deck) state.deck = createDeck();
      translateSlidesUI();
      el('slides-title').value = state.deck.title; await loadSlide(state.deck.slides[0].id, { savePrevious: false }); renderDiagramLibrary(); validateDeck(); fitCanvasStage();
      window.lucide?.createIcons?.({ nodes: [shell] });
    }
  }

  function leaveSlides() {
    if (!state.active) return; captureCurrentSlide({ persist: false, check: false }); state.active = false; resetSlideWheelGesture(); state.slideWheelLockedUntil = 0; document.body.classList.remove('is-slides-mode'); shell.hidden = true; clearTimeout(state.saveTimer); saveLocal({ immediate: true });
  }

  function populateDiagramFamilies() {
    const select = el('slides-diagram-family'); const families = [...new Set(Object.keys(DIAGRAMS).map((id) => diagramFamily(id, diagramMeta(id))))].sort();
    families.forEach((family) => { const option = document.createElement('option'); option.value = family; option.textContent = family; select.append(option); });
  }

  function route() {
    if (location.hash === '#slides' || location.hash.startsWith('#slides/')) enterSlides(); else leaveSlides();
  }

  el('slides-link')?.addEventListener('click', () => { if (!location.hash.startsWith('#slides')) state.previousHash = location.hash && !location.hash.startsWith('#learn') ? location.hash : '#explorer'; });
  window.addEventListener('petakerja:languagechange', () => {
    translateSlidesUI();
    if (state.canvas) renderLayouts();
    if (state.active && state.deck) { renderDiagramLibrary(); validateDeck(); renderProperties(); }
  });
  window.addEventListener('online', () => { if (state.active) syncCloud({ silent: true }); });
  window.addEventListener('hashchange', route);
  translateSlidesUI();
  route();
}());
