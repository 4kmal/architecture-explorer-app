(function () {
  'use strict';

  const data = window.PETAKERJA_ARCHITECTURE;
  const assets = window.PETAKERJA_DIAGRAM_ASSETS || {};
  const fypReportTables = window.PETAKERJA_FYP_REPORT_TABLES || { pages: {} };
  const translations = window.PETAKERJA_TRANSLATIONS || {};
  const editorAPI = window.PETAKERJA_EDITOR;
  const agentAPI = window.PETAKERJA_AGENT;
  const codeSnippetHighlighter = window.PETAKERJA_CODE_SNIPPET_HIGHLIGHTER;
  const codeSnippetClipboard = window.PETAKERJA_CODE_SNIPPET_CLIPBOARD;
  const runtimeCapabilities = window.PETAKERJA_EXPLORER_RUNTIME?.capabilities || {};
  const localAPI = (path) => window.PETAKERJA_EXPLORER_RUNTIME?.api(path) || `/api/${String(path || '').replace(/^\/+/, '')}`;
  if (!data) throw new Error('PETAKERJA_ARCHITECTURE is not loaded.');
  if (!editorAPI) throw new Error('PETAKERJA_EDITOR is not loaded.');
  if (!codeSnippetHighlighter) throw new Error('PETAKERJA_CODE_SNIPPET_HIGHLIGHTER is not loaded.');
  if (!codeSnippetClipboard) throw new Error('PETAKERJA_CODE_SNIPPET_CLIPBOARD is not loaded.');

  function isCanonicalEditable(id) {
    return Array.isArray(editorAPI.EDITABLE_DIAGRAMS) && editorAPI.EDITABLE_DIAGRAMS.includes(id);
  }

  const DIAGRAM_ICONS = Object.freeze({
    overview: 'panels-top-left',
    usecase: 'users-round',
    activity: 'list-checks',
    sequence: 'search',
    'auth-sequence': 'log-in',
    'google-oauth-sequence': 'log-in',
    'user-google-sign-in-flowchart': 'log-in',
    'user-search-jobs-flowchart': 'search',
    'user-explore-3d-map-flowchart': 'map',
    'user-sign-out-flowchart': 'log-out',
    'admin-access-dashboard-flowchart': 'layout-dashboard',
    'admin-monitor-activity-flowchart': 'activity',
    'admin-manage-users-flowchart': 'users-round',
    'admin-manage-ai-configuration-flowchart': 'bot',
    'admin-sign-out-flowchart': 'log-out',
    'user-explore-3d-map-sequence': 'map',
    'user-sign-out-sequence': 'log-out',
    'admin-access-dashboard-sequence': 'layout-dashboard',
    'admin-monitor-activity-sequence': 'activity',
    'admin-manage-users-sequence': 'users-round',
    'admin-manage-ai-configuration-sequence': 'bot',
    'admin-sign-out-sequence': 'log-out',
    domain: 'boxes',
    implementation: 'network',
    'architecture-visual-stack': 'layers-2',
    architecture: 'layers-2',
    modules: 'folder-tree',
    'modules-layered-stack': 'layers-2',
    erd: 'database',
    'data-flow': 'waypoints',
    'map-routing-responsibility-stack': 'route',
    'nominatim-valhalla-workflow': 'waypoints',
    'nominatim-maplibre-workflow': 'map',
    'valhalla-maplibre-workflow': 'route',
    'geo-server-communication-workflow': 'network',
    'etl-pipeline': 'workflow',
    'daily-index-workflow': 'database',
    'live-search-workflow': 'search',
    'deployment-infrastructure': 'network',
    supabase: 'table-properties',
    jobops: 'briefcase-business',
    blog: 'newspaper',
    community: 'users-round',
    'v2-geo-usecase': 'users-round',
    'v2-geo-map-flowchart': 'map',
    'v2-geo-route-sequence': 'map',
    'v2-geo-travel-analysis-sequence': 'waypoints',
    'v2-geo-job-route-sequence': 'briefcase-business',
    'v2-geo-domain': 'boxes',
    'v2-geo-implementation': 'network',
    'v2-geo-architecture': 'layers-2',
    'v2-geo-modules': 'folder-tree',
    'v2-geo-data-flow': 'waypoints',
    'v2-geo-erd': 'database',
    'v2-geo-routing-stack': 'layers-2',
    'v2-geo-supabase': 'table-properties',
    'code-geo-routing': 'map',
    'code-job-scraping': 'briefcase-business',
    'code-poi-search': 'search',
    'code-poi-clustering': 'map',
    'code-live-job-search': 'search',
    'code-job-location-resolution': 'map',
    'fyp-kamus-data': 'table-properties',
    'fyp-use-case-specification': 'list-checks',
  });

  function storedLanguage() {
    try {
      const stored = localStorage.getItem('petakerja-explorer-language');
      return stored === 'ms' ? 'ms' : 'en';
    } catch (_error) { return 'en'; }
  }

  function storeLanguage(language) {
    try { localStorage.setItem('petakerja-explorer-language', language); }
    catch (_error) { /* Some file:// browser policies disable storage. */ }
  }

  function storedThemePreference() {
    try {
      const stored = localStorage.getItem('petakerja-explorer-theme');
      return ['light', 'dark', 'system'].includes(stored) ? stored : 'system';
    } catch (_error) { return 'system'; }
  }

  function effectiveTheme(preference) {
    if (preference === 'light' || preference === 'dark') return preference;
    return window.matchMedia?.('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
  }

  function storeThemePreference(preference) {
    try { localStorage.setItem('petakerja-explorer-theme', preference); }
    catch (_error) { /* Some file:// browser policies disable storage. */ }
  }

  function storedSequenceFolders() {
    try {
      const value = JSON.parse(localStorage.getItem('petakerja-explorer-sequence-folders') || '{}');
      return { user: value.user !== false, administrator: value.administrator === true };
    } catch (_error) { return { user: true, administrator: false }; }
  }

  function storeSequenceFolders(value) {
    try { localStorage.setItem('petakerja-explorer-sequence-folders', JSON.stringify(value)); }
    catch (_error) { /* Some file:// browser policies disable storage. */ }
  }

  function storedFlowchartFolders() {
    try {
      const value = JSON.parse(localStorage.getItem('petakerja-explorer-flowchart-folders') || '{}');
      return { user: value.user !== false, administrator: value.administrator === true };
    } catch (_error) { return { user: true, administrator: false }; }
  }

  function storeFlowchartFolders(value) {
    try { localStorage.setItem('petakerja-explorer-flowchart-folders', JSON.stringify(value)); }
    catch (_error) { /* Some file:// browser policies disable storage. */ }
  }

  function storedCodeSnippetFolders() {
    try {
      const value = JSON.parse(localStorage.getItem('petakerja-explorer-code-snippet-folders') || '{}');
      return { Algorithms: value.Algorithms !== false };
    } catch (_error) { return { Algorithms: true }; }
  }

  function storeCodeSnippetFolders(value) {
    try { localStorage.setItem('petakerja-explorer-code-snippet-folders', JSON.stringify(value)); }
    catch (_error) { /* Some file:// browser policies disable storage. */ }
  }

  function storedCodeSnippetLanguage() {
    try { return localStorage.getItem('petakerja-explorer-code-snippet-language') === 'en' ? 'en' : 'ms'; }
    catch (_error) { return 'ms'; }
  }

  function storeCodeSnippetLanguage(value) {
    try { localStorage.setItem('petakerja-explorer-code-snippet-language', value); }
    catch (_error) { /* Some file:// browser policies disable storage. */ }
  }

  function storedReportTableLanguage() {
    try { return localStorage.getItem('petakerja-explorer-report-table-language') === 'en' ? 'en' : 'ms'; }
    catch (_error) { return 'ms'; }
  }

  function storeReportTableLanguage(value) {
    try { localStorage.setItem('petakerja-explorer-report-table-language', value); }
    catch (_error) { /* Some file:// browser policies disable storage. */ }
  }

  function storedDictionaryColumnMode() {
    try { return localStorage.getItem('petakerja-explorer-data-dictionary-column') === 'size' ? 'size' : 'constraints'; }
    catch (_error) { return 'constraints'; }
  }

  function storeDictionaryColumnMode(value) {
    try { localStorage.setItem('petakerja-explorer-data-dictionary-column', value); }
    catch (_error) { /* Some file:// browser policies disable storage. */ }
  }

  function storedDiagramVariantFolders() {
    try {
      const current = localStorage.getItem('petakerja-explorer-diagram-variant-folders');
      const legacy = localStorage.getItem('petakerja-explorer-flowchart-variant-folders');
      const value = JSON.parse(current || legacy || '{}');
      return value && typeof value === 'object' ? value : {};
    } catch (_error) { return {}; }
  }

  function storeDiagramVariantFolders(value) {
    try { localStorage.setItem('petakerja-explorer-diagram-variant-folders', JSON.stringify(value)); }
    catch (_error) { /* Some file:// browser policies disable storage. */ }
  }

  function storedDiagramCollections() {
    try {
      const value = JSON.parse(localStorage.getItem('petakerja-explorer-diagram-collections') || '{}');
      return value && typeof value === 'object' && Object.keys(value).length ? value : { 'v2-georouting': true };
    } catch (_error) { return { 'v2-georouting': true }; }
  }

  function storeDiagramCollections(value) {
    try { localStorage.setItem('petakerja-explorer-diagram-collections', JSON.stringify(value)); }
    catch (_error) { /* Some file:// browser policies disable storage. */ }
  }

  function storedDiagramCollectionGroups() {
    try {
      const value = JSON.parse(localStorage.getItem('petakerja-explorer-diagram-collection-groups') || '{}');
      return value && typeof value === 'object' ? value : {};
    } catch (_error) { return {}; }
  }

  function storeDiagramCollectionGroups(value) {
    try { localStorage.setItem('petakerja-explorer-diagram-collection-groups', JSON.stringify(value)); }
    catch (_error) { /* Some file:// browser policies disable storage. */ }
  }

  function storedDiagramLabelMode() {
    try {
      const current = localStorage.getItem('petakerja-explorer-diagram-label-mode');
      const legacy = localStorage.getItem('petakerja-explorer-sequence-label-mode');
      return (current || legacy) === 'code' ? 'code' : 'simple';
    }
    catch (_error) { return 'simple'; }
  }

  function storeDiagramLabelMode(value) {
    try { localStorage.setItem('petakerja-explorer-diagram-label-mode', value); }
    catch (_error) { /* Some file:// browser policies disable storage. */ }
  }

  const byId = (id) => document.getElementById(id);
  const state = {
    diagramId: 'domain', scopeId: 'core', renderMode: 'actual',
    language: storedLanguage(), themePreference: storedThemePreference(), effectiveTheme: 'light',
    selected: null, hovered: null, selectedComponentKey: null, hoveredComponentKey: null, selectedConnectionId: null,
    uiViewId: 'map', mobilePanel: 'diagram',
    scale: 1, panX: 0, panY: 0, fitMode: true, naturalWidth: 1000, naturalHeight: 700,
    pointer: null, suppressClick: false,
    workspaceMode: 'view', editorAnalysis: null, pendingImport: null, dropDepth: 0,
    runtimeDocuments: new Map(), importedDiagrams: [], runtimeExporting: false, editorDocumentKey: null, agentProviderStatus: null,
    workspaceToken: null, workspaceDiagramIds: new Set(), workspaceLoaded: new Set(), workspaceSessionPromise: null,
    sequenceFolders: storedSequenceFolders(), flowchartFolders: storedFlowchartFolders(), codeSnippetFolders: storedCodeSnippetFolders(), snippetLanguage: storedCodeSnippetLanguage(),
    reportTableLanguage: storedReportTableLanguage(), dictionaryColumnMode: storedDictionaryColumnMode(), reportColumnSelection: null,
    diagramVariantFolders: storedDiagramVariantFolders(), diagramCollections: storedDiagramCollections(),
    diagramCollectionGroups: storedDiagramCollectionGroups(), diagramLabelMode: storedDiagramLabelMode(), diagramLabelModeSwitching: false,
  };

  const DIAGRAM_COLLECTION_GROUPS = Object.freeze({
    'map-routing': Object.freeze([
      { id: 'overview', labelKey: 'ui.collectionRoutingOverview', icon: 'route' },
      { id: 'provider-workflows', labelKey: 'ui.collectionProviderWorkflows', icon: 'waypoints' },
      { id: 'infrastructure', labelKey: 'ui.collectionRoutingInfrastructure', icon: 'network' },
    ]),
    'etl-pipeline': Object.freeze([
      { id: 'overview', labelKey: 'ui.collectionETLOverview', icon: 'workflow' },
      { id: 'job-search-workflows', labelKey: 'ui.collectionJobSearchWorkflows', icon: 'search' },
    ]),
    'v2-georouting': Object.freeze([
      { id: 'use-cases', labelKey: 'ui.collectionUseCases', icon: 'users-round' },
      { id: 'flowcharts', labelKey: 'ui.collectionFlowcharts', icon: 'workflow' },
      { id: 'sequences', labelKey: 'ui.collectionSequences', icon: 'waypoints' },
      { id: 'classes', labelKey: 'ui.collectionClasses', icon: 'boxes' },
      { id: 'architecture-modules', labelKey: 'ui.collectionArchitectureModules', icon: 'layers-2' },
      { id: 'data', labelKey: 'ui.collectionData', icon: 'database' },
    ]),
  });

  const els = {
    skip: byId('skip-link'), subtitle: byId('app-subtitle'), scope: byId('scope-filter'), diagramPicker: byId('diagram-picker'),
    themeSelect: byId('theme-select'), themeLabel: byId('theme-label'), themeValue: byId('theme-value'),
    languageSelect: byId('language-select'), languageLabel: byId('language-label'), languageValue: byId('language-value'),
    search: byId('global-search'), searchLabel: byId('search-label'), searchResults: byId('search-results'), snapshot: byId('snapshot-status'),
    diagramNav: byId('diagram-nav'), navTitle: byId('nav-title'), navDescription: byId('nav-description'),
    diagramTitle: byId('diagram-title'), diagramDescription: byId('diagram-description'), diagramStatus: byId('diagram-status'),
    graph: byId('graph-canvas'), graphViewport: byId('graph-viewport'), empty: byId('graph-empty'), details: byId('details-content'),
    uiView: byId('ui-view-select'), uiImage: byId('ui-image'), uiStage: byId('ui-stage'), uiHotspots: byId('ui-hotspots'), uiCaption: byId('ui-caption'),
    zoomValue: byId('zoom-value'), modeControl: byId('render-mode-control'), actualMode: byId('mode-actual'), mapMode: byId('mode-map'),
    diagramLabelControl: byId('diagram-label-control'), diagramSimple: byId('diagram-label-simple'), diagramCode: byId('diagram-label-code'),
    referenceButton: byId('open-reference'), referenceDialog: byId('reference-dialog'), referenceImage: byId('reference-image'),
    referenceTitle: byId('reference-title'), statusMessage: byId('status-message'),
    workspaceModeControl: byId('workspace-mode-control'), workspaceView: byId('workspace-view'), workspaceEdit: byId('workspace-edit'), workspaceAgent: byId('workspace-agent'),
    importButton: byId('import-diagram'), validateButton: byId('validate-diagram'), workspaceSaveButton: byId('save-workspace-diagram'), saveButton: byId('save-diagram'), fileInput: byId('diagram-file-input'),
    editorSurface: byId('editor-surface'), editorFrame: byId('drawio-editor'), editorLoading: byId('editor-loading'), dropOverlay: byId('diagram-drop-overlay'),
    validationPanel: byId('validation-panel'), validationTitle: byId('validation-title'), validationChangeKind: byId('validation-change-kind'),
    validationSummary: byId('validation-summary'), validationIssues: byId('validation-issues'),
    importDialog: byId('import-dialog'), importTitle: byId('import-title'), importSubtitle: byId('import-subtitle'), importSummary: byId('import-file-summary'),
    importPages: byId('import-pages'), confirmImport: byId('confirm-import'),
    runtimeDialog: byId('runtime-dialog'), runtimeTitle: byId('runtime-title'), runtimeSubtitle: byId('runtime-subtitle'),
    runtimeDescription: byId('runtime-description'), runtimeStepLauncher: byId('runtime-step-launcher'), runtimeStepCommand: byId('runtime-step-command'),
    runtimeCommand: byId('runtime-command'), copyRuntimeCommand: byId('copy-runtime-command'),
    agentPanel: byId('agent-panel'), agentState: byId('agent-state'), agentProvider: byId('agent-provider'), agentProviderStatus: byId('agent-provider-status'),
    agentBaseField: byId('agent-base-field'), agentModelField: byId('agent-model-field'), agentKeyField: byId('agent-key-field'), agentBaseURL: byId('agent-base-url'), agentModel: byId('agent-model'),
    agentAPIKey: byId('agent-api-key'), agentTest: byId('agent-test'), agentPrompt: byId('agent-prompt'), agentPropose: byId('agent-propose'),
    agentRun: byId('agent-run'), agentStop: byId('agent-stop'), agentRevert: byId('agent-revert'), agentPlan: byId('agent-plan-content'), agentLog: byId('agent-log'),
    bridgeStatus: byId('bridge-status'), bridgeConfig: byId('bridge-config'), copyBridgeConfig: byId('copy-bridge-config'),
  };
  let editorController = null;
  let diagramAgent = null;
  let cloudManager = null;
  let pendingEditorThemePreference = null;
  let reportContextMenu = null;
  let reportContextTarget = null;
  const systemThemeQuery = window.matchMedia?.('(prefers-color-scheme: dark)') || null;

  function syncEditorThemePreference(preference, options = {}) {
    if (!editorController) return;
    editorController.setThemePreference(preference).then(() => {
      if (options.announce) els.statusMessage.textContent = t('ui.themeApplied');
    }).catch((error) => {
      els.statusMessage.textContent = `${t('ui.themeReloadFailed')}: ${error.message}`;
    });
  }

  function applyThemePreference(preference, options = {}) {
    const nextPreference = ['light', 'dark', 'system'].includes(preference) ? preference : 'system';
    const nextEffective = effectiveTheme(nextPreference);
    state.themePreference = nextPreference;
    state.effectiveTheme = nextEffective;
    document.documentElement.dataset.themePreference = nextPreference;
    document.documentElement.dataset.theme = nextEffective;
    document.documentElement.style.colorScheme = nextEffective;
    document.querySelector('meta[name="color-scheme"]')?.setAttribute('content', 'light dark');
    if (els.themeSelect) els.themeSelect.value = nextPreference;
    syncHeaderChoiceControls();
    if (options.persist !== false) storeThemePreference(nextPreference);
    if (options.syncEditor !== false && editorController) {
      if (diagramAgent?.running) {
        pendingEditorThemePreference = nextPreference === editorController.themePreference ? null : nextPreference;
        if (options.announce) els.statusMessage.textContent = t('ui.themeApplied');
      } else {
        pendingEditorThemePreference = null;
        syncEditorThemePreference(nextPreference, options);
      }
    } else if (options.announce) {
      els.statusMessage.textContent = t('ui.themeApplied');
    }
  }

  function escapeHTML(value) {
    return String(value ?? '').replace(/[&<>'"]/g, (character) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', "'": '&#39;', '"': '&quot;' }[character]));
  }

  function t(key) {
    if (state.language === 'en') return key.split('.').reduce((value, part) => value && value[part], translations.en) ?? key;
    const ms = {
      'ui.skip': 'Langkau ke rajah', 'ui.subtitle': 'Jejaki UI → kelas → route → jadual bagi kod semasa, model FYP dan modul legacy.',
      'ui.scope': 'Skop sistem', 'ui.search': 'Carian global', 'ui.searchPlaceholder': 'Kelas, route, jadual atau UI…',
      'ui.actual': 'Rajah sebenar', 'ui.map': 'Peta interaktif', 'ui.language': 'Bahasa', 'ui.theme': 'Tema',
      'ui.themeSystem': 'Sistem', 'ui.themeLight': 'Cerah', 'ui.themeDark': 'Gelap', 'ui.themeApplied': 'Tema digunakan',
      'ui.themeReloadFailed': 'Tema Explorer digunakan tetapi editor tidak dapat dimuatkan semula',
      'ui.diagram': 'Rajah', 'ui.uiTab': 'UI', 'ui.detailsTab': 'Butiran',
      'ui.diagrams': 'Rajah', 'ui.chooseView': 'Pilih sudut pandang seni bina.', 'ui.fit': 'Muat', 'ui.zoomOut': 'Kurangkan zoom', 'ui.zoomIn': 'Tambah zoom',
      'ui.empty': 'Tiada nod untuk skop ini.', 'ui.hoverHelp': 'Hover / fokus: sorot hubungan', 'ui.clickHelp': 'Klik: kunci pilihan',
      'ui.escapeHelp': 'kosongkan', 'ui.searchHelp': 'carian', 'ui.uiMapping': 'Pemetaan UI sebenar', 'ui.chooseUI': 'Pilih paparan UI',
      'ui.screenshotNote': 'Screenshot tetamu yang dianonimkan. Pilih hotspot untuk membuka pelaksanaan berkaitan.',
      'ui.implementation': 'Butiran pelaksanaan', 'ui.checkout': 'Rujukan silang kepada checkout semasa.',
      'ui.chooseItem': 'Pilih nod, jadual atau hotspot UI.', 'ui.chooseItemBody': 'Panel ini menerangkan tanggungjawab, aliran hujung ke hujung, fail sumber, route, jadual Supabase, selector UI dan syarat akses.',
      'ui.publicTables': 'Jadual public', 'ui.foreignKeys': 'Foreign key', 'ui.authLinks': 'Hubungan auth logik',
      'ui.sequenceUser': 'Pengguna', 'ui.sequenceAdministrator': 'Pentadbir', 'ui.sequenceEmpty': 'Tiada rajah lagi',
      'ui.sequenceSimple': 'Ringkas', 'ui.sequenceCode': 'Kod', 'ui.sequenceLabelMode': 'Butiran mesej jujukan',
      'ui.diagramSimple': 'Ringkas', 'ui.diagramCode': 'Kod', 'ui.diagramLabelMode': 'Butiran label rajah',
      'ui.flowchartUser': 'Pengguna', 'ui.flowchartAdministrator': 'Pentadbir', 'ui.flowchartEmpty': 'Tiada rajah lagi',
      'ui.variantPolished': 'Dikemas', 'ui.variantOriginal': 'Asal', 'ui.variantRecommended': 'Disyorkan', 'ui.variantReference': 'Rujukan asal',
      'ui.variantLayeredStack': 'Susunan Bertingkat', 'ui.variantHierarchyTree': 'Pokok Hierarki', 'ui.variantCurrent': 'Kod semasa',
      'ui.openVanilla': 'Buka vanilla', 'ui.openV2': 'Buka V2', 'ui.collectionCollapse': 'Tutup koleksi', 'ui.collectionExpand': 'Buka koleksi',
      'ui.collectionUseCases': 'Rajah Kes Guna', 'ui.collectionFlowcharts': 'Carta Alir', 'ui.collectionSequences': 'Rajah Jujukan',
      'ui.collectionClasses': 'Rajah Kelas', 'ui.collectionArchitectureModules': 'Seni Bina & Modul', 'ui.collectionData': 'Rajah Data',
      'ui.collectionETLOverview': 'Gambaran Keseluruhan', 'ui.collectionJobSearchWorkflows': 'Aliran Kerja Carian Pekerjaan',
      'ui.collectionRoutingOverview': 'Gambaran Keseluruhan', 'ui.collectionProviderWorkflows': 'Aliran Kerja Penyedia', 'ui.collectionRoutingInfrastructure': 'Infrastruktur',
      'ui.collectionDiagram': 'rajah', 'ui.collectionDiagrams': 'rajah',
      'ui.reportExplanation': 'Penerangan laporan', 'ui.copyReportParagraph': 'Salin perenggan', 'ui.reportParagraphCopied': 'Perenggan disalin',
      'ui.copyCode': 'Salin kod', 'ui.copyCaption': 'Salin kapsyen', 'ui.copyTable': 'Salin jadual', 'ui.copyFlow': 'Salin aliran', 'ui.codeCopied': 'Kod disalin', 'ui.captionCopied': 'Kapsyen disalin', 'ui.tableCopied': 'Jadual disalin', 'ui.flowCopied': 'Aliran disalin',
      'ui.reportTableReady': 'Jadual sedia laporan', 'ui.reportVerified': 'Snapshot disahkan', 'ui.reportSource': 'Sumber', 'ui.reportNote': 'Catatan',
      'ui.reportCaption': 'Kapsyen laporan', 'ui.codeSources': 'Fail sumber kod', 'ui.reportReadyCode': 'Kod pseudo sedia laporan',
      'ui.snippetLanguage': 'Bahasa kod pseudo', 'ui.snippetLanguageChanged': 'Bahasa kod pseudo ditukar',
      'ui.reportLanguage': 'Bahasa jadual laporan', 'ui.reportLanguageChanged': 'Bahasa jadual laporan ditukar',
      'ui.dictionaryColumn': 'Paparan lajur Kamus Data', 'ui.dictionaryConstraints': 'Wajib / Kekangan', 'ui.dictionarySize': 'Saiz Data',
      'ui.dictionaryColumnChanged': 'Paparan lajur Kamus Data ditukar',
      'ui.flow': 'Aliran hujung ke hujung', 'ui.sourceFiles': 'Fail sumber', 'ui.routes': 'Route / RPC', 'ui.tables': 'Jadual Supabase',
      'ui.uiComponents': 'Komponen UI', 'ui.auth': 'Syarat akses', 'ui.related': 'Nod berhubung', 'ui.reference': 'Aset rujukan', 'ui.close': 'Tutup',
      'ui.dependsOn': 'Bergantung pada', 'ui.usedBy': 'Digunakan oleh', 'ui.dataRelations': 'Hubungan data', 'ui.secondLevel': 'Konteks tahap kedua',
      'ui.connectionHover': 'Hover: 1 tahap · klik: 2 tahap',
      'ui.searchResults': 'Hasil carian', 'ui.noResults': 'Tiada kelas, route, jadual atau UI yang sepadan.',
      'ui.table': 'Jadual', 'ui.primaryKey': 'Primary key', 'ui.foreignKeyLinks': 'Hubungan foreign key', 'ui.rlsOn': 'RLS aktif', 'ui.rlsOff': 'RLS tidak aktif',
      'ui.viewMode': 'Lihat', 'ui.editMode': 'Edit', 'ui.importDiagram': 'Import .drawio', 'ui.validateDiagram': 'Semak', 'ui.saveAs': 'Simpan sebagai',
      'ui.saveWorkspace': 'Simpan ke ruang kerja', 'ui.workspaceSaved': 'Disimpan ke ruang kerja', 'ui.workspaceSaving': 'Menyimpan...',
      'ui.workspaceConflict': 'Versi ruang kerja yang lebih baharu wujud. Muat semula rajah ini sebelum menyimpan.',
      'ui.editorLoading': 'Memuatkan editor lokal…', 'ui.editorHttpRequired': 'Editor penuh memerlukan pelayan HTTP lokal. Mod file:// kekal baca sahaja.',
      'ui.editorRuntimeTitle': 'Mulakan editor lokal', 'ui.editorRuntimeSubtitle': 'Salinan ini dibuka dalam mod fail baca sahaja.',
      'ui.editorRuntimeDescription': 'Editor Draw.io terbina dalam memerlukan pelayan HTTP lokal dengan origin yang sama. Semua fail masih diproses pada komputer ini.',
      'ui.editorRuntimeLauncher': 'Tutup tab ini dan klik dua kali Start-Explorer.cmd dalam folder Explorer.',
      'ui.editorRuntimeCommand': 'Atau jalankan arahan berikut dalam PowerShell:', 'ui.copyCommand': 'Salin arahan', 'ui.commandCopied': 'Arahan disalin',
      'ui.validation': 'Pengesahan rajah', 'ui.layoutChange': 'Susun atur sahaja', 'ui.logicChange': 'Model berubah', 'ui.loadedChange': 'Dokumen dimuatkan',
      'ui.noIssues': 'Tiada isu logik ditemui.', 'ui.errors': 'Ralat', 'ui.warnings': 'Amaran', 'ui.info': 'Info',
      'ui.exactMatches': 'Tepat', 'ui.semanticMatches': 'Semantik', 'ui.ambiguousMatches': 'Kabur', 'ui.unmappedMatches': 'Belum dipetakan',
      'ui.importTitle': 'Semak import Draw.io', 'ui.importSubtitle': 'Pilih halaman yang hendak difokuskan sebelum membuka editor.',
      'ui.openEditor': 'Buka dalam editor', 'ui.cancel': 'Batal', 'ui.dropTitle': 'Lepaskan fail .drawio atau .xml',
      'ui.dropBody': 'Fail diproses secara lokal dan tidak dimuat naik.', 'ui.resolveMapping': 'Pilih padanan PetaKerja', 'ui.notMapped': 'Tidak dipetakan',
      'ui.schemaScope': 'jadual dalam skop ini', 'ui.schemaFull': 'snapshot penuh', 'ui.logicalLink': 'hubungan logik', 'ui.directOffline': 'Offline · sedia file://',
    };
    return ms[key] ?? key;
  }

  function labelStatus(status) {
    if (state.language === 'en') return translations.en.status[status] || status;
    return { current: 'Kod semasa', concept: 'Model konseptual FYP', legacy: 'Legacy / tidak tersedia', warning: 'Perhatian', gated: 'Berpagar ciri' }[status] || status;
  }

  function labelKind(kind) {
    if (state.language === 'en') return translations.en.kind[kind] || kind;
    return ({ actor: 'Aktor', runtime: 'Runtime', entry: 'Entry point', class: 'Kelas', interface: 'Antara muka', module: 'Modul',
      service: 'Servis', api: 'API', database: 'Pangkalan data', entity: 'Entiti', external: 'Perkhidmatan luar', middleware: 'Middleware',
      data: 'Kumpulan data', warning: 'Amaran', missing: 'Tidak tersedia', 'system-table': 'Jadual sistem', application: 'Aplikasi' })[kind] || kind;
  }

  function canonicalDiagram(diagram = activeDiagram()) {
    if (!diagram?.canonicalDiagramId || diagram.canonicalDiagramId === diagram.id) return diagram;
    return allDiagrams().find((item) => item.id === diagram.canonicalDiagramId) || diagram;
  }

  function logicalDiagramId(diagram = activeDiagram()) {
    return diagram?.canonicalDiagramId || diagram?.id || state.diagramId;
  }

  function diagramBaseText(diagram) {
    const canonical = canonicalDiagram(diagram);
    const translated = state.language === 'en' && translations.en.diagrams[canonical.id];
    return translated ? { title: translated[0], description: translated[1] } : { title: canonical.title, description: canonical.description || '' };
  }

  function diagramVariantLabel(diagram) {
    const custom = state.language === 'en' ? diagram.variantLabelEn : diagram.variantLabelMs;
    if (custom) return custom;
    if (diagram.variantKind === 'polished') return t('ui.variantPolished');
    if (diagram.variantKind === 'original') return t('ui.variantOriginal');
    return diagram.variantKind || '';
  }

  function diagramVariantMeta(diagram) {
    const custom = state.language === 'en' ? diagram.variantMetaEn : diagram.variantMetaMs;
    if (custom) return custom;
    if (diagram.variantRecommended || diagram.variantKind === 'polished') return t('ui.variantRecommended');
    if (diagram.variantKind === 'original') return t('ui.variantReference');
    return labelStatus(diagram.status);
  }

  function diagramText(diagram) {
    const base = diagramBaseText(diagram);
    if (!diagram.variantKind) return base;
    const variant = diagramVariantLabel(diagram);
    const suffix = diagram.variantRecommended || diagram.variantKind === 'polished'
      ? (state.language === 'en' ? 'Recommended presentation layout.' : 'Susun atur persembahan yang disyorkan.')
      : diagram.variantKind === 'original'
        ? (state.language === 'en' ? 'Original layout retained for comparison.' : 'Susun atur asal dikekalkan untuk perbandingan.')
        : (state.language === 'en' ? 'Current implementation view.' : 'Paparan pelaksanaan semasa.');
    return { title: `${base.title} — ${variant}`, description: `${base.description} ${suffix}` };
  }

  function scopeLabel(scope) { return state.language === 'en' ? translations.en.scopes[scope.id] || scope.label : scope.label; }

  function syncSelectTitle(select) {
    if (!select) return;
    const selected = select.selectedOptions?.[0];
    select.title = selected?.textContent?.trim() || select.getAttribute('aria-label') || '';
  }

  function syncHeaderChoiceControls() {
    if (els.themeSelect) {
      const themeLabels = { system: t('ui.themeSystem'), light: t('ui.themeLight'), dark: t('ui.themeDark') };
      const preferenceLabel = themeLabels[state.themePreference] || themeLabels.system;
      const effectiveLabel = themeLabels[state.effectiveTheme] || state.effectiveTheme;
      const themeTooltip = state.themePreference === 'system'
        ? `${t('ui.theme')}: ${preferenceLabel} (${effectiveLabel})`
        : `${t('ui.theme')}: ${preferenceLabel}`;
      els.themeSelect.value = state.themePreference;
      els.themeSelect.setAttribute('aria-label', themeTooltip);
      els.themeSelect.title = themeTooltip;
      els.themeSelect.closest('.header-choice-control')?.setAttribute('title', themeTooltip);
      if (els.themeValue) els.themeValue.textContent = preferenceLabel;
    }
    if (els.languageSelect) {
      const compactLanguage = state.language === 'ms' ? 'BM' : 'EN';
      const languageName = state.language === 'ms' ? 'Bahasa Melayu' : 'English';
      const languageTooltip = `${t('ui.language')}: ${languageName}`;
      els.languageSelect.value = state.language;
      els.languageSelect.setAttribute('aria-label', languageTooltip);
      els.languageSelect.title = languageTooltip;
      els.languageSelect.closest('.header-choice-control')?.setAttribute('title', languageTooltip);
      if (els.languageValue) els.languageValue.textContent = compactLanguage;
    }
  }

  function applyLanguagePreference(language) {
    const nextLanguage = language === 'ms' ? 'ms' : 'en';
    state.language = nextLanguage;
    state.fitMode = true;
    editorController?.setLanguage(nextLanguage);
    cloudManager?.applyLanguage();
    renderAll();
    window.dispatchEvent(new CustomEvent('petakerja:languagechange', { detail: { language: nextLanguage } }));
  }
  function categoryLabel(category) { return state.language === 'en' ? translations.en.categories[category] || category : category; }
  function viewText(view) { const x = state.language === 'en' && translations.en.views[view.id]; return x ? { label: x[0], description: x[1] } : view; }
  function hotspotLabel(hotspot) { return state.language === 'en' ? translations.en.hotspots[hotspot.id] || hotspot.label : hotspot.label; }
  function nodeLabel(node) { return state.language === 'en' ? translations.en.nodeLabels[node.id] || node.label : node.label; }
  function nodeDescription(node) {
    if (state.language !== 'en') return node.description || '';
    return translations.en.descriptions[node.id] || `Current ${labelKind(node.kind).toLowerCase()} in PetaKerja. Inspect the linked source files, routes, tables and UI components below.`;
  }
  function nodeFlow(node) {
    if (!node.flow?.length) return [];
    if (state.language !== 'en') return node.flow;
    const known = {
      'Buka PetaKerja': 'Open PetaKerja', 'Pilih ruang kerja': 'Choose a workspace', 'Gunakan fungsi peta atau pekerjaan': 'Use a map or job feature',
      'pilih dataset': 'Choose a dataset', 'agregat negeri': 'Aggregate by state', 'warna peta + carta': 'Render map colours and charts',
      'aktifkan Highlight': 'Enable Highlight', 'lukis kawasan': 'Draw an area', 'kumpul POI': 'Collect contained POIs', 'hantar konteks': 'Send spatial context',
      'input carian': 'Enter a search query', 'papar keputusan': 'Render results',
    };
    return node.flow.map((step, index) => known[step] || (/^[A-Za-z0-9_./:'() +*-]+$/.test(step) ? step : `Implementation step ${index + 1} for ${nodeLabel(node)}`));
  }
  function authLabel(value) { return state.language === 'en' ? translations.en.auth[value] || 'Role or session required' : value; }
  function edgeLabel(edge) { return state.language === 'en' ? translations.en.edge[edge.type] || 'connects to' : edge.label; }
  function connectionKindLabel(kind) {
    if (state.language === 'en') return translations.en.edge[kind] || 'connects to';
    return ({ composition: 'memiliki', aggregation: 'mengagregat', dependency: 'bergantung pada', logical: 'hubungan logik', association: 'berhubung dengan', include: 'merangkumi', extend: 'melanjutkan', flow: 'aliran proses', 'flow-decision': 'cabang keputusan' })[kind] || 'berhubung dengan';
  }

  function scopeDefinition() { return data.scopeGroups.find((scope) => scope.id === state.scopeId) || data.scopeGroups[0]; }
  function normaliseSchemaScope(group) { return group === 'ai' ? 'core' : group === 'auth' ? 'infra' : group; }
  function scopeAllows(scope) { return scopeDefinition().includes.includes(scope); }
  function allDiagrams() { return [...data.diagrams, ...state.importedDiagrams]; }
  function activeDiagram() { return allDiagrams().find((diagram) => diagram.id === state.diagramId) || data.diagrams[0]; }
  function isCodeDiagram(diagram = activeDiagram()) { return diagram?.layout === 'code'; }
  function isReportTableDiagram(diagram = activeDiagram()) { return diagram?.layout === 'report-table'; }
  function isDocumentDiagram(diagram = activeDiagram()) { return isCodeDiagram(diagram) || isReportTableDiagram(diagram); }
  function activeReportPage(diagram = activeDiagram()) { return fypReportTables.pages?.[diagram?.reportTableKey] || null; }
  function reportValue(value, language = state.reportTableLanguage) {
    if (value && typeof value === 'object' && !Array.isArray(value) && ('ms' in value || 'en' in value)) {
      return String(value[language] ?? value.ms ?? value.en ?? '');
    }
    return String(value ?? '');
  }
  function reportList(values) { return (Array.isArray(values) ? values : []).map((value) => reportValue(value)); }
  function codeSnippetText(diagram = activeDiagram()) {
    const english = state.snippetLanguage === 'en';
    return {
      reportHeading: english ? diagram.reportHeadingEn || diagram.reportHeading : diagram.reportHeading,
      caption: english ? diagram.captionEn || diagram.caption : diagram.caption,
      code: english ? diagram.codeEn || diagram.code : diagram.code,
    };
  }
  function runtimeDocument(id = state.diagramId) { return state.runtimeDocuments.get(id) || null; }
  async function ensureWorkspaceSession() {
    if (!editorController?.available || runtimeCapabilities.localWorkspace === false) return null;
    if (state.workspaceToken) return { token: state.workspaceToken, diagrams: [...state.workspaceDiagramIds] };
    if (state.workspaceSessionPromise) return state.workspaceSessionPromise;
    state.workspaceSessionPromise = fetch(localAPI('workspace/session'), { cache: 'no-store' })
      .then(async (response) => {
        if (!response.ok) throw new Error(`Workspace session is unavailable (${response.status}).`);
        const payload = await response.json();
        state.workspaceToken = payload.token;
        state.workspaceDiagramIds = new Set(payload.diagrams || []);
        renderWorkspaceControls();
        return payload;
      })
      .catch(() => null)
      .finally(() => { state.workspaceSessionPromise = null; });
    return state.workspaceSessionPromise;
  }

  async function hydrateWorkspaceDocument(diagramId = state.diagramId, options = {}) {
    if (!editorController?.available || runtimeCapabilities.localWorkspace === false || activeDiagram()?.sessionOnly) return null;
    if (!options.force && state.workspaceLoaded.has(diagramId)) return runtimeDocument(diagramId);
    const session = await ensureWorkspaceSession();
    if (!session || !state.workspaceDiagramIds.has(diagramId)) return null;
    try {
      const response = await fetch(localAPI(`workspace/diagrams/${encodeURIComponent(diagramId)}`), { cache: 'no-store' });
      if (!response.ok) throw new Error(`Workspace diagram is unavailable (${response.status}).`);
      const payload = await response.json();
      const analysis = editorController.preflight(payload.xml);
      if (analysis.fatal) {
        const diagnostic = analysis.issues?.[0]?.message?.[state.language]
          || analysis.issues?.[0]?.message?.en
          || 'The saved workspace XML could not be analysed.';
        throw new Error(diagnostic);
      }
      const sanitized = sanitizeRuntimeSVG(payload.svg);
      const asset = runtimeAssetFromAnalysis(sanitized, analysis);
      const source = editorAPI.SOURCE_FILES[diagramId];
      state.runtimeDocuments.set(diagramId, {
        workingXml: payload.xml,
        pageId: analysis.selectedPage?.id || source?.pageId || null,
        filename: source?.filename || `${diagramId}.drawio`,
        analysis,
        dirty: false,
        diagramType: diagramId,
        runtimeSvg: sanitized,
        asset,
        lastValidAsset: asset,
        revision: payload.revision,
        modifiedAt: payload.modifiedAt,
        workspace: true,
      });
      state.workspaceLoaded.add(diagramId);
      if (state.diagramId === diagramId && state.workspaceMode === 'view') renderDiagram();
      return state.runtimeDocuments.get(diagramId);
    } catch (error) {
      els.statusMessage.textContent = `${state.language === 'en' ? 'Workspace load failed' : 'Ruang kerja gagal dimuatkan'}: ${error.message}`;
      return null;
    }
  }

  async function saveActiveDiagramToWorkspace() {
    const diagramId = state.editorDocumentKey || state.diagramId;
    const session = await ensureWorkspaceSession();
    if (!session || !state.workspaceDiagramIds.has(diagramId)) {
      els.statusMessage.textContent = state.language === 'en' ? 'This diagram is not registered for workspace saving.' : 'Rajah ini belum didaftarkan untuk simpanan ruang kerja.';
      return false;
    }
    let runtime = runtimeDocument(diagramId) || await hydrateWorkspaceDocument(diagramId);
    if (!runtime?.revision) return false;
    els.workspaceSaveButton.disabled = true;
    els.workspaceSaveButton.textContent = t('ui.workspaceSaving');
    try {
      const exported = await editorController.exportRuntimeSVG();
      const svg = sanitizeRuntimeSVG(exported.svg);
      const xml = exported.xml || editorController.workingXml;
      const response = await fetch(localAPI(`workspace/diagrams/${encodeURIComponent(diagramId)}`), {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json', 'X-PetaKerja-Workspace-Token': state.workspaceToken },
        body: JSON.stringify({ revision: runtime.revision, xml, svg }),
      });
      const payload = await response.json().catch(() => ({}));
      if (response.status === 409) {
        const message = t('ui.workspaceConflict');
        els.statusMessage.textContent = message;
        window.alert(message);
        return false;
      }
      if (!response.ok) throw new Error(payload.error?.message || `Workspace save failed (${response.status}).`);
      const analysis = editorController.analysis || editorController.preflight(xml);
      const asset = runtimeAssetFromAnalysis(svg, analysis);
      runtime = { ...runtime, workingXml: xml, runtimeSvg: svg, asset, lastValidAsset: asset, analysis, dirty: false, revision: payload.revision, modifiedAt: payload.modifiedAt, workspace: true };
      state.runtimeDocuments.set(diagramId, runtime);
      editorController.markClean();
      els.workspaceSaveButton.textContent = t('ui.workspaceSaved');
      els.statusMessage.textContent = t('ui.workspaceSaved');
      window.setTimeout(() => { if (els.workspaceSaveButton.isConnected) els.workspaceSaveButton.textContent = t('ui.saveWorkspace'); }, 1400);
      return true;
    } catch (error) {
      els.statusMessage.textContent = `${state.language === 'en' ? 'Workspace save failed' : 'Simpanan ruang kerja gagal'}: ${error.message}`;
      return false;
    } finally {
      els.workspaceSaveButton.disabled = false;
    }
  }
  function activeAsset() {
    const runtime = runtimeDocument();
    const runtimeAsset = runtime?.asset || runtime?.lastValidAsset || null;
    const canonical = assets[state.diagramId] || null;
    if (!runtimeAsset) return canonical;
    if (!canonical) return runtimeAsset;
    return {
      ...canonical,
      ...runtimeAsset,
      svg: runtimeAsset.svg || canonical.svg,
      components: runtimeAsset.components?.length ? runtimeAsset.components : canonical.components,
      connections: runtimeAsset.connections?.length ? runtimeAsset.connections : canonical.connections,
      labelElements: runtimeAsset.labelElements?.length ? runtimeAsset.labelElements : canonical.labelElements,
      labelModes: runtimeAsset.labelModes?.length ? runtimeAsset.labelModes : canonical.labelModes,
      supportsLabelModes: Boolean(runtimeAsset.supportsLabelModes || canonical.supportsLabelModes),
      supportsSequenceLabels: Boolean(runtimeAsset.supportsSequenceLabels || canonical.supportsSequenceLabels),
    };
  }
  function diagramSupportsLabelModes() {
    const capabilityAsset = assets[state.diagramId] || activeAsset();
    return Boolean(capabilityAsset?.supportsLabelModes || capabilityAsset?.supportsSequenceLabels);
  }
  function effectiveMode() { return state.renderMode === 'actual' && (activeAsset() || runtimeDocument()?.workingXml) ? 'actual' : 'map'; }
  function currentFocus() { return state.hovered || state.selected; }
  function currentComponentKey() { return state.hovered ? state.hoveredComponentKey : state.selectedComponentKey; }

  function componentTarget(component) {
    if (!component) return null;
    return component.tableName ? `table:${component.tableName}` : component.nodeIds?.[0] || component.id;
  }

  function componentByKey(asset, key) {
    return key ? asset?.components?.find((component) => component.componentKey === key) || null : null;
  }

  function activeComponent(asset = activeAsset()) {
    const focus = currentFocus();
    return componentByKey(asset, currentComponentKey()) || asset?.components?.find((component) => {
      const target = componentTarget(component);
      return target === focus || component.nodeIds?.includes(focus);
    }) || null;
  }

  function componentLabel(component) {
    if (!component) return '';
    const variants = component.labels?.[state.diagramLabelMode];
    if (variants) return variants[state.language] || variants.en || variants.ms;
    return (state.language === 'en' ? component.labelEn : component.label) || component.tableName || component.id;
  }

  function connectionLabel(connection) {
    const variants = connection?.labels?.[state.diagramLabelMode];
    return variants?.[state.language] || variants?.en || connection?.label?.[state.language] || connection?.label?.ms || connectionKindLabel(connection?.kind);
  }

  function actualConnectionContext(asset, component, includeSecond = false) {
    const connections = asset?.connections || [];
    const focusKey = component?.componentKey;
    const directConnections = connections.filter((item) => item.sourceComponentKey === focusKey || item.targetComponentKey === focusKey);
    const directKeys = new Set();
    directConnections.forEach((item) => directKeys.add(item.sourceComponentKey === focusKey ? item.targetComponentKey : item.sourceComponentKey));
    const directIds = new Set(directConnections.map((item) => item.id));
    const secondaryConnections = includeSecond ? connections.filter((item) => !directIds.has(item.id)
      && (directKeys.has(item.sourceComponentKey) || directKeys.has(item.targetComponentKey))) : [];
    const secondaryKeys = new Set();
    secondaryConnections.forEach((item) => {
      if (item.sourceComponentKey !== focusKey && !directKeys.has(item.sourceComponentKey)) secondaryKeys.add(item.sourceComponentKey);
      if (item.targetComponentKey !== focusKey && !directKeys.has(item.targetComponentKey)) secondaryKeys.add(item.targetComponentKey);
    });
    return { focusKey, directConnections, directKeys, secondaryConnections, secondaryKeys };
  }

  function graphConnectionContext(nodeId, includeSecond = false) {
    const relevant = data.edges.filter((item) => item.diagrams.includes(logicalDiagramId()));
    const directEdges = relevant.filter((item) => item.from === nodeId || item.to === nodeId);
    const directNodes = new Set(data.mappings[nodeId]?.relatedNodes || []);
    directEdges.forEach((item) => directNodes.add(item.from === nodeId ? item.to : item.from));
    const directEdgeSet = new Set(directEdges);
    const secondaryEdges = includeSecond ? relevant.filter((item) => !directEdgeSet.has(item)
      && (directNodes.has(item.from) || directNodes.has(item.to))) : [];
    const secondaryNodes = new Set();
    secondaryEdges.forEach((item) => {
      if (item.from !== nodeId && !directNodes.has(item.from)) secondaryNodes.add(item.from);
      if (item.to !== nodeId && !directNodes.has(item.to)) secondaryNodes.add(item.to);
    });
    return { directEdges, directNodes, secondaryEdges, secondaryNodes };
  }

  function diagramScopeAllows(diagram) {
    if (diagram.sessionOnly) return true;
    if (diagram.layout === 'schema') return true;
    const scopes = new Set((diagram.columns || []).flat().map((id) => data.nodes[id]?.scope).filter(Boolean));
    return !scopes.size || [...scopes].some(scopeAllows);
  }

  function nodeRelations(nodeId) {
    const context = graphConnectionContext(nodeId, false);
    return { edges: context.directEdges, nodes: new Set([nodeId, ...context.directNodes]) };
  }

  function tableRelations(tableName) {
    return data.schemaForeignKeys.filter((fk) => fk.sourceTable === tableName || fk.targetTable === tableName);
  }

  function populateControls() {
    els.scope.innerHTML = data.scopeGroups.map((scope) => `<option value="${scope.id}">${escapeHTML(scopeLabel(scope))}</option>`).join('');
    els.scope.value = state.scopeId;
    syncSelectTitle(els.scope);
    renderDiagramNav();
    renderUIViewOptions();
  }

  function renderDiagramNav() {
    const visible = allDiagrams().filter(diagramScopeAllows);
    const categories = [...new Set(visible.map((diagram) => diagram.category))];
    const diagramButton = (diagram, options = {}) => {
      const text = options.text || diagramText(diagram);
      const icon = options.icon || diagram.variantIcon || (diagram.variantKind === 'polished' ? 'sparkles' : diagram.variantKind === 'original' ? 'history' : DIAGRAM_ICONS[diagram.id]) || 'file-question-mark';
      const meta = options.meta || labelStatus(diagram.status);
      return `<button class="nav-item${options.variant ? ' nav-item--variant' : ''}${diagram.id === state.diagramId ? ' is-active' : ''}" type="button" data-diagram="${diagram.id}" aria-current="${diagram.id === state.diagramId ? 'page' : 'false'}"><span class="nav-item__icon" aria-hidden="true"><i data-bp-icon="${icon}"></i></span><span class="nav-item__copy"><span class="nav-item__title">${escapeHTML(text.title)}</span><small>${escapeHTML(meta)}</small></span></button>`;
    };
    const variantFolder = (familyKey, diagrams) => {
      const ordered = [...diagrams].sort((a, b) => (a.variantOrder || 99) - (b.variantOrder || 99));
      const canonical = canonicalDiagram(ordered.find((item) => item.variantRecommended) || ordered.find((item) => item.variantKind === 'polished') || ordered[0]);
      const title = diagramBaseText(canonical).title;
      const active = ordered.some((item) => item.id === state.diagramId);
      if (active) state.diagramVariantFolders[familyKey] = true;
      const open = state.diagramVariantFolders[familyKey] === true;
      return `<details class="nav-variant-group" data-diagram-variant-family="${escapeHTML(familyKey)}"${open ? ' open' : ''}><summary><span class="nav-variant-group__icon" aria-hidden="true"><i data-bp-icon="folder"></i></span><span>${escapeHTML(title)}</span><i class="nav-variant-group__chevron" data-bp-icon="chevron-right" aria-hidden="true"></i></summary><div class="nav-variant-group__items">${ordered.map((diagram) => diagramButton(diagram, {
        variant: true,
        text: { title: diagramVariantLabel(diagram) },
        meta: diagramVariantMeta(diagram),
      })).join('')}</div></details>`;
    };
    const variantItems = (diagrams) => {
      const families = [];
      diagrams.forEach((diagram, index) => {
        const familyKey = diagram.variantFamily || diagram.id;
        let group = families.find((item) => item.key === familyKey);
        if (!group) {
          group = { key: familyKey, order: index, diagrams: [] };
          families.push(group);
        }
        group.diagrams.push(diagram);
      });
      return families.sort((a, b) => a.order - b.order).map((group) => group.diagrams.length > 1
        ? variantFolder(group.key, group.diagrams)
        : diagramButton(group.diagrams[0])).join('');
    };
    const audienceItems = (_family, _audience, diagrams) => variantItems(diagrams);
    const audienceGroup = (family, audience, diagrams, icon, open) => {
      const labelKey = family === 'flowchart' ? `ui.flowchart${audience === 'user' ? 'User' : 'Administrator'}` : `ui.sequence${audience === 'user' ? 'User' : 'Administrator'}`;
      const emptyKey = family === 'flowchart' ? 'ui.flowchartEmpty' : 'ui.sequenceEmpty';
      return `<details class="nav-subgroup" data-nav-family="${family}" data-nav-audience="${audience}"${open ? ' open' : ''}><summary><span class="nav-subgroup__icon" aria-hidden="true"><i data-bp-icon="${icon}"></i></span><span>${escapeHTML(t(labelKey))}</span><i class="nav-subgroup__chevron" data-bp-icon="chevron-right" aria-hidden="true"></i></summary><div class="nav-subgroup__items">${diagrams.length ? audienceItems(family, audience, diagrams) : `<p class="nav-subgroup__empty">${escapeHTML(t(emptyKey))}</p>`}</div></details>`;
    };
    const codeSnippetGroup = (group, diagrams) => {
      const active = diagrams.some((diagram) => diagram.id === state.diagramId);
      if (active) state.codeSnippetFolders[group] = true;
      const open = state.codeSnippetFolders[group] !== false;
      return `<details class="nav-subgroup nav-subgroup--code" data-nav-family="code-snippets" data-nav-audience="${escapeHTML(group)}"${open ? ' open' : ''}><summary><span class="nav-subgroup__icon" aria-hidden="true"><i data-bp-icon="folder"></i></span><span>${escapeHTML(group)}</span><i class="nav-subgroup__chevron" data-bp-icon="chevron-right" aria-hidden="true"></i></summary><div class="nav-subgroup__items">${variantItems(diagrams)}</div></details>`;
    };
    const collectionFolder = (collectionId, category, diagrams) => {
      const ordered = [...diagrams].sort((a, b) => (a.collectionOrder || 99) - (b.collectionOrder || 99));
      const open = state.diagramCollections[collectionId] !== false;
      const groupSpecs = DIAGRAM_COLLECTION_GROUPS[collectionId] || [];
      const grouped = groupSpecs.map((spec) => ({
        ...spec,
        diagrams: ordered.filter((diagram) => diagram.collectionGroupId === spec.id),
      })).filter((group) => group.diagrams.length);
      const ungrouped = ordered.filter((diagram) => !groupSpecs.some((spec) => spec.id === diagram.collectionGroupId));
      if (ungrouped.length) grouped.push({ id: 'other', labelKey: null, icon: 'folder', diagrams: ungrouped });
      const groupMarkup = grouped.map((group) => {
        const storageKey = `${collectionId}:${group.id}`;
        const active = group.diagrams.some((diagram) => diagram.id === state.diagramId);
        const hasStoredState = Object.prototype.hasOwnProperty.call(state.diagramCollectionGroups, storageKey);
        const groupOpen = hasStoredState ? state.diagramCollectionGroups[storageKey] === true : active;
        const label = group.labelKey ? t(group.labelKey) : (state.language === 'en' ? 'Other diagrams' : 'Rajah lain');
        const countLabel = group.diagrams.length === 1 ? t('ui.collectionDiagram') : t('ui.collectionDiagrams');
        return `<details class="nav-collection-group" data-diagram-collection-group="${escapeHTML(storageKey)}"${groupOpen ? ' open' : ''}><summary><span class="nav-collection-group__icon" aria-hidden="true"><i data-bp-icon="${escapeHTML(group.icon)}"></i></span><span class="nav-collection-group__copy"><strong>${escapeHTML(label)}</strong><small>${group.diagrams.length} ${escapeHTML(countLabel)}</small></span><i class="nav-collection-group__chevron" data-bp-icon="chevron-right" aria-hidden="true"></i></summary><div class="nav-collection-group__items">${group.diagrams.map((diagram) => diagramButton(diagram, { meta: diagram.versionTag || labelStatus(diagram.status) })).join('')}</div></details>`;
      }).join('');
      return `<section class="nav-group nav-group--collection"><details class="nav-collection" data-diagram-collection="${escapeHTML(collectionId)}"${open ? ' open' : ''}><summary><span class="nav-collection__icon" aria-hidden="true"><i data-bp-icon="folder-tree"></i></span><span class="nav-collection__copy"><strong>${escapeHTML(categoryLabel(category))}</strong><small>${ordered.length} ${state.language === 'en' ? 'editable diagrams' : 'rajah boleh sunting'}</small></span><i class="nav-collection__chevron" data-bp-icon="chevron-right" aria-hidden="true"></i></summary><div class="nav-collection__items">${groupMarkup}</div></details></section>`;
    };
    els.diagramNav.innerHTML = categories.map((category) => {
      const categoryDiagrams = visible.filter((diagram) => diagram.category === category);
      const collectionId = categoryDiagrams[0]?.collectionId;
      if (collectionId && categoryDiagrams.every((diagram) => diagram.collectionId === collectionId)) return collectionFolder(collectionId, category, categoryDiagrams);
      if (category === 'Code Snippets') {
        const groups = [...new Set(categoryDiagrams.map((diagram) => diagram.snippetGroup).filter(Boolean))];
        return `<section class="nav-group nav-group--code"><h2>${escapeHTML(categoryLabel(category))}</h2>${groups.map((group) => codeSnippetGroup(group, categoryDiagrams.filter((diagram) => diagram.snippetGroup === group))).join('')}</section>`;
      }
      if (category !== 'Jujukan' && category !== 'Carta Alir') return `<section class="nav-group"><h2>${escapeHTML(categoryLabel(category))}</h2>${variantItems(categoryDiagrams)}</section>`;
      const isFlowchart = category === 'Carta Alir';
      const family = isFlowchart ? 'flowchart' : 'sequence';
      const audienceField = isFlowchart ? 'flowchartAudience' : 'sequenceAudience';
      const orderField = isFlowchart ? 'flowchartOrder' : 'sequenceOrder';
      const folderState = isFlowchart ? state.flowchartFolders : state.sequenceFolders;
      const userDiagrams = categoryDiagrams.filter((diagram) => (diagram[audienceField] || 'user') === 'user').sort((a, b) => (a[orderField] || 99) - (b[orderField] || 99));
      const administratorDiagrams = categoryDiagrams.filter((diagram) => diagram[audienceField] === 'administrator').sort((a, b) => (a[orderField] || 99) - (b[orderField] || 99));
      const active = categoryDiagrams.find((diagram) => diagram.id === state.diagramId);
      if (active?.[audienceField] === 'administrator') folderState.administrator = true;
      else if (active) folderState.user = true;
      const categoryIcon = isFlowchart ? '<i data-bp-icon="workflow" aria-hidden="true"></i>' : '';
      return `<section class="nav-group nav-group--sequence nav-group--${family}"><h2>${categoryIcon}${escapeHTML(categoryLabel(category))}</h2>${audienceGroup(family, 'user', userDiagrams, 'user-round', folderState.user)}${audienceGroup(family, 'administrator', administratorDiagrams, 'shield-user', folderState.administrator)}</section>`;
    }).join('');
    els.diagramNav.querySelectorAll('.nav-subgroup').forEach((folder) => folder.addEventListener('toggle', () => {
      const target = folder.dataset.navFamily === 'flowchart' ? state.flowchartFolders
        : folder.dataset.navFamily === 'code-snippets' ? state.codeSnippetFolders : state.sequenceFolders;
      target[folder.dataset.navAudience] = folder.open;
      if (folder.dataset.navFamily === 'flowchart') storeFlowchartFolders(target);
      else if (folder.dataset.navFamily === 'code-snippets') storeCodeSnippetFolders(target);
      else storeSequenceFolders(target);
    }));
    els.diagramNav.querySelectorAll('.nav-variant-group').forEach((folder) => folder.addEventListener('toggle', () => {
      state.diagramVariantFolders[folder.dataset.diagramVariantFamily] = folder.open;
      storeDiagramVariantFolders(state.diagramVariantFolders);
    }));
    els.diagramNav.querySelectorAll('.nav-collection').forEach((folder) => folder.addEventListener('toggle', () => {
      state.diagramCollections[folder.dataset.diagramCollection] = folder.open;
      storeDiagramCollections(state.diagramCollections);
    }));
    els.diagramNav.querySelectorAll('.nav-collection-group').forEach((folder) => folder.addEventListener('toggle', () => {
      state.diagramCollectionGroups[folder.dataset.diagramCollectionGroup] = folder.open;
      storeDiagramCollectionGroups(state.diagramCollectionGroups);
    }));
    window.renderBlueprintIcons?.(els.diagramNav);
    els.diagramPicker.innerHTML = visible.map((diagram) => `<option value="${diagram.id}">${escapeHTML(diagramText(diagram).title)}</option>`).join('');
    els.diagramPicker.value = state.diagramId;
    syncSelectTitle(els.diagramPicker);
  }

  function renderUIViewOptions() {
    const visible = data.uiViews.filter((view) => scopeAllows(view.scope));
    if (!visible.some((view) => view.id === state.uiViewId)) state.uiViewId = visible[0]?.id || 'map';
    els.uiView.innerHTML = visible.map((view) => `<option value="${view.id}">${escapeHTML(viewText(view).label)}</option>`).join('');
    els.uiView.value = state.uiViewId;
  }

  function renderStaticLanguage() {
    document.documentElement.lang = state.language;
    storeLanguage(state.language);
    els.skip.textContent = t('ui.skip'); els.subtitle.textContent = t('ui.subtitle');
    els.search.placeholder = t('ui.searchPlaceholder'); els.searchLabel.textContent = t('ui.search');
    els.actualMode.textContent = t('ui.actual'); els.actualMode.dataset.short = state.language === 'en' ? 'Actual' : 'Sebenar';
    els.mapMode.textContent = t('ui.map'); els.mapMode.dataset.short = state.language === 'en' ? 'Map' : 'Peta';
    els.actualMode.title = t('ui.actual'); els.mapMode.title = t('ui.map');
    els.themeLabel.textContent = t('ui.theme');
    els.languageLabel.textContent = t('ui.language');
    const themeLabels = { system: t('ui.themeSystem'), light: t('ui.themeLight'), dark: t('ui.themeDark') };
    [...els.themeSelect.options].forEach((option) => { option.textContent = themeLabels[option.value] || option.value; });
    els.themeSelect.value = state.themePreference;
    syncHeaderChoiceControls();
    els.navTitle.textContent = t('ui.diagrams'); els.navDescription.textContent = t('ui.chooseView');
    byId('legend-title').textContent = state.language === 'en' ? 'Content status' : 'Status kandungan';
    byId('legend-current').textContent = labelStatus('current'); byId('legend-concept').textContent = labelStatus('concept'); byId('legend-legacy').textContent = labelStatus('legacy');
    byId('ui-panel-title').textContent = t('ui.uiMapping'); byId('details-title').textContent = t('ui.implementation'); byId('details-subtitle').textContent = t('ui.checkout');
    byId('screenshot-note').textContent = t('ui.screenshotNote'); byId('graph-empty').textContent = t('ui.empty');
    byId('help-hover').textContent = t('ui.connectionHover'); byId('help-click').textContent = t('ui.clickHelp'); byId('help-escape').textContent = t('ui.escapeHelp'); byId('help-search').textContent = t('ui.searchHelp');
    byId('zoom-fit').textContent = t('ui.fit'); byId('zoom-out').ariaLabel = t('ui.zoomOut'); byId('zoom-in').ariaLabel = t('ui.zoomIn');
    els.referenceButton.textContent = t('ui.reference'); byId('reference-title').textContent = t('ui.reference'); byId('close-reference').ariaLabel = t('ui.close');
    els.workspaceView.textContent = t('ui.viewMode'); els.workspaceEdit.textContent = t('ui.editMode'); els.workspaceAgent.textContent = state.language === 'en' ? 'Agent' : 'Ejen';
    els.diagramSimple.textContent = t('ui.diagramSimple'); els.diagramCode.textContent = t('ui.diagramCode');
    els.diagramLabelControl.setAttribute('aria-label', t('ui.diagramLabelMode'));
    els.importButton.textContent = t('ui.importDiagram'); els.validateButton.textContent = t('ui.validateDiagram');
    els.workspaceSaveButton.textContent = t('ui.saveWorkspace'); els.saveButton.textContent = t('ui.saveAs');
    els.editorLoading.textContent = t('ui.editorLoading'); els.validationTitle.textContent = t('ui.validation');
    els.importTitle.textContent = t('ui.importTitle'); els.importSubtitle.textContent = t('ui.importSubtitle'); els.confirmImport.textContent = t('ui.openEditor');
    byId('cancel-import').textContent = t('ui.cancel'); els.dropOverlay.querySelector('strong').textContent = t('ui.dropTitle'); els.dropOverlay.querySelector('span').textContent = t('ui.dropBody');
    els.runtimeTitle.textContent = t('ui.editorRuntimeTitle'); els.runtimeSubtitle.textContent = t('ui.editorRuntimeSubtitle');
    els.runtimeDescription.textContent = t('ui.editorRuntimeDescription');
    els.runtimeStepLauncher.innerHTML = escapeHTML(t('ui.editorRuntimeLauncher')).replace('Start-Explorer.cmd', '<code>Start-Explorer.cmd</code>');
    els.runtimeStepCommand.textContent = t('ui.editorRuntimeCommand'); els.copyRuntimeCommand.textContent = t('ui.copyCommand');
    byId('close-runtime').ariaLabel = t('ui.close'); byId('dismiss-runtime').textContent = t('ui.close');
    byId('agent-title').textContent = state.language === 'en' ? 'Diagram Agent' : 'Ejen Rajah';
    byId('agent-subtitle').textContent = state.language === 'en' ? 'Plan first, then draw visibly in the editor.' : 'Semak pelan dahulu, kemudian lukis secara nyata dalam editor.';
    byId('agent-provider-label').textContent = state.language === 'en' ? 'Provider' : 'Penyedia';
    byId('agent-base-label').textContent = 'Base URL'; byId('agent-model-label').textContent = state.language === 'en' ? 'Model' : 'Model';
    byId('agent-key-label').textContent = state.language === 'en' ? 'API key' : 'Kunci API';
    els.agentAPIKey.placeholder = state.language === 'en' ? 'Session only' : 'Sesi ini sahaja';
    byId('agent-prompt-label').textContent = state.language === 'en' ? 'Diagram request' : 'Permintaan rajah';
    els.agentPrompt.placeholder = state.language === 'en' ? 'Describe the diagram or change you want...' : 'Terangkan rajah atau perubahan yang anda mahu...';
    byId('agent-plan-title').textContent = state.language === 'en' ? 'Plan preview' : 'Pratonton pelan';
    byId('agent-log-title').textContent = state.language === 'en' ? 'Activity' : 'Aktiviti';
    byId('bridge-title').textContent = state.language === 'en' ? 'Optional Codex bridge' : 'Bridge Codex pilihan';
    byId('bridge-description').innerHTML = state.language === 'en'
      ? 'Connect Codex to the same visible operation queue. The Explorer never edits <code>.mcp.json</code>.'
      : 'Sambungkan Codex kepada baris gilir operasi yang sama. Explorer tidak pernah mengubah <code>.mcp.json</code>.';
    els.copyBridgeConfig.textContent = state.language === 'en' ? 'Copy MCP configuration' : 'Salin konfigurasi MCP';
    els.agentTest.textContent = state.language === 'en' ? 'Test connection' : 'Uji sambungan';
    els.agentPropose.textContent = state.language === 'en' ? 'Create plan' : 'Cipta pelan';
    els.agentRun.textContent = state.language === 'en' ? 'Run plan' : 'Jalankan pelan';
    els.agentStop.textContent = state.language === 'en' ? 'Stop' : 'Henti';
    els.agentRevert.textContent = state.language === 'en' ? 'Revert run' : 'Undur larian';
    setAgentState(els.agentState.dataset.state || 'idle');
    if (state.agentProviderStatus) renderAgentProviderStatus(state.agentProviderStatus);
    const runtime = editorController?.available ? 'HTTP · editor' : 'file:// · read-only';
    els.snapshot.textContent = `73 ${state.language === 'en' ? 'tables' : 'jadual'} · 86 FK · ${runtime}`;
    document.querySelectorAll('[data-mobile-panel]').forEach((button) => {
      button.textContent = button.dataset.mobilePanel === 'diagram' ? t('ui.diagram') : button.dataset.mobilePanel === 'ui' ? t('ui.uiTab') : t('ui.detailsTab');
    });
  }

  function editorIssueText(entry) {
    return entry.message?.[state.language] || entry.message?.ms || entry.ruleId;
  }

  function editorChangeLabel(kind) {
    return kind === 'geometry' ? t('ui.layoutChange') : kind === 'logic' ? t('ui.logicChange') : t('ui.loadedChange');
  }

  function isEditableDiagram(id = state.diagramId) {
    const runtime = runtimeDocument(id);
    return Boolean(runtime && !runtime.readOnly) || (isCanonicalEditable(id) && Boolean(assets[id]));
  }

  function explorerFolderPath() {
    if (window.location.protocol !== 'file:') return '.';
    let pathname = decodeURIComponent(new URL('.', window.location.href).pathname);
    if (/^\/[A-Za-z]:\//.test(pathname)) pathname = pathname.slice(1);
    return pathname.replace(/\//g, '\\').replace(/\\$/, '');
  }

  function runtimeLaunchCommand() {
    return `powershell.exe -NoProfile -ExecutionPolicy Bypass -File "${explorerFolderPath()}\\Start-Explorer.ps1"`;
  }

  function showRuntimeDialog() {
    els.statusMessage.textContent = t('ui.editorHttpRequired');
    els.runtimeCommand.textContent = runtimeLaunchCommand();
    if (!els.runtimeDialog.open) els.runtimeDialog.showModal();
  }

  function renderValidation(analysis = state.editorAnalysis, meta = {}) {
    state.editorAnalysis = analysis;
    els.validationPanel.hidden = state.workspaceMode === 'view';
    if (state.workspaceMode === 'view') return;
    if (!analysis) {
      els.validationSummary.innerHTML = '';
      els.validationIssues.innerHTML = `<p class="validation-empty">${escapeHTML(t('ui.editorLoading'))}</p>`;
      return;
    }
    const page = analysis.selectedPage;
    const issues = analysis.issues || [];
    const counts = page?.counts || { exact: 0, semantic: 0, ambiguous: 0, unmapped: 0 };
    const errors = issues.filter((entry) => entry.severity === 'fatal' || entry.severity === 'error').length;
    const warnings = issues.filter((entry) => entry.severity === 'warning').length;
    const info = issues.filter((entry) => entry.severity === 'info').length;
    els.validationChangeKind.textContent = editorChangeLabel(meta.changeKind || 'load');
    els.validationSummary.innerHTML = [
      [t('ui.errors'), errors], [t('ui.warnings'), warnings], [t('ui.info'), info],
      [t('ui.exactMatches'), counts.exact], [t('ui.semanticMatches'), counts.semantic],
      [t('ui.ambiguousMatches'), counts.ambiguous], [t('ui.unmappedMatches'), counts.unmapped],
    ].map(([label, value]) => `<span><b>${value}</b> ${escapeHTML(label)}</span>`).join('');
    const visibleIssues = issues.slice(0, 40).map((entry, index) => `<button type="button" class="validation-issue" data-issue-index="${index}" data-severity="${escapeHTML(entry.severity)}"><span>${escapeHTML(editorIssueText(entry))}<small>${escapeHTML(entry.ruleId)}${entry.pageId ? ` · ${escapeHTML(entry.pageId)}` : ''}</small></span></button>`);
    const unresolved = (page?.matches || []).filter((match) => match.confidence === 'ambiguous' || match.confidence === 'unmapped');
    const manifest = page && editorController?.manifests?.[page.diagramId];
    const resolution = unresolved.map((match) => {
      const options = (manifest?.identities || []).map((identity) => `<option value="${escapeHTML(identity.key)}">${escapeHTML(state.language === 'en' ? identity.labelEn : identity.label)}</option>`).join('');
      return `<div class="validation-issue" data-severity="info"><span>${escapeHTML(t('ui.resolveMapping'))}<small>${escapeHTML(match.cellId)}</small></span><label class="mapping-resolution"><span class="sr-only">${escapeHTML(t('ui.resolveMapping'))}</span><select data-resolve-cell="${escapeHTML(match.cellId)}" data-resolve-page="${escapeHTML(match.pageId)}"><option value="">${escapeHTML(t('ui.notMapped'))}</option>${options}</select></label></div>`;
    });
    els.validationIssues.innerHTML = visibleIssues.length || resolution.length
      ? [...visibleIssues, ...resolution].join('') : `<p class="validation-empty">${escapeHTML(t('ui.noIssues'))}</p>`;
  }

  function renderImportDialog(pending) {
    state.pendingImport = pending;
    const analysis = pending.analysis;
    els.importTitle.textContent = t('ui.importTitle');
    els.importSubtitle.textContent = state.language === 'en' ? 'Choose a page and confirm or override its detected type.' : 'Pilih halaman dan sahkan atau tukar jenis rajah yang dikesan.';
    if (analysis.fatal) {
      els.importSummary.textContent = editorIssueText(analysis.issues[0]);
      els.importPages.innerHTML = '';
      els.confirmImport.disabled = true;
    } else {
      const totalComponents = analysis.pages.reduce((sum, page) => sum + page.componentCount, 0);
      const totalRelations = analysis.pages.reduce((sum, page) => sum + page.relationshipCount, 0);
      els.importSummary.textContent = `${pending.filename} · ${analysis.pages.length} ${state.language === 'en' ? 'pages' : 'halaman'} · ${totalComponents} ${state.language === 'en' ? 'components' : 'komponen'} · ${totalRelations} ${state.language === 'en' ? 'connectors' : 'penyambung'}`;
      const best = analysis.selectedPage?.id;
      const typeOptions = ['usecase', 'domain', 'implementation', 'supabase', 'generic-class', 'generic-usecase', 'generic-erd', 'generic-activity', 'generic-sequence', 'unknown'];
      els.importPages.innerHTML = analysis.pages.map((page) => {
        const detection = page.detection || { diagramType: page.diagramId, confidence: 0, status: 'generic' };
        const options = typeOptions.map((type) => `<option value="${type}"${type === detection.diagramType ? ' selected' : ''}>${escapeHTML(type)}</option>`).join('');
        return `<label class="import-page"><input type="radio" name="import-page" value="${escapeHTML(page.id)}"${page.id === best ? ' checked' : ''}><span><strong>${escapeHTML(page.name)}</strong><small>${escapeHTML(detection.status)} · ${escapeHTML(detection.diagramType)} · ${Math.round(detection.confidence * 100)}% · ${page.componentCount} ${state.language === 'en' ? 'components' : 'komponen'} · ${page.relationshipCount} ${state.language === 'en' ? 'links' : 'hubungan'} · ${page.issues.length} ${state.language === 'en' ? 'issues' : 'isu'}</small><select data-type-override="${escapeHTML(page.id)}" aria-label="${state.language === 'en' ? 'Diagram type override' : 'Tukar jenis rajah'}">${options}</select></span></label>`;
      }).join('');
      els.confirmImport.disabled = false;
    }
    if (!els.importDialog.open) els.importDialog.showModal();
  }

  async function processImportFile(file) {
    if (!file || !/\.(?:drawio|xml)$/i.test(file.name)) {
      renderImportDialog({ filename: file?.name || 'Unknown file', xml: '', analysis: { fatal: true, pages: [], issues: [{ ruleId: 'unsupported-file', severity: 'fatal', message: { ms: 'Gunakan fail .drawio atau .xml.', en: 'Use a .drawio or .xml file.' } }] } });
      return;
    }
    const xml = await file.text();
    const pending = { filename: file.name, xml, analysis: editorController.preflight(xml) };
    const recognized = pending.analysis.fatal ? [] : pending.analysis.pages.filter((page) => page.detection?.status === 'recognized' && isCanonicalEditable(page.detection.diagramType));
    if (pending.analysis.pages.length === 1 && recognized.length === 1) {
      await openImportedPage(pending, recognized[0].id, recognized[0].detection.diagramType);
      return;
    }
    renderImportDialog(pending);
  }

  async function openImportedPage(pending, pageId, diagramOverride = null) {
    if (!pending || pending.analysis.fatal) return;
    const page = pending.analysis.pages.find((item) => item.id === pageId) || pending.analysis.selectedPage;
    const detectedType = diagramOverride || page?.detection?.diagramType || page?.diagramId || 'unknown';
    const canonical = isCanonicalEditable(detectedType);
    if (canonical && data.diagrams.some((item) => item.id === detectedType)) {
      state.diagramId = detectedType;
    } else {
      const sessionId = `imported-${Date.now()}-${String(pageId || 'page').replace(/[^a-z0-9_-]+/gi, '-')}`;
      const title = page?.name || pending.filename.replace(/\.(?:drawio|xml)$/i, '');
      state.importedDiagrams.push({ id: sessionId, title: `Imported Diagram · ${title}`, description: `${detectedType} · session-only`, category: 'Imported', status: 'concept', sessionOnly: true, layout: 'free', columns: [] });
      state.diagramId = sessionId;
    }
    state.editorDocumentKey = state.diagramId;
    closeImportDialog();
    state.workspaceMode = 'edit'; renderAll();
    editorController.openXML(pending.analysis.xml, { filename: pending.filename, diagramHint: canonical ? detectedType : null, pageId, dirty: true });
    await setWorkspaceMode('edit', { loadCanonical: false });
  }

  function openCloudDocument(record) {
    if (!record?.diagram?.id || !record.xml) return false;
    const key = `cloud-${record.diagram.id}`;
    const canonicalId = data.diagrams.some((item) => item.id === record.diagram.source_diagram_id)
      ? record.diagram.source_diagram_id : null;
    const base = canonicalId ? data.diagrams.find((item) => item.id === canonicalId) : null;
    const descriptor = {
      ...(base || {}),
      id: key,
      canonicalDiagramId: canonicalId,
      title: record.diagram.title,
      titleMs: record.diagram.title,
      description: record.diagram.visibility === 'canonical' ? 'Cloud canonical diagram' : 'Private cloud diagram',
      descriptionMs: record.diagram.visibility === 'canonical' ? 'Rajah awan kanonikal' : 'Rajah awan peribadi',
      category: 'Cloud',
      status: 'current',
      layout: base?.layout || 'free',
      columns: base?.columns || [],
      sessionOnly: false,
      cloud: true,
      readOnly: !record.diagram.can_edit,
    };
    const existingIndex = state.importedDiagrams.findIndex((item) => item.id === key);
    if (existingIndex >= 0) state.importedDiagrams.splice(existingIndex, 1, descriptor);
    else state.importedDiagrams.push(descriptor);

    const analysis = editorController.preflight(record.xml);
    const svg = record.svg ? sanitizeRuntimeSVG(record.svg) : null;
    const asset = svg ? runtimeAssetFromAnalysis(svg, analysis) : (canonicalId ? assets[canonicalId] : null);
    state.runtimeDocuments.set(key, {
      workingXml: record.xml,
      pageId: analysis.selectedPage?.id || null,
      filename: `${record.diagram.title}.drawio`,
      analysis,
      dirty: Boolean(record.dirty),
      diagramType: canonicalId || record.diagram.diagram_type || 'unknown',
      runtimeSvg: svg,
      asset,
      lastValidAsset: asset,
      readOnly: !record.diagram.can_edit,
      cloud: true,
      cloudId: record.diagram.id,
      cloudBranchId: record.branch?.id || null,
      revision: record.branch?.revision || 0,
    });
    state.diagramId = key;
    state.editorDocumentKey = key;
    state.renderMode = 'actual';
    state.workspaceMode = record.diagram.can_edit ? 'edit' : 'view';
    renderAll();
    if (record.diagram.can_edit) {
      editorController.openXML(record.xml, { filename: `${record.diagram.title}.drawio`, diagramHint: canonicalId && isCanonicalEditable(canonicalId) ? canonicalId : null, pageId: analysis.selectedPage?.id || null, dirty: Boolean(record.dirty) });
      setWorkspaceMode('edit', { loadCanonical: false });
    } else {
      setWorkspaceMode('view', { loadCanonical: false });
    }
    return true;
  }

  function sanitizeRuntimeSVG(svgText) {
    const documentNode = new DOMParser().parseFromString(String(svgText || ''), 'image/svg+xml');
    if (documentNode.querySelector('parsererror') || documentNode.documentElement.tagName.toLocaleLowerCase() !== 'svg') throw new Error('Draw.io returned invalid SVG.');
    documentNode.querySelectorAll('script, iframe, object, embed, link, meta').forEach((element) => element.remove());
    documentNode.querySelectorAll('*').forEach((element) => {
      [...element.attributes].forEach((attribute) => {
        const name = attribute.name.toLocaleLowerCase();
        const value = attribute.value.trim();
        if (name.startsWith('on')) element.removeAttribute(attribute.name);
        if ((name === 'href' || name === 'xlink:href') && !/^(?:#|data:image\/|blob:)/i.test(value)) element.removeAttribute(attribute.name);
        if (name === 'style') element.setAttribute(attribute.name, value.replace(/url\((?!["']?(?:#|data:image\/))[^)]+\)/gi, 'none'));
      });
    });
    documentNode.querySelectorAll('style').forEach((element) => {
      element.textContent = element.textContent.replace(/@import[^;]+;/gi, '').replace(/url\((?!["']?(?:#|data:image\/))[^)]+\)/gi, 'none');
    });
    return new XMLSerializer().serializeToString(documentNode.documentElement);
  }

  const RUNTIME_DIAGRAM_EN = {
    domain: [
      ['Model domain berdasarkan kod TypeScript dan jadual Supabase langsung. Operasi pada entiti mewakili tanggungjawab aplikasi yang mengurus rekod, bukan kaedah ORM atau kaedah literal pada entiti.', 'Domain model based on TypeScript code and live Supabase tables. Entity operations represent application responsibilities that manage records, not ORM methods or literal methods on the entities.'],
      ['Legenda: <<entity>> = rekod Supabase; <<service>> = servis TypeScript; <<interface>> = kontrak TypeScript; JobListing menormalkan rekod public.scraped_jobs; garisan putus-putus = hubungan logik atau dependency; berlian kosong = aggregation.', 'Legend: <<entity>> = Supabase record; <<service>> = TypeScript service; <<interface>> = TypeScript contract; JobListing normalizes public.scraped_jobs records; dashed line = logical relationship or dependency; hollow diamond = aggregation.'],
      ['Rajah Kelas Domain Teras Sistem PetaKerja', 'PetaKerja Core Domain Class Diagram'],
      ['PEMETAAN, POI & DATA TERBUKA', 'MAPPING, POI & OPEN DATA'],
      ['PEKERJAAN & STATUS PENGGUNA', 'JOBS & USER STATUS'],
      ['AI & PENTADBIRAN', 'AI & ADMINISTRATION'],
      ['IDENTITI & PROFIL', 'IDENTITY & PROFILE'],
      ['dipadankan melalui provider_id', 'resolved through provider_id'],
      ['kumpulan mengikut negeri', 'groups by state'],
      ['membekalkan', 'supplies'],
      ['berada di', 'located in'],
      ['mengandungi', 'contains'],
      ['mengelaskan', 'classifies'],
      ['mengagregat', 'aggregates'],
    ],
  };

  const RUNTIME_DIAGRAM_MS = {
    'user-google-sign-in-flowchart': [
      ['PetaKerja Sign in with Google Flow Chart', 'Carta Alir Log Masuk PetaKerja dengan Google'],
      ['Google-only authentication; password sign-in, registration and password reset are not part of this flow.', 'Pengesahan Google sahaja; log masuk kata laluan, pendaftaran dan tetapan semula kata laluan tidak termasuk dalam aliran ini.'],
      ['User selects Sign in', 'Pengguna memilih Log Masuk'],
      ['Display the Google sign-in prompt', 'Paparkan prompt log masuk Google'],
      ['User selects Continue with Google', 'Pengguna memilih Teruskan dengan Google'],
      ['Start Google OAuth', 'Mulakan Google OAuth'],
      ['Google authorization completed?', 'Pengesahan Google selesai?'],
      ['Display cancellation or sign-in error', 'Paparkan pembatalan atau ralat log masuk'],
      ['Remain in guest state and display Sign in', 'Kekal dalam keadaan tetamu dan paparkan Log Masuk'],
      ['Create or update identity, account and session', 'Cipta atau kemas kini identiti, akaun dan sesi'],
      ['Redirect to PetaKerja', 'Ubah hala ke PetaKerja'],
      ['Check the active session', 'Semak sesi aktif'],
      ['Active session found?', 'Sesi aktif ditemui?'],
      ['Request the PetaKerja profile', 'Minta profil PetaKerja'],
      ['Linked profile found?', 'Profil terpaut ditemui?'],
      ['Load the linked profile', 'Muatkan profil terpaut'],
      ['Matching email profile found?', 'Profil dengan e-mel sepadan ditemui?'],
      ['Link the existing profile', 'Pautkan profil sedia ada'],
      ['Create a new PetaKerja profile', 'Cipta profil PetaKerja baharu'],
      ['Profile obtained successfully?', 'Profil berjaya diperoleh?'],
      ['Return the profile to the application', 'Pulangkan profil kepada aplikasi'],
      ['Update the signed-in user state', 'Kemas kini keadaan pengguna yang log masuk'],
      ['Display the authenticated user menu', 'Paparkan menu pengguna yang disahkan'],
      ['Start', 'Mula'],
      ['End', 'Tamat'],
      ['Yes', 'Ya'],
      ['No', 'Tidak'],
    ],
    'admin-manage-users-flowchart': [
      ['PetaKerja Administrator Manage Users Flow Chart', 'Carta Alir Pentadbir PetaKerja Mengurus Pengguna'],
      ['Precondition: the Administrator has signed in, passed the administrator-role check and opened the dashboard.', 'Prasyarat: Pentadbir telah log masuk, melepasi semakan peranan pentadbir dan membuka papan pemuka.'],
      ['Administrator selects the Users section', 'Pentadbir memilih bahagian Pengguna'],
      ['Display the loading state', 'Paparkan keadaan pemuatan'],
      ['Request recent user information', 'Minta maklumat pengguna terkini'],
      ['Retrieve up to 100 recent profiles and roles', 'Dapatkan sehingga 100 profil dan peranan terkini'],
      ['Request successful?', 'Permintaan berjaya?'],
      ['Clear loading state and display dashboard error', 'Tamatkan pemuatan dan paparkan ralat papan pemuka'],
      ['Store records and clear loading state', 'Simpan rekod dan tamatkan pemuatan'],
      ['Users returned?', 'Pengguna dipulangkan?'],
      ['Display No users returned', 'Paparkan Tiada pengguna dipulangkan'],
      ['Display the Users table', 'Paparkan jadual Pengguna'],
      ['Manage Users is read-only. Role changes, account suspension and account deletion are not implemented.', 'Urus Pengguna hanya untuk paparan. Perubahan peranan, penggantungan akaun dan pemadaman akaun belum dilaksanakan.'],
      ['Start', 'Mula'],
      ['End', 'Tamat'],
      ['Yes', 'Ya'],
      ['No', 'Tidak'],
    ],
    'admin-access-dashboard-flowchart': [
      ['PetaKerja Access Administrator Dashboard Flow Chart', 'Carta Alir Pentadbir PetaKerja Mengakses Papan Pemuka'],
      ['Administrator entry, local access guard and protected dashboard-data loading.', 'Kemasukan pentadbir, kawalan akses setempat dan pemuatan data papan pemuka terlindung.'],
      ['Precondition: The Administrator entry is selected from the signed-in user menu or the /admin route is opened directly.', 'Prasyarat: Pilihan Pentadbir dipilih daripada menu pengguna yang log masuk atau route /admin dibuka secara terus.'],
      ['Administrator selects the Admin Dashboard', 'Pentadbir memilih Papan Pemuka Pentadbir'],
      ['Check the current signed-in user', 'Semak pengguna yang sedang log masuk'],
      ['Active session found?', 'Sesi aktif ditemui?'],
      ['Return to PetaKerja and request administrator sign-in', 'Kembali ke PetaKerja dan minta log masuk pentadbir'],
      ['Administrator role allowed?', 'Peranan pentadbir dibenarkan?'],
      ['Return to PetaKerja and deny administrator access', 'Kembali ke PetaKerja dan nafikan akses pentadbir'],
      ['Open the administrator dashboard', 'Buka papan pemuka pentadbir'],
      ['Display the dashboard loading state', 'Paparkan keadaan pemuatan papan pemuka'],
      ['Request provider, AI usage and user information', 'Minta maklumat penyedia, penggunaan AI dan pengguna'],
      ['Retrieve the three protected dashboard data sets', 'Dapatkan tiga set data papan pemuka terlindung'],
      ['Dashboard requests successful?', 'Permintaan papan pemuka berjaya?'],
      ['Clear loading and display the dashboard loading error', 'Tamatkan pemuatan dan paparkan ralat pemuatan papan pemuka'],
      ['Store the returned provider, usage and user information', 'Simpan maklumat penyedia, penggunaan dan pengguna yang diterima'],
      ['Clear the dashboard loading state', 'Tamatkan keadaan pemuatan papan pemuka'],
      ['Display the administrator Overview', 'Paparkan Overview pentadbir'],
      ['Start', 'Mula'], ['End', 'Tamat'], ['Yes', 'Ya'], ['No', 'Tidak'],
    ],
    'admin-monitor-activity-flowchart': [
      ['PetaKerja Administrator Monitor System Activity Logs Flow Chart', 'Carta Alir Pentadbir PetaKerja Memantau Aktiviti Sistem'],
      ['Current implementation: the latest 100 AI assistant usage events, not general server logs.', 'Pelaksanaan semasa: 100 peristiwa penggunaan pembantu AI terkini, bukan log pelayan umum.'],
      ['Precondition: The Administrator is signed in, has the admin or owner role, and the Admin Dashboard is open.', 'Prasyarat: Pentadbir telah log masuk, mempunyai peranan admin atau owner, dan Papan Pemuka Pentadbir telah dibuka.'],
      ['Administrator selects the Usage section', 'Pentadbir memilih bahagian Usage'],
      ['Display the loading state', 'Paparkan keadaan pemuatan'],
      ['Request recent AI activity information', 'Minta maklumat aktiviti AI terkini'],
      ['Retrieve up to 100 recent AI usage events and calculate totals', 'Dapatkan sehingga 100 peristiwa penggunaan AI terkini dan kira jumlah'],
      ['Request successful?', 'Permintaan berjaya?'],
      ['Clear loading and display the dashboard loading error', 'Tamatkan pemuatan dan paparkan ralat pemuatan papan pemuka'],
      ['Store the activity rows and totals, then clear loading', 'Simpan baris aktiviti dan jumlah, kemudian tamatkan pemuatan'],
      ['Activity events returned?', 'Peristiwa aktiviti dipulangkan?'],
      ['Display No usage events yet', 'Paparkan Belum ada peristiwa penggunaan'],
      ['Display usage totals and the activity table', 'Paparkan jumlah penggunaan dan jadual aktiviti'],
      ['Start', 'Mula'], ['End', 'Tamat'], ['Yes', 'Ya'], ['No', 'Tidak'],
    ],
    'admin-manage-ai-configuration-flowchart': [
      ['PetaKerja Administrator Manage AI Chatbot Configuration Flow Chart', 'Carta Alir Pentadbir PetaKerja Mengurus Konfigurasi Chatbot AI'],
      ['Provider visibility for administrators and owners; shared-key and model-refresh actions are owner-only.', 'Status penyedia boleh dilihat oleh admin dan owner; tindakan kunci bersama serta segar semula model hanya untuk owner.'],
      ['Precondition: The Administrator is signed in, has the admin or owner role, and the Admin Dashboard is open.', 'Prasyarat: Pentadbir telah log masuk, mempunyai peranan admin atau owner, dan Papan Pemuka Pentadbir telah dibuka.'],
      ['Administrator selects the AI Providers section', 'Pentadbir memilih bahagian AI Providers'],
      ['Display the loading state', 'Paparkan keadaan pemuatan'],
      ['Request provider configuration', 'Minta konfigurasi penyedia'],
      ['Read platform credentials and combine them with the provider registry', 'Baca kelayakan platform dan gabungkan dengan daftar penyedia'],
      ['Request successful?', 'Permintaan berjaya?'],
      ['Clear loading and display the provider loading error', 'Tamatkan pemuatan dan paparkan ralat pemuatan penyedia'],
      ['Display provider names, key status, model counts and fetch status', 'Paparkan nama penyedia, status kunci, bilangan model dan status pengambilan'],
      ['Owner role?', 'Peranan owner?'],
      ['Display provider information in read-only mode and explain the owner requirement', 'Paparkan maklumat penyedia dalam mod baca sahaja dan jelaskan keperluan owner'],
      ['Owner action?', 'Tindakan owner?'],
      ['Open the platform-key dialog', 'Buka dialog kunci platform'],
      ['Enter and submit a platform API key', 'Masukkan dan hantar kunci API platform'],
      ['Provider and key valid?', 'Penyedia dan kunci sah?'],
      ['Display the platform-key validation error', 'Paparkan ralat pengesahan kunci platform'],
      ['Encrypt and save the shared platform credential', 'Enkripsi dan simpan kelayakan platform bersama'],
      ['Credential saved successfully?', 'Kelayakan berjaya disimpan?'],
      ['Display the platform-key request error', 'Paparkan ralat permintaan kunci platform'],
      ['Record the platform key saved audit event', 'Rekod peristiwa audit kunci platform disimpan'],
      ['Display success for the saved platform key', 'Paparkan kejayaan kunci platform yang disimpan'],
      ['Request model-list refresh', 'Minta segar semula senarai model'],
      ['Read available platform credentials', 'Baca kelayakan platform yang tersedia'],
      ['Refresh every supported provider and continue after individual failures', 'Segarkan setiap penyedia yang disokong dan teruskan selepas kegagalan individu'],
      ['Any provider failures?', 'Ada kegagalan penyedia?'],
      ['Save model metadata, invalidate caches and display complete success', 'Simpan metadata model, batalkan cache dan paparkan kejayaan penuh'],
      ['Save successful metadata, record errors and display partial results', 'Simpan metadata berjaya, rekod ralat dan paparkan hasil separa'],
      ['Reload the provider table', 'Muatkan semula jadual penyedia'],
      ['Reload provider information and display the result', 'Muatkan semula maklumat penyedia dan paparkan hasil'],
      ['Start', 'Mula'], ['End', 'Tamat'], ['Yes', 'Ya'], ['No', 'Tidak'], ['Save key', 'Simpan kunci'], ['Refresh models', 'Segar semula model'], ['Finish', 'Selesai'],
    ],
    'admin-sign-out-flowchart': [
      ['PetaKerja Administrator Sign Out Flow Chart', 'Carta Alir Pentadbir PetaKerja Log Keluar'],
      ['Better Auth sign-out followed by application-state and administrator-dashboard synchronization.', 'Log keluar Better Auth diikuti penyelarasan keadaan aplikasi dan papan pemuka pentadbir.'],
      ['Precondition: The Administrator is signed in and an authenticated Sign Out control is available.', 'Prasyarat: Pentadbir telah log masuk dan kawalan Sign Out yang disahkan tersedia.'],
      ['Administrator selects Sign Out', 'Pentadbir memilih Sign Out'],
      ['Disable the available Sign Out control', 'Nyahaktifkan kawalan Sign Out yang tersedia'],
      ['Submit the sign-out request to Better Auth', 'Hantar permintaan log keluar kepada Better Auth'],
      ['Sign-out successful?', 'Log keluar berjaya?'],
      ['Keep the current session and re-enable Sign Out', 'Kekalkan sesi semasa dan aktifkan semula Sign Out'],
      ['Invalidate the session and clear its cookie', 'Batalkan sesi dan kosongkan kukinya'],
      ['Clear the PetaKerja user state', 'Kosongkan keadaan pengguna PetaKerja'],
      ['Notify authentication subscribers', 'Maklumkan pelanggan pengesahan'],
      ['Display the signed-out dashboard access state and guest menu', 'Paparkan keadaan akses papan pemuka signed-out dan menu tetamu'],
      ['Start', 'Mula'], ['End', 'Tamat'], ['Yes', 'Ya'], ['No', 'Tidak'],
    ],
  };

  function translateRuntimeSvg(svg, diagramType, language, localizedPairs = []) {
    const fallbackPairs = language === 'en' ? RUNTIME_DIAGRAM_EN[diagramType] : RUNTIME_DIAGRAM_MS[diagramType];
    const replacements = new Map();
    (fallbackPairs || []).forEach(([source, target]) => {
      if (source && target && source !== target) replacements.set(source, target);
    });
    localizedPairs.forEach((pair) => {
      const target = pair?.[language];
      if (!target) return;
      [pair.en, pair.ms].filter(Boolean).forEach((source) => {
        if (source !== target) replacements.set(source, target);
      });
    });
    if (!replacements.size) return svg;
    const parsed = new DOMParser().parseFromString(svg, 'image/svg+xml');
    if (parsed.querySelector('parsererror')) return svg;
    const ordered = [...replacements.entries()].sort((left, right) => right[0].length - left[0].length);
    const walker = parsed.createTreeWalker(parsed.documentElement, NodeFilter.SHOW_TEXT);
    let textNode = walker.nextNode();
    while (textNode) {
      if (!['style', 'script'].includes(textNode.parentElement?.localName)) {
        let translated = textNode.nodeValue || '';
        const applied = [];
        ordered.forEach(([source, target], index) => {
          if (!translated.includes(source)) return;
          const token = `\uE000PETAKERJA_${index}_\uE001`;
          translated = translated.split(source).join(token);
          applied.push([token, target]);
        });
        applied.forEach(([token, target]) => { translated = translated.split(token).join(target); });
        textNode.nodeValue = translated;
      }
      textNode = walker.nextNode();
    }
    return new XMLSerializer().serializeToString(parsed.documentElement);
  }

  function runtimeAssetFromAnalysis(svg, analysis) {
    const page = analysis?.selectedPage;
    const localizedPairs = editorAPI?.localizedLabelPairs?.(analysis?.xml || '') || [];
    if (!page) return {
      svg: {
        ms: translateRuntimeSvg(svg, state.diagramId, 'ms', localizedPairs),
        en: translateRuntimeSvg(svg, state.diagramId, 'en', localizedPairs),
      },
      components: [], connections: [],
    };
    const components = (page.matches || []).filter((match) => match.identity).map((match) => ({
      componentKey: match.identity.componentKey,
      id: match.identity.target || match.identity.key,
      label: match.identity.label,
      labelEn: match.identity.labelEn,
      tableName: match.identity.tableName,
      nodeIds: match.identity.nodeIds?.length ? match.identity.nodeIds : (match.identity.target ? [match.identity.target] : []),
      cellIds: [match.cellId],
      uiHotspots: match.identity.uiHotspots || [],
      matchTexts: [match.identity.label, match.identity.labelEn].filter(Boolean),
    }));
    const connections = (page.relations || []).filter((relation) => relation.sourceComponentKey && relation.targetComponentKey).map((relation) => ({
      id: relation.id,
      sourceComponentKey: relation.sourceComponentKey,
      targetComponentKey: relation.targetComponentKey,
      kind: relation.kind,
      label: relation.labels?.simple || { ms: relation.label || '', en: relation.label || '' },
      labels: relation.labels || null,
      petakerjaKey: relation.petakerjaKey || '',
    }));
    const diagramType = page.detection?.diagramType || state.diagramId;
    // Draw.io occasionally omits wrapper metadata for nested UML frames or
    // actor shapes during its SVG export. Preserve interactivity for canonical
    // documents by recovering only components whose original cell IDs are
    // actually present in the runtime SVG. Reorganised/imported diagrams with
    // different IDs continue to rely solely on semantic/stable-key matching.
    const canonicalAsset = assets[diagramType] || assets[state.diagramId];
    if (canonicalAsset) {
      const runtimeSvgDocument = new DOMParser().parseFromString(svg, 'image/svg+xml');
      const presentCellIds = new Set([...runtimeSvgDocument.querySelectorAll('[data-cell-id]')]
        .map((element) => element.getAttribute('data-cell-id')).filter(Boolean));
      const componentKeys = new Set(components.map((component) => component.componentKey));
      (canonicalAsset.components || []).forEach((component) => {
        if (componentKeys.has(component.componentKey)) return;
        const cellIds = (component.cellIds || []).filter((cellId) => presentCellIds.has(cellId));
        if (!cellIds.length) return;
        components.push({ ...component, cellIds });
        componentKeys.add(component.componentKey);
      });
      const connectionIds = new Set(connections.map((connection) => connection.id));
      (canonicalAsset.connections || []).forEach((connection) => {
        if (connectionIds.has(connection.id)) return;
        if (connection.visual !== false && !presentCellIds.has(connection.id)) return;
        if (!componentKeys.has(connection.sourceComponentKey) || !componentKeys.has(connection.targetComponentKey)) return;
        connections.push({ ...connection });
        connectionIds.add(connection.id);
      });
    }
    return {
      svg: {
        ms: translateRuntimeSvg(svg, diagramType, 'ms', localizedPairs),
        en: translateRuntimeSvg(svg, diagramType, 'en', localizedPairs),
      },
      components, connections, runtime: true,
      supportsLabelModes: components.some((item) => item.labels?.simple && item.labels?.code)
        || connections.some((item) => item.labels?.simple && item.labels?.code),
      supportsSequenceLabels: connections.some((item) => item.labels?.simple && item.labels?.code),
    };
  }

  function updateRuntimeDocument(snapshot, key = state.editorDocumentKey || state.diagramId) {
    if (!snapshot?.xml || !key) return;
    const existing = state.runtimeDocuments.get(key) || {};
    state.runtimeDocuments.set(key, {
      ...existing,
      workingXml: snapshot.xml,
      pageId: snapshot.pageId,
      filename: snapshot.filename,
      analysis: snapshot.analysis,
      dirty: snapshot.dirty,
      diagramType: snapshot.analysis?.selectedPage?.detection?.diagramType || snapshot.diagramId,
      runtimeSvg: existing.workingXml === snapshot.xml ? existing.runtimeSvg : null,
      asset: existing.workingXml === snapshot.xml ? existing.asset : null,
      lastValidAsset: existing.lastValidAsset || existing.asset || null,
    });
  }

  async function refreshRuntimeView() {
    const key = state.editorDocumentKey || state.diagramId;
    const runtime = state.runtimeDocuments.get(key);
    if (!runtime?.workingXml || !editorController.available) return runtime?.asset || null;
    state.runtimeExporting = true;
    els.statusMessage.textContent = state.language === 'en' ? 'Exporting the current Draw.io layout...' : 'Mengeksport susun atur Draw.io semasa...';
    try {
      const exported = await editorController.exportRuntimeSVG();
      const sanitized = sanitizeRuntimeSVG(exported.svg);
      const analysis = editorController.analysis;
      const asset = runtimeAssetFromAnalysis(sanitized, analysis);
      const next = { ...runtime, workingXml: exported.xml || runtime.workingXml, analysis, runtimeSvg: sanitized, asset, lastValidAsset: asset };
      state.runtimeDocuments.set(key, next);
      els.statusMessage.textContent = state.language === 'en' ? 'View updated from the current Draw.io document.' : 'Paparan dikemas kini daripada dokumen Draw.io semasa.';
      return next.asset;
    } catch (error) {
      els.statusMessage.textContent = `${state.language === 'en' ? 'Could not refresh View' : 'Paparan tidak dapat dikemas kini'}: ${error.message}`;
      return runtime.asset || null;
    } finally {
      state.runtimeExporting = false;
    }
  }

  function renderWorkspaceControls() {
    const editorEnabled = runtimeCapabilities.editor !== false;
    const importEnabled = runtimeCapabilities.import !== false;
    const agentEnabled = runtimeCapabilities.agent !== false;
    const localWorkspaceEnabled = runtimeCapabilities.localWorkspace !== false;
    const documentLayout = isDocumentDiagram();
    const editable = isEditableDiagram();
    const canEdit = editorEnabled && editable && editorController?.available;
    els.workspaceModeControl.hidden = documentLayout || !editorEnabled || !editable;
    els.workspaceView.setAttribute('aria-pressed', String(state.workspaceMode === 'view'));
    els.workspaceEdit.setAttribute('aria-pressed', String(state.workspaceMode === 'edit'));
    els.workspaceAgent.setAttribute('aria-pressed', String(state.workspaceMode === 'agent'));
    // In file:// mode Edit remains clickable so launch guidance is not hidden
    // behind native disabled-button behaviour. Non-editable views stay disabled.
    els.workspaceEdit.disabled = !editable;
    els.workspaceEdit.setAttribute('aria-disabled', String(!editable));
    els.workspaceEdit.dataset.runtimeRequired = String(editable && !canEdit);
    els.workspaceEdit.title = canEdit ? '' : t('ui.editorHttpRequired');
    els.workspaceAgent.hidden = !agentEnabled;
    els.workspaceAgent.disabled = !agentEnabled || !editable;
    els.workspaceAgent.setAttribute('aria-disabled', String(!agentEnabled || !editable));
    els.workspaceAgent.dataset.runtimeRequired = String(editable && !canEdit);
    els.workspaceAgent.title = canEdit ? '' : t('ui.editorHttpRequired');
    els.importButton.hidden = documentLayout || !importEnabled;
    els.importButton.disabled = !importEnabled;
    els.importButton.setAttribute('aria-disabled', 'false');
    els.importButton.dataset.runtimeRequired = String(!editorController?.available);
    els.importButton.title = editorController?.available ? '' : t('ui.editorHttpRequired');
    els.validateButton.hidden = !editorEnabled || state.workspaceMode === 'view'; els.saveButton.hidden = !editorEnabled || state.workspaceMode === 'view';
    els.workspaceSaveButton.hidden = !localWorkspaceEnabled || state.workspaceMode === 'view' || !state.workspaceDiagramIds.has(state.diagramId);
    byId('zoom-out').parentElement.hidden = documentLayout || state.workspaceMode !== 'view';
    els.referenceButton.hidden = documentLayout || state.workspaceMode !== 'view' || !activeDiagram().reference;
    const showDiagramLabels = !documentLayout && (state.workspaceMode === 'view' || state.workspaceMode === 'edit')
      && effectiveMode() === 'actual' && diagramSupportsLabelModes();
    els.diagramLabelControl.hidden = !showDiagramLabels;
    els.diagramSimple.disabled = state.diagramLabelModeSwitching;
    els.diagramCode.disabled = state.diagramLabelModeSwitching;
    els.diagramSimple.setAttribute('aria-pressed', String(state.diagramLabelMode === 'simple'));
    els.diagramCode.setAttribute('aria-pressed', String(state.diagramLabelMode === 'code'));
    cloudManager?.updateControls();
  }

  async function setWorkspaceMode(mode, options = {}) {
    if (mode === 'agent' && runtimeCapabilities.agent === false) {
      els.statusMessage.textContent = state.language === 'en' ? 'Agent Mode is available only in the trusted local Explorer.' : 'Mod Ejen hanya tersedia dalam Explorer tempatan yang dipercayai.';
      return;
    }
    if ((mode === 'edit' || mode === 'agent') && (!isEditableDiagram() || !editorController.available)) {
      if (isEditableDiagram() && !editorController.available) showRuntimeDialog();
      else els.statusMessage.textContent = t('ui.editorHttpRequired');
      return;
    }
    if (mode === 'view' && state.workspaceMode !== 'view' && runtimeDocument(state.editorDocumentKey || state.diagramId)?.workingXml) {
      await refreshRuntimeView();
    }
    state.workspaceMode = mode;
    document.body.classList.toggle('is-editor-mode', mode === 'edit' || mode === 'agent');
    document.body.classList.toggle('is-agent-mode', mode === 'agent');
    els.graph.hidden = mode !== 'view'; els.editorSurface.hidden = mode === 'view';
    els.agentPanel.hidden = mode !== 'agent';
    els.validationPanel.hidden = mode === 'view';
    renderWorkspaceControls();
    if (mode === 'edit' || mode === 'agent') {
      state.renderMode = 'actual';
      els.editorSurface.classList.remove('is-ready');
      renderValidation(state.editorAnalysis);
      const runtime = runtimeDocument();
      if (runtime?.workingXml && state.editorDocumentKey !== state.diagramId) {
        state.editorDocumentKey = state.diagramId;
        editorController.openXML(runtime.workingXml, { filename: runtime.filename, diagramHint: isCanonicalEditable(runtime.diagramType) ? runtime.diagramType : null, pageId: runtime.pageId, dirty: runtime.dirty });
      } else if (options.loadCanonical !== false && (editorController.diagramId !== state.diagramId || !editorController.workingXml || state.editorDocumentKey !== state.diagramId)) {
        try {
          state.editorDocumentKey = state.diagramId;
          const analysis = await editorController.openCanonical(state.diagramId);
          if (analysis.fatal) renderValidation(analysis, { changeKind: 'load' });
        } catch (error) {
          renderValidation({ selectedPage: null, issues: [{ ruleId: 'editor-source', severity: 'fatal', message: { ms: error.message, en: error.message } }] }, { changeKind: 'load' });
        }
      } else {
        editorController.startFrame();
      }
    } else {
      renderDiagram();
    }
  }

  function renderAll(options = {}) {
    renderStaticLanguage(); populateControls(); renderDiagram(); renderUI(); renderDetails(); updateMobilePanels();
    renderWorkspaceControls();
    if (state.workspaceMode !== 'view') renderValidation(state.editorAnalysis);
    if (options.announce) els.statusMessage.textContent = options.announce;
  }

  function renderCodeSnippet(diagram) {
    const snippet = codeSnippetText(diagram);
    const sourceFiles = (diagram.sourceFiles || []).map((file) => `<li><code>${escapeHTML(file)}</code></li>`).join('');
    const english = state.snippetLanguage === 'en';
    const legendItems = [
      ['control', 'If', english ? 'Control flow' : 'Kawalan aliran'],
      ['function', english ? 'SearchPOI()' : 'CariPOI()', english ? 'Function' : 'Fungsi'],
      ['message', english ? '"Message"' : '"Mesej"', english ? 'Message' : 'Mesej'],
      ['system', 'MapLibre', english ? 'System/data' : 'Sistem/data'],
    ].map(([type, sample, label]) => `<li><code class="pseudo-token pseudo-token--${type}">${escapeHTML(sample)}</code><span>${escapeHTML(label)}</span></li>`).join('');
    const upstreamRows = (diagram.upstreamSources || []).map((source) => {
      const method = english ? source.methodEn : source.method;
      const requestScope = english ? source.requestScopeEn : source.requestScope;
      const websiteLabel = String(source.website || '').replace(/^https:\/\//, '').replace(/\/$/, '');
      return `<tr data-source-kind="${escapeHTML(source.kind)}"><th scope="row">${escapeHTML(source.name)}</th><td><a href="${escapeHTML(source.website)}" target="_blank" rel="noopener noreferrer">${escapeHTML(websiteLabel)}</a></td><td>${escapeHTML(method)}</td><td>${escapeHTML(requestScope)}</td></tr>`;
    }).join('');
    const upstreamSourceTable = upstreamRows ? `<section class="code-upstream-sources" aria-labelledby="code-upstream-sources-title">
      <div class="code-upstream-sources__header">
        <h4 id="code-upstream-sources-title">${escapeHTML(english ? 'Verified Live Search sources' : 'Sumber Carian Langsung yang disahkan')}</h4>
        <button type="button" class="secondary-button" data-copy-upstream-table><i data-bp-icon="copy-plus" aria-hidden="true"></i><span>${escapeHTML(t('ui.copyTable'))}</span></button>
      </div>
      <div class="code-upstream-table-wrap" role="region" aria-label="${escapeHTML(english ? 'Live Search source table' : 'Jadual sumber Carian Langsung')}">
        <table class="code-upstream-table">
          <thead><tr><th scope="col">${escapeHTML(english ? 'Source' : 'Sumber')}</th><th scope="col">${escapeHTML(english ? 'Website' : 'Laman')}</th><th scope="col">${escapeHTML(english ? 'Method' : 'Kaedah')}</th><th scope="col">${escapeHTML(english ? 'Request scope' : 'Skop permintaan')}</th></tr></thead>
          <tbody>${upstreamRows}</tbody>
        </table>
      </div>
    </section>` : '';
    const markerFlowSteps = english ? diagram.markerFlowEn : diagram.markerFlow;
    const markerFlowTitle = english ? diagram.markerFlowTitleEn : diagram.markerFlowTitle;
    const markerFlowItems = (markerFlowSteps || []).map((step, index, steps) => `<li><span>${escapeHTML(step)}</span>${index < steps.length - 1 ? '<span class="code-marker-flow__arrow" aria-hidden="true">↓</span>' : ''}</li>`).join('');
    const markerFlow = markerFlowItems ? `<section class="code-marker-flow" aria-labelledby="code-marker-flow-title">
      <div class="code-marker-flow__header">
        <h4 id="code-marker-flow-title">${escapeHTML(markerFlowTitle)}</h4>
        <button type="button" class="secondary-button" data-copy-marker-flow><i data-bp-icon="copy-plus" aria-hidden="true"></i><span>${escapeHTML(t('ui.copyFlow'))}</span></button>
      </div>
      <ol>${markerFlowItems}</ol>
    </section>` : '';
    els.graphViewport.innerHTML = `<article class="code-snippet-view" aria-labelledby="code-snippet-heading">
      <header class="code-snippet-header">
        <div><p class="eyebrow">${escapeHTML(t('ui.reportReadyCode'))}</p><h3 id="code-snippet-heading">${escapeHTML(snippet.reportHeading)}</h3></div>
        <div class="code-snippet-tools">
          <div class="segmented code-snippet-language" role="group" aria-label="${escapeHTML(t('ui.snippetLanguage'))}">
            <button type="button" data-snippet-language="ms" aria-pressed="${state.snippetLanguage === 'ms'}">BM</button>
            <button type="button" data-snippet-language="en" aria-pressed="${state.snippetLanguage === 'en'}">English</button>
          </div>
          <div class="code-snippet-actions" aria-label="${escapeHTML(state.language === 'en' ? 'Copy report content' : 'Salin kandungan laporan')}">
            <button type="button" class="secondary-button" data-copy-snippet-code><i data-bp-icon="copy-plus" aria-hidden="true"></i><span>${escapeHTML(t('ui.copyCode'))}</span></button>
            <button type="button" class="secondary-button" data-copy-snippet-caption><i data-bp-icon="heading" aria-hidden="true"></i><span>${escapeHTML(t('ui.copyCaption'))}</span></button>
          </div>
        </div>
      </header>
      <div class="code-snippet-legend" aria-label="${escapeHTML(english ? 'Semantic colour legend' : 'Petunjuk warna semantik')}"><span class="code-snippet-legend__title">${escapeHTML(english ? 'Colour meaning:' : 'Maksud warna:')}</span><ul>${legendItems}</ul></div>
      ${upstreamSourceTable}
      <pre class="report-code-block" tabindex="0" aria-label="${escapeHTML(snippet.reportHeading)}"><code>${codeSnippetHighlighter.highlightHTML(snippet.code)}</code></pre>
      <section class="report-caption-preview" aria-labelledby="report-caption-title"><h4 id="report-caption-title">${escapeHTML(t('ui.reportCaption'))}</h4><p>${escapeHTML(snippet.caption)}</p></section>
      ${markerFlow}
      <details class="code-source-files"><summary>${escapeHTML(t('ui.codeSources'))}</summary><ul>${sourceFiles}</ul></details>
    </article>`;
    window.renderBlueprintIcons?.(els.graphViewport);
  }

  function dictionaryTableDefinition(table) {
    const english = state.reportTableLanguage === 'en';
    const showSize = state.dictionaryColumnMode === 'size';
    return {
      id: table.id,
      title: reportValue(table.title),
      source: reportValue(table.source),
      note: reportValue(table.operation),
      sourceLabel: english ? 'Source' : 'Sumber',
      noteLabel: english ? 'Note' : 'Catatan',
      columns: [
        { label: english ? 'No.' : 'Bil.', width: '7%' },
        { label: english ? 'Field' : 'Medan', width: '19%' },
        { label: english ? 'Data Type' : 'Jenis Data', width: '15%' },
        { label: showSize ? (english ? 'Data Size' : 'Saiz Data') : (english ? 'Required / Constraints' : 'Wajib / Kekangan'), width: '25%' },
        { label: english ? 'Description' : 'Huraian', width: '34%' },
      ],
      rows: (table.fields || []).map((field, index) => [index + 1, field.name, reportValue(field.type), reportValue(showSize ? field.size : field.constraints), reportValue(field.description)]),
      rowHeaderIndex: 1,
    };
  }

  function useCaseTableDefinition(useCase) {
    const english = state.reportTableLanguage === 'en';
    return {
      id: useCase.id.toLowerCase(),
      title: `${useCase.id} — ${reportValue(useCase.name)}`,
      source: english ? 'PetaKerja System Use Case Diagram' : 'Rajah Kes Guna Sistem PetaKerja',
      note: english ? 'Relationships verified against the current use-case diagram asset.' : 'Hubungan disahkan terhadap aset rajah kes guna semasa.',
      sourceLabel: english ? 'Source' : 'Sumber',
      noteLabel: english ? 'Note' : 'Catatan',
      columns: [{ label: english ? 'Item' : 'Perkara', width: '24%' }, { label: english ? 'Specification' : 'Spesifikasi', width: '76%' }],
      rows: [
        ['ID', useCase.id],
        [english ? 'Name' : 'Nama', reportValue(useCase.name)],
        [english ? 'Purpose' : 'Tujuan', reportValue(useCase.purpose)],
        [english ? 'Actor' : 'Pelakon', reportValue(useCase.actors)],
        [english ? 'Preconditions' : 'Prasyarat', reportList(useCase.preconditions)],
        [english ? 'Main Scenario' : 'Senario Utama', reportList(useCase.mainFlow)],
        [english ? 'Alternative Scenario' : 'Senario Alternatif', reportList(useCase.alternatives)],
        [english ? 'Postconditions' : 'Pascasyarat', reportList(useCase.postconditions)],
        [english ? 'Relationships' : 'Hubungan', reportList(useCase.relationships)],
      ],
      rowHeaderIndex: 0,
    };
  }

  function reportPageSections(page) {
    if (!page) return [];
    if (Array.isArray(page.sections)) return page.sections.map((section) => ({
      ...section,
      title: reportValue(section.title),
      description: reportValue(section.description),
      tables: (section.tables || []).map(dictionaryTableDefinition),
    }));
    const definitions = (page.useCases || []).map(useCaseTableDefinition);
    const english = state.reportTableLanguage === 'en';
    return [
      {
        id: 'pengguna-dan-bersama', title: english ? 'User and shared functions' : 'Pengguna dan fungsi bersama',
        description: english ? 'User use cases together with authentication and sign-out functions also used by administrators.' : 'Kes guna pengguna serta fungsi pengesahan dan log keluar yang turut digunakan oleh pentadbir.',
        tables: definitions.slice(0, 11),
      },
      {
        id: 'pentadbir', title: english ? 'Administrator' : 'Pentadbir',
        description: english ? 'Protected use cases for the admin or owner role.' : 'Kes guna terlindung bagi peranan admin atau owner.',
        tables: definitions.slice(11),
      },
    ];
  }

  function reportCellMarkup(value) {
    if (!Array.isArray(value)) return escapeHTML(value);
    return `<ol>${value.map((item) => `<li>${escapeHTML(item)}</li>`).join('')}</ol>`;
  }

  function reportTableMarkup(table) {
    const english = state.reportTableLanguage === 'en';
    const headings = table.columns.map((column, index) => {
      const selectLabel = english ? `Select ${column.label} column` : `Pilih lajur ${column.label}`;
      return `<th scope="col" data-report-column-index="${index}" data-report-row-index="-1">
        <span class="fyp-report-column-heading"><span>${escapeHTML(column.label)}</span><button type="button" data-report-column-select="${escapeHTML(table.id)}" data-report-column-index="${index}" data-report-column-label="${escapeHTML(column.label)}" aria-label="${escapeHTML(selectLabel)}" title="${escapeHTML(selectLabel)}" aria-pressed="false"><i data-bp-icon="chevron-down" aria-hidden="true"></i></button></span>
      </th>`;
    }).join('');
    const columns = `<colgroup>${table.columns.map((column) => `<col style="width:${escapeHTML(column.width)}">`).join('')}</colgroup>`;
    const rows = table.rows.map((row, rowIndex) => `<tr data-report-row-index="${rowIndex}">${table.columns.map((_column, index) => {
      const tag = index === table.rowHeaderIndex ? 'th' : 'td';
      const scope = tag === 'th' ? ' scope="row"' : '';
      return `<${tag}${scope} data-report-column-index="${index}" data-report-row-index="${rowIndex}">${reportCellMarkup(row[index])}</${tag}>`;
    }).join('')}</tr>`).join('');
    const sourceId = `fyp-report-source-${table.id}`;
    return `<article class="fyp-report-table-card" data-report-table-card="${escapeHTML(table.id)}">
      <header class="fyp-report-table-card__header">
        <div><h4>${escapeHTML(table.title)}</h4><p id="${escapeHTML(sourceId)}"><strong>${escapeHTML(table.sourceLabel || 'Sumber')}:</strong> ${escapeHTML(table.source)}</p></div>
        <button type="button" class="secondary-button" data-copy-report-table="${escapeHTML(table.id)}"><i data-bp-icon="copy-plus" aria-hidden="true"></i><span>${escapeHTML(t('ui.copyTable'))}</span></button>
      </header>
      <div class="fyp-report-table-wrap" role="region" aria-label="${escapeHTML(table.title)}" tabindex="0">
        <table class="fyp-report-table" aria-describedby="${escapeHTML(sourceId)}">
          <caption>${escapeHTML(table.title)}</caption>${columns}<thead><tr>${headings}</tr></thead><tbody>${rows}</tbody>
        </table>
      </div>
      <p class="fyp-report-table-note"><strong>${escapeHTML(table.noteLabel || 'Catatan')}:</strong> ${escapeHTML(table.note)}</p>
    </article>`;
  }

  function renderReportTables(diagram) {
    const page = activeReportPage(diagram);
    const sections = reportPageSections(page);
    if (!page) {
      els.graphViewport.innerHTML = `<p class="empty-state">${escapeHTML(state.language === 'en' ? 'Report-table data is unavailable.' : 'Data jadual laporan tidak tersedia.')}</p>`;
      return;
    }
    const english = state.reportTableLanguage === 'en';
    const isDictionary = diagram.reportTableKey === 'kamus-data';
    const languageControl = `<div class="segmented fyp-report-control" role="group" aria-label="${escapeHTML(t('ui.reportLanguage'))}">
      <button type="button" data-report-language="ms" aria-pressed="${state.reportTableLanguage === 'ms'}">BM</button>
      <button type="button" data-report-language="en" aria-pressed="${state.reportTableLanguage === 'en'}">English</button>
    </div>`;
    const columnControl = isDictionary ? `<div class="segmented fyp-report-control" role="group" aria-label="${escapeHTML(t('ui.dictionaryColumn'))}">
      <button type="button" data-report-column-mode="constraints" aria-pressed="${state.dictionaryColumnMode === 'constraints'}">${escapeHTML(english ? 'Required / Constraints' : 'Wajib / Kekangan')}</button>
      <button type="button" data-report-column-mode="size" aria-pressed="${state.dictionaryColumnMode === 'size'}">${escapeHTML(english ? 'Data Size' : 'Saiz Data')}</button>
    </div>` : '';
    const sectionMarkup = sections.map((section) => `<section class="fyp-report-section" aria-labelledby="fyp-report-section-${escapeHTML(section.id)}">
      <header class="fyp-report-section__header"><h3 id="fyp-report-section-${escapeHTML(section.id)}">${escapeHTML(section.title)}</h3><p>${escapeHTML(section.description || '')}</p></header>
      <div class="fyp-report-table-list">${section.tables.map(reportTableMarkup).join('')}</div>
    </section>`).join('');
    els.graphViewport.innerHTML = `<article class="fyp-report-view" lang="${english ? 'en' : 'ms'}" aria-labelledby="fyp-report-heading">
      <header class="fyp-report-view__header">
        <p class="eyebrow">${escapeHTML(reportValue(page.eyebrow))}</p>
        <h3 id="fyp-report-heading">${escapeHTML(reportValue(page.title))}</h3>
        <p>${escapeHTML(reportValue(page.description))}</p>
        <small>${english ? 'Verified snapshot' : 'Snapshot disahkan'}: ${escapeHTML(reportValue(fypReportTables.verifiedAt))}</small>
        <div class="fyp-report-view__tools">${languageControl}${columnControl}</div>
      </header>
      ${sectionMarkup}
    </article>`;
    window.renderBlueprintIcons?.(els.graphViewport);
    applyReportColumnSelection();
  }

  function reportColumnSelectionMessage(columnLabel) {
    return state.reportTableLanguage === 'en'
      ? `Column ${columnLabel} selected. Press Ctrl+C or Command+C to copy it.`
      : `Lajur ${columnLabel} dipilih. Tekan Ctrl+C atau Command+C untuk menyalinnya.`;
  }

  function applyReportColumnSelection() {
    const selected = state.reportColumnSelection;
    els.graphViewport.querySelectorAll('[data-report-table-card]').forEach((card) => {
      const tableSelected = selected?.tableId === card.dataset.reportTableCard;
      card.querySelectorAll('th[data-report-column-index], td[data-report-column-index]').forEach((cell) => {
        const active = tableSelected && Number(cell.dataset.reportColumnIndex) === selected.columnIndex;
        cell.classList.toggle('is-report-column-selected', active);
      });
      card.querySelectorAll('[data-report-column-select]').forEach((button) => {
        const active = tableSelected && Number(button.dataset.reportColumnIndex) === selected.columnIndex;
        button.setAttribute('aria-pressed', String(active));
      });
    });
  }

  function clearReportColumnSelection(options = {}) {
    if (!state.reportColumnSelection) return false;
    state.reportColumnSelection = null;
    applyReportColumnSelection();
    if (options.announce) {
      els.statusMessage.textContent = state.reportTableLanguage === 'en' ? 'Column selection cleared.' : 'Pemilihan lajur dikosongkan.';
    }
    return true;
  }

  function toggleReportColumnSelection(tableId, columnIndex, columnLabel) {
    const current = state.reportColumnSelection;
    const sameColumn = current?.tableId === tableId && current.columnIndex === columnIndex;
    closeReportContextMenu();
    if (sameColumn) {
      clearReportColumnSelection({ announce: true });
      return;
    }
    state.reportColumnSelection = { tableId, columnIndex };
    applyReportColumnSelection();
    els.statusMessage.textContent = reportColumnSelectionMessage(columnLabel);
  }

  function selectedReportColumnCopyData() {
    const selected = state.reportColumnSelection;
    if (!selected || !isReportTableDiagram()) return null;
    const table = activeReportTableById(selected.tableId);
    const column = table?.columns?.[selected.columnIndex];
    if (!table || !column) return null;
    const payload = codeSnippetClipboard.reportTableFragmentPayload(table, {
      kind: 'column',
      rowIndex: -1,
      columnIndex: selected.columnIndex,
    });
    return { column, payload };
  }

  function reportContextLabels() {
    return state.reportTableLanguage === 'en'
      ? { title: 'Copy for Word', selection: 'Copy selected text', cell: 'Copy cell', row: 'Copy row', column: 'Copy column', copied: 'Copied' }
      : { title: 'Salin untuk Word', selection: 'Salin teks dipilih', cell: 'Salin sel', row: 'Salin baris', column: 'Salin lajur', copied: 'Disalin' };
  }

  function activeReportTableById(tableId) {
    return reportPageSections(activeReportPage()).flatMap((section) => section.tables).find((item) => item.id === tableId) || null;
  }

  function selectedReportText() {
    const selection = window.getSelection?.();
    if (!selection || selection.isCollapsed) return '';
    const view = els.graphViewport.querySelector('.fyp-report-view');
    const anchor = selection.anchorNode?.nodeType === 1 ? selection.anchorNode : selection.anchorNode?.parentElement;
    const focus = selection.focusNode?.nodeType === 1 ? selection.focusNode : selection.focusNode?.parentElement;
    return view?.contains(anchor) && view?.contains(focus) ? selection.toString().trim() : '';
  }

  function closeReportContextMenu() {
    if (reportContextMenu) reportContextMenu.hidden = true;
    reportContextTarget = null;
  }

  function ensureReportContextMenu() {
    if (reportContextMenu) return reportContextMenu;
    reportContextMenu = document.createElement('div');
    reportContextMenu.className = 'fyp-report-context-menu';
    reportContextMenu.hidden = true;
    reportContextMenu.setAttribute('role', 'menu');
    document.body.appendChild(reportContextMenu);
    reportContextMenu.addEventListener('click', async (event) => {
      const button = event.target.closest('[data-report-context-copy]');
      if (!button || !reportContextTarget) return;
      const action = button.dataset.reportContextCopy;
      let payload;
      if (action === 'selection') {
        const plainText = reportContextTarget.selectionText;
        payload = {
          plainText,
          htmlText: `<p style="margin:0;color:#000000;font-family:'Times New Roman',serif;font-size:10pt;line-height:1.25;">${escapeHTML(plainText).replace(/\r?\n/g, '<br>')}</p>`,
        };
      } else {
        const table = activeReportTableById(reportContextTarget.tableId);
        if (!table) return;
        payload = codeSnippetClipboard.reportTableFragmentPayload(table, {
          kind: action,
          rowIndex: reportContextTarget.rowIndex,
          columnIndex: reportContextTarget.columnIndex,
        });
      }
      await codeSnippetClipboard.writeClipboardPayload(payload.plainText, payload.htmlText);
      const labels = reportContextLabels();
      els.statusMessage.textContent = `${labels.copied}: ${button.textContent.trim()}`;
      closeReportContextMenu();
    });
    return reportContextMenu;
  }

  function openReportContextMenu(event) {
    if (!isReportTableDiagram()) return;
    const cell = event.target.closest('.fyp-report-table th, .fyp-report-table td');
    const selectionText = selectedReportText();
    if (!cell && !selectionText) return;
    const card = cell?.closest('[data-report-table-card]');
    const labels = reportContextLabels();
    const actions = [];
    if (selectionText) actions.push(['selection', labels.selection]);
    if (cell && card) actions.push(['cell', labels.cell], ['row', labels.row], ['column', labels.column]);
    if (!actions.length) return;
    event.preventDefault();
    event.stopPropagation();
    reportContextTarget = {
      tableId: card?.dataset.reportTableCard || '',
      rowIndex: Number(cell?.dataset.reportRowIndex ?? -1),
      columnIndex: Number(cell?.dataset.reportColumnIndex ?? -1),
      selectionText,
    };
    const menu = ensureReportContextMenu();
    menu.setAttribute('aria-label', labels.title);
    menu.innerHTML = `<p class="fyp-report-context-menu__title">${escapeHTML(labels.title)}</p>${actions.map(([action, label]) => `<button type="button" role="menuitem" data-report-context-copy="${action}">${escapeHTML(label)}</button>`).join('')}`;
    menu.hidden = false;
    const bounds = menu.getBoundingClientRect();
    menu.style.left = `${Math.max(8, Math.min(event.clientX, window.innerWidth - bounds.width - 8))}px`;
    menu.style.top = `${Math.max(8, Math.min(event.clientY, window.innerHeight - bounds.height - 8))}px`;
    menu.querySelector('[role="menuitem"]')?.focus();
  }

  function renderDiagram() {
    closeReportContextMenu();
    const diagram = activeDiagram(); const text = diagramText(diagram); const hasAsset = Boolean(activeAsset() || runtimeDocument()?.workingXml);
    const codeLayout = isCodeDiagram(diagram);
    const reportTableLayout = isReportTableDiagram(diagram);
    document.body.classList.toggle('is-code-snippet-mode', codeLayout);
    document.body.classList.toggle('is-report-table-mode', reportTableLayout);
    els.diagramTitle.textContent = text.title; els.diagramDescription.textContent = text.description;
    els.diagramStatus.textContent = labelStatus(diagram.status); els.diagramStatus.dataset.status = diagram.status;
    els.modeControl.hidden = codeLayout || reportTableLayout || !hasAsset;
    els.actualMode.setAttribute('aria-pressed', String(effectiveMode() === 'actual'));
    els.mapMode.setAttribute('aria-pressed', String(effectiveMode() === 'map'));
    els.referenceButton.hidden = codeLayout || reportTableLayout || !diagram.reference;
    els.empty.hidden = true;
    renderWorkspaceControls();
    if (state.workspaceMode !== 'view') return;
    if (codeLayout) renderCodeSnippet(diagram);
    else if (reportTableLayout) renderReportTables(diagram);
    else if (effectiveMode() === 'actual') renderActualDiagram();
    else if (diagram.layout === 'schema') renderSchema();
    else renderGraph(diagram);
  }

  function renderActualDiagram() {
    const asset = activeAsset();
    if (!asset?.svg) { els.graphViewport.innerHTML = ''; els.empty.hidden = false; return; }
    const svgText = asset.svg[state.language] || asset.svg.en || asset.svg.ms;
    els.graphViewport.innerHTML = `<div class="diagram-transform">${svgText}</div>`;
    const transform = els.graphViewport.firstElementChild; const svg = transform.querySelector('svg');
    if (!svg) { els.empty.hidden = false; return; }
    svg.classList.add('actual-diagram');
    applyDiagramLabels(svg, asset);
    const viewBox = svg.viewBox.baseVal;
    state.naturalWidth = viewBox?.width || Number(svg.getAttribute('width')) || 1200;
    state.naturalHeight = viewBox?.height || Number(svg.getAttribute('height')) || 800;
    svg.setAttribute('width', state.naturalWidth); svg.setAttribute('height', state.naturalHeight);
    addDiagramOverlays(svg, asset.components || []);
    requestAnimationFrame(() => { if (state.fitMode) fitDiagram(); else applyTransform(); applyHighlights(); });
  }

  function replaceSvgCellLabel(svg, cellId, label) {
    if (!cellId || !label) return;
    const group = svg.querySelector(`[data-cell-id="${CSS.escape(cellId)}"]`);
    if (!group) return;
    const foreignObject = group.querySelector('foreignObject');
    if (foreignObject) {
      const leaves = [...foreignObject.querySelectorAll('div')].filter((element) => !element.querySelector('div'));
      const target = leaves.at(-1) || foreignObject.querySelector('div');
      if (target) target.textContent = label;
    }
    const text = group.querySelector('text');
    if (text) {
      const tspans = [...text.querySelectorAll('tspan')];
      if (tspans.length) { tspans[0].textContent = label; tspans.slice(1).forEach((item) => item.remove()); }
      else text.textContent = label;
    }
    group.setAttribute('aria-label', label);
  }

  function modeLabel(item) {
    const variants = item?.labels?.[state.diagramLabelMode];
    return variants?.[state.language] || variants?.en || variants?.ms || '';
  }

  function labelProjectionAsset(asset) {
    if (asset?.supportsLabelModes || asset?.supportsSequenceLabels) return asset;
    const canonical = assets[state.diagramId];
    return canonical?.supportsLabelModes || canonical?.supportsSequenceLabels ? canonical : asset;
  }

  function applyDiagramLabels(svg, asset) {
    if (!diagramSupportsLabelModes()) return;
    const labels = labelProjectionAsset(asset);
    const applied = new Set();
    (labels.labelElements || []).forEach((item) => {
      const label = modeLabel(item);
      if (!label) return;
      replaceSvgCellLabel(svg, item.cellId, label);
      applied.add(item.cellId);
    });
    (labels.components || []).forEach((component) => {
      const label = modeLabel(component);
      if (!label) return;
      (component.cellIds || []).filter((cellId) => !applied.has(cellId)).forEach((cellId) => replaceSvgCellLabel(svg, cellId, label));
    });
    (labels.connections || []).forEach((connection) => {
      const label = connectionLabel(connection);
      if (label) replaceSvgCellLabel(svg, connection.id, label);
    });
  }

  function unionBox(elements, svg) {
    let box = null;
    const svgRect = svg.getBoundingClientRect();
    const viewBox = svg.viewBox.baseVal;
    const scaleX = svgRect.width ? viewBox.width / svgRect.width : 1;
    const scaleY = svgRect.height ? viewBox.height / svgRect.height : 1;
    elements.forEach((element) => {
      try {
        const client = element.getBoundingClientRect();
        const next = {
          x: viewBox.x + (client.left - svgRect.left) * scaleX,
          y: viewBox.y + (client.top - svgRect.top) * scaleY,
          width: client.width * scaleX,
          height: client.height * scaleY,
        };
        if (!next.width && !next.height) return;
        box = box ? { x: Math.min(box.x, next.x), y: Math.min(box.y, next.y),
          maxX: Math.max(box.maxX, next.x + next.width), maxY: Math.max(box.maxY, next.y + next.height) }
          : { x: next.x, y: next.y, maxX: next.x + next.width, maxY: next.y + next.height };
      } catch (_error) { /* Hidden SVG nodes can have no box. */ }
    });
    return box && { x: box.x, y: box.y, width: box.maxX - box.x, height: box.maxY - box.y };
  }

  function componentCellElements(svg, component) {
    let elements = (component.cellIds || []).flatMap((id) => [...svg.querySelectorAll(`[data-cell-id="${CSS.escape(id)}"]`)]);
    if (!elements.length && component.componentKey) {
      // HTML parsing normalises custom SVG attribute names to lowercase.
      elements = [...svg.querySelectorAll('[data-meta-petakerjakey]')].filter((element) => {
        const stableKey = element.getAttribute('data-meta-petakerjakey') || '';
        return stableKey === component.componentKey || stableKey.endsWith(`/${component.componentKey}`);
      });
    }
    return elements;
  }

  function addDiagramOverlays(svg, components) {
    const ns = 'http://www.w3.org/2000/svg';
    const layer = document.createElementNS(ns, 'g'); layer.classList.add('diagram-overlay-layer');
    components.forEach((component, index) => {
      let targets = componentCellElements(svg, component);
      targets = targets.flatMap((element) => {
        if (element.tagName.toLowerCase() !== 'g') return [element];
        // Draw.io foreignObject elements report the whole SVG bounds when
        // injected through innerHTML. The vector primitives retain precise
        // class/use-case geometry and are therefore the stable hit target.
        const primitives = [...element.querySelectorAll('path,rect,ellipse,polygon,polyline,line,text')];
        return primitives.length ? primitives : [element];
      });
      if (!targets.length && component.matchTexts?.length) {
        targets = [...svg.querySelectorAll('text, foreignObject')].filter((element) => component.matchTexts.some((text) => element.textContent.includes(text)));
      }
      const box = unionBox(targets, svg); if (!box) return;
      const group = document.createElementNS(ns, 'g'); group.classList.add('diagram-overlay'); group.dataset.componentIndex = index;
      group.dataset.componentKey = component.componentKey || '';
      group.setAttribute('role', 'button'); group.setAttribute('tabindex', '0');
      const target = component.tableName ? `table:${component.tableName}` : component.nodeIds?.[0] || component.id;
      const accessible = component.tableName ? `${t('ui.table')} ${component.tableName}`
        : (state.language === 'en' ? component.labelEn : component.label) || nodeLabel(data.nodes[target] || { id: target, label: target });
      group.setAttribute('aria-label', accessible);
      const rect = document.createElementNS(ns, 'rect'); rect.classList.add('diagram-hitbox');
      rect.setAttribute('x', box.x - 4); rect.setAttribute('y', box.y - 4); rect.setAttribute('width', box.width + 8); rect.setAttribute('height', box.height + 8); rect.setAttribute('rx', '4');
      group.appendChild(rect); layer.appendChild(group);
      const enter = () => setHover(target, component.componentKey);
      const leave = () => clearHover();
      group.addEventListener('mouseenter', enter); group.addEventListener('mouseleave', leave);
      group.addEventListener('focus', enter); group.addEventListener('blur', leave);
      group.addEventListener('click', (event) => {
        event.stopPropagation();
        if (!state.suppressClick) pinSelection(target, component.componentKey);
      });
      group.addEventListener('keydown', (event) => {
        if (event.key === 'Enter' || event.key === ' ') {
          event.preventDefault();
          pinSelection(target, component.componentKey);
        }
      });
    });
    svg.appendChild(layer);
  }

  function renderGraph(diagram) {
    const columns = (diagram.columns || []).map((column) => column.filter((id) => data.nodes[id] && scopeAllows(data.nodes[id].scope))).filter((column) => column.length);
    if (!columns.length) { els.graphViewport.innerHTML = ''; els.empty.hidden = false; return; }
    const columnWidth = 236; const width = Math.max(980, columns.length * columnWidth + 96); const maxRows = Math.max(...columns.map((column) => column.length)); const height = Math.max(660, maxRows * 94 + 140);
    const positions = {}; const nodeHTML = [];
    columns.forEach((column, columnIndex) => column.forEach((id, rowIndex) => {
      const node = data.nodes[id]; const x = 48 + columnIndex * columnWidth; const y = 62 + rowIndex * 94;
      positions[id] = { x, y, cx: x + 88, cy: y + 31 };
      nodeHTML.push(`<button type="button" class="diagram-node" data-node="${id}" data-kind="${escapeHTML(node.kind)}" data-status="${escapeHTML(node.status)}" style="left:${x}px;top:${y}px" aria-label="${escapeHTML(nodeLabel(node))}. ${escapeHTML(labelKind(node.kind))}. ${escapeHTML(labelStatus(node.status))}"><span class="node-label">${escapeHTML(nodeLabel(node))}</span><span class="node-meta">${escapeHTML(labelKind(node.kind))}</span></button>`);
    }));
    const ids = new Set(Object.keys(positions)); const graphEdges = data.edges.filter((edge) => edge.diagrams.includes(logicalDiagramId(diagram)) && ids.has(edge.from) && ids.has(edge.to));
    const markers = `<defs><marker id="arrow-open" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto-start-reverse"><path d="M1 1L9 5L1 9" fill="none" stroke="currentColor" stroke-width="1.5"/></marker><marker id="diamond-open" viewBox="0 0 12 12" refX="1" refY="6" markerWidth="10" markerHeight="10" orient="auto"><path d="M1 6L6 1L11 6L6 11Z" fill="var(--control)" stroke="currentColor"/></marker><marker id="diamond-filled" viewBox="0 0 12 12" refX="1" refY="6" markerWidth="10" markerHeight="10" orient="auto"><path d="M1 6L6 1L11 6L6 11Z" fill="currentColor"/></marker></defs>`;
    const edgeHTML = graphEdges.map((edge, index) => {
      const from = positions[edge.from]; const to = positions[edge.to]; const direction = to.cx >= from.cx ? 1 : -1;
      const startX = from.cx + direction * 88; const endX = to.cx - direction * 88; const bend = Math.max(45, Math.abs(endX - startX) * 0.42);
      const path = `M${startX} ${from.cy}C${startX + direction * bend} ${from.cy},${endX - direction * bend} ${to.cy},${endX} ${to.cy}`;
      const marker = edge.type === 'dependency' || edge.type === 'logical' ? ' marker-end="url(#arrow-open)"' : edge.type === 'aggregation' ? ' marker-start="url(#diamond-open)"' : edge.type === 'composition' ? ' marker-start="url(#diamond-filled)"' : '';
      return `<g class="diagram-edge" data-edge="${index}" data-from="${edge.from}" data-to="${edge.to}" data-type="${edge.type}"><path d="${path}"${marker}></path>${edgeLabel(edge) ? `<text x="${(startX + endX) / 2}" y="${(from.cy + to.cy) / 2 - 7}">${escapeHTML(edgeLabel(edge))}</text>` : ''}</g>`;
    }).join('');
    els.graphViewport.innerHTML = `<div class="diagram-transform" style="width:${width}px;height:${height}px"><svg class="edge-layer" viewBox="0 0 ${width} ${height}" width="${width}" height="${height}" aria-hidden="true">${markers}${edgeHTML}</svg>${nodeHTML.join('')}</div>`;
    state.naturalWidth = width; state.naturalHeight = height; requestAnimationFrame(() => { if (state.fitMode) fitDiagram(); else applyTransform(); applyHighlights(); });
  }

  function schemaGroupLabel(group) {
    const ms = { auth: 'Auth', core: 'Profil, geo & POI', jobops: 'Jobs, pipeline, Gmail, watchlist & extractor', ai: 'AI & admin', blog: 'Blog & newsletter', community: 'Community & intel', infra: 'Infrastructure' };
    const en = { auth: 'Auth', core: 'Profile, geo & POI', jobops: 'Jobs, pipeline, Gmail, watchlist & extractor', ai: 'AI & admin', blog: 'Blog & newsletter', community: 'Community & intel', infra: 'Infrastructure' };
    return (state.language === 'en' ? en : ms)[group] || group;
  }

  function renderSchema() {
    const tables = data.schemaTables.filter((table) => scopeAllows(normaliseSchemaScope(table.group))); const groups = [...new Set(tables.map((table) => table.group))];
    els.graphViewport.innerHTML = `<div class="diagram-transform"><div class="schema-summary"><strong>${tables.length}</strong> ${t('ui.schemaScope')} · ${t('ui.schemaFull')} <strong>${data.meta.schema.tables}</strong> · <strong>${data.meta.schema.foreignKeys}</strong> FK · <strong>${data.meta.schema.logicalLinks}</strong> ${t('ui.logicalLink')}</div><div class="schema-groups">${groups.map((group) => `<section class="schema-group"><h3>${escapeHTML(schemaGroupLabel(group))}</h3><div class="schema-grid">${tables.filter((table) => table.group === group).map((table) => `<button type="button" class="schema-table${table.name === 'spatial_ref_sys' ? ' is-warning' : ''}" data-table="${escapeHTML(table.name)}" aria-label="${t('ui.table')} ${escapeHTML(table.name)}"><strong>${escapeHTML(table.name)}</strong><small>PK: ${escapeHTML(table.pk.join(', '))}</small><small>${table.rls ? t('ui.rlsOn') : t('ui.rlsOff')}</small></button>`).join('')}</div></section>`).join('')}</div></div>`;
    const transform = els.graphViewport.firstElementChild; const box = transform.getBoundingClientRect(); state.naturalWidth = Math.max(900, box.width); state.naturalHeight = Math.max(700, transform.scrollHeight);
    requestAnimationFrame(() => { if (state.fitMode) fitDiagram(); else applyTransform(); applyHighlights(); });
  }

  function fitDiagram() {
    if (isDocumentDiagram()) return;
    const padding = 18; const width = Math.max(100, els.graph.clientWidth - padding * 2); const height = Math.max(100, els.graph.clientHeight - padding * 2);
    state.scale = Math.min(width / state.naturalWidth, height / state.naturalHeight, 1.35);
    state.panX = (els.graph.clientWidth - state.naturalWidth * state.scale) / 2;
    state.panY = (els.graph.clientHeight - state.naturalHeight * state.scale) / 2;
    state.fitMode = true; applyTransform();
  }

  function applyTransform() {
    const transform = els.graphViewport.querySelector('.diagram-transform'); if (!transform) return;
    transform.style.transform = `translate(${state.panX}px, ${state.panY}px) scale(${state.scale})`;
    els.zoomValue.textContent = state.fitMode ? t('ui.fit') : `${Math.round(state.scale * 100)}%`;
  }

  function zoomBy(factor) {
    if (isDocumentDiagram()) return;
    const old = state.scale; const next = Math.min(4, Math.max(0.12, old * factor)); const cx = els.graph.clientWidth / 2; const cy = els.graph.clientHeight / 2;
    state.panX = cx - (cx - state.panX) * (next / old); state.panY = cy - (cy - state.panY) * (next / old); state.scale = next; state.fitMode = false; applyTransform();
  }

  function renderUI() {
    const view = data.uiViews.find((item) => item.id === state.uiViewId) || data.uiViews[0]; if (!view) return; const text = viewText(view);
    els.uiView.value = view.id; els.uiImage.src = view.image; els.uiImage.alt = `PetaKerja: ${text.label}`; els.uiCaption.textContent = text.description;
    const hotspots = data.hotspots.filter((hotspot) => hotspot.view === view.id && hotspot.nodes.some((nodeId) => scopeAllows(data.nodes[nodeId]?.scope || 'infra')));
    els.uiHotspots.innerHTML = hotspots.map((hotspot) => `<button type="button" class="ui-hotspot" data-hotspot="${hotspot.id}" style="left:${hotspot.x}%;top:${hotspot.y}%;width:${hotspot.w}%;height:${hotspot.h}%" aria-label="${escapeHTML(hotspotLabel(hotspot))}"><span>${escapeHTML(hotspotLabel(hotspot))}</span></button>`).join('');
    applyHighlights();
  }

  function listSection(title, values, ordered = false, className = '') {
    if (!values?.length) return ''; const tag = ordered ? 'ol' : 'ul';
    return `<section><h4>${escapeHTML(title)}</h4><${tag}${className ? ` class="${className}"` : ''}>${values.map((value) => `<li>${escapeHTML(value)}</li>`).join('')}</${tag}></section>`;
  }

  function relationshipSection(title, entries) {
    if (!entries?.length) return '';
    const seen = new Set();
    const rows = entries.filter((entry) => {
      const key = `${entry.target}|${entry.componentKey || ''}|${entry.meta || ''}`;
      if (seen.has(key)) return false;
      seen.add(key); return true;
    });
    return `<section class="relationship-section"><h4>${escapeHTML(title)}</h4><div class="relationship-list">${rows.map((entry) => `<button type="button" class="relationship-link" data-related-target="${escapeHTML(entry.target)}"${entry.componentKey ? ` data-related-component="${escapeHTML(entry.componentKey)}"` : ''}><span>${escapeHTML(entry.label)}</span><small>${escapeHTML(entry.meta)}</small></button>`).join('')}</div></section>`;
  }

  function actualRelationshipSections() {
    const asset = activeAsset(); const component = activeComponent(asset);
    if (!asset || !component || !(asset.connections || []).length) return '';
    const includeSecond = !state.hovered && Boolean(state.selected);
    const context = actualConnectionContext(asset, component, includeSecond);
    const components = new Map(asset.components.map((item) => [item.componentKey, item]));
    const dependsOn = []; const usedBy = []; const dataRelations = []; const secondLevel = [];
    context.directConnections.forEach((connection) => {
      const otherKey = connection.sourceComponentKey === component.componentKey ? connection.targetComponentKey : connection.sourceComponentKey;
      const other = components.get(otherKey); if (!other) return;
      const entry = { target: componentTarget(other), componentKey: other.componentKey, label: componentLabel(other), meta: connectionLabel(connection) };
      if (connection.kind === 'dependency' && connection.sourceComponentKey === component.componentKey) dependsOn.push(entry);
      else if (connection.kind === 'dependency' && connection.targetComponentKey === component.componentKey) usedBy.push(entry);
      else dataRelations.push(entry);
    });
    context.secondaryConnections.forEach((connection) => {
      const secondKey = context.secondaryKeys.has(connection.sourceComponentKey) ? connection.sourceComponentKey
        : context.secondaryKeys.has(connection.targetComponentKey) ? connection.targetComponentKey : null;
      if (!secondKey) return;
      const second = components.get(secondKey); if (!second) return;
      const bridgeKey = connection.sourceComponentKey === secondKey ? connection.targetComponentKey : connection.sourceComponentKey;
      const bridge = components.get(bridgeKey);
      secondLevel.push({
        target: componentTarget(second), componentKey: second.componentKey, label: componentLabel(second),
        meta: `${bridge ? componentLabel(bridge) : componentLabel(component)} → ${connectionLabel(connection)}`,
      });
    });
    return relationshipSection(t('ui.dependsOn'), dependsOn)
      + relationshipSection(t('ui.usedBy'), usedBy)
      + relationshipSection(t('ui.dataRelations'), dataRelations)
      + relationshipSection(t('ui.secondLevel'), secondLevel);
  }

  function graphRelationshipSections(nodeId) {
    if (!nodeId || !data.nodes[nodeId]) return '';
    const includeSecond = !state.hovered && Boolean(state.selected);
    const context = graphConnectionContext(nodeId, includeSecond);
    const dependsOn = []; const usedBy = []; const dataRelations = []; const secondLevel = [];
    context.directEdges.forEach((connection) => {
      const otherId = connection.from === nodeId ? connection.to : connection.from;
      const other = data.nodes[otherId]; if (!other) return;
      const entry = { target: otherId, label: nodeLabel(other), meta: edgeLabel(connection) || connectionKindLabel(connection.type) };
      if (connection.type === 'dependency' && connection.from === nodeId) dependsOn.push(entry);
      else if (connection.type === 'dependency' && connection.to === nodeId) usedBy.push(entry);
      else dataRelations.push(entry);
    });
    context.secondaryEdges.forEach((connection) => {
      const secondId = context.secondaryNodes.has(connection.from) ? connection.from : context.secondaryNodes.has(connection.to) ? connection.to : null;
      const second = secondId && data.nodes[secondId]; if (!second) return;
      const bridgeId = connection.from === secondId ? connection.to : connection.from;
      secondLevel.push({ target: secondId, label: nodeLabel(second), meta: `${nodeLabel(data.nodes[bridgeId] || { id: bridgeId, label: bridgeId })} → ${edgeLabel(connection) || connectionKindLabel(connection.type)}` });
    });
    return relationshipSection(t('ui.dependsOn'), dependsOn)
      + relationshipSection(t('ui.usedBy'), usedBy)
      + relationshipSection(t('ui.dataRelations'), dataRelations)
      + relationshipSection(t('ui.secondLevel'), secondLevel);
  }

  function relationshipSections(nodeId) {
    return effectiveMode() === 'actual' && activeAsset()?.connections?.length ? actualRelationshipSections() : graphRelationshipSections(nodeId);
  }

  function reportExplanationBlock(diagram = activeDiagram()) {
    const reportExplanation = canonicalDiagram(diagram).reportExplanation?.[state.language];
    return reportExplanation ? `<section class="report-explanation" aria-labelledby="report-explanation-title"><div class="report-explanation__heading"><h3 id="report-explanation-title">${escapeHTML(t('ui.reportExplanation'))}</h3><button class="secondary-button compact-button" type="button" data-copy-report-paragraph>${escapeHTML(t('ui.copyReportParagraph'))}</button></div><p>${escapeHTML(reportExplanation)}</p></section>` : '';
  }

  function diagramComparisonBlock(diagram = activeDiagram()) {
    const targetId = diagram.basedOnDiagramId
      || allDiagrams().find((candidate) => candidate.basedOnDiagramId === diagram.id)?.id;
    const target = targetId && allDiagrams().find((candidate) => candidate.id === targetId);
    if (!target) return '';
    const label = diagram.basedOnDiagramId ? t('ui.openVanilla') : t('ui.openV2');
    return `<section class="diagram-comparison" aria-label="${escapeHTML(label)}"><span><strong>${escapeHTML(diagram.versionTag || 'Vanilla')}</strong><small>${escapeHTML(diagramText(target).title)}</small></span><button class="secondary-button compact-button" type="button" data-open-comparison="${escapeHTML(target.id)}">${escapeHTML(label)}</button></section>`;
  }

  function renderDetails() {
    const selected = currentFocus(); const diagram = activeDiagram();
    const reportBlock = reportExplanationBlock(diagram);
    const comparisonBlock = diagramComparisonBlock(diagram);
    const schemaSnapshot = diagram.collectionId === 'v2-georouting'
      ? { tables: 87, foreignKeys: 119, logicalLinks: data.meta.schema.logicalLinks }
      : data.meta.schema;
    if (!selected) {
      els.details.innerHTML = `${comparisonBlock}${reportBlock}<div class="detail-empty"><p><strong>${escapeHTML(t('ui.chooseItem'))}</strong></p><p>${escapeHTML(t('ui.chooseItemBody'))}</p><dl class="snapshot-list"><div><dt>${escapeHTML(t('ui.publicTables'))}</dt><dd>${schemaSnapshot.tables}</dd></div><div><dt>${escapeHTML(t('ui.foreignKeys'))}</dt><dd>${schemaSnapshot.foreignKeys}</dd></div><div><dt>${escapeHTML(t('ui.authLinks'))}</dt><dd>${schemaSnapshot.logicalLinks}</dd></div></dl><p class="detail-note">${escapeHTML(diagramText(diagram).description)}</p></div>`;
      return;
    }
    if (selected.startsWith('table:')) { renderTableDetails(selected.slice(6)); return; }
    const node = data.nodes[selected]; if (!node) return;
    const hotspotLabels = (data.mappings[node.id]?.hotspots || []).map((id) => data.hotspots.find((hotspot) => hotspot.id === id)).filter(Boolean).map(hotspotLabel);
    els.details.innerHTML = `${comparisonBlock}${reportBlock}<article class="detail-card"><header><div><p class="eyebrow">${escapeHTML(labelKind(node.kind))}</p><h3>${escapeHTML(nodeLabel(node))}</h3></div><span class="status-chip" data-status="${escapeHTML(node.status)}">${escapeHTML(labelStatus(node.status))}</span></header><p>${escapeHTML(nodeDescription(node))}</p>${relationshipSections(node.id)}${listSection(t('ui.flow'), nodeFlow(node), true)}${listSection(t('ui.sourceFiles'), node.files, false, 'code')}${listSection(t('ui.routes'), node.routes, false, 'code')}${listSection(t('ui.tables'), node.tables, false, 'code')}${listSection(t('ui.uiComponents'), hotspotLabels)}${node.auth ? `<section><h4>${escapeHTML(t('ui.auth'))}</h4><p>${escapeHTML(authLabel(node.auth))}</p></section>` : ''}</article>`;
  }

  function renderTableDetails(name) {
    const table = data.schemaTables.find((item) => item.name === name); if (!table) return;
    const relations = tableRelations(name); const links = relations.map((fk) => `${fk.sourceTable}.${fk.sourceColumn} → ${fk.targetTable}.${fk.targetColumn}`);
    data.logicalLinks.filter((link) => link.sourceTable === name || link.targetTable === name).forEach((link) => links.push(`${link.sourceTable}.${link.sourceColumn} ⇢ ${link.targetTable}.${link.targetColumn} (${t('ui.logicalLink')})`));
    const nodeId = Object.keys(data.nodes).find((id) => data.nodes[id].tables?.includes(name)); const node = nodeId && data.nodes[nodeId];
    els.details.innerHTML = `${diagramComparisonBlock()}${reportExplanationBlock()}<article class="detail-card"><header><div><p class="eyebrow">${escapeHTML(t('ui.table'))}</p><h3>public.${escapeHTML(name)}</h3></div><span class="status-chip" data-status="${table.rls ? 'current' : 'warning'}">${escapeHTML(table.rls ? t('ui.rlsOn') : t('ui.rlsOff'))}</span></header><p>${node ? escapeHTML(nodeDescription(node)) : (state.language === 'en' ? 'Supabase public-schema table from the current live metadata snapshot.' : 'Jadual skema public daripada snapshot metadata Supabase langsung semasa.')}</p>${relationshipSections(nodeId)}${listSection(t('ui.primaryKey'), table.pk, false, 'code')}${listSection(state.language === 'en' ? 'Key columns' : 'Lajur penting', table.columns, false, 'code')}${listSection(t('ui.foreignKeyLinks'), links, false, 'code')}${name === 'spatial_ref_sys' ? `<p class="warning-box">${escapeHTML(nodeDescription(data.nodes['spatial-ref']))} <a href="https://supabase.com/docs/guides/database/postgres/row-level-security" target="_blank" rel="noreferrer">${state.language === 'en' ? 'Supabase RLS guide' : 'Panduan RLS Supabase'}</a>.</p>` : ''}</article>`;
  }

  function setHover(target, componentKey = null) {
    if (state.pointer?.dragged) return;
    state.hovered = target; state.hoveredComponentKey = componentKey; applyHighlights(); renderDetails();
  }
  function clearHover() {
    if (state.pointer?.dragged) return;
    state.hovered = null; state.hoveredComponentKey = null; applyHighlights(); renderDetails();
  }
  function pinSelection(target, componentKey = null, connectionId = null) {
    const component = componentByKey(activeAsset(), componentKey);
    state.selected = target; state.hovered = null; state.selectedComponentKey = componentKey; state.hoveredComponentKey = null; state.selectedConnectionId = connectionId;
    const nodeId = target.startsWith('table:') ? component?.nodeIds?.[0] : target; const hotspotId = component?.uiHotspots?.[0] || data.mappings[nodeId]?.hotspots?.[0];
    const hotspot = data.hotspots.find((item) => item.id === hotspotId); if (hotspot) state.uiViewId = hotspot.view;
    renderUIViewOptions(); renderUI(); renderDetails(); applyHighlights();
    if (state.workspaceMode !== 'view' && componentKey) {
      const canonicalType = runtimeDocument()?.analysis?.selectedPage?.detection?.diagramType || state.diagramId;
      editorController.focusComponent(`${canonicalType}/${componentKey}`);
    }
  }

  function applyHighlights() {
    const focus = currentFocus();
    const transientClasses = ['is-selected', 'is-related', 'is-secondary', 'is-active', 'is-muted'];
    document.querySelectorAll('.diagram-node, .schema-table, .diagram-edge, .ui-hotspot').forEach((element) => element.classList.remove(...transientClasses));
    const actualClasses = ['is-focus-cell', 'is-direct-cell', 'is-secondary-cell', 'is-context-cell', 'is-relation-primary', 'is-relation-secondary', 'is-context-edge'];
    document.querySelectorAll('.actual-diagram [data-cell-id]').forEach((element) => element.classList.remove(...actualClasses));
    document.querySelectorAll('.diagram-hitbox').forEach((element) => element.classList.remove('is-selected', 'is-related', 'is-secondary'));
    const svg = els.graphViewport.querySelector('.actual-diagram');
    if (!focus) return;
    const includeSecond = !state.hovered && Boolean(state.selected);

    if (focus.startsWith('table:')) {
      const table = focus.slice(6);
      const directRelations = tableRelations(table);
      const direct = new Set(directRelations.flatMap((fk) => [fk.sourceTable, fk.targetTable])); direct.delete(table);
      data.logicalLinks.filter((link) => link.sourceTable === table || link.targetTable === table).forEach((link) => direct.add(link.sourceTable === table ? link.targetTable : link.sourceTable));
      const secondary = new Set();
      if (includeSecond) {
        data.schemaForeignKeys.filter((fk) => direct.has(fk.sourceTable) || direct.has(fk.targetTable)).forEach((fk) => {
          if (fk.sourceTable !== table && !direct.has(fk.sourceTable)) secondary.add(fk.sourceTable);
          if (fk.targetTable !== table && !direct.has(fk.targetTable)) secondary.add(fk.targetTable);
        });
      }
      document.querySelectorAll('.schema-table').forEach((element) => {
        const name = element.dataset.table;
        element.classList.add(name === table ? 'is-selected' : direct.has(name) ? 'is-related' : secondary.has(name) ? 'is-secondary' : 'is-muted');
      });
    } else {
      const context = graphConnectionContext(focus, includeSecond);
      document.querySelectorAll('.diagram-node').forEach((element) => {
        const id = element.dataset.node;
        element.classList.add(id === focus ? 'is-selected' : context.directNodes.has(id) ? 'is-related' : context.secondaryNodes.has(id) ? 'is-secondary' : 'is-muted');
      });
      document.querySelectorAll('.diagram-edge').forEach((element) => {
        const direct = element.dataset.from === focus || element.dataset.to === focus;
        const secondary = includeSecond && !direct && (context.directNodes.has(element.dataset.from) || context.directNodes.has(element.dataset.to));
        element.classList.add(direct ? 'is-active' : secondary ? 'is-secondary' : 'is-muted');
      });
    }

    const asset = activeAsset();
    if (svg && asset) {
      const component = activeComponent(asset);
      if (component) {
        const context = actualConnectionContext(asset, component, includeSecond);
        const applyCellClass = (ids, className) => ids.forEach((id) => svg.querySelector(`[data-cell-id="${CSS.escape(id)}"]`)?.classList.add(className));
        asset.components.forEach((item) => {
          const className = item.componentKey === context.focusKey ? 'is-focus-cell'
            : context.directKeys.has(item.componentKey) ? 'is-direct-cell'
              : context.secondaryKeys.has(item.componentKey) ? 'is-secondary-cell' : 'is-context-cell';
          componentCellElements(svg, item).forEach((element) => element.classList.add(className));
          const hitbox = svg.querySelector(`.diagram-overlay[data-component-key="${CSS.escape(item.componentKey)}"] .diagram-hitbox`);
          const hitboxClass = item.componentKey === context.focusKey ? 'is-selected'
            : context.directKeys.has(item.componentKey) ? 'is-related'
              : context.secondaryKeys.has(item.componentKey) ? 'is-secondary' : null;
          if (hitbox && hitboxClass) hitbox.classList.add(hitboxClass);
        });
        const directIds = new Set(context.directConnections.map((item) => item.id));
        const secondaryIds = new Set(context.secondaryConnections.map((item) => item.id));
        (asset.connections || []).forEach((connection) => {
          applyCellClass([connection.id], connection.id === state.selectedConnectionId ? 'is-relation-primary'
            : directIds.has(connection.id) ? 'is-relation-primary'
            : secondaryIds.has(connection.id) ? 'is-relation-secondary' : 'is-context-edge');
        });
      }
    }

    const component = activeComponent(asset); const nodeId = focus.startsWith('table:') ? component?.nodeIds?.[0] : focus;
    const hotspots = new Set([...(data.mappings[nodeId]?.hotspots || []), ...(component?.uiHotspots || [])]);
    const relatedHotspots = new Set();
    if (asset && component) {
      const context = actualConnectionContext(asset, component, false);
      asset.components.filter((item) => context.directKeys.has(item.componentKey)).forEach((item) => {
        (item.uiHotspots || []).forEach((id) => relatedHotspots.add(id));
        (item.nodeIds || []).forEach((id) => (data.mappings[id]?.hotspots || []).forEach((hotspot) => relatedHotspots.add(hotspot)));
      });
    } else if (nodeId) {
      const context = graphConnectionContext(nodeId, false);
      context.directNodes.forEach((id) => (data.mappings[id]?.hotspots || []).forEach((hotspot) => relatedHotspots.add(hotspot)));
    }
    document.querySelectorAll('.ui-hotspot').forEach((element) => {
      if (hotspots.has(element.dataset.hotspot)) element.classList.add(focus === state.selected ? 'is-selected' : 'is-active');
      else if (relatedHotspots.has(element.dataset.hotspot)) element.classList.add('is-related');
    });
  }

  function renderSearch() {
    const query = els.search.value.trim().toLocaleLowerCase();
    if (!query) { els.searchResults.hidden = true; els.searchResults.innerHTML = ''; return; }
    const nodeResults = Object.values(data.nodes).filter((node) => {
      const englishLabel = translations.en.nodeLabels[node.id] || node.label; const englishDescription = translations.en.descriptions[node.id] || '';
      return [node.label, englishLabel, node.description, englishDescription, ...(node.files || []), ...(node.routes || []), ...(node.tables || []), ...(node.ui || [])].join(' ').toLocaleLowerCase().includes(query);
    }).slice(0, 14);
    const tableResults = data.schemaTables.filter((table) => table.name.toLocaleLowerCase().includes(query)).slice(0, 8);
    const hotspotResults = data.hotspots.filter((hotspot) => `${hotspot.label} ${translations.en.hotspots[hotspot.id] || ''}`.toLocaleLowerCase().includes(query)).slice(0, 6);
    const items = [
      ...nodeResults.map((node) => ({ target: node.id, label: nodeLabel(node), meta: `${labelKind(node.kind)} · ${labelStatus(node.status)}` })),
      ...tableResults.map((table) => ({ target: `table:${table.name}`, label: table.name, meta: t('ui.table') })),
      ...hotspotResults.map((hotspot) => ({ target: `hotspot:${hotspot.id}`, label: hotspotLabel(hotspot), meta: 'UI' })),
    ];
    els.searchResults.innerHTML = items.length ? items.map((item) => `<button type="button" role="option" data-search-target="${escapeHTML(item.target)}"><span>${escapeHTML(item.label)}</span><small>${escapeHTML(item.meta)}</small></button>`).join('') : `<p>${escapeHTML(t('ui.noResults'))}</p>`;
    els.searchResults.hidden = false;
  }

  function chooseDiagram(id) {
    const nextDiagram = allDiagrams().find((diagram) => diagram.id === id);
    if (!nextDiagram) return;
    const previousWorkspaceMode = state.workspaceMode;
    if (nextDiagram.collectionId) {
      state.diagramCollections[nextDiagram.collectionId] = true;
      storeDiagramCollections(state.diagramCollections);
      if (nextDiagram.collectionGroupId) {
        state.diagramCollectionGroups[`${nextDiagram.collectionId}:${nextDiagram.collectionGroupId}`] = true;
        storeDiagramCollectionGroups(state.diagramCollectionGroups);
      }
    }
    clearReportColumnSelection();
    state.diagramId = id; state.selected = null; state.hovered = null; state.selectedComponentKey = null; state.hoveredComponentKey = null; state.selectedConnectionId = null; state.fitMode = true;
    if (isDocumentDiagram(nextDiagram)) state.mobilePanel = 'diagram';
    cloudManager?.setActiveFromDocumentKey(id);
    if (previousWorkspaceMode !== 'view' && !isEditableDiagram(id)) state.workspaceMode = 'view';
    renderAll();
    if (previousWorkspaceMode !== 'view' && isEditableDiagram(id)) setWorkspaceMode(previousWorkspaceMode);
    else if (state.workspaceMode === 'view') setWorkspaceMode('view', { loadCanonical: false });
    hydrateWorkspaceDocument(id);
  }

  function openExplorerExample(detail = {}) {
    const diagramId = detail.diagramId;
    if (!diagramId || !allDiagrams().some((diagram) => diagram.id === diagramId)) return false;
    state.renderMode = 'actual'; state.mobilePanel = 'diagram';
    chooseDiagram(diagramId);
    if (state.workspaceMode !== 'view') setWorkspaceMode('view', { loadCanonical: false });
    const asset = activeAsset();
    const connection = detail.connectionId ? asset?.connections?.find((item) => item.id === detail.connectionId) : null;
    let component = componentByKey(asset, detail.componentKey);
    if (!component && detail.componentKey) component = asset?.components?.find((item) => item.nodeIds?.includes(detail.componentKey) || item.tableName === detail.componentKey.replace(/^table:/, '')) || null;
    if (!component && connection) component = componentByKey(asset, connection.sourceComponentKey) || componentByKey(asset, connection.targetComponentKey);
    if (component) pinSelection(componentTarget(component), component.componentKey, connection?.id || null);
    else if (detail.componentKey && data.nodes[detail.componentKey]) {
      state.selected = detail.componentKey; state.selectedConnectionId = connection?.id || null; renderAll();
    } else renderDiagram();
    els.statusMessage.textContent = state.language === 'en' ? 'Opened the learning example in Explorer.' : 'Contoh pembelajaran dibuka dalam Explorer.';
    return true;
  }

  function chooseSearchTarget(target) {
    els.search.value = ''; els.searchResults.hidden = true; state.selectedComponentKey = null; state.hoveredComponentKey = null;
    if (target.startsWith('hotspot:')) {
      const hotspot = data.hotspots.find((item) => item.id === target.slice(8)); if (!hotspot) return;
      state.uiViewId = hotspot.view; state.selected = hotspot.nodes[0] || null; renderUIViewOptions(); renderUI(); renderDetails(); applyHighlights(); return;
    }
    if (target.startsWith('table:')) { state.diagramId = 'supabase'; state.selected = target; state.renderMode = assets.supabase ? 'actual' : 'map'; renderAll(); return; }
    const node = data.nodes[target]; if (!node) return;
    const candidate = data.diagrams.find((diagram) => (diagram.columns || []).flat().includes(target) || data.edges.some((edge) => edge.diagrams.includes(diagram.id) && (edge.from === target || edge.to === target)));
    if (candidate) state.diagramId = candidate.id; state.selected = target; state.fitMode = true; renderAll();
  }

  function updateMobilePanels() {
    const documentLayout = isDocumentDiagram();
    if (documentLayout) state.mobilePanel = 'diagram';
    document.querySelectorAll('[data-panel]').forEach((panel) => panel.classList.toggle('mobile-active', panel.dataset.panel === state.mobilePanel));
    document.querySelectorAll('[data-mobile-panel]').forEach((button) => {
      const active = button.dataset.mobilePanel === state.mobilePanel;
      button.hidden = documentLayout && button.dataset.mobilePanel !== 'diagram';
      button.classList.toggle('is-active', active);
      button.setAttribute('aria-selected', String(active));
    });
  }

  function agentCredentials() {
    return { provider: els.agentProvider.value, baseURL: els.agentBaseURL.value, model: els.agentModel.value, apiKey: els.agentAPIKey.value };
  }

  function updateAgentProviderUI(options = {}) {
    const provider = els.agentProvider.value;
    const isOpenAI = provider === 'openai';
    const isCodex = provider === 'codex';
    els.agentBaseField.hidden = isCodex;
    els.agentModelField.hidden = isCodex;
    els.agentKeyField.hidden = isCodex;
    els.agentBaseURL.readOnly = isOpenAI;
    if (isOpenAI) {
      els.agentBaseURL.value = 'https://api.openai.com/v1';
      if (options.forceModel || !els.agentModel.value.trim()) els.agentModel.value = window.PETAKERJA_OPENAI_POLICY?.defaultModel || 'gpt-5.6-terra';
    } else if (provider === 'compatible' && options.providerChanged) {
      if (els.agentBaseURL.value === 'https://api.openai.com/v1') els.agentBaseURL.value = 'http://127.0.0.1:11434/v1';
    }
    els.agentPropose.disabled = isCodex;
    diagramAgent?.configure(agentCredentials());
  }

  function renderAgentProviderStatus(status) {
    if (!status) return;
    const providerNames = { openai: 'OpenAI', compatible: 'OpenAI-compatible', codex: 'Codex bridge' };
    const stateLabels = state.language === 'en'
      ? { current: 'current', unknown: 'not tested', blocked: 'blocked', error: 'unavailable', unverified: 'not tested', bridge: 'host ready' }
      : { current: 'semasa', unknown: 'belum diuji', blocked: 'disekat', error: 'tidak tersedia', unverified: 'belum diuji', bridge: 'hos sedia' };
    const modelName = status.provider === 'codex' ? (state.language === 'en' ? 'No browser API key' : 'Tiada kunci API pelayar') : (status.model?.id || '—');
    const replacement = status.model?.state === 'blocked' && status.model?.replacement ? ` · ${state.language === 'en' ? 'use' : 'guna'} ${status.model.replacement}` : '';
    const stale = status.stale ? ` · ${state.language === 'en' ? 'policy refresh due' : 'polisi perlu disegar'}` : '';
    els.agentProviderStatus.dataset.state = status.model?.state || 'unknown';
    els.agentProviderStatus.innerHTML = `<strong>${escapeHTML(providerNames[status.provider] || status.provider)}</strong><span>${escapeHTML(modelName)} · ${escapeHTML(stateLabels[status.model?.state] || status.model?.state || '')} · ${state.language === 'en' ? 'policy' : 'polisi'} ${escapeHTML(status.policyDate || '—')}${escapeHTML(replacement)}${escapeHTML(stale)}</span>`;
  }

  function agentContext() {
    const page = editorController.analysis?.selectedPage;
    const components = (page?.matches || []).map((match) => {
      const cell = page.cellById?.get(match.cellId);
      const geometry = cell?.querySelector?.('mxGeometry');
      return {
        key: match.identity?.key || match.stableKey || match.cellId,
        componentKey: match.identity?.componentKey || null,
        label: match.identity?.labelEn || match.identity?.label || cell?.getAttribute('value') || match.cellId,
        confidence: match.confidence,
        geometry: geometry ? { x: Number(geometry.getAttribute('x') || 0), y: Number(geometry.getAttribute('y') || 0), width: Number(geometry.getAttribute('width') || 0), height: Number(geometry.getAttribute('height') || 0) } : null,
      };
    });
    return {
      diagramId: state.diagramId,
      diagramType: page?.detection?.diagramType || page?.diagramId || 'unknown',
      detection: page?.detection || null,
      pageId: page?.id || editorController.pageId,
      title: diagramText(activeDiagram()).title,
      components,
      relations: page?.relations || [],
      validationIssues: (editorController.analysis?.issues || []).map((entry) => ({ severity: entry.severity, ruleId: entry.ruleId, message: editorIssueText(entry) })),
    };
  }

  function bridgeValidationResult(analysis = editorController.analysis) {
    const page = analysis?.selectedPage;
    return {
      fatal: Boolean(analysis?.fatal),
      diagramType: page?.detection?.diagramType || page?.diagramId || 'unknown',
      detection: page?.detection || null,
      counts: page?.counts || null,
      componentCount: page?.componentCount || 0,
      relationshipCount: page?.relationshipCount || 0,
      issues: (analysis?.issues || []).map((entry) => ({ severity: entry.severity, ruleId: entry.ruleId, cellIds: entry.cellIds, message: editorIssueText(entry) })),
    };
  }

  function agentLog(entry) {
    const item = document.createElement('li');
    item.dataset.kind = entry.kind;
    const time = new Date(entry.time).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' });
    item.innerHTML = `<time>${escapeHTML(time)}</time><span>${escapeHTML(entry.message)}</span>`;
    els.agentLog.appendChild(item);
    while (els.agentLog.children.length > 80) els.agentLog.firstElementChild.remove();
    els.agentLog.scrollTop = els.agentLog.scrollHeight;
  }

  function renderAgentPlan(plan) {
    if (!plan) { els.agentPlan.innerHTML = `<p>${state.language === 'en' ? 'No plan yet.' : 'Belum ada pelan.'}</p>`; els.agentRun.disabled = true; return; }
    els.agentPlan.innerHTML = `<div class="agent-plan-summary"><strong>${escapeHTML(plan.title)}</strong><span>${plan.operations.length} ${state.language === 'en' ? 'operations' : 'operasi'}</span></div><p>${escapeHTML(plan.summary || '')}</p>${plan.warnings?.length ? `<ul>${plan.warnings.map((warning) => `<li>${escapeHTML(warning)}</li>`).join('')}</ul>` : ''}<ol>${plan.operations.map((operation) => `<li><code>${escapeHTML(operation.type)}</code><span>${escapeHTML(operation.key || operation.name || operation.sourceKey || '')}</span></li>`).join('')}</ol>`;
    els.agentRun.disabled = false;
  }

  function setAgentState(value) {
    const labels = state.language === 'en'
      ? { idle: 'Idle', testing: 'Testing', planning: 'Planning', review: 'Review', running: 'Running', stopping: 'Stopping', stopped: 'Stopped', complete: 'Complete', error: 'Error' }
      : { idle: 'Sedia', testing: 'Menguji', planning: 'Merancang', review: 'Semakan', running: 'Berjalan', stopping: 'Menghenti', stopped: 'Dihenti', complete: 'Selesai', error: 'Ralat' };
    els.agentState.textContent = labels[value] || value;
    els.agentState.dataset.state = value;
    els.editorSurface.dataset.agentState = value;
    els.editorSurface.setAttribute('aria-busy', String(value === 'running' || value === 'stopping'));
  }

  async function handleBridgeCommand(command) {
    if (!command?.id) return;
    let result;
    try {
      if (command.tool === 'get_explorer_status') result = { workspaceMode: state.workspaceMode, diagramId: state.diagramId, dirty: editorController.dirty, agentState: els.agentState.dataset.state || 'idle' };
      else if (command.tool === 'get_diagram_context') result = agentContext();
      else if (command.tool === 'start_new_diagram_session') {
        const diagramType = String(command.arguments?.diagramType || 'unknown');
        const name = String(command.arguments?.name || 'PetaKerja Diagram');
        const known = data.diagrams.some((item) => item.id === diagramType);
        const key = known ? diagramType : `imported-${Date.now()}`;
        if (!known) state.importedDiagrams.push({ id: key, title: name, description: 'Session-only Agent diagram.', category: 'Imported', status: 'current', sessionOnly: true, columns: [] });
        state.diagramId = key; state.editorDocumentKey = key; state.selected = null; state.selectedComponentKey = null;
        const pageId = command.arguments?.pageId || (diagramType === 'auth-sequence' ? 'petakerja_auth_sequence' : `petakerja-${Date.now()}`);
        const analysis = editorController.newSession({ name, diagramType, pageId, filename: command.arguments?.filename || `${name}.drawio` });
        updateRuntimeDocument(editorController.documentSnapshot(), key);
        renderAll();
        result = { diagramId: key, diagramType, pageId, fatal: Boolean(analysis.fatal), issueCount: analysis.issues?.length || 0 };
      }
      else if (command.tool === 'propose_diagram_plan') result = diagramAgent.setPlan(command.arguments?.plan || command.arguments);
      else if (command.tool === 'await_plan_decision') result = {
        decision: diagramAgent.decision,
        approved: ['approved', 'applied', 'stopped'].includes(diagramAgent.decision),
        plan: diagramAgent.plan,
      };
      else if (command.tool === 'apply_diagram_operations') {
        const plan = command.arguments?.plan || { id: `codex-${Date.now()}`, title: 'Codex diagram operations', diagramType: agentContext().diagramType, summary: 'Operations supplied through the local Codex bridge.', operations: command.arguments?.operations || [], warnings: [] };
        diagramAgent.setPlan(plan); result = await diagramAgent.run(plan);
      } else if (command.tool === 'validate_active_diagram') result = bridgeValidationResult(editorController.validateNow());
      else if (command.tool === 'export_active_diagram') {
        const exported = await editorController.exportRuntimeSVG(); result = { svg: sanitizeRuntimeSVG(exported.svg), xml: exported.xml, pageId: exported.pageId };
      } else throw new Error(`Unknown bridge tool: ${command.tool}`);
      await fetch(localAPI('bridge/result'), { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ id: command.id, ok: true, result }) });
    } catch (error) {
      await fetch(localAPI('bridge/result'), { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ id: command.id, ok: false, error: error.message }) }).catch(() => {});
    }
  }

  let bridgeCursor = 0;
  let bridgeInitialized = false;
  async function pollBridge() {
    if (!editorController.available || runtimeCapabilities.mcp === false) {
      els.bridgeStatus.textContent = state.language === 'en' ? 'Localhost only' : 'Localhost sahaja';
      return;
    }
    try {
      const status = await fetch(localAPI('bridge/status'), { cache: 'no-store' });
      if (!status.ok) throw new Error('Bridge host unavailable');
      const payload = await status.json();
      els.bridgeStatus.textContent = payload.mcpConnected
        ? (state.language === 'en' ? 'Connected' : 'Bersambung')
        : (state.language === 'en' ? 'Host ready' : 'Hos sedia');
      els.bridgeConfig.textContent = payload.configSnippet || '';
      if (!bridgeInitialized) {
        bridgeCursor = Number(payload.sequence || 0);
        bridgeInitialized = true;
        return;
      }
      if (state.workspaceMode !== 'agent' || !editorController.ready) return;
      const response = await fetch(`${localAPI('bridge/commands')}?since=${bridgeCursor}`, { cache: 'no-store' });
      if (response.ok) {
        const queue = await response.json();
        for (const command of queue.commands || []) { bridgeCursor = Math.max(bridgeCursor, command.sequence || 0); await handleBridgeCommand(command); }
      }
    } catch (_error) {
      els.bridgeStatus.textContent = 'Unavailable';
    } finally {
      window.setTimeout(pollBridge, 900);
    }
  }

  editorController = editorAPI.createController({
    iframe: els.editorFrame, data, assets, translations, language: state.language,
    diagramLabelMode: state.diagramLabelMode, themePreference: state.themePreference,
    callbacks: {
      onFrameReload() { els.editorSurface.classList.remove('is-ready'); },
      onReady() { els.editorSurface.classList.add('is-ready'); },
      onAnalysis(analysis, meta) {
        state.editorAnalysis = analysis;
        const page = analysis.selectedPage;
        if (!activeDiagram().sessionOnly && page?.diagramId && page.diagramId !== state.diagramId && data.diagrams.some((item) => item.id === page.diagramId)) {
          state.diagramId = page.diagramId;
          renderDiagramNav();
          const text = diagramText(activeDiagram());
          els.diagramTitle.textContent = text.title; els.diagramDescription.textContent = text.description;
        }
        renderValidation(analysis, meta);
      },
      onSelection(match) {
        if (!match?.identity) return;
        const identity = match.identity;
        if (!activeDiagram().sessionOnly && identity.diagramId !== state.diagramId && data.diagrams.some((item) => item.id === identity.diagramId)) {
          state.diagramId = identity.diagramId;
          renderDiagramNav();
        }
        state.selected = identity.target; state.hovered = null;
        state.selectedComponentKey = identity.componentKey; state.hoveredComponentKey = null;
        const component = componentByKey(activeAsset(), identity.componentKey);
        const nodeId = identity.target?.startsWith('table:') ? component?.nodeIds?.[0] : identity.target;
        const hotspotId = identity.uiHotspots?.[0] || data.mappings[nodeId]?.hotspots?.[0];
        const hotspot = data.hotspots.find((item) => item.id === hotspotId);
        if (hotspot) state.uiViewId = hotspot.view;
        renderUIViewOptions(); renderUI(); renderDetails(); applyHighlights();
      },
      onDirtyChange(dirty) {
        els.saveButton.textContent = `${t('ui.saveAs')}${dirty ? ' *' : ''}`;
        els.workspaceSaveButton.textContent = `${t('ui.saveWorkspace')}${dirty ? ' *' : ''}`;
      },
      onWorkingDocument(snapshot) {
        updateRuntimeDocument(snapshot);
        cloudManager?.notifyWorking(snapshot);
      },
    },
  });

  cloudManager = window.PETAKERJA_CLOUD?.createManager({
    getLanguage: () => state.language,
    isEditorAvailable: () => Boolean(editorController?.available),
    getSnapshot: () => editorController?.documentSnapshot?.() || null,
    exportPreview: async () => {
      const exported = await editorController.exportRuntimeSVG();
      return { xml: exported.xml || editorController.workingXml, svg: sanitizeRuntimeSVG(exported.svg) };
    },
    markClean: () => editorController.markClean(),
    openDocument: openCloudDocument,
    onStatus(message) { els.statusMessage.textContent = message; },
  }) || null;

  diagramAgent = new agentAPI.DiagramAgent({
    editor: editorController,
    getContext: async () => agentContext(),
    callbacks: {
      onState: setAgentState,
      onPlan: renderAgentPlan,
      onLog: agentLog,
      onProviderStatus(status) { state.agentProviderStatus = status; renderAgentProviderStatus(status); },
      onRunStart() { els.agentRun.disabled = true; els.agentStop.disabled = false; els.agentRevert.disabled = true; },
      onOperation(event) { agentLog({ time: new Date().toISOString(), kind: 'ack', message: `Applied ${event.completed}/${event.total}: ${event.operation.type}` }); },
      onRunEnd(event) {
        els.agentStop.disabled = true; els.agentRun.disabled = false; els.agentRevert.disabled = !event.canRevert;
        if (pendingEditorThemePreference) {
          const nextPreference = pendingEditorThemePreference;
          pendingEditorThemePreference = null;
          syncEditorThemePreference(nextPreference);
        }
      },
      onRevert() { els.agentRevert.disabled = true; },
    },
  });
  updateAgentProviderUI({ forceModel: true });

  els.diagramNav.addEventListener('click', (event) => { const button = event.target.closest('[data-diagram]'); if (button) chooseDiagram(button.dataset.diagram); });
  els.diagramPicker.addEventListener('change', () => chooseDiagram(els.diagramPicker.value));
  els.scope.addEventListener('change', () => {
    state.scopeId = els.scope.value; state.selected = null; state.hovered = null; state.selectedComponentKey = null; state.hoveredComponentKey = null; state.selectedConnectionId = null; state.fitMode = true; renderAll();
  });
  els.uiView.addEventListener('change', () => { state.uiViewId = els.uiView.value; renderUI(); });
  document.querySelectorAll('[data-render-mode]').forEach((button) => button.addEventListener('click', () => { state.renderMode = button.dataset.renderMode; state.fitMode = true; renderDiagram(); }));
  els.diagramLabelControl.addEventListener('click', async (event) => {
    const button = event.target.closest('[data-diagram-label-mode]');
    if (!button || state.diagramLabelModeSwitching) return;
    const next = button.dataset.diagramLabelMode === 'code' ? 'code' : 'simple';
    if (next === state.diagramLabelMode) return;
    state.diagramLabelMode = next;
    storeDiagramLabelMode(next);
    state.diagramLabelModeSwitching = true;
    renderWorkspaceControls();
    try {
      if (state.workspaceMode === 'edit') await editorController.setDiagramLabelMode(next);
      renderDiagram(); renderDetails();
    } catch (_error) {
      els.statusMessage.textContent = state.language === 'en'
        ? 'The label mode changed, but the editor could not reload.'
        : 'Mod label berubah tetapi editor tidak dapat dimuatkan semula.';
    } finally {
      state.diagramLabelModeSwitching = false;
      renderWorkspaceControls();
    }
  });
  els.languageSelect.addEventListener('change', () => applyLanguagePreference(els.languageSelect.value));
  els.themeSelect.addEventListener('change', () => applyThemePreference(els.themeSelect.value, { announce: true }));
  systemThemeQuery?.addEventListener?.('change', () => {
    if (state.themePreference === 'system') applyThemePreference('system', { persist: false, syncEditor: false });
  });
  els.workspaceModeControl.addEventListener('click', (event) => {
    const button = event.target.closest('[data-workspace-mode]');
    if (button && !button.disabled) setWorkspaceMode(button.dataset.workspaceMode);
  });
  els.importButton.addEventListener('click', () => {
    if (!editorController.available) { showRuntimeDialog(); return; }
    els.fileInput.click();
  });
  els.fileInput.addEventListener('change', () => { if (els.fileInput.files?.[0]) processImportFile(els.fileInput.files[0]); els.fileInput.value = ''; });
  els.validateButton.addEventListener('click', () => renderValidation(editorController.validateNow(), { changeKind: 'logic' }));
  els.workspaceSaveButton.addEventListener('click', saveActiveDiagramToWorkspace);
  els.saveButton.addEventListener('click', () => editorController.saveAs());
  els.agentTest.addEventListener('click', async () => {
    diagramAgent.configure(agentCredentials());
    try { await diagramAgent.testConnection(); } catch (_error) { /* The activity log contains the actionable error. */ }
  });
  els.agentProvider.addEventListener('change', () => updateAgentProviderUI({ providerChanged: true, forceModel: els.agentProvider.value === 'openai' }));
  els.agentModel.addEventListener('input', () => diagramAgent.configure(agentCredentials()));
  els.agentBaseURL.addEventListener('input', () => diagramAgent.configure(agentCredentials()));
  els.agentPropose.addEventListener('click', async () => {
    diagramAgent.configure(agentCredentials());
    els.agentPropose.disabled = true;
    try { await diagramAgent.propose(els.agentPrompt.value); }
    catch (error) { agentLog({ time: new Date().toISOString(), kind: 'error', message: error.message }); setAgentState('error'); }
    finally { els.agentPropose.disabled = false; }
  });
  els.agentRun.addEventListener('click', async () => {
    try { await diagramAgent.run(); }
    catch (error) { agentLog({ time: new Date().toISOString(), kind: 'error', message: error.message }); setAgentState('error'); }
  });
  els.agentStop.addEventListener('click', () => diagramAgent.stop());
  els.agentRevert.addEventListener('click', () => {
    try { diagramAgent.revert(); } catch (error) { agentLog({ time: new Date().toISOString(), kind: 'error', message: error.message }); }
  });
  els.copyBridgeConfig.addEventListener('click', async () => {
    try { await navigator.clipboard.writeText(els.bridgeConfig.textContent); els.copyBridgeConfig.textContent = 'Copied'; }
    catch (_error) { /* The configuration remains visible for manual copy. */ }
    window.setTimeout(() => { els.copyBridgeConfig.textContent = state.language === 'en' ? 'Copy MCP configuration' : 'Salin konfigurasi MCP'; }, 1200);
  });
  els.search.addEventListener('input', renderSearch);
  els.searchResults.addEventListener('click', (event) => { const button = event.target.closest('[data-search-target]'); if (button) chooseSearchTarget(button.dataset.searchTarget); });
  els.graph.addEventListener('mouseover', (event) => { const node = event.target.closest('[data-node]'); const table = event.target.closest('[data-table]'); if (node) setHover(node.dataset.node); else if (table) setHover(`table:${table.dataset.table}`); });
  els.graph.addEventListener('mouseout', (event) => { if (event.target.closest('[data-node], [data-table]') && !event.relatedTarget?.closest?.('[data-node], [data-table]')) clearHover(); });
  els.graph.addEventListener('focusin', (event) => { const node = event.target.closest('[data-node]'); const table = event.target.closest('[data-table]'); if (node) setHover(node.dataset.node); else if (table) setHover(`table:${table.dataset.table}`); });
  els.graph.addEventListener('focusout', (event) => { if (event.target.closest('[data-node], [data-table]')) clearHover(); });
  els.graph.addEventListener('click', (event) => {
    if (state.suppressClick) return;
    const node = event.target.closest('[data-node]'); const table = event.target.closest('[data-table]');
    if (node) pinSelection(node.dataset.node); else if (table) pinSelection(`table:${table.dataset.table}`);
  });
  els.graph.addEventListener('click', async (event) => {
    const reportColumnButton = event.target.closest('[data-report-column-select]');
    if (reportColumnButton && isReportTableDiagram()) {
      toggleReportColumnSelection(
        reportColumnButton.dataset.reportColumnSelect,
        Number(reportColumnButton.dataset.reportColumnIndex),
        reportColumnButton.dataset.reportColumnLabel || '',
      );
      return;
    }
    const reportButton = event.target.closest('[data-copy-report-table]');
    if (reportButton && isReportTableDiagram()) {
      const tableId = reportButton.dataset.copyReportTable;
      const table = reportPageSections(activeReportPage()).flatMap((section) => section.tables).find((item) => item.id === tableId);
      if (!table) return;
      const payload = codeSnippetClipboard.reportTablePayload(table);
      await codeSnippetClipboard.writeClipboardPayload(payload.plainText, payload.htmlText);
      const label = reportButton.querySelector('span');
      if (label) label.textContent = t('ui.tableCopied');
      els.statusMessage.textContent = `${t('ui.tableCopied')}: ${table.title}`;
      window.setTimeout(() => { if (label?.isConnected) label.textContent = t('ui.copyTable'); }, 1400);
      return;
    }
    const reportLanguageButton = event.target.closest('[data-report-language]');
    if (reportLanguageButton && isReportTableDiagram()) {
      const nextLanguage = reportLanguageButton.dataset.reportLanguage === 'en' ? 'en' : 'ms';
      if (nextLanguage !== state.reportTableLanguage) clearReportColumnSelection();
      state.reportTableLanguage = nextLanguage;
      storeReportTableLanguage(state.reportTableLanguage);
      renderDiagram();
      els.statusMessage.textContent = `${t('ui.reportLanguageChanged')}: ${state.reportTableLanguage === 'en' ? 'English' : 'BM'}`;
      return;
    }
    const dictionaryColumnButton = event.target.closest('[data-report-column-mode]');
    if (dictionaryColumnButton && activeDiagram()?.reportTableKey === 'kamus-data') {
      const nextColumnMode = dictionaryColumnButton.dataset.reportColumnMode === 'size' ? 'size' : 'constraints';
      if (nextColumnMode !== state.dictionaryColumnMode) clearReportColumnSelection();
      state.dictionaryColumnMode = nextColumnMode;
      storeDictionaryColumnMode(state.dictionaryColumnMode);
      renderDiagram();
      const modeLabel = state.dictionaryColumnMode === 'size'
        ? (state.reportTableLanguage === 'en' ? 'Data Size' : 'Saiz Data')
        : (state.reportTableLanguage === 'en' ? 'Required / Constraints' : 'Wajib / Kekangan');
      els.statusMessage.textContent = `${t('ui.dictionaryColumnChanged')}: ${modeLabel}`;
      return;
    }
    const languageButton = event.target.closest('[data-snippet-language]');
    if (languageButton && isCodeDiagram()) {
      state.snippetLanguage = languageButton.dataset.snippetLanguage === 'en' ? 'en' : 'ms';
      storeCodeSnippetLanguage(state.snippetLanguage);
      renderDiagram();
      const languageLabel = state.snippetLanguage === 'en' ? 'English' : 'BM';
      els.statusMessage.textContent = `${t('ui.snippetLanguageChanged')}: ${languageLabel}`;
      return;
    }
    const codeButton = event.target.closest('[data-copy-snippet-code]');
    const captionButton = event.target.closest('[data-copy-snippet-caption]');
    const tableButton = event.target.closest('[data-copy-upstream-table]');
    const flowButton = event.target.closest('[data-copy-marker-flow]');
    const button = codeButton || captionButton || tableButton || flowButton;
    const diagram = activeDiagram();
    if (!button || !isCodeDiagram(diagram)) return;
    const snippet = codeSnippetText(diagram);
    let plainText;
    let htmlText;
    let copiedLabel;
    let defaultLabel;
    if (flowButton) {
      const english = state.snippetLanguage === 'en';
      const flowTitle = english ? diagram.markerFlowTitleEn : diagram.markerFlowTitle;
      const flowSteps = english ? diagram.markerFlowEn : diagram.markerFlow;
      const payload = codeSnippetClipboard.markerFlowPayload(flowTitle, flowSteps);
      plainText = payload.plainText;
      htmlText = payload.htmlText;
      copiedLabel = t('ui.flowCopied');
      defaultLabel = t('ui.copyFlow');
    } else if (tableButton) {
      const payload = codeSnippetClipboard.sourceTablePayload(diagram.upstreamSources, state.snippetLanguage);
      plainText = payload.plainText;
      htmlText = payload.htmlText;
      copiedLabel = t('ui.tableCopied');
      defaultLabel = t('ui.copyTable');
    } else if (codeButton) {
      plainText = snippet.code;
      htmlText = codeSnippetClipboard.codeHTML(snippet.code);
      copiedLabel = t('ui.codeCopied');
      defaultLabel = t('ui.copyCode');
    } else {
      plainText = snippet.caption;
      htmlText = codeSnippetClipboard.captionHTML(snippet.caption);
      copiedLabel = t('ui.captionCopied');
      defaultLabel = t('ui.copyCaption');
    }
    await codeSnippetClipboard.writeClipboardPayload(plainText, htmlText);
    const label = button.querySelector('span');
    if (label) label.textContent = copiedLabel;
    els.statusMessage.textContent = copiedLabel;
    window.setTimeout(() => { if (label?.isConnected) label.textContent = defaultLabel; }, 1400);
  });
  els.graph.addEventListener('keydown', (event) => {
    const button = event.target.closest('[data-snippet-language], [data-copy-snippet-code], [data-copy-snippet-caption], [data-copy-upstream-table], [data-copy-marker-flow]');
    if (!button || !isCodeDiagram() || (event.key !== 'Enter' && event.key !== ' ')) return;
    event.preventDefault();
    button.click();
  });
  els.uiHotspots.addEventListener('mouseover', (event) => { const button = event.target.closest('[data-hotspot]'); if (button) { const hotspot = data.hotspots.find((item) => item.id === button.dataset.hotspot); if (hotspot?.nodes[0]) setHover(hotspot.nodes[0]); } });
  els.uiHotspots.addEventListener('mouseout', (event) => { if (event.target.closest('[data-hotspot]')) clearHover(); });
  els.uiHotspots.addEventListener('click', (event) => { const button = event.target.closest('[data-hotspot]'); const hotspot = button && data.hotspots.find((item) => item.id === button.dataset.hotspot); if (hotspot?.nodes[0]) pinSelection(hotspot.nodes[0]); });
  els.details.addEventListener('click', (event) => {
    const comparison = event.target.closest('[data-open-comparison]');
    if (comparison) { chooseDiagram(comparison.dataset.openComparison); return; }
    const button = event.target.closest('[data-related-target]');
    if (button) pinSelection(button.dataset.relatedTarget, button.dataset.relatedComponent || null);
  });
  els.validationIssues.addEventListener('click', (event) => {
    const button = event.target.closest('[data-issue-index]');
    if (!button) return;
    const entry = state.editorAnalysis?.issues?.[Number(button.dataset.issueIndex)];
    const page = state.editorAnalysis?.pages.find((item) => item.id === entry?.pageId) || state.editorAnalysis?.selectedPage;
    const match = page?.matches.find((item) => entry?.cellIds?.includes(item.cellId));
    if (match) editorController.focusMatch(match);
    else if (entry?.cellIds?.[0]) editorController.post({ action: 'petakerja-focus-cell', cellId: entry.cellIds[0] });
  });
  els.validationIssues.addEventListener('change', (event) => {
    const select = event.target.closest('[data-resolve-cell]');
    if (select) editorController.resolveMatch(select.dataset.resolvePage, select.dataset.resolveCell, select.value || null);
  });
  els.details.addEventListener('click', async (event) => {
    const button = event.target.closest('[data-copy-report-paragraph]');
    if (!button) return;
    const paragraph = canonicalDiagram().reportExplanation?.[state.language];
    if (!paragraph) return;
    try {
      await navigator.clipboard.writeText(paragraph);
    } catch (_error) {
      const textarea = document.createElement('textarea');
      textarea.value = paragraph; textarea.setAttribute('readonly', ''); textarea.style.position = 'fixed'; textarea.style.opacity = '0';
      document.body.appendChild(textarea); textarea.select(); document.execCommand('copy'); textarea.remove();
    }
    button.textContent = t('ui.reportParagraphCopied');
    els.statusMessage.textContent = t('ui.reportParagraphCopied');
    window.setTimeout(() => { if (button.isConnected) button.textContent = t('ui.copyReportParagraph'); }, 1400);
  });
  byId('zoom-in').addEventListener('click', () => zoomBy(1.2)); byId('zoom-out').addEventListener('click', () => zoomBy(1 / 1.2)); byId('zoom-fit').addEventListener('click', fitDiagram);
  els.graph.addEventListener('wheel', (event) => { if (isDocumentDiagram()) return; event.preventDefault(); zoomBy(event.deltaY < 0 ? 1.08 : 1 / 1.08); }, { passive: false });
  els.graph.addEventListener('contextmenu', openReportContextMenu);
  els.graph.addEventListener('selectstart', (event) => { if (!isDocumentDiagram()) event.preventDefault(); });
  els.graph.addEventListener('dragstart', (event) => { if (!isDocumentDiagram()) event.preventDefault(); });
  els.graph.addEventListener('pointerdown', (event) => {
    if (isDocumentDiagram()) return;
    if (event.button !== 0) return;
    event.preventDefault();
    state.suppressClick = false;
    state.pointer = {
      id: event.pointerId,
      x: event.clientX,
      y: event.clientY,
      panX: state.panX,
      panY: state.panY,
      dragged: false,
      tapTarget: event.target.closest?.('.diagram-overlay, [data-node], [data-table]') || null,
    };
    els.graph.setPointerCapture(event.pointerId);
  });
  document.addEventListener('pointerdown', (event) => { if (!event.target.closest('.fyp-report-context-menu')) closeReportContextMenu(); });
  document.addEventListener('keydown', async (event) => {
    if (event.key === 'Escape') {
      closeReportContextMenu();
      clearReportColumnSelection({ announce: true });
    }
  });
  document.addEventListener('copy', (event) => {
    if (!isReportTableDiagram() || !state.reportColumnSelection || !event.clipboardData) return;
    const activeElement = document.activeElement;
    const editableTarget = activeElement?.isContentEditable || /^(INPUT|TEXTAREA|SELECT)$/.test(activeElement?.tagName || '');
    if (editableTarget || selectedReportText()) return;
    const copyData = selectedReportColumnCopyData();
    if (!copyData) return;
    event.preventDefault();
    event.clipboardData.setData('text/plain', copyData.payload.plainText);
    event.clipboardData.setData('text/html', copyData.payload.htmlText);
    els.statusMessage.textContent = state.reportTableLanguage === 'en'
      ? `Column copied: ${copyData.column.label}`
      : `Lajur disalin: ${copyData.column.label}`;
  });
  els.graph.addEventListener('scroll', closeReportContextMenu, true);
  window.addEventListener('resize', closeReportContextMenu);
  els.graph.addEventListener('pointermove', (event) => {
    if (!state.pointer || state.pointer.id !== event.pointerId) return;
    const dx = event.clientX - state.pointer.x; const dy = event.clientY - state.pointer.y;
    if (!state.pointer.dragged && Math.hypot(dx, dy) < 5) return;
    if (!state.pointer.dragged) {
      state.pointer.dragged = true; state.suppressClick = true; els.graph.classList.add('is-dragging');
      state.hovered = null; state.hoveredComponentKey = null; applyHighlights(); renderDetails();
    }
    state.fitMode = false; state.panX = state.pointer.panX + dx; state.panY = state.pointer.panY + dy; applyTransform();
  });
  function endPointer(event) {
    if (!state.pointer || state.pointer.id !== event.pointerId) return;
    const { dragged, tapTarget } = state.pointer; state.pointer = null; els.graph.classList.remove('is-dragging');
    if (!dragged && tapTarget) {
      const overlay = tapTarget.closest?.('.diagram-overlay');
      const node = tapTarget.closest?.('[data-node]');
      const table = tapTarget.closest?.('[data-table]');
      if (overlay) {
        const component = (activeAsset()?.components || []).find((item) => item.componentKey === overlay.dataset.componentKey);
        if (component) pinSelection(componentTarget(component), component.componentKey);
      } else if (node) pinSelection(node.dataset.node);
      else if (table) pinSelection(`table:${table.dataset.table}`);
      state.suppressClick = true;
    }
    setTimeout(() => { state.suppressClick = false; }, 0);
  }
  els.graph.addEventListener('pointerup', endPointer); els.graph.addEventListener('pointercancel', endPointer);
  els.referenceButton.addEventListener('click', () => { const diagram = activeDiagram(); if (!diagram.reference) return; els.referenceTitle.textContent = `${t('ui.reference')} · ${diagramText(diagram).title}`; els.referenceImage.src = diagram.reference; els.referenceImage.alt = diagramText(diagram).title; els.referenceDialog.showModal(); });
  byId('close-reference').addEventListener('click', () => els.referenceDialog.close());
  els.referenceDialog.addEventListener('click', (event) => { if (event.target === els.referenceDialog) els.referenceDialog.close(); });
  function closeImportDialog() { if (els.importDialog.open) els.importDialog.close(); state.pendingImport = null; }
  byId('close-import').addEventListener('click', closeImportDialog); byId('cancel-import').addEventListener('click', closeImportDialog);
  els.importDialog.addEventListener('click', (event) => { if (event.target === els.importDialog) closeImportDialog(); });
  function closeRuntimeDialog() { if (els.runtimeDialog.open) els.runtimeDialog.close(); }
  byId('close-runtime').addEventListener('click', closeRuntimeDialog); byId('dismiss-runtime').addEventListener('click', closeRuntimeDialog);
  els.runtimeDialog.addEventListener('click', (event) => { if (event.target === els.runtimeDialog) closeRuntimeDialog(); });
  els.copyRuntimeCommand.addEventListener('click', async () => {
    const command = runtimeLaunchCommand();
    try {
      await navigator.clipboard.writeText(command);
    } catch (_error) {
      const selection = window.getSelection(); const range = document.createRange();
      range.selectNodeContents(els.runtimeCommand); selection.removeAllRanges(); selection.addRange(range);
      document.execCommand('copy'); selection.removeAllRanges();
    }
    els.statusMessage.textContent = t('ui.commandCopied');
    els.copyRuntimeCommand.textContent = t('ui.commandCopied');
    window.setTimeout(() => { els.copyRuntimeCommand.textContent = t('ui.copyCommand'); }, 1400);
  });
  els.confirmImport.addEventListener('click', async () => {
    const pending = state.pendingImport; if (!pending || pending.analysis.fatal) return;
    const pageId = els.importPages.querySelector('input[name="import-page"]:checked')?.value || pending.analysis.selectedPage?.id;
    const override = els.importPages.querySelector(`[data-type-override="${CSS.escape(pageId)}"]`)?.value || null;
    await openImportedPage(pending, pageId, override);
  });

  function containsFiles(event) { return [...(event.dataTransfer?.types || [])].includes('Files'); }
  document.addEventListener('dragenter', (event) => {
    if (!containsFiles(event) || !editorController.available) return;
    event.preventDefault(); state.dropDepth += 1; els.dropOverlay.hidden = false;
  });
  document.addEventListener('dragover', (event) => {
    if (!containsFiles(event) || !editorController.available) return;
    event.preventDefault(); if (event.dataTransfer) event.dataTransfer.dropEffect = 'copy'; els.dropOverlay.hidden = false;
  });
  document.addEventListener('dragleave', (event) => {
    if (!containsFiles(event)) return;
    state.dropDepth = Math.max(0, state.dropDepth - 1); if (!state.dropDepth) els.dropOverlay.hidden = true;
  });
  document.addEventListener('drop', (event) => {
    if (!containsFiles(event) || !editorController.available) return;
    event.preventDefault(); state.dropDepth = 0; els.dropOverlay.hidden = true;
    if (event.dataTransfer.files?.[0]) processImportFile(event.dataTransfer.files[0]);
  });
  document.querySelectorAll('[data-mobile-panel]').forEach((button) => button.addEventListener('click', () => { state.mobilePanel = button.dataset.mobilePanel; updateMobilePanels(); if (state.mobilePanel === 'diagram') requestAnimationFrame(fitDiagram); }));
  document.addEventListener('keydown', (event) => {
    if (event.key === 'Escape') {
      state.selected = null; state.hovered = null; state.selectedComponentKey = null; state.hoveredComponentKey = null; state.selectedConnectionId = null; applyHighlights(); renderDetails(); els.searchResults.hidden = true;
      if (state.workspaceMode !== 'view') editorController.post({ action: 'resetEditor' });
    }
    if (event.key === '/' && !/INPUT|TEXTAREA|SELECT/.test(document.activeElement.tagName)) { event.preventDefault(); els.search.focus(); }
  });
  document.addEventListener('click', (event) => { if (!event.target.closest('.search-shell')) els.searchResults.hidden = true; });
  window.addEventListener('petakerja:open-example', (event) => openExplorerExample(event.detail || {}));
  new ResizeObserver(() => { if (state.fitMode && state.mobilePanel === 'diagram') requestAnimationFrame(fitDiagram); }).observe(els.graph);
  window.addEventListener('beforeunload', (event) => {
    if (!editorController.dirty) return;
    event.preventDefault(); event.returnValue = '';
  });

  window.PETAKERJA_EXPLORER_TEST = { state, editorController, processImportFile, setWorkspaceMode, renderValidation, applyThemePreference, setAgentState, openExplorerExample };

  applyThemePreference(state.themePreference, { persist: false, syncEditor: false });
  renderAll();
  window.renderBlueprintIcons?.(document);
  ensureWorkspaceSession().then(() => hydrateWorkspaceDocument(state.diagramId));
  setAgentState('idle');
  renderAgentPlan(null);
  if (runtimeCapabilities.mcp !== false) pollBridge();
}());
