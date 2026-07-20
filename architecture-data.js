(function () {
  'use strict';

  const ROOT = 'C:/xampp/htdocs/petakerja/';
  const source = (...paths) => paths.map((path) => ROOT + path);

  const scopeGroups = [
    { id: 'core', label: 'Teras FYP', includes: ['core', 'infra'] },
    { id: 'jobops', label: 'JobOps', includes: ['core', 'jobops', 'infra'] },
    { id: 'blog', label: 'Blog & Newsletter', includes: ['blog', 'infra'] },
    { id: 'community', label: 'Community & Intel', includes: ['core', 'community', 'infra'] },
    { id: 'infra', label: 'Infrastructure', includes: ['infra'] },
    { id: 'all', label: 'Semua modul', includes: ['core', 'jobops', 'blog', 'community', 'infra'] },
  ];

  const nodeList = [
    {
      id: 'pengguna', label: 'Pengguna', kind: 'actor', scope: 'core', status: 'concept',
      description: 'Pencari kerja awam atau berdaftar yang meneroka peta, POI, data terbuka, pekerjaan dan pembantu AI.',
      ui: ['start-workspaces', 'map-search', 'jobs-search', 'assistant-panel', 'auth-modal'],
      flow: ['Buka PetaKerja', 'Pilih ruang kerja', 'Gunakan fungsi peta atau pekerjaan'],
    },
    {
      id: 'pentadbir', label: 'Pentadbir', kind: 'actor', scope: 'core', status: 'concept',
      description: 'Pengguna berperanan admin atau owner. Peranan ialah atribut pada profil, bukan subclass berasingan.',
      files: source('src/managers/AdminDashboardManager.ts', 'server/middleware/requireAdmin.ts'),
      routes: ['/api/admin/users', '/api/admin/ai/providers', '/api/admin/ai/usage'],
      tables: ['users', 'ai_admin_audit_logs'], ui: ['auth-modal', 'user-menu'], auth: 'Admin atau owner',
    },
    {
      id: 'browser', label: 'Browser', kind: 'runtime', scope: 'infra', status: 'current',
      description: 'Menjalankan SPA vanilla TypeScript, MapLibre, Chart.js dan semua manager frontend.',
      ui: ['start-workspaces', 'map-canvas'], flow: ['index.html', 'src/main.ts', 'MyPetaApp.init()'],
    },
    {
      id: 'index-html', label: 'index.html', kind: 'entry', scope: 'infra', status: 'current',
      description: 'Dokumen masuk Vite yang menyediakan #app dan memuatkan src/main.ts.', files: source('index.html'), ui: ['start-workspaces'],
    },
    {
      id: 'main-ts', label: 'src/main.ts', kind: 'entry', scope: 'infra', status: 'current',
      description: 'Memilih boot mode blog atau main, mendaftarkan diagnostik dan membina MyPetaApp.', files: source('src/main.ts'),
      flow: ['resolveAppMode()', "new MyPetaApp('app', appMode)", 'app.init()'],
    },
    {
      id: 'mypeta-app', label: 'MyPetaApp', kind: 'class', scope: 'core', status: 'current',
      description: 'Composition root frontend. Membina AppState, shell UI dan manager, kemudian mengikat interaksi.',
      files: source('src/MyPetaApp.ts'), ui: ['start-workspaces', 'ribbon', 'contents-pane', 'catalog-pane'],
      flow: ['buildAppShell()', 'construct managers', 'bind()', 'MapManager.init()'],
    },
    {
      id: 'app-state', label: 'AppState', kind: 'interface', scope: 'infra', status: 'current',
      description: 'Keadaan bersama untuk map, auth, chatbot, job finder, dashboard, kamera dan pilihan pengguna.',
      files: source('src/types.ts'),
    },
    {
      id: 'shared-types', label: 'Jenis Kongsi', kind: 'interface', scope: 'infra', status: 'current',
      description: 'Kontrak TypeScript bersama seperti AppState, AuthUser, JobListing dan UserJobStateRow.',
      files: source('src/types.ts', 'src/modes/jobs/types.ts'),
    },
    {
      id: 'ui-templates', label: 'ui/templates.ts', kind: 'module', scope: 'infra', status: 'current',
      description: 'Templat HTML sebenar bagi start page, ribbon, panes, assistant, settings dan status bar.',
      files: source('src/ui/templates.ts'), ui: ['ribbon', 'contents-pane', 'catalog-pane', 'assistant-panel', 'jobs-cards'],
    },
    {
      id: 'map-manager', label: 'MapManager', kind: 'class', scope: 'core', status: 'current',
      description: 'Mencipta MapLibre map, mengawal kamera, basemap, bangunan 3D dan peralihan masuk workspace.',
      files: source('src/managers/MapManager.ts'), ui: ['map-canvas', 'ribbon-map', 'start-map-preset'],
      flow: ['init()', 'enterWorkspace()', 'fitMalaysiaOverview()', 'setBasemapMode()'],
    },
    {
      id: 'map-tools-manager', label: 'MapToolsPanelManager', kind: 'class', scope: 'core', status: 'current',
      description: 'Mengurus rel alat peta, Navigator A/B, analisis perjalanan, rupa laluan dan serahan Studio Geo.',
      files: source('src/managers/MapToolsPanelManager.ts'), ui: ['map-canvas'],
    },
    {
      id: 'geo-navigation-manager', label: 'GeoNavigationManager', kind: 'class', scope: 'core', status: 'current',
      description: 'Mengorkestrasi titik A/B, GPS, profil perjalanan, alternatif, matriks, isokron dan laluan tempat kerja.',
      files: source('src/managers/GeoNavigationManager.ts'), routes: ['/api/geo/route', '/api/geo/matrix', '/api/geo/isochrone'], ui: ['map-canvas'],
    },
    {
      id: 'geo-route-renderer', label: 'GeoRouteRenderer', kind: 'class', scope: 'core', status: 'current',
      description: 'Menterjemah GeoJSON laluan dan alternatif kepada source/layer MapLibre yang tersusun.',
      files: source('src/managers/GeoRouteRenderer.ts'), ui: ['map-canvas'],
    },
    {
      id: 'route-appearance-manager', label: 'RouteAppearanceManager', kind: 'class', scope: 'core', status: 'current',
      description: 'Mengawal warna, lebar, kelegapan dan gaya paparan laluan tanpa mengubah hasil penghalaan.',
      files: source('src/managers/RouteAppearanceManager.ts', 'src/geo/route-appearance.ts'), ui: ['map-canvas'],
    },
    {
      id: 'geo-service', label: 'Geo client', kind: 'module', scope: 'infra', status: 'current',
      description: 'Klien same-origin TypeScript untuk status, route, matrix, isochrone dan operasi geokod berpagar ciri.',
      files: source('src/services/geo.ts', 'src/geo/contracts.ts'), routes: ['/api/geo/status', '/api/geo/route', '/api/geo/matrix', '/api/geo/isochrone'],
    },
    {
      id: 'geo-api', label: 'Express /api/geo', kind: 'api', scope: 'infra', status: 'current',
      description: 'API same-origin yang menyemak kontrak, mendedahkan status feature flag dan memanggil GeoGateway.',
      files: source('server/routes/geo.ts'), routes: ['/api/geo/status', '/api/geo/route', '/api/geo/matrix', '/api/geo/isochrone', '/api/geo/geocode'],
    },
    {
      id: 'geo-gateway', label: 'GeoGateway', kind: 'service', scope: 'infra', status: 'current',
      description: 'Gerbang penyedia yang menormalkan Valhalla/Nominatim, mengurus cache dan menghasilkan sandaran Haversine yang jelas.',
      files: source('server/geo/gateway.ts', 'server/geo/normalize.ts'), tables: ['geo_route_cache', 'geo_geocode_cache'],
    },
    { id: 'valhalla', label: 'Valhalla', kind: 'external', scope: 'infra', status: 'current', description: 'Penyedia route, matrix dan isochrone. Diaktifkan dan tersedia pada pengesahan 19 Julai 2026.', routes: ['Valhalla HTTP API'] },
    { id: 'nominatim', label: 'Nominatim', kind: 'external', scope: 'infra', status: 'gated', description: 'Penyedia geokod dan carian sempadan yang disokong kod tetapi kini dinyahaktifkan dan tidak tersedia.', routes: ['Nominatim HTTP API'] },
    { id: 'geo-location', label: 'GeoLocation', kind: 'interface', scope: 'core', status: 'current', description: 'Koordinat, label dan ketepatan lokasi yang digunakan oleh Navigator dan laluan pekerjaan.', files: source('src/geo/contracts.ts') },
    { id: 'geo-place', label: 'GeoPlace', kind: 'interface', scope: 'core', status: 'gated', description: 'Hasil geokod tempat/alamat dan sempadan pilihan.', files: source('src/geo/contracts.ts') },
    { id: 'geo-route', label: 'GeoRoute', kind: 'interface', scope: 'core', status: 'current', description: 'GeoJSON laluan ternormal, jarak, tempoh, manuver, profil dan metadata penyedia.', files: source('src/geo/contracts.ts') },
    { id: 'geo-route-alternative', label: 'GeoRouteAlternative', kind: 'interface', scope: 'core', status: 'current', description: 'Pilihan laluan tambahan yang boleh dipilih pengguna.', files: source('src/geo/contracts.ts') },
    { id: 'geo-maneuver', label: 'GeoManeuver', kind: 'interface', scope: 'core', status: 'current', description: 'Arahan belokan dan jarak langkah daripada respons Valhalla.', files: source('src/geo/contracts.ts') },
    { id: 'geo-matrix', label: 'GeoMatrix', kind: 'interface', scope: 'core', status: 'current', description: 'Perbandingan jarak dan tempoh antara berbilang asal/destinasi.', files: source('src/geo/contracts.ts') },
    { id: 'geo-isochrone', label: 'GeoIsochrone', kind: 'interface', scope: 'core', status: 'current', description: 'Poligon kebolehcapaian mengikut masa atau jarak.', files: source('src/geo/contracts.ts') },
    {
      id: 'job-location-resolver', label: 'Job location resolver', kind: 'service', scope: 'jobops', status: 'current',
      description: 'Menyelesaikan alamat tempat kerja, menggunakan keyakinan/cache dan menolak kerja remote atau lokasi keyakinan rendah.',
      files: source('server/geo/job-location.ts', 'server/lib/job-location.ts'), tables: ['job_location_resolutions', 'scraped_jobs'],
    },
    { id: 'job-location-resolution', label: 'JobLocationResolution', kind: 'entity', scope: 'jobops', status: 'current', description: 'Hasil lokasi kerja yang dicache bersama tahap keyakinan dan sebab penolakan.', tables: ['job_location_resolutions'] },
    { id: 'geo-route-cache', label: 'geo_route_cache', kind: 'entity', scope: 'infra', status: 'current', description: 'Cache respons laluan/matrix/isokron ternormal.', tables: ['geo_route_cache'] },
    { id: 'geo-geocode-cache', label: 'geo_geocode_cache', kind: 'entity', scope: 'infra', status: 'gated', description: 'Cache geokod tersedia, walaupun Nominatim kini dinyahaktifkan.', tables: ['geo_geocode_cache'] },
    {
      id: 'geo-studio', label: 'Geo Studio', kind: 'application', scope: 'infra', status: 'current',
      description: 'Aplikasi analitik geospatial berasingan yang menerima serahan konteks daripada alat peta.',
      files: source('apps/geo-studio/src/App.tsx', 'apps/geo-studio/src/api.ts'), tables: ['geo_workspaces', 'geo_workspace_assets'],
    },
    {
      id: 'poi-manager', label: 'POIManager', kind: 'class', scope: 'core', status: 'current',
      description: 'Memuat POI mengikut viewport, menyediakan GeoJSON source, cluster, point dan popup butiran.',
      files: source('src/managers/POIManager.ts'), routes: ['RPC get_pois_in_bounds', 'RPC get_poi_details'],
      tables: ['pois', 'poi_categories', 'data_sources'], ui: ['map-canvas', 'contents-poi'],
      flow: ['loadForView()', 'fetchPOIsInBounds()', "source 'pois'.setData()", 'showPopup()'],
    },
    {
      id: 'search-manager', label: 'SearchManager', kind: 'class', scope: 'core', status: 'current',
      description: 'Mengendalikan carian POI debounced dan fly-to daripada hasil carian.',
      files: source('src/managers/SearchManager.ts'), routes: ['RPC search_pois'], tables: ['pois'], ui: ['map-search'],
      flow: ['input carian', 'searchPOIs()', 'papar keputusan', 'flyTo()'],
    },
    {
      id: 'category-manager', label: 'CategoryManager', kind: 'class', scope: 'core', status: 'current',
      description: 'Membina senarai kategori, mengurus pilihan kategori dan memuat kiraan POI.',
      files: source('src/managers/CategoryManager.ts'), routes: ['RPC get_poi_categories_with_counts'],
      tables: ['poi_categories', 'poi_category_groups', 'pois'], ui: ['contents-poi'],
    },
    {
      id: 'insights-manager', label: 'InsightsManager', kind: 'class', scope: 'core', status: 'current',
      description: 'Mengikat dataset nasional kepada choropleth dan carta negeri.',
      files: source('src/managers/InsightsManager.ts'), tables: ['states'], ui: ['ribbon-data', 'catalog-national'],
      flow: ['pilih dataset', 'OpenDataAPI', 'agregat negeri', 'warna peta + carta'],
    },
    {
      id: 'national-data-cube-manager', label: 'NationalDataCubeManager', kind: 'class', scope: 'core', status: 'current',
      description: 'Mengurus lapisan kubus data 3D nasional yang dimiliki MapManager dan menyegar semula visual mengikut kamera serta tetapan pengguna.',
      files: source('src/managers/NationalDataCubeManager.ts', 'src/managers/MapManager.ts'),
      ui: ['ribbon-data', 'catalog-national', 'map-canvas'],
      flow: ['MapManager', 'renderDataset()', 'refresh()', 'lapisan kubus 3D'],
    },
    {
      id: 'highlight-manager', label: 'HighlightManager', kind: 'class', scope: 'core', status: 'current',
      description: 'Mengurus polygon atau box, POI dalam kawasan dan konteks spatial untuk assistant.',
      files: source('src/managers/HighlightManager.ts'), ui: ['assistant-highlight', 'map-canvas'],
      flow: ['aktifkan Highlight', 'lukis kawasan', 'kumpul POI', 'hantar konteks'],
    },
    {
      id: 'job-manager', label: 'JobFinderManager', kind: 'class', scope: 'core', status: 'current',
      description: 'Mengurus mod Daily Index, Pipeline Index dan Live Search serta kad dan marker pekerjaan.',
      files: source('src/modes/jobs/manager.ts'), routes: ['/api/jobs/supa', '/api/search-jobs', '/api/jobs/me/states'],
      tables: ['scraped_jobs', 'user_job_states'], ui: ['jobs-search', 'jobs-cards', 'jobs-map'],
      flow: ['masukkan query', 'pilih sumber', 'panggil API', 'normalisasi', 'kad + marker'],
    },
    {
      id: 'chatbot-manager', label: 'ChatbotManager', kind: 'class', scope: 'core', status: 'current',
      description: 'Mengurus composer assistant, mode Ask/Plan/Agent, tools dan respons penstriman.',
      files: source('src/managers/ChatbotManager.ts'), routes: ['/api/assistant/chat/stream'],
      tables: ['ai_usage_events', 'ai_user_model_preferences'], ui: ['assistant-panel', 'assistant-highlight'], auth: 'Log masuk',
      flow: ['bina konteks', 'streamAssistantResponse()', 'SSE chunks', 'papar timeline'],
    },
    {
      id: 'auth-manager', label: 'AuthManager', kind: 'class', scope: 'core', status: 'current',
      description: 'Menghidrat sesi Better Auth, Google OAuth, log keluar dan profil aplikasi.',
      files: source('src/managers/AuthManager.ts', 'src/services/auth-client.ts'), routes: ['/api/auth/*', '/api/me/auth-profile'],
      tables: ['user', 'session', 'account', 'users'], ui: ['user-menu', 'auth-modal'],
    },
    {
      id: 'user-menu-manager', label: 'UserMenuManager', kind: 'class', scope: 'core', status: 'current',
      description: 'Mengawal kawalan log masuk/log keluar, menu pengguna dan penutupan paparan terlindung selepas sesi berubah.',
      files: source('src/managers/UserMenuManager.ts'), routes: ['/api/auth/sign-out'], ui: ['user-menu', 'auth-modal'],
    },
    {
      id: 'auth-modal-manager', label: 'AuthModalManager', kind: 'class', scope: 'core', status: 'current',
      description: 'Memaparkan prompt pengesahan dan memulakan aliran Google OAuth tanpa menyokong kata laluan tempatan.',
      files: source('src/managers/AuthModalManager.ts'), routes: ['/api/auth/sign-in/social'], ui: ['auth-modal'],
    },
    {
      id: 'auth-client', label: 'authClient', kind: 'module', scope: 'core', status: 'current',
      description: 'Klien Better Auth pelayar untuk signIn.social(), getSession() dan signOut().',
      files: source('src/services/auth-client.ts'), routes: ['/api/auth/sign-in/social', '/api/auth/get-session', '/api/auth/sign-out'], ui: ['auth-modal', 'user-menu'],
    },
    {
      id: 'profile-bridge', label: 'PetaKerja Profile API', kind: 'service', scope: 'core', status: 'current',
      description: 'Route /api/me/auth-profile dan getAppSessionFromHeaders() yang mencari, memaut atau mencipta public.users.',
      files: source('server/app.ts', 'server/middleware/requireAuth.ts', 'server/lib/auth-user.ts'), routes: ['/api/me/auth-profile'], tables: ['user', 'users'], ui: ['user-menu'], auth: 'Log masuk',
    },
    {
      id: 'google-oauth', label: 'Google OAuth', kind: 'external', scope: 'infra', status: 'current',
      description: 'Penyedia OAuth luaran untuk pemilihan akaun dan persetujuan pengguna.', routes: ['Google OAuth authorize/callback'], ui: ['auth-modal'],
    },
    {
      id: 'admin-manager', label: 'AdminDashboardManager', kind: 'class', scope: 'core', status: 'current',
      description: 'Membuka papan pemuka terlindung, memuat ringkasan, rekod penggunaan AI, senarai pengguna, status penyedia AI dan tindakan owner untuk kekunci platform serta model.',
      files: source('src/managers/AdminDashboardManager.ts'), routes: ['/api/admin/ai/providers', '/api/admin/ai/usage', '/api/admin/users'],
      tables: ['users', 'ai_provider_credentials', 'ai_usage_events', 'ai_admin_audit_logs'], ui: ['[data-dropdown-action="admin"]', '#admin-dashboard', '[data-admin-action="tab"][data-tab="overview"]', '[data-admin-action="tab"][data-tab="usage"]', '[data-admin-action="tab"][data-tab="users"]', '[data-admin-action="tab"][data-tab="providers"]', '.admin-table', '.admin-provider-table', '[data-admin-action="platform-key"]', '[data-admin-action="refresh-models"]'], auth: 'Admin atau owner',
    },
    {
      id: 'admin-ui', label: 'PetaKerja Admin UI', kind: 'interface', scope: 'core', status: 'current',
      description: 'Pencetus papan pemuka, paparan Overview, Usage, Users dan Providers, jadual status, modal kekunci platform serta keadaan kosong atau ralat.',
      files: source('src/managers/AdminDashboardManager.ts', 'src/styles/admin-ai.css'),
      ui: ['[data-dropdown-action="admin"]', '#admin-dashboard', '[data-admin-action="tab"][data-tab="overview"]', '[data-admin-action="tab"][data-tab="usage"]', '[data-admin-action="tab"][data-tab="users"]', '[data-admin-action="tab"][data-tab="providers"]', '.admin-usage-table', '.admin-table', '.admin-provider-table', '#admin-platform-key-modal', '[data-admin-action="refresh-models"]'], auth: 'Admin atau owner',
    },
    {
      id: 'admin-api-client', label: 'Admin API Client', kind: 'module', scope: 'core', status: 'current',
      description: 'Klien berautentikasi dalam aiProviderApi.ts untuk ringkasan penggunaan AI, pengguna, status penyedia, simpanan kekunci platform dan segar semula model.',
      files: source('src/services/aiProviderApi.ts'), routes: ['/api/admin/ai/usage', '/api/admin/users', '/api/admin/ai/providers', '/api/admin/ai/providers/:providerId/platform-key', '/api/admin/ai/providers/refresh-models'], tables: ['users', 'ai_usage_events', 'ai_provider_credentials'],
      ui: ['[data-admin-action="tab"][data-tab="overview"]', '[data-admin-action="tab"][data-tab="usage"]', '.admin-usage-table', '[data-admin-action="tab"][data-tab="users"]', '.admin-table', '[data-admin-action="tab"][data-tab="providers"]', '.admin-provider-table'], auth: 'Admin atau owner',
    },
    {
      id: 'admin-dashboard-api', label: 'Protected Admin APIs', kind: 'api', scope: 'core', status: 'current',
      description: 'Kumpulan endpoint papan pemuka yang mengesahkan sesi dan peranan sebelum memulangkan ringkasan penyedia, penggunaan AI dan pengguna.',
      files: source('server/app.ts', 'server/routes/admin.ts', 'server/middleware/requireAuth.ts', 'server/middleware/requireAdmin.ts'),
      routes: ['GET /api/admin/ai/providers', 'GET /api/admin/ai/usage', 'GET /api/admin/users', 'requireAuth()', 'requireAdmin()'],
      tables: ['users', 'ai_provider_credentials', 'ai_usage_events'], ui: ['#admin-dashboard', '[data-admin-action="tab"][data-tab="overview"]'], auth: 'Admin atau owner',
    },
    {
      id: 'admin-usage-api', label: 'Admin Usage API', kind: 'api', scope: 'core', status: 'current',
      description: 'GET /api/admin/ai/usage memulangkan sehingga 100 peristiwa penggunaan pembantu AI terkini serta jumlah permintaan, ralat, token dan kos. Ia bukan log pelayan umum atau ai_admin_audit_logs.',
      files: source('server/app.ts', 'server/routes/admin.ts', 'server/middleware/requireAuth.ts', 'server/middleware/requireAdmin.ts'),
      routes: ['GET /api/admin/ai/usage', 'requireAuth()', 'requireAdmin()'], tables: ['users', 'ai_usage_events'],
      ui: ['[data-admin-action="tab"][data-tab="usage"]', '.admin-usage-table'], auth: 'Admin atau owner',
    },
    {
      id: 'admin-users-api', label: 'Admin Users API', kind: 'api', scope: 'core', status: 'current',
      description: 'Route GET /api/admin/users yang menjalankan requireAuth dan requireAdmin sebelum membaca 100 profil terkini.',
      files: source('server/app.ts', 'server/routes/admin.ts', 'server/middleware/requireAuth.ts', 'server/middleware/requireAdmin.ts'),
      routes: ['GET /api/admin/users', 'requireAuth()', 'requireAdmin()'], tables: ['users'], ui: ['.admin-table'], auth: 'Admin atau owner',
    },
    {
      id: 'admin-ai-providers-api', label: 'Admin AI Providers API', kind: 'api', scope: 'core', status: 'warning',
      description: 'Route pentadbir untuk melihat penyedia. Simpanan kekunci platform dan segar semula model dihadkan kepada owner; laluan refresh mempunyai ketidakselarasan medan dengan skema langsung semasa.',
      files: source('server/app.ts', 'server/routes/admin.ts', 'server/middleware/requireAuth.ts', 'server/middleware/requireAdmin.ts', 'server/services/ai-provider-service.ts'),
      routes: ['GET /api/admin/ai/providers', 'POST /api/admin/ai/providers/:providerId/platform-key', 'POST /api/admin/ai/providers/refresh-models', 'requireAuth()', 'requireAdmin()', 'encryptSecret()', 'ModelCache.invalidate()'],
      tables: ['users', 'ai_provider_credentials', 'ai_admin_audit_logs'],
      ui: ['[data-admin-action="tab"][data-tab="providers"]', '.admin-provider-table', '[data-admin-action="platform-key"]', '#admin-platform-key-modal', '[data-admin-action="refresh-models"]'], auth: 'Admin atau owner; hanya owner boleh menulis',
    },
    {
      id: 'panel-manager', label: 'PanelManager', kind: 'class', scope: 'core', status: 'current',
      description: 'Mengawal ribbon, tab, contents/catalog panes, settings dan paparan mudah alih.',
      files: source('src/managers/PanelManager.ts'), ui: ['ribbon', 'contents-pane', 'catalog-pane'],
    },
    {
      id: 'workspace-ui', label: 'PetaKerja Workspace UI', kind: 'interface', scope: 'core', status: 'current',
      description: 'Kad preset, kanvas peta dan kawalan ribbon untuk memasuki workspace, memilih terrain serta menghidupkan bangunan 3D.',
      files: source('src/ui/templates.ts', 'src/MyPetaApp.ts'),
      ui: ['start-workspaces', 'start-map-preset', 'map-canvas', 'ribbon-map', '.basemap-mode-btn[data-basemap="terrain"]', '#toggle-3d-buildings'],
    },
    {
      id: 'maplibre-gl', label: 'MapLibre GL', kind: 'runtime', scope: 'infra', status: 'current',
      description: 'Runtime peta yang mengurus kamera, sumber/lapisan POI, DEM terrain, satellite raster dan lapisan bangunan 3D.',
      files: source('src/managers/MapManager.ts', 'src/managers/POIManager.ts'), ui: ['map-canvas', 'ribbon-map'],
    },
    {
      id: 'supabase-module', label: 'supabase.ts', kind: 'module', scope: 'infra', status: 'current',
      description: 'Klien supabase-js untuk bacaan geospatial dan RPC frontend. Bukan lapisan ORM.',
      files: source('src/services/supabase.ts'), routes: ['get_pois_in_bounds', 'search_pois', 'get_poi_details'],
      tables: ['pois', 'poi_categories'],
    },
    {
      id: 'open-data-api', label: 'OpenDataAPI', kind: 'service', scope: 'core', status: 'current',
      description: 'Memuat dan cache dataset data.gov.my, memilih tempoh terbaru dan mengagregat nilai mengikut negeri.',
      files: source('src/services/OpenDataAPI.ts'), routes: ['https://api.data.gov.my/data-catalogue'], tables: ['states'], ui: ['catalog-national'],
    },
    {
      id: 'assistant-stream', label: 'assistantStream.ts', kind: 'module', scope: 'core', status: 'current',
      description: 'Klien browser untuk POST berautentikasi dan pembacaan respons assistant secara streaming.',
      files: source('src/services/assistantStream.ts'), routes: ['/api/assistant/chat/stream'], ui: ['assistant-panel'],
    },
    {
      id: 'jobs-api', label: 'Jobs API modules', kind: 'module', scope: 'core', status: 'current',
      description: 'api.ts, grep-api.ts, supa-api.ts dan me-api.ts menyatukan tiga sumber carian serta status pengguna.',
      files: source('src/modes/jobs/api.ts', 'src/modes/jobs/grep-api.ts', 'src/modes/jobs/supa-api.ts', 'src/modes/jobs/me-api.ts'),
      routes: ['/api/search-jobs', '/api/jobs/supa', '/api/jobs/me/states'], tables: ['scraped_jobs', 'user_job_states'], ui: ['jobs-search'],
    },
    {
      id: 'supa-jobs-route', label: 'Supa Jobs Route', kind: 'service', scope: 'core', status: 'current',
      description: 'Route Daily Index awam yang mengesah parameter, mengurus cache segar/stale, menapis rekod scraped_jobs dan memulangkan JobGrepResponse.',
      files: source('server/routes/intel-jobs.ts'), routes: ['GET /api/jobs/supa'], tables: ['scraped_jobs'], ui: ['jobs-search'],
      flow: ['GET /api/jobs/supa', 'semak cache', 'query scraped_jobs', 'tapis dan halaman', 'JobGrepResponse'],
    },
    {
      id: 'job-search-relevance', label: 'jobSearchRelevance', kind: 'module', scope: 'core', status: 'current',
      description: 'Modul kongsi yang menormalkan istilah carian dan menapis pekerjaan mengikut perkaitan tajuk serta konteks teknologi.',
      files: source('shared/jobSearchRelevance.ts'), tables: ['scraped_jobs'], ui: ['jobs-search', 'jobs-cards'],
      flow: ['filterJobsBySearchQuery()', 'skor perkaitan', 'susun hasil'],
    },
    {
      id: 'express-app', label: 'server/app.ts', kind: 'runtime', scope: 'infra', status: 'current',
      description: 'Mendaftarkan middleware Express, route awam, route berautentikasi dan route admin.',
      files: source('server/app.ts'), routes: ['/api/health', '/api/search-jobs', '/api/assistant/chat/stream', '/api/jobs/me/*'],
    },
    {
      id: 'github-actions', label: 'GitHub Actions', kind: 'runtime', scope: 'infra', status: 'current',
      description: 'Menjadualkan ingest pekerjaan, extractor HTTP, kafe dan acara melalui empat workflow kelompok yang berasingan.',
      files: source('.github/workflows/scrape-jobs.yml', '.github/workflows/extractors-cron.yml', '.github/workflows/scrape-coffee-shops.yml', '.github/workflows/scrape-events.yml'),
      flow: ['jadual UTC', 'runner CI', 'service-role Supabase'],
    },
    {
      id: 'vercel-runtime', label: 'Vercel runtime', kind: 'runtime', scope: 'infra', status: 'current',
      description: 'Menempatkan binaan Vite dan route Express same-origin melalui konfigurasi vercel.json.',
      files: source('vercel.json', 'api/server.ts', 'server/app.ts'), routes: ['/api/*', '/architecture-explorer/*'],
    },
    {
      id: 'vercel-daily-cron', label: 'Vercel daily cron', kind: 'service', scope: 'infra', status: 'current',
      description: 'Menjalankan promosi post, gulungan analitik, penghantaran siaran dan polling watchlist setiap hari sebagai langkah terasing.',
      files: source('vercel.json', 'server/app.ts'), routes: ['GET /api/cron/daily'], auth: 'CRON_SECRET',
    },
    {
      id: 'digitalocean-geo-host', label: 'DigitalOcean geo host', kind: 'runtime', scope: 'infra', status: 'current',
      description: 'Droplet Singapura untuk rintis penghalaan Valhalla sahaja, dilindungi Caddy dan token pelayan.',
      files: source('infra/geo/compose.routing.yaml', 'infra/geo/Caddy.routing', 'infra/geo/README.md'), routes: ['https://geo.petakerja.my'],
    },
    {
      id: 'valhalla-tile-builder', label: 'Valhalla tile builder', kind: 'service', scope: 'infra', status: 'current',
      description: 'Membina valhalla_tiles.tar daripada PBF wilayah dengan prasemak cakera, arkib undur dan semakan laluan contoh.',
      files: source('infra/geo/scripts/rebuild-valhalla-routing.sh', 'infra/geo/scripts/preflight-routing.sh', 'infra/geo/compose.routing.yaml'),
    },
    {
      id: 'github-repository', label: 'GitHub repository', kind: 'runtime', scope: 'infra', status: 'current',
      description: 'Repositori sumber produksi; perubahan pada main mencetuskan laluan bina dan release produksi Vercel.',
      files: source('package.json', 'vercel.json', '.github/workflows'), flow: ['main branch', 'Vercel production deployment'],
    },
    {
      id: 'vercel-build-pipeline', label: 'Vercel build pipeline', kind: 'runtime', scope: 'infra', status: 'current',
      description: 'Menjalankan npm run build dan menghasilkan aplikasi Vite, docs Docusaurus, Geo Studio, Architecture Explorer serta bundle server Express.',
      files: source('package.json', 'scripts/build-docs.mjs', 'scripts/build-geo-studio.mjs', 'scripts/build-architecture-explorer.mjs'),
      flow: ['npm run build', 'dist/'],
    },
    {
      id: 'vercel-edge-delivery', label: 'Vercel edge delivery', kind: 'runtime', scope: 'infra', status: 'current',
      description: 'Menyampaikan aset statik dan respons CDN sebelum route API same-origin dihantar kepada Node Function.',
      files: source('vercel.json'), routes: ['https://petakerja.my/*'],
    },
    {
      id: 'vercel-node-function', label: 'Vercel Node Function', kind: 'runtime', scope: 'infra', status: 'current',
      description: 'Menjalankan api/server.ts dan server/app.ts sebagai API produksi same-origin serta titik masuk cron harian.',
      files: source('api/server.ts', 'server/app.ts'), routes: ['/api/*', '/api/cron/daily'],
    },
    {
      id: 'cloudflare-dns', label: 'Cloudflare authoritative DNS', kind: 'external', scope: 'infra', status: 'current',
      description: 'Rekod DNS-only berkuasa untuk petakerja.my dan geo.petakerja.my; origin penghalaan tidak diproksi.',
      files: source('docs/development/custom-domain-and-staging.md'), routes: ['petakerja.my', 'geo.petakerja.my'],
    },
    {
      id: 'exabytes-registrar', label: 'Exabytes registrar', kind: 'external', scope: 'infra', status: 'current',
      description: 'Pendaftar domain produksi yang didelegasikan kepada nameserver berkuasa Cloudflare.',
      files: source('docs/development/custom-domain-and-staging.md'), routes: ['petakerja.my'],
    },
    {
      id: 'supabase-storage', label: 'Supabase Storage', kind: 'database', scope: 'infra', status: 'current',
      description: 'Storan objek berkawalan polisi untuk media blog, diagram, pembentangan, resume dan aset Geo Studio; pentadbiran kekal pada server atau CI dipercayai.',
      files: source('server/routes/blog.ts', 'server/routes/architecture-diagrams.ts', 'server/routes/geo-studio.ts', 'server/routes/resumes.ts'),
      routes: ['Supabase Storage API'],
    },
    {
      id: 'google-cloud-services', label: 'Google OAuth + Gmail', kind: 'external', scope: 'infra', status: 'current',
      description: 'Perkhidmatan Google berkumpulan untuk OAuth dan integrasi Gmail melalui laluan backend berautentikasi.',
      files: source('server/lib/auth.ts', 'server/routes/gmail.ts'),
    },
    {
      id: 'email-platforms', label: 'SMTP / Mailgun', kind: 'external', scope: 'infra', status: 'current',
      description: 'Penyedia penghantaran e-mel berkumpulan yang dipanggil hanya melalui proses backend dipercayai.',
      files: source('server/services/email-provider.ts', 'server/services/blog-broadcasts.ts'),
    },
    {
      id: 'external-data-platforms', label: 'Public data + job-source APIs', kind: 'external', scope: 'infra', status: 'current',
      description: 'API data awam dan sumber pekerjaan berkumpulan yang digunakan oleh server atau ingestion berjadual.',
      files: source('server/routes/open-data.ts', 'server/extractors', '.github/workflows'),
    },
    {
      id: 'better-auth', label: 'Better Auth', kind: 'service', scope: 'infra', status: 'current',
      description: 'Identiti Google dan sesi cookie. Server memetakan identiti kepada public.users.',
      files: source('server/lib/auth.ts', 'server/lib/auth-user.ts'), tables: ['user', 'session', 'account', 'verification', 'users'],
      routes: ['/api/auth/*'], ui: ['auth-modal'],
    },
    {
      id: 'supabase-db', label: 'Supabase Postgres + PostGIS', kind: 'database', scope: 'infra', status: 'current',
      description: 'Datastore operasi PetaKerja: 73 jadual public, 86 foreign key dan PostGIS.',
      tables: ['73 public tables'], routes: ['supabase-js Data API', 'pg.Pool direct SQL'],
    },
    {
      id: 'data-gov', label: 'data.gov.my', kind: 'external', scope: 'infra', status: 'current',
      description: 'Sumber statistik nasional yang dibaca dan dicache oleh OpenDataAPI.', routes: ['api.data.gov.my/data-catalogue'], ui: ['catalog-national'],
    },
    {
      id: 'ai-provider', label: 'AI Providers', kind: 'external', scope: 'infra', status: 'current',
      description: 'Provider native atau OpenAI-compatible yang dipilih melalui resolver backend.',
      files: source('server/ai/provider-resolver.ts', 'server/ai/openai-compatible-client.ts'),
      tables: ['ai_provider_credentials', 'ai_user_model_preferences', 'ai_usage_events'], ui: ['assistant-panel'],
    },
    {
      id: 'ai-provider-registry', label: 'AI_PROVIDER_REGISTRY', kind: 'module', scope: 'core', status: 'current',
      description: 'Pendaftaran backend bagi nama, model terbina dalam, URL asas dan keupayaan pengambilan model setiap penyedia AI.',
      files: source('server/ai/provider-registry.ts'), routes: ['getProviderFetchConfig()'],
      ui: ['.admin-provider-table'],
    },
    {
      id: 'auth-identity', label: 'AuthIdentity', kind: 'entity', scope: 'core', status: 'current',
      description: 'Rekod Better Auth public.user untuk identiti log masuk.', tables: ['user'], files: source('server/lib/auth.ts'), ui: ['auth-modal'],
    },
    {
      id: 'user-profile', label: 'UserProfile', kind: 'entity', scope: 'core', status: 'current',
      description: 'Profil aplikasi public.users dengan role, selected_state dan bridge Better Auth.', tables: ['users'], routes: ['/api/me/auth-profile'], ui: ['user-menu'],
    },
    { id: 'state-entity', label: 'State', kind: 'entity', scope: 'core', status: 'current', description: 'Negeri Malaysia untuk profil, POI dan agregasi data.', tables: ['states'], ui: ['map-canvas', 'catalog-national'] },
    { id: 'data-source-entity', label: 'DataSource', kind: 'entity', scope: 'core', status: 'current', description: 'Pendaftaran sumber import POI.', tables: ['data_sources'], ui: ['contents-poi'] },
    { id: 'poi-group-entity', label: 'POICategoryGroup', kind: 'entity', scope: 'core', status: 'current', description: 'Kumpulan kategori seperti Finance, Health dan Transport.', tables: ['poi_category_groups'], ui: ['contents-poi'] },
    { id: 'poi-category-entity', label: 'POICategory', kind: 'entity', scope: 'core', status: 'current', description: 'Kategori POI yang mengawal ikon, warna, label dan min zoom.', tables: ['poi_categories'], ui: ['contents-poi'] },
    { id: 'poi-entity', label: 'POI', kind: 'entity', scope: 'core', status: 'current', description: 'Lokasi geospatial yang dipaparkan sebagai cluster, point dan popup.', tables: ['pois'], ui: ['map-canvas', 'contents-poi'] },
    { id: 'highlight-entity', label: 'HighlightArea', kind: 'interface', scope: 'core', status: 'current', description: 'Jenis HighlightEntry bagi polygon/box dan POI yang terkandung.', files: source('src/types.ts'), ui: ['assistant-highlight', 'map-canvas'] },
    { id: 'job-entity', label: 'JobListing', kind: 'interface', scope: 'core', status: 'current', description: 'Kontrak pekerjaan normalisasi daripada pelbagai sumber.', files: source('src/modes/jobs/types.ts'), tables: ['scraped_jobs'], ui: ['jobs-cards', 'jobs-map'] },
    { id: 'job-state-entity', label: 'UserJobState', kind: 'entity', scope: 'core', status: 'current', description: 'Status pekerjaan per pengguna: saved, applied, interviewing dan lain-lain.', tables: ['user_job_states'], routes: ['/api/jobs/me/states'], ui: ['jobs-cards'], auth: 'Log masuk' },
    { id: 'ai-credential-entity', label: 'AIProviderCredential', kind: 'entity', scope: 'core', status: 'current', description: 'Credential AI user/platform yang disimpan terenkripsi oleh backend.', tables: ['ai_provider_credentials'], routes: ['/api/ai/providers'], ui: ['assistant-panel'], auth: 'Log masuk' },
    { id: 'ai-preference-entity', label: 'AIModelPreference', kind: 'entity', scope: 'core', status: 'current', description: 'Pilihan provider dan model per mode assistant.', tables: ['ai_user_model_preferences'], ui: ['assistant-panel'], auth: 'Log masuk' },
    { id: 'ai-usage-entity', label: 'AIUsageEvent', kind: 'entity', scope: 'core', status: 'current', description: 'Ledger penggunaan AI dengan provider/model, status, token, anggaran kos dan metadata konteks.', tables: ['ai_usage_events'], routes: ['/api/admin/ai/usage'], auth: 'Admin atau owner untuk ringkasan' },
    { id: 'audit-log-entity', label: 'AdminAuditLog', kind: 'entity', scope: 'core', status: 'current', description: 'Jejak tindakan pentadbir terhadap konfigurasi AI.', tables: ['ai_admin_audit_logs'], auth: 'Admin atau owner' },
    {
      id: 'job-listings-legacy', label: 'public.job_listings', kind: 'missing', scope: 'jobops', status: 'legacy',
      description: 'Dijangka oleh mod Grep/pipeline tertentu tetapi tidak wujud dalam skema Supabase langsung semasa.',
      files: source('src/modes/jobs/grep-api.ts'), ui: ['jobs-search'],
    },
    {
      id: 'pipeline-service', label: 'PipelineService', kind: 'service', scope: 'jobops', status: 'current',
      description: 'Orkestrasi asynchronous untuk saved-job pipeline, scoring, tailoring dan item progress.',
      files: source('server/services/pipeline-service.ts'), routes: ['/api/jobs/me/pipeline/runs'],
      tables: ['pipeline_runs', 'pipeline_run_items', 'user_job_states'], ui: ['jobs-cards'], auth: 'Log masuk',
    },
    { id: 'user-dashboard', label: 'UserDashboardManager', kind: 'class', scope: 'jobops', status: 'current', description: 'Dashboard pengguna untuk profil, pekerjaan, pipeline, Gmail dan watchlist.', files: source('src/managers/UserDashboardManager.ts'), routes: ['/api/me/*', '/api/jobs/me/*'], tables: ['users', 'user_job_states'], ui: ['user-menu'], auth: 'Log masuk' },
    { id: 'gmail-service', label: 'Gmail tracking', kind: 'service', scope: 'jobops', status: 'current', description: 'OAuth Gmail, sync mesej, padanan tahap permohonan dan linkage job state.', files: source('server/services/gmail-tracking/gmail-sync.ts'), routes: ['/api/jobs/me/gmail/*'], tables: ['user_gmail_integrations', 'user_gmail_messages', 'user_gmail_sync_runs'], auth: 'Log masuk' },
    { id: 'watchlist-service', label: 'Company Watchlist', kind: 'service', scope: 'jobops', status: 'current', description: 'Menyimpan syarikat/ATS, polling pekerjaan dan notifikasi hasil baharu.', files: source('server/services/watchlist/index.ts'), routes: ['/api/jobs/me/watchlist/*'], tables: ['user_company_watchlist', 'watchlist_discovered_jobs', 'watchlist_polls'], auth: 'Log masuk' },
    { id: 'extractor-service', label: 'Extractor Registry', kind: 'service', scope: 'jobops', status: 'current', description: 'Registry dan runner extractor untuk pelbagai job boards dengan rekod run dan hasil.', files: source('server/services/extractors/runner.ts', 'server/services/extractors/extractor-registry.ts'), routes: ['/api/admin/extractors/*'], tables: ['extractor_runs', 'extractor_jobs', 'scraped_jobs'], auth: 'Admin' },
    { id: 'pipeline-runs-entity', label: 'pipeline_runs', kind: 'entity', scope: 'jobops', status: 'current', description: 'Header bagi setiap pipeline run pengguna.', tables: ['pipeline_runs'] },
    { id: 'pipeline-items-entity', label: 'pipeline_run_items', kind: 'entity', scope: 'jobops', status: 'current', description: 'Item pekerjaan dan status langkah dalam pipeline run.', tables: ['pipeline_run_items'] },
    { id: 'gmail-entity', label: 'Gmail entities', kind: 'entity', scope: 'jobops', status: 'current', description: 'Integration, message dan sync-run Gmail per pengguna.', tables: ['user_gmail_integrations', 'user_gmail_messages', 'user_gmail_sync_runs'] },
    { id: 'watchlist-entity', label: 'Watchlist entities', kind: 'entity', scope: 'jobops', status: 'current', description: 'Watchlist entry, discovered jobs dan poll history.', tables: ['user_company_watchlist', 'watchlist_discovered_jobs', 'watchlist_polls'] },
    { id: 'extractor-entity', label: 'Extractor entities', kind: 'entity', scope: 'jobops', status: 'current', description: 'Metadata invocation extractor dan full job output.', tables: ['extractor_runs', 'extractor_jobs'] },
    { id: 'blog-manager', label: 'BlogManager', kind: 'class', scope: 'blog', status: 'current', description: 'Boot berasingan untuk /blog, senarai post, carian, filter dan sesi author.', files: source('src/modes/blog/manager.ts'), routes: ['/api/blog/posts', '/api/blog/search'], tables: ['blog_posts', 'blog_categories', 'blog_tags'], ui: ['blog-posts', 'blog-search'] },
    { id: 'blog-editor', label: 'BlogEditor', kind: 'class', scope: 'blog', status: 'current', description: 'Editor TipTap dengan export, media, Draw.io, Mermaid dan AI typewriter.', files: source('src/modes/blog/editor-v2/BlogEditor.ts'), routes: ['/api/blog/me/posts', '/api/blog/media'], tables: ['blog_posts', 'blog_media', 'blog_post_revisions'], ui: ['blog-write'], auth: 'Log masuk' },
    { id: 'blog-routes', label: 'Blog API routes', kind: 'module', scope: 'blog', status: 'current', description: 'Route awam, author, admin, analytics, comments, reactions, newsletter dan broadcast.', files: source('server/routes/blog.ts', 'server/routes/blog-newsletters.ts', 'server/routes/blog-broadcasts.ts'), routes: ['/api/blog/*', '/api/admin/blog/*'], tables: ['blog_posts', 'blog_subscribers', 'blog_broadcasts'] },
    { id: 'blog-data', label: 'Blog entities', kind: 'entity', scope: 'blog', status: 'current', description: 'Post, author, category, tag, comment, reaction, revision dan analytics.', tables: ['blog_posts', 'blog_author_profiles', 'blog_comments', 'blog_analytics_events'], ui: ['blog-posts'] },
    { id: 'newsletter-data', label: 'Newsletter entities', kind: 'entity', scope: 'blog', status: 'current', description: 'Subscriber, newsletter, broadcast, recipients, event e-mel dan suppression.', tables: ['blog_newsletters', 'blog_subscribers', 'blog_broadcasts', 'blog_email_events'], ui: ['blog-subscribe'] },
    { id: 'intel-manager', label: 'IntelManager', kind: 'class', scope: 'community', status: 'current', description: 'Layer intel, marker, analytics dan panel wiki bagi pekerjaan, startup, event, VC dan masjid.', files: source('src/managers/IntelManager.ts'), ui: ['contents-intel', 'catalog-intel', 'map-canvas'] },
    { id: 'kopi-manager', label: 'KopiManager', kind: 'class', scope: 'community', status: 'current', description: 'Mod kopi dan specialty coffee berasaskan Supabase/API.', files: source('src/modes/kopi/manager.ts'), routes: ['/api/intel/kopi/:source'], tables: ['coffee_shops'], ui: ['contents-intel', 'map-canvas'] },
    { id: 'event-manager', label: 'EventManager', kind: 'class', scope: 'community', status: 'current', description: 'Memuat acara teknologi dan marker peta.', files: source('src/modes/event/manager.ts'), routes: ['/api/intel/events'], tables: ['events'], ui: ['contents-intel', 'map-canvas'] },
    { id: 'community-data', label: 'Community entities', kind: 'entity', scope: 'community', status: 'current', description: 'Masjid, submission komuniti, poll, option dan vote.', tables: ['rc_masjids', 'rc_submissions', 'polls', 'poll_options', 'votes'], ui: ['contents-intel'] },
    { id: 'spatial-ref', label: 'spatial_ref_sys', kind: 'system-table', scope: 'infra', status: 'warning', description: 'Jadual sistem PostGIS. RLS tidak aktif dalam snapshot semasa; tiada perubahan dibuat oleh explorer.', tables: ['spatial_ref_sys'], routes: ['Supabase RLS guide'] },
  ];

  const nodes = Object.fromEntries(nodeList.map((node) => [node.id, node]));

  const edge = (from, to, label, diagrams, type = 'association') => ({ from, to, label, diagrams, type });
  const edges = [
    edge('browser', 'index-html', 'memuat', ['overview', 'architecture']),
    edge('index-html', 'main-ts', 'import', ['overview', 'architecture']),
    edge('main-ts', 'mypeta-app', 'membina', ['overview', 'implementation', 'architecture'], 'composition'),
    edge('mypeta-app', 'app-state', 'memiliki', ['overview', 'implementation'], 'composition'),
    edge('mypeta-app', 'shared-types', 'menggunakan jenis', ['implementation'], 'dependency'),
    edge('mypeta-app', 'ui-templates', 'render shell', ['overview', 'implementation', 'architecture'], 'dependency'),
    edge('mypeta-app', 'map-manager', 'memiliki', ['overview', 'implementation', 'modules'], 'composition'),
    edge('mypeta-app', 'poi-manager', 'memiliki', ['overview', 'implementation', 'modules'], 'composition'),
    edge('mypeta-app', 'search-manager', 'memiliki', ['implementation', 'modules'], 'composition'),
    edge('mypeta-app', 'category-manager', 'memiliki', ['implementation', 'modules'], 'composition'),
    edge('mypeta-app', 'insights-manager', 'memiliki', ['implementation', 'modules'], 'composition'),
    edge('mypeta-app', 'highlight-manager', 'memiliki', ['implementation', 'modules'], 'composition'),
    edge('mypeta-app', 'job-manager', 'memiliki', ['overview', 'implementation', 'modules'], 'composition'),
    edge('mypeta-app', 'chatbot-manager', 'memiliki', ['overview', 'implementation', 'modules'], 'composition'),
    edge('mypeta-app', 'auth-manager', 'memiliki', ['overview', 'implementation', 'modules'], 'composition'),
    edge('mypeta-app', 'panel-manager', 'memiliki', ['implementation'], 'composition'),
    edge('mypeta-app', 'admin-manager', 'memiliki', ['implementation', 'modules'], 'composition'),
    edge('poi-manager', 'supabase-module', 'RPC POI', ['overview', 'implementation', 'architecture', 'data-flow'], 'dependency'),
    edge('search-manager', 'supabase-module', 'search_pois', ['implementation', 'data-flow'], 'dependency'),
    edge('category-manager', 'supabase-module', 'counts', ['implementation', 'data-flow'], 'dependency'),
    edge('supabase-module', 'supabase-db', 'Data API', ['overview', 'architecture', 'data-flow'], 'dependency'),
    edge('insights-manager', 'open-data-api', 'dataset', ['overview', 'implementation', 'architecture', 'data-flow'], 'dependency'),
    edge('open-data-api', 'data-gov', 'HTTP GET', ['overview', 'architecture', 'data-flow'], 'dependency'),
    edge('job-manager', 'jobs-api', 'search', ['overview', 'implementation', 'sequence', 'activity', 'data-flow', 'user-search-jobs-flowchart'], 'dependency'),
    edge('jobs-api', 'express-app', 'HTTP', ['overview', 'architecture', 'data-flow'], 'dependency'),
    edge('express-app', 'supabase-db', 'pg.Pool', ['overview', 'architecture', 'data-flow'], 'dependency'),
    edge('jobs-api', 'supa-jobs-route', 'GET /api/jobs/supa', ['sequence', 'user-search-jobs-flowchart'], 'dependency'),
    edge('supa-jobs-route', 'supabase-db', 'SELECT public.scraped_jobs', ['sequence', 'user-search-jobs-flowchart'], 'dependency'),
    edge('supa-jobs-route', 'job-search-relevance', 'filterJobsBySearchQuery()', ['sequence', 'user-search-jobs-flowchart'], 'dependency'),
    edge('job-search-relevance', 'job-entity', 'JobListing[]', ['sequence', 'user-search-jobs-flowchart'], 'dependency'),
    edge('job-manager', 'map-manager', 'renderJobMarkers()', ['sequence', 'user-search-jobs-flowchart'], 'dependency'),
    edge('chatbot-manager', 'assistant-stream', 'stream', ['overview', 'implementation'], 'dependency'),
    edge('assistant-stream', 'express-app', 'POST + SSE', ['overview'], 'dependency'),
    edge('express-app', 'ai-provider', 'resolve model', ['overview'], 'dependency'),
    edge('auth-manager', 'better-auth', 'session', ['overview', 'implementation', 'architecture'], 'dependency'),
    edge('better-auth', 'supabase-db', 'auth tables', ['overview', 'architecture', 'google-oauth-sequence'], 'dependency'),
    edge('pengguna', 'user-menu-manager', 'select Sign in', ['google-oauth-sequence']),
    edge('user-menu-manager', 'auth-modal-manager', 'openAuthPrompt()', ['google-oauth-sequence']),
    edge('user-menu-manager', 'auth-manager', 'requireAuth()', ['google-oauth-sequence'], 'dependency'),
    edge('auth-modal-manager', 'auth-manager', 'signInWithOAuth()', ['google-oauth-sequence'], 'dependency'),
    edge('auth-manager', 'auth-client', 'Better Auth browser client', ['google-oauth-sequence'], 'dependency'),
    edge('auth-client', 'better-auth', '/api/auth/sign-in/social + get-session', ['google-oauth-sequence'], 'dependency'),
    edge('better-auth', 'google-oauth', 'OAuth redirect + callback', ['google-oauth-sequence'], 'dependency'),
    edge('auth-manager', 'profile-bridge', '/api/me/auth-profile', ['google-oauth-sequence'], 'dependency'),
    edge('profile-bridge', 'better-auth', 'getAppSessionFromHeaders()', ['google-oauth-sequence'], 'dependency'),
    edge('profile-bridge', 'supabase-db', 'find / link / create public.users', ['google-oauth-sequence'], 'dependency'),
    edge('pentadbir', 'admin-ui', 'pilih papan pemuka pentadbir', ['admin-manage-users-sequence']),
    edge('admin-ui', 'admin-manager', 'buka dan papar Users', ['admin-manage-users-sequence'], 'dependency'),
    edge('admin-manager', 'admin-api-client', 'listAdminUsers()', ['admin-manage-users-sequence'], 'dependency'),
    edge('admin-api-client', 'admin-users-api', 'GET /api/admin/users', ['admin-manage-users-sequence'], 'dependency'),
    edge('admin-users-api', 'better-auth', 'requireAuth()', ['admin-manage-users-sequence'], 'dependency'),
    edge('admin-users-api', 'supabase-db', 'requireAdmin() + users query', ['admin-manage-users-sequence'], 'dependency'),
    edge('pentadbir', 'admin-ui', 'pilih bahagian Users', ['admin-manage-users-flowchart']),
    edge('admin-ui', 'admin-manager', 'papar keadaan pemuatan dan hasil', ['admin-manage-users-flowchart'], 'dependency'),
    edge('admin-manager', 'admin-api-client', 'minta maklumat pengguna terkini', ['admin-manage-users-flowchart'], 'dependency'),
    edge('admin-api-client', 'admin-users-api', 'GET /api/admin/users', ['admin-manage-users-flowchart'], 'dependency'),
    edge('admin-users-api', 'supabase-db', 'baca sehingga 100 profil terkini', ['admin-manage-users-flowchart'], 'dependency'),
    edge('pentadbir', 'admin-ui', 'pilih papan pemuka pentadbir', ['admin-access-dashboard-flowchart']),
    edge('admin-ui', 'auth-manager', 'semak sesi dan peranan semasa', ['admin-access-dashboard-flowchart'], 'dependency'),
    edge('admin-ui', 'admin-manager', 'buka dan muat papan pemuka', ['admin-access-dashboard-flowchart'], 'dependency'),
    edge('admin-manager', 'admin-api-client', 'minta data Overview terlindung', ['admin-access-dashboard-flowchart'], 'dependency'),
    edge('admin-api-client', 'admin-dashboard-api', 'permintaan providers, usage dan users', ['admin-access-dashboard-flowchart'], 'dependency'),
    edge('admin-dashboard-api', 'better-auth', 'sahkan sesi Better Auth', ['admin-access-dashboard-flowchart'], 'dependency'),
    edge('admin-dashboard-api', 'user-profile', 'semak peranan admin atau owner', ['admin-access-dashboard-flowchart'], 'dependency'),
    edge('admin-dashboard-api', 'supabase-db', 'baca tiga set data papan pemuka', ['admin-access-dashboard-flowchart'], 'dependency'),
    edge('pentadbir', 'admin-ui', 'pilih bahagian Usage', ['admin-monitor-activity-flowchart']),
    edge('admin-ui', 'admin-manager', 'papar pemuatan dan hasil Usage', ['admin-monitor-activity-flowchart'], 'dependency'),
    edge('admin-manager', 'admin-api-client', 'minta aktiviti AI terkini', ['admin-monitor-activity-flowchart'], 'dependency'),
    edge('admin-api-client', 'admin-usage-api', 'GET /api/admin/ai/usage', ['admin-monitor-activity-flowchart'], 'dependency'),
    edge('admin-usage-api', 'ai-usage-entity', 'baca sehingga 100 peristiwa dan kira jumlah', ['admin-monitor-activity-flowchart'], 'dependency'),
    edge('ai-usage-entity', 'supabase-db', 'public.ai_usage_events', ['admin-monitor-activity-flowchart'], 'association'),
    edge('pentadbir', 'admin-ui', 'pilih bahagian AI Providers', ['admin-manage-ai-configuration-flowchart']),
    edge('admin-ui', 'admin-manager', 'papar status dan tindakan owner', ['admin-manage-ai-configuration-flowchart'], 'dependency'),
    edge('admin-manager', 'admin-api-client', 'senarai, simpan kunci atau segar semula model', ['admin-manage-ai-configuration-flowchart'], 'dependency'),
    edge('admin-api-client', 'admin-ai-providers-api', '/api/admin/ai/providers*', ['admin-manage-ai-configuration-flowchart'], 'dependency'),
    edge('admin-ai-providers-api', 'user-profile', 'semak keupayaan admin atau owner', ['admin-manage-ai-configuration-flowchart'], 'dependency'),
    edge('admin-ai-providers-api', 'ai-provider-registry', 'gabungkan daftar penyedia', ['admin-manage-ai-configuration-flowchart'], 'dependency'),
    edge('admin-ai-providers-api', 'ai-credential-entity', 'baca atau simpan kelayakan platform', ['admin-manage-ai-configuration-flowchart'], 'dependency'),
    edge('admin-ai-providers-api', 'audit-log-entity', 'rekod platform_key_saved', ['admin-manage-ai-configuration-flowchart'], 'dependency'),
    edge('admin-ai-providers-api', 'ai-provider', 'segar semula senarai model', ['admin-manage-ai-configuration-flowchart'], 'dependency'),
    edge('admin-ai-providers-api', 'supabase-db', 'baca dan simpan konfigurasi AI', ['admin-manage-ai-configuration-flowchart'], 'dependency'),
    edge('pentadbir', 'user-menu-manager', 'pilih Sign Out', ['admin-sign-out-flowchart']),
    edge('user-menu-manager', 'auth-manager', 'mulakan log keluar', ['admin-sign-out-flowchart'], 'dependency'),
    edge('auth-manager', 'auth-client', 'hantar permintaan log keluar', ['admin-sign-out-flowchart'], 'dependency'),
    edge('auth-client', 'better-auth', 'POST /api/auth/sign-out', ['admin-sign-out-flowchart'], 'dependency'),
    edge('auth-manager', 'admin-manager', 'maklum perubahan sesi', ['admin-sign-out-flowchart'], 'dependency'),
    edge('admin-manager', 'admin-ui', 'papar keadaan akses signed-out', ['admin-sign-out-flowchart'], 'dependency'),
    edge('pentadbir', 'admin-ui', 'buka papan pemuka pentadbir', ['admin-manage-ai-configuration-sequence']),
    edge('admin-ui', 'admin-manager', 'papar tab Providers dan tindakan owner', ['admin-manage-ai-configuration-sequence'], 'dependency'),
    edge('admin-manager', 'admin-api-client', 'list / save key / refresh models', ['admin-manage-ai-configuration-sequence'], 'dependency'),
    edge('admin-api-client', 'admin-ai-providers-api', '/api/admin/ai/providers*', ['admin-manage-ai-configuration-sequence'], 'dependency'),
    edge('admin-ai-providers-api', 'better-auth', 'requireAuth() + requireAdmin()', ['admin-manage-ai-configuration-sequence'], 'dependency'),
    edge('admin-ai-providers-api', 'user-profile', 'semak role admin atau owner', ['admin-manage-ai-configuration-sequence'], 'dependency'),
    edge('admin-ai-providers-api', 'ai-provider-registry', 'gabung status penyedia', ['admin-manage-ai-configuration-sequence'], 'dependency'),
    edge('admin-ai-providers-api', 'ai-credential-entity', 'baca / upsert kelayakan platform', ['admin-manage-ai-configuration-sequence'], 'dependency'),
    edge('admin-ai-providers-api', 'audit-log-entity', 'platform_key_saved', ['admin-manage-ai-configuration-sequence'], 'dependency'),
    edge('admin-ai-providers-api', 'ai-provider', 'ambil senarai model', ['admin-manage-ai-configuration-sequence'], 'dependency'),
    edge('admin-ai-providers-api', 'supabase-db', 'simpan metadata atau ralat segar semula', ['admin-manage-ai-configuration-sequence'], 'dependency'),
    edge('pentadbir', 'admin-ui', 'pilih papan pemuka pentadbir', ['admin-access-dashboard-sequence']),
    edge('admin-ui', 'auth-manager', 'semak profil semasa', ['admin-access-dashboard-sequence'], 'dependency'),
    edge('admin-ui', 'admin-manager', 'buka papan pemuka', ['admin-access-dashboard-sequence'], 'dependency'),
    edge('admin-manager', 'admin-api-client', 'muat data overview', ['admin-access-dashboard-sequence'], 'dependency'),
    edge('admin-api-client', 'admin-dashboard-api', 'tiga permintaan pentadbir', ['admin-access-dashboard-sequence'], 'dependency'),
    edge('admin-dashboard-api', 'better-auth', 'sahkan sesi', ['admin-access-dashboard-sequence'], 'dependency'),
    edge('admin-dashboard-api', 'user-profile', 'semak role admin/owner', ['admin-access-dashboard-sequence'], 'dependency'),
    edge('admin-dashboard-api', 'supabase-db', 'baca providers, usage dan users', ['admin-access-dashboard-sequence'], 'dependency'),
    edge('pentadbir', 'admin-ui', 'pilih tab Usage', ['admin-monitor-activity-sequence']),
    edge('admin-ui', 'admin-manager', 'minta aktiviti AI', ['admin-monitor-activity-sequence'], 'dependency'),
    edge('admin-manager', 'admin-api-client', 'listAdminUsage()', ['admin-monitor-activity-sequence'], 'dependency'),
    edge('admin-api-client', 'admin-usage-api', 'GET /api/admin/ai/usage', ['admin-monitor-activity-sequence'], 'dependency'),
    edge('admin-usage-api', 'better-auth', 'sahkan sesi', ['admin-monitor-activity-sequence'], 'dependency'),
    edge('admin-usage-api', 'user-profile', 'semak role admin/owner', ['admin-monitor-activity-sequence'], 'dependency'),
    edge('admin-usage-api', 'ai-usage-entity', '100 peristiwa penggunaan AI terkini', ['admin-monitor-activity-sequence'], 'dependency'),
    edge('ai-usage-entity', 'supabase-db', 'public.ai_usage_events', ['admin-monitor-activity-sequence'], 'association'),
    edge('pentadbir', 'user-menu-manager', 'pilih Sign Out', ['admin-sign-out-sequence']),
    edge('user-menu-manager', 'auth-manager', 'signOut()', ['admin-sign-out-sequence'], 'dependency'),
    edge('auth-manager', 'auth-client', 'signOut()', ['admin-sign-out-sequence'], 'dependency'),
    edge('auth-client', 'better-auth', 'POST /api/auth/sign-out', ['admin-sign-out-sequence'], 'dependency'),
    edge('auth-manager', 'admin-manager', 'maklum perubahan sesi', ['admin-sign-out-sequence'], 'dependency'),
    edge('admin-manager', 'admin-ui', 'papar keadaan signed-out', ['admin-sign-out-sequence'], 'dependency'),
    edge('pengguna', 'workspace-ui', 'pilih preset peta Malaysia', ['user-explore-3d-map-sequence', 'user-explore-3d-map-flowchart']),
    edge('workspace-ui', 'mypeta-app', 'onPresetSelected()', ['user-explore-3d-map-sequence', 'user-explore-3d-map-flowchart'], 'dependency'),
    edge('mypeta-app', 'map-manager', 'enterWorkspace()', ['user-explore-3d-map-sequence', 'user-explore-3d-map-flowchart'], 'dependency'),
    edge('map-manager', 'maplibre-gl', 'flyTo + terrain + bangunan 3D', ['user-explore-3d-map-sequence', 'user-explore-3d-map-flowchart'], 'dependency'),
    edge('mypeta-app', 'poi-manager', 'loadForView()', ['user-explore-3d-map-sequence', 'user-explore-3d-map-flowchart'], 'dependency'),
    edge('mypeta-app', 'category-manager', 'loadCounts()', ['user-explore-3d-map-sequence', 'user-explore-3d-map-flowchart'], 'dependency'),
    edge('poi-manager', 'supabase-module', 'get_pois_in_bounds', ['user-explore-3d-map-sequence', 'user-explore-3d-map-flowchart'], 'dependency'),
    edge('category-manager', 'supabase-module', 'get_poi_categories_with_counts', ['user-explore-3d-map-sequence', 'user-explore-3d-map-flowchart'], 'dependency'),
    edge('pengguna', 'user-menu-manager', 'pilih Sign Out', ['user-sign-out-sequence', 'user-sign-out-flowchart']),
    edge('user-menu-manager', 'auth-manager', 'signOut()', ['user-sign-out-sequence', 'user-sign-out-flowchart'], 'dependency'),
    edge('auth-manager', 'auth-client', 'signOut()', ['user-sign-out-sequence', 'user-sign-out-flowchart'], 'dependency'),
    edge('auth-client', 'better-auth', 'POST /api/auth/sign-out', ['user-sign-out-sequence', 'user-sign-out-flowchart'], 'dependency'),
    edge('auth-manager', 'user-dashboard', 'maklum perubahan sesi', ['user-sign-out-sequence', 'user-sign-out-flowchart'], 'dependency'),
    edge('user-dashboard', 'workspace-ui', 'tutup paparan terlindung', ['user-sign-out-sequence', 'user-sign-out-flowchart'], 'dependency'),
    edge('pengguna', 'auth-manager', 'log masuk / keluar', ['usecase']),
    edge('pengguna', 'map-manager', 'teroka peta', ['usecase']),
    edge('pengguna', 'search-manager', 'cari POI', ['usecase']),
    edge('pengguna', 'job-manager', 'cari pekerjaan', ['usecase', 'activity', 'sequence']),
    edge('pengguna', 'chatbot-manager', 'bertanya AI', ['usecase']),
    edge('pentadbir', 'admin-manager', 'urus sistem', ['usecase']),
    edge('poi-manager', 'map-manager', 'MapLibre source', ['implementation']),
    edge('map-manager', 'national-data-cube-manager', 'memiliki', ['implementation'], 'composition'),
    edge('search-manager', 'map-manager', 'flyTo', ['implementation']),
    edge('search-manager', 'poi-manager', 'detail', ['implementation']),
    edge('highlight-manager', 'poi-manager', 'POI dalam kawasan', ['implementation']),
    edge('auth-identity', 'user-profile', 'better_auth_user_id', ['domain', 'erd'], 'logical'),
    edge('state-entity', 'user-profile', 'selected_state', ['domain', 'erd']),
    edge('data-source-entity', 'poi-entity', '1 : 0..*', ['domain', 'erd']),
    edge('poi-group-entity', 'poi-category-entity', '1 : 0..*', ['domain', 'erd']),
    edge('poi-category-entity', 'poi-entity', '1 : 0..*', ['domain', 'erd']),
    edge('state-entity', 'poi-entity', '0..1 : 0..*', ['domain', 'erd']),
    edge('open-data-api', 'state-entity', 'kumpulan mengikut negeri', ['domain'], 'dependency'),
    edge('highlight-entity', 'poi-entity', 'agregat', ['domain'], 'aggregation'),
    edge('user-profile', 'job-state-entity', '1 : 0..*', ['domain', 'erd']),
    edge('job-entity', 'job-state-entity', 'source + job_key', ['domain', 'erd'], 'logical'),
    edge('user-profile', 'ai-credential-entity', '0..1 : 0..*', ['domain']),
    edge('user-profile', 'ai-preference-entity', '1 : 0..1', ['domain']),
    edge('ai-credential-entity', 'ai-preference-entity', 'dipadankan melalui provider_id', ['domain'], 'dependency'),
    edge('user-profile', 'ai-usage-entity', '0..1 : 0..*', ['domain']),
    edge('user-profile', 'audit-log-entity', '0..1 : 0..*', ['domain']),
    edge('job-manager', 'pipeline-service', 'saved jobs', ['jobops', 'modules']),
    edge('pipeline-service', 'pipeline-runs-entity', 'mencipta run', ['jobops', 'data-flow']),
    edge('pipeline-runs-entity', 'pipeline-items-entity', '1 : n', ['jobops', 'erd']),
    edge('user-dashboard', 'gmail-service', 'sync', ['jobops', 'modules']),
    edge('gmail-service', 'gmail-entity', 'simpan', ['jobops', 'data-flow']),
    edge('user-dashboard', 'watchlist-service', 'poll', ['jobops', 'modules']),
    edge('watchlist-service', 'watchlist-entity', 'simpan', ['jobops', 'data-flow']),
    edge('extractor-service', 'extractor-entity', 'run output', ['jobops', 'data-flow']),
    edge('extractor-service', 'job-entity', 'ingest', ['jobops', 'data-flow']),
    edge('main-ts', 'blog-manager', '/blog boot', ['blog']),
    edge('blog-manager', 'blog-routes', 'HTTP', ['blog', 'data-flow']),
    edge('blog-editor', 'blog-routes', 'save/media', ['blog']),
    edge('blog-routes', 'blog-data', 'CRUD', ['blog', 'erd']),
    edge('blog-routes', 'newsletter-data', 'broadcast', ['blog', 'erd']),
    edge('mypeta-app', 'intel-manager', 'memiliki', ['community', 'modules'], 'composition'),
    edge('mypeta-app', 'kopi-manager', 'memiliki', ['community', 'modules'], 'composition'),
    edge('mypeta-app', 'event-manager', 'memiliki', ['community', 'modules'], 'composition'),
    edge('intel-manager', 'community-data', 'papar', ['community', 'data-flow']),
    edge('kopi-manager', 'supabase-db', 'coffee_shops', ['community', 'data-flow']),
    edge('event-manager', 'supabase-db', 'events', ['community', 'data-flow']),
    edge('github-actions', 'extractor-service', 'scheduled ingestion', ['etl-pipeline'], 'dependency'),
    edge('github-actions', 'kopi-manager', 'coffee scrape', ['etl-pipeline'], 'dependency'),
    edge('github-actions', 'event-manager', 'event scrape', ['etl-pipeline'], 'dependency'),
    edge('vercel-daily-cron', 'blog-routes', 'promote, roll up, drain', ['etl-pipeline'], 'dependency'),
    edge('vercel-daily-cron', 'watchlist-service', 'poll watchlists', ['etl-pipeline'], 'dependency'),
    edge('extractor-service', 'supabase-db', 'service-role batch upsert', ['etl-pipeline'], 'dependency'),
    edge('valhalla-tile-builder', 'digitalocean-geo-host', 'validated tile archive', ['etl-pipeline'], 'dependency'),
    edge('digitalocean-geo-host', 'valhalla', 'hosts routing provider', ['etl-pipeline']),
    edge('vercel-runtime', 'express-app', 'same-origin API runtime', ['etl-pipeline'], 'composition'),
    edge('express-app', 'supabase-db', 'server and Data API reads', ['etl-pipeline'], 'dependency'),
    edge('geo-gateway', 'valhalla', 'server-only provider call', ['etl-pipeline'], 'dependency'),
    edge('browser', 'vercel-runtime', 'HTTPS application request', ['etl-pipeline'], 'dependency'),
    edge('exabytes-registrar', 'cloudflare-dns', 'delegates authoritative nameservers', ['deployment-infrastructure'], 'dependency'),
    edge('cloudflare-dns', 'vercel-edge-delivery', 'petakerja.my DNS-only', ['deployment-infrastructure'], 'dependency'),
    edge('cloudflare-dns', 'digitalocean-geo-host', 'geo.petakerja.my DNS-only', ['deployment-infrastructure'], 'dependency'),
    edge('github-repository', 'vercel-build-pipeline', 'main triggers production build', ['deployment-infrastructure'], 'dependency'),
    edge('github-repository', 'github-actions', 'scheduled workflows', ['deployment-infrastructure'], 'dependency'),
    edge('github-actions', 'supabase-db', 'trusted CI batch writes', ['deployment-infrastructure'], 'dependency'),
    edge('vercel-build-pipeline', 'vercel-runtime', 'deploys production bundle', ['deployment-infrastructure'], 'dependency'),
    edge('vercel-runtime', 'vercel-edge-delivery', 'serves static outputs', ['deployment-infrastructure'], 'composition'),
    edge('vercel-runtime', 'vercel-node-function', 'hosts same-origin API', ['deployment-infrastructure'], 'composition'),
    edge('vercel-edge-delivery', 'browser', 'HTTPS application delivery', ['deployment-infrastructure'], 'dependency'),
    edge('vercel-edge-delivery', 'vercel-node-function', '/api/* rewrite', ['deployment-infrastructure'], 'dependency'),
    edge('vercel-node-function', 'express-app', 'api/server.ts to server/app.ts', ['deployment-infrastructure'], 'composition'),
    edge('vercel-daily-cron', 'vercel-node-function', 'GET /api/cron/daily', ['deployment-infrastructure'], 'dependency'),
    edge('express-app', 'supabase-db', 'server SQL and service-role operations', ['deployment-infrastructure'], 'dependency'),
    edge('express-app', 'supabase-storage', 'trusted object administration', ['deployment-infrastructure'], 'dependency'),
    edge('express-app', 'better-auth', 'session and identity persistence', ['deployment-infrastructure'], 'dependency'),
    edge('browser', 'supabase-module', 'publishable key plus RLS', ['deployment-infrastructure'], 'dependency'),
    edge('supabase-module', 'supabase-db', 'Data API and RPC', ['deployment-infrastructure'], 'dependency'),
    edge('geo-gateway', 'digitalocean-geo-host', 'server token over HTTPS', ['deployment-infrastructure'], 'dependency'),
    edge('valhalla-tile-builder', 'digitalocean-geo-host', 'validated archive plus rollback copy', ['deployment-infrastructure'], 'dependency'),
    edge('digitalocean-geo-host', 'valhalla', 'Caddy to private container', ['deployment-infrastructure'], 'composition'),
    edge('geo-gateway', 'nominatim', 'feature gate disabled', ['deployment-infrastructure'], 'dependency'),
    edge('express-app', 'google-cloud-services', 'OAuth and Gmail APIs', ['deployment-infrastructure'], 'dependency'),
    edge('express-app', 'email-platforms', 'server-only delivery', ['deployment-infrastructure'], 'dependency'),
    edge('express-app', 'ai-provider', 'server-side provider calls', ['deployment-infrastructure'], 'dependency'),
    edge('github-actions', 'external-data-platforms', 'scheduled source reads', ['deployment-infrastructure'], 'dependency'),
    edge('pengguna', 'map-tools-manager', 'tetapkan A/B dan pilih analisis', ['v2-geo-usecase', 'v2-geo-map-flowchart', 'v2-geo-route-sequence']),
    edge('map-tools-manager', 'geo-navigation-manager', 'orchestrate navigation', ['v2-geo-implementation', 'v2-geo-architecture', 'v2-geo-modules']),
    edge('geo-navigation-manager', 'geo-service', 'same-origin geo request', ['v2-geo-route-sequence', 'v2-geo-travel-analysis-sequence', 'v2-geo-data-flow']),
    edge('geo-service', 'geo-api', 'HTTP /api/geo', ['v2-geo-route-sequence', 'v2-geo-travel-analysis-sequence', 'v2-geo-data-flow']),
    edge('geo-api', 'geo-gateway', 'validated gateway call', ['v2-geo-route-sequence', 'v2-geo-travel-analysis-sequence', 'v2-geo-architecture']),
    edge('geo-gateway', 'geo-route-cache', 'route cache hit or write', ['v2-geo-route-sequence', 'v2-geo-data-flow', 'v2-geo-erd']),
    edge('geo-gateway', 'geo-geocode-cache', 'geocode cache', ['v2-geo-travel-analysis-sequence', 'v2-geo-data-flow', 'v2-geo-erd']),
    edge('geo-gateway', 'valhalla', 'route, matrix, isochrone', ['v2-geo-route-sequence', 'v2-geo-travel-analysis-sequence', 'v2-geo-routing-stack']),
    edge('geo-gateway', 'nominatim', 'feature-gated geocoding', ['v2-geo-travel-analysis-sequence', 'v2-geo-routing-stack']),
    edge('geo-navigation-manager', 'geo-route-renderer', 'render normalized route', ['v2-geo-route-sequence', 'v2-geo-implementation']),
    edge('geo-route-renderer', 'maplibre-gl', 'ordered GeoJSON layers', ['v2-geo-route-sequence', 'v2-geo-data-flow', 'v2-geo-routing-stack']),
    edge('route-appearance-manager', 'geo-route-renderer', 'visual settings', ['v2-geo-implementation', 'v2-geo-modules']),
    edge('geo-route', 'geo-route-alternative', 'contains alternatives', ['v2-geo-domain']),
    edge('geo-route', 'geo-maneuver', 'contains maneuvers', ['v2-geo-domain']),
    edge('job-location-resolver', 'job-location-resolution', 'cache or persist confidence', ['v2-geo-job-route-sequence', 'v2-geo-erd']),
    edge('job-location-resolution', 'job-entity', 'scraped job relationship', ['v2-geo-job-route-sequence', 'v2-geo-erd']),
    edge('geo-navigation-manager', 'geo-studio', 'optional context handoff', ['v2-geo-usecase', 'v2-geo-map-flowchart', 'v2-geo-architecture']),
  ];

  const diagrams = [
    {
      id: 'overview', title: 'Gambaran keseluruhan', category: 'Sistem', status: 'current', reference: null,
      description: 'Laluan utama daripada browser kepada orchestrator, manager, API, Supabase dan perkhidmatan luar.',
      columns: [
        ['browser'], ['index-html', 'main-ts'], ['mypeta-app', 'app-state'],
        ['map-manager', 'poi-manager', 'job-manager', 'chatbot-manager', 'auth-manager'],
        ['supabase-module', 'jobs-api', 'assistant-stream', 'open-data-api', 'better-auth'],
        ['express-app', 'supabase-db', 'data-gov', 'ai-provider'],
      ],
    },
    {
      id: 'usecase', title: 'Rajah kes guna', category: 'Keperluan', status: 'concept', reference: 'assets/diagrams/use-case.svg',
      description: 'Fungsi teras yang dilihat oleh Pengguna dan Pentadbir, disambungkan kepada kelas pelaksanaan sebenar.',
      columns: [['pengguna'], ['auth-manager', 'map-manager', 'search-manager', 'job-manager', 'chatbot-manager'], ['admin-manager'], ['pentadbir']],
    },
    {
      id: 'activity', title: 'Aktiviti carian pekerjaan', category: 'Tingkah laku', status: 'concept', reference: 'assets/diagrams/activity-job-search.svg',
      description: 'Urutan pilihan pengguna daripada query sehingga kad dan marker pekerjaan dipaparkan.',
      columns: [['pengguna'], ['job-manager'], ['jobs-api'], ['express-app'], ['job-entity', 'job-state-entity']],
    },
    {
      id: 'sequence', title: 'Jujukan carian pekerjaan', category: 'Jujukan', status: 'current', reference: 'assets/diagrams/sequence-job-search.svg',
      description: 'Interaksi terperinci Daily Index daripada UI, client API, Express dan scraped_jobs.',
      sequenceAudience: 'user', sequenceOrder: 2,
      columns: [['pengguna'], ['job-manager'], ['jobs-api'], ['supa-jobs-route'], ['supabase-db'], ['job-search-relevance'], ['job-entity', 'map-manager']],
    },
    {
      id: 'google-oauth-sequence', title: 'Jujukan log masuk Google OAuth', category: 'Jujukan', status: 'current', reference: 'assets/diagrams/sequence-google-oauth.svg',
      description: 'Aliran Google OAuth, sesi Better Auth dan bridge profil public.users berdasarkan kod semasa.',
      sequenceAudience: 'user', sequenceOrder: 1,
      columns: [['pengguna'], ['user-menu-manager', 'auth-modal-manager'], ['auth-manager'], ['auth-client'], ['better-auth'], ['google-oauth'], ['profile-bridge'], ['supabase-db']],
    },
    {
      id: 'user-google-sign-in-flowchart', title: 'Carta alir log masuk dengan Google', category: 'Carta Alir', status: 'current', reference: 'assets/diagrams/flowchart-user-google-sign-in.svg',
      description: 'Keputusan log masuk Google daripada prompt tetamu hingga sesi Better Auth, pemetaan profil dan menu pengguna yang disahkan.',
      flowchartAudience: 'user', flowchartOrder: 1,
      variantFamily: 'user-google-sign-in-flowchart', variantKind: 'polished', variantOrder: 1, canonicalDiagramId: 'user-google-sign-in-flowchart',
      reportExplanation: {
        en: 'This flow chart shows the Google sign-in process for PetaKerja. The process begins when a guest selects Sign in and chooses Google from the authentication prompt. PetaKerja redirects the user to Google for account authorization; if the request is rejected, cancelled or unsuccessful, the user remains in guest mode. After successful authorization, Better Auth creates or updates the identity, account and session before redirecting the user to PetaKerja. The application verifies the active session and obtains the associated application profile. A profile linked through the Better Auth user ID is loaded directly, an email-matching profile is linked, or a new profile is created. When the profile is returned successfully, PetaKerja updates its user state and displays the authenticated user menu.',
        ms: 'Carta alir ini menunjukkan proses log masuk Google bagi PetaKerja. Proses bermula apabila pengguna tetamu memilih Log Masuk dan memilih Google pada paparan pengesahan. PetaKerja mengarahkan pengguna ke Google untuk pengesahan akaun; jika permintaan ditolak, dibatalkan atau gagal, pengguna kekal dalam mod tetamu. Selepas pengesahan berjaya, Better Auth mencipta atau mengemas kini rekod identiti, akaun dan sesi sebelum mengarahkan pengguna kembali ke PetaKerja. Sistem kemudian mengesahkan sesi aktif dan mendapatkan profil aplikasi pengguna. Profil yang telah dipautkan dimuatkan terus, profil dengan e-mel yang sepadan dipautkan, atau profil baharu dicipta. Setelah profil berjaya diperoleh, PetaKerja mengemas kini keadaan pengguna dan memaparkan menu pengguna yang telah log masuk.',
      },
      columns: [['pengguna'], ['user-menu-manager', 'auth-modal-manager'], ['auth-manager'], ['auth-client'], ['better-auth', 'google-oauth'], ['profile-bridge'], ['auth-identity', 'user-profile', 'supabase-db']],
    },
    {
      id: 'user-google-sign-in-flowchart-original', title: 'Carta alir log masuk dengan Google — Asal', category: 'Carta Alir', status: 'current', reference: 'assets/diagrams/flowchart-user-google-sign-in-original.svg',
      description: 'Susun atur asal untuk perbandingan dengan varian dikemas.',
      flowchartAudience: 'user', flowchartOrder: 1,
      variantFamily: 'user-google-sign-in-flowchart', variantKind: 'original', variantOrder: 2, canonicalDiagramId: 'user-google-sign-in-flowchart',
      columns: [['pengguna'], ['user-menu-manager', 'auth-modal-manager'], ['auth-manager'], ['auth-client'], ['better-auth', 'google-oauth'], ['profile-bridge'], ['auth-identity', 'user-profile', 'supabase-db']],
    },
    {
      id: 'user-search-jobs-flowchart', title: 'Carta alir carian pekerjaan', category: 'Carta Alir', status: 'current', reference: 'assets/diagrams/flowchart-user-search-jobs.svg',
      description: 'Aliran Daily Index awam daripada borang carian kepada cache, scraped_jobs, penapisan, kad hasil dan marker peta.',
      flowchartAudience: 'user', flowchartOrder: 2,
      variantFamily: 'user-search-jobs-flowchart', variantKind: 'polished', variantOrder: 1, canonicalDiagramId: 'user-search-jobs-flowchart',
      reportExplanation: {
        en: 'This flow chart shows the public Daily Index job-search process in PetaKerja. The user opens Job Finder, enters a job title, location and filters, and starts the search. PetaKerja first uses a fresh cached response when available; otherwise the server reads matching records from public.scraped_jobs, filters, ranks and paginates them. If retrieval fails, a stale cached response is used when possible. The returned jobs are then adjusted using profile matching and the selected client filters. PetaKerja displays job cards, result and source information, and map markers, or an empty state when no jobs match. A request without usable cache displays the Daily Index error. The loading state is cleared for every outcome.',
        ms: 'Carta alir ini menunjukkan proses carian pekerjaan Daily Index yang boleh digunakan secara awam dalam PetaKerja. Pengguna membuka Job Finder, memasukkan tajuk pekerjaan, lokasi dan penapis, kemudian memulakan carian. PetaKerja menggunakan respons cache yang masih baharu jika tersedia; jika tidak, pelayan membaca rekod yang sepadan daripada public.scraped_jobs sebelum menapis, menyusun dan membahagikan hasil kepada halaman. Jika pengambilan data gagal, respons cache lama digunakan apabila masih tersedia. Hasil pekerjaan kemudian disesuaikan dengan pemadanan profil dan penapis yang dipilih. PetaKerja memaparkan kad pekerjaan, maklumat hasil dan sumber serta marker peta, atau keadaan kosong apabila tiada pekerjaan sepadan. Permintaan tanpa cache yang boleh digunakan memaparkan ralat Daily Index. Keadaan pemuatan ditamatkan bagi setiap hasil.',
      },
      columns: [['pengguna'], ['job-manager'], ['jobs-api'], ['supa-jobs-route', 'job-search-relevance'], ['job-entity', 'supabase-db'], ['map-manager']],
    },
    {
      id: 'user-search-jobs-flowchart-original', title: 'Carta alir carian pekerjaan — Asal', category: 'Carta Alir', status: 'current', reference: 'assets/diagrams/flowchart-user-search-jobs-original.svg',
      description: 'Susun atur neutral asal untuk perbandingan dengan varian dikemas.',
      flowchartAudience: 'user', flowchartOrder: 2,
      variantFamily: 'user-search-jobs-flowchart', variantKind: 'original', variantOrder: 2, canonicalDiagramId: 'user-search-jobs-flowchart',
      columns: [['pengguna'], ['job-manager'], ['jobs-api'], ['supa-jobs-route', 'job-search-relevance'], ['job-entity', 'supabase-db'], ['map-manager']],
    },
    {
      id: 'user-explore-3d-map-flowchart', title: 'Carta alir meneroka peta 3D', category: 'Carta Alir', status: 'current', reference: 'assets/diagrams/flowchart-user-explore-3d-map.svg',
      description: 'Aliran ruang kerja Malaysia daripada peta asas kepada POI, terrain pilihan, bangunan 3D dan paparan MapLibre.',
      flowchartAudience: 'user', flowchartOrder: 3,
      variantFamily: 'user-explore-3d-map-flowchart', variantKind: 'polished', variantOrder: 1, canonicalDiagramId: 'user-explore-3d-map-flowchart',
      reportExplanation: {
        en: 'This flow chart shows how a public user explores PetaKerja\'s Malaysia map. After the workspace opens and the base map is ready, the camera moves to Malaysia and PetaKerja requests visible POIs and category counts. Available data is rendered on the map; if it is unavailable, the base MapLibre workspace remains usable. The user may select 3D Terrain, which adds satellite imagery and terrain elevation on viewports wider than 768 pixels, and may toggle 3D building visibility. PetaKerja then displays the updated interactive map.',
        ms: 'Carta alir ini menunjukkan cara pengguna awam meneroka peta Malaysia dalam PetaKerja. Selepas ruang kerja dibuka dan peta asas sedia digunakan, kamera bergerak ke Malaysia dan PetaKerja meminta POI yang kelihatan serta bilangan kategori. Data yang tersedia dipaparkan pada peta; jika data tidak tersedia, ruang kerja asas MapLibre masih boleh digunakan. Pengguna boleh memilih Terrain 3D untuk menambah imej satelit dan ketinggian terrain pada paparan yang lebih lebar daripada 768 piksel, serta boleh menukar paparan bangunan 3D. PetaKerja kemudian memaparkan peta interaktif yang telah dikemas kini.',
      },
      columns: [['pengguna'], ['workspace-ui'], ['mypeta-app'], ['map-manager', 'maplibre-gl'], ['poi-manager', 'category-manager'], ['supabase-module', 'supabase-db']],
    },
    {
      id: 'user-explore-3d-map-flowchart-original', title: 'Carta alir meneroka peta 3D — Asal', category: 'Carta Alir', status: 'current', reference: 'assets/diagrams/flowchart-user-explore-3d-map-original.svg',
      description: 'Susun atur neutral asal untuk perbandingan dengan varian dikemas.',
      flowchartAudience: 'user', flowchartOrder: 3,
      variantFamily: 'user-explore-3d-map-flowchart', variantKind: 'original', variantOrder: 2, canonicalDiagramId: 'user-explore-3d-map-flowchart',
      columns: [['pengguna'], ['workspace-ui'], ['mypeta-app'], ['map-manager', 'maplibre-gl'], ['poi-manager', 'category-manager'], ['supabase-module', 'supabase-db']],
    },
    {
      id: 'user-sign-out-flowchart', title: 'Carta alir pengguna log keluar', category: 'Carta Alir', status: 'current', reference: 'assets/diagrams/flowchart-user-sign-out.svg',
      description: 'Log keluar Better Auth yang mengosongkan keadaan pengguna, membersihkan Dashboard terbuka dan memulihkan kawalan tetamu.',
      flowchartAudience: 'user', flowchartOrder: 4,
      variantFamily: 'user-sign-out-flowchart', variantKind: 'polished', variantOrder: 1, canonicalDiagramId: 'user-sign-out-flowchart',
      reportExplanation: {
        en: 'This flow chart shows how a signed-in PetaKerja user signs out. The Sign Out control is temporarily disabled while Better Auth processes the request. When sign-out succeeds, the session cookie and local user state are cleared and authentication subscribers are notified. If the User Dashboard is open, it closes and clears user-specific cached information before PetaKerja displays the guest Sign in control. If sign-out fails, the current session remains active, the control is re-enabled and an error is displayed.',
        ms: 'Carta alir ini menunjukkan cara pengguna PetaKerja yang telah log masuk keluar daripada sistem. Kawalan Sign Out dinyahaktifkan sementara Better Auth memproses permintaan. Apabila log keluar berjaya, kuki sesi dan keadaan pengguna setempat dikosongkan serta pelanggan pengesahan dimaklumkan. Jika User Dashboard sedang terbuka, paparan itu ditutup dan maklumat cache khusus pengguna dikosongkan sebelum PetaKerja memaparkan kawalan Log Masuk untuk tetamu. Jika log keluar gagal, sesi semasa kekal aktif, kawalan diaktifkan semula dan ralat dipaparkan.',
      },
      columns: [['pengguna'], ['user-menu-manager'], ['auth-manager'], ['auth-client', 'better-auth'], ['user-dashboard', 'workspace-ui']],
    },
    {
      id: 'user-sign-out-flowchart-original', title: 'Carta alir pengguna log keluar — Asal', category: 'Carta Alir', status: 'current', reference: 'assets/diagrams/flowchart-user-sign-out-original.svg',
      description: 'Susun atur neutral asal untuk perbandingan dengan varian dikemas.',
      flowchartAudience: 'user', flowchartOrder: 4,
      variantFamily: 'user-sign-out-flowchart', variantKind: 'original', variantOrder: 2, canonicalDiagramId: 'user-sign-out-flowchart',
      columns: [['pengguna'], ['user-menu-manager'], ['auth-manager'], ['auth-client', 'better-auth'], ['user-dashboard', 'workspace-ui']],
    },
    {
      id: 'admin-access-dashboard-flowchart', title: 'Carta alir pentadbir mengakses papan pemuka', category: 'Carta Alir', status: 'current', reference: 'assets/diagrams/flowchart-admin-access-dashboard.svg',
      description: 'Semakan sesi dan peranan sebelum data penyedia, penggunaan AI dan pengguna dimuatkan untuk Overview.',
      flowchartAudience: 'administrator', flowchartOrder: 1,
      variantFamily: 'admin-access-dashboard-flowchart', variantKind: 'polished', variantOrder: 1, canonicalDiagramId: 'admin-access-dashboard-flowchart',
      reportExplanation: {
        en: 'This flow chart shows how an authorized PetaKerja administrator accesses the Admin Dashboard. The flow begins when the administrator selects the dashboard and the application checks the current signed-in user. A missing session returns the user to PetaKerja and requests administrator sign-in, while a user without the admin or owner role is denied access. For an authorized administrator, PetaKerja opens the dashboard, displays its loading state and requests provider configuration, recent AI usage and recent user information through protected administrator APIs. These server requests repeat the Better Auth session and role checks. If all required requests succeed, the returned information is stored, loading is cleared and the administrator Overview is displayed. If a protected request fails, the dashboard clears loading and displays its loading error. Blog statistics are loaded separately only when the Blog section is selected.',
        ms: 'Carta alir ini menunjukkan cara pentadbir PetaKerja yang sah mengakses Papan Pemuka Pentadbir. Aliran bermula apabila pentadbir memilih papan pemuka dan aplikasi menyemak pengguna yang sedang log masuk. Jika sesi tidak ditemui, pengguna dikembalikan ke PetaKerja dan diminta log masuk sebagai pentadbir, manakala pengguna tanpa peranan admin atau owner dinafikan akses. Bagi pentadbir yang sah, PetaKerja membuka papan pemuka, memaparkan keadaan pemuatan dan meminta konfigurasi penyedia, penggunaan AI terkini serta maklumat pengguna terkini melalui API pentadbir yang dilindungi. Permintaan pelayan ini mengulangi semakan sesi Better Auth dan peranan. Jika semua permintaan yang diperlukan berjaya, maklumat yang diterima disimpan, pemuatan ditamatkan dan paparan Overview pentadbir dipaparkan. Jika permintaan terlindung gagal, papan pemuka menamatkan pemuatan dan memaparkan ralat pemuatan. Statistik blog dimuatkan secara berasingan hanya apabila bahagian Blog dipilih.',
      },
      columns: [['pentadbir'], ['admin-ui', 'auth-manager'], ['admin-manager'], ['admin-api-client'], ['admin-dashboard-api'], ['better-auth', 'user-profile'], ['supabase-db']],
    },
    {
      id: 'admin-access-dashboard-flowchart-original', title: 'Carta alir pentadbir mengakses papan pemuka — Asal', category: 'Carta Alir', status: 'current', reference: 'assets/diagrams/flowchart-admin-access-dashboard-original.svg',
      description: 'Susun atur asal untuk perbandingan dengan varian dikemas.',
      flowchartAudience: 'administrator', flowchartOrder: 1,
      variantFamily: 'admin-access-dashboard-flowchart', variantKind: 'original', variantOrder: 2, canonicalDiagramId: 'admin-access-dashboard-flowchart',
      columns: [['pentadbir'], ['admin-ui', 'auth-manager'], ['admin-manager'], ['admin-api-client'], ['admin-dashboard-api'], ['better-auth', 'user-profile'], ['supabase-db']],
    },
    {
      id: 'admin-monitor-activity-flowchart', title: 'Carta alir pentadbir memantau aktiviti sistem', category: 'Carta Alir', status: 'current', reference: 'assets/diagrams/flowchart-admin-monitor-activity.svg',
      description: 'Paparan Usage membaca 100 peristiwa penggunaan pembantu AI terkini dan jumlahnya, bukan log pelayan umum.',
      flowchartAudience: 'administrator', flowchartOrder: 2,
      variantFamily: 'admin-monitor-activity-flowchart', variantKind: 'polished', variantOrder: 1, canonicalDiagramId: 'admin-monitor-activity-flowchart',
      reportExplanation: {
        en: 'This flow chart shows how an authorized PetaKerja administrator monitors the activity currently exposed by the Usage section. After the Admin Dashboard is open, the administrator selects Usage and PetaKerja displays a loading state before requesting recent AI activity information. The protected API retrieves up to 100 recent records from public.ai_usage_events and calculates request, error, token and estimated-cost totals. If the request fails, loading is cleared and the dashboard displays an error. If it succeeds, the activity rows and totals are stored and loading is cleared. PetaKerja then displays either the usage totals and activity table or an empty-state message when no events are returned. This use case represents AI-assistant usage activity only; it does not display general server logs or public.ai_admin_audit_logs.',
        ms: 'Carta alir ini menunjukkan cara pentadbir PetaKerja yang sah memantau aktiviti yang kini tersedia melalui bahagian Usage. Selepas Papan Pemuka Pentadbir dibuka, pentadbir memilih Usage dan PetaKerja memaparkan keadaan pemuatan sebelum meminta maklumat aktiviti AI terkini. API terlindung mendapatkan sehingga 100 rekod terkini daripada public.ai_usage_events serta mengira jumlah permintaan, ralat, token dan anggaran kos. Jika permintaan gagal, pemuatan ditamatkan dan papan pemuka memaparkan ralat. Jika berjaya, baris aktiviti dan jumlah disimpan serta pemuatan ditamatkan. PetaKerja kemudian memaparkan sama ada jumlah penggunaan dan jadual aktiviti atau mesej keadaan kosong jika tiada peristiwa dipulangkan. Kes guna ini hanya mewakili aktiviti penggunaan pembantu AI; ia tidak memaparkan log pelayan umum atau public.ai_admin_audit_logs.',
      },
      columns: [['pentadbir'], ['admin-ui'], ['admin-manager'], ['admin-api-client'], ['admin-usage-api'], ['ai-usage-entity', 'supabase-db']],
    },
    {
      id: 'admin-monitor-activity-flowchart-original', title: 'Carta alir pentadbir memantau aktiviti sistem — Asal', category: 'Carta Alir', status: 'current', reference: 'assets/diagrams/flowchart-admin-monitor-activity-original.svg',
      description: 'Susun atur asal untuk perbandingan dengan varian dikemas.',
      flowchartAudience: 'administrator', flowchartOrder: 2,
      variantFamily: 'admin-monitor-activity-flowchart', variantKind: 'original', variantOrder: 2, canonicalDiagramId: 'admin-monitor-activity-flowchart',
      columns: [['pentadbir'], ['admin-ui'], ['admin-manager'], ['admin-api-client'], ['admin-usage-api'], ['ai-usage-entity', 'supabase-db']],
    },
    {
      id: 'admin-manage-users-flowchart', title: 'Carta alir pentadbir mengurus pengguna', category: 'Carta Alir', status: 'current', reference: 'assets/diagrams/flowchart-admin-manage-users.svg',
      description: 'Aliran baca sahaja yang meminta sehingga 100 profil pengguna terkini dan memaparkan jadual, keadaan kosong atau ralat pemuatan.',
      flowchartAudience: 'administrator', flowchartOrder: 3,
      variantFamily: 'admin-manage-users-flowchart', variantKind: 'polished', variantOrder: 1, canonicalDiagramId: 'admin-manage-users-flowchart',
      reportExplanation: {
        en: 'This flow chart shows how an authorized PetaKerja administrator views recent users from the Users section. The flow begins after the administrator has signed in, passed the administrator-role check and opened the dashboard. When Users is selected, PetaKerja loads the user-list branch of the dashboard and requests up to 100 recent profiles, ordered by account-creation date. If the request succeeds, the returned records are stored and the loading state is cleared; PetaKerja then displays either the user table with names, emails, roles, creation dates and last-login dates, or an empty-state message when no users are returned. If the request fails, the loading state is cleared and the dashboard displays an error. The current implementation is read-only and does not change roles, suspend users or delete accounts.',
        ms: 'Carta alir ini menunjukkan cara pentadbir PetaKerja yang sah melihat pengguna terkini melalui bahagian Pengguna. Aliran bermula selepas pentadbir log masuk, melepasi semakan peranan pentadbir dan membuka papan pemuka. Apabila bahagian Pengguna dipilih, PetaKerja memuatkan aliran senarai pengguna pada papan pemuka dan meminta sehingga 100 profil terkini mengikut tarikh akaun dicipta. Jika permintaan berjaya, rekod yang diterima disimpan dan keadaan pemuatan ditamatkan; PetaKerja kemudian memaparkan sama ada jadual pengguna yang mengandungi nama, e-mel, peranan, tarikh akaun dicipta dan tarikh log masuk terakhir, atau mesej keadaan kosong jika tiada pengguna dipulangkan. Jika permintaan gagal, keadaan pemuatan ditamatkan dan papan pemuka memaparkan ralat. Pelaksanaan semasa hanya untuk paparan dan tidak menyokong perubahan peranan, penggantungan pengguna atau pemadaman akaun.',
      },
      columns: [['pentadbir'], ['admin-ui'], ['admin-manager'], ['admin-api-client'], ['admin-users-api'], ['supabase-db', 'user-profile']],
    },
    {
      id: 'admin-manage-users-flowchart-original', title: 'Carta alir pentadbir mengurus pengguna — Asal', category: 'Carta Alir', status: 'current', reference: 'assets/diagrams/flowchart-admin-manage-users-original.svg',
      description: 'Susun atur asal untuk perbandingan dengan varian dikemas.',
      flowchartAudience: 'administrator', flowchartOrder: 3,
      variantFamily: 'admin-manage-users-flowchart', variantKind: 'original', variantOrder: 2, canonicalDiagramId: 'admin-manage-users-flowchart',
      columns: [['pentadbir'], ['admin-ui'], ['admin-manager'], ['admin-api-client'], ['admin-users-api'], ['supabase-db', 'user-profile']],
    },
    {
      id: 'admin-manage-ai-configuration-flowchart', title: 'Carta alir pentadbir mengurus konfigurasi chatbot AI', category: 'Carta Alir', status: 'current', reference: 'assets/diagrams/flowchart-admin-manage-ai-configuration.svg',
      description: 'Paparan status penyedia untuk admin dan owner, dengan simpanan kunci platform serta segar semula model terhad kepada owner.',
      flowchartAudience: 'administrator', flowchartOrder: 4,
      variantFamily: 'admin-manage-ai-configuration-flowchart', variantKind: 'polished', variantOrder: 1, canonicalDiagramId: 'admin-manage-ai-configuration-flowchart',
      reportExplanation: {
        en: 'This flow chart shows how PetaKerja administrators view and manage AI provider configuration. After the AI Providers section is selected, PetaKerja reads platform credentials, combines them with the provider registry and displays provider names, key status, model counts and fetch status. A request failure displays the provider loading error. Administrators may view this information in read-only mode, while owners may save a shared platform key or refresh provider model lists. A submitted key is validated, encrypted and saved before an audit event and success result are recorded; validation and request failures follow separate error paths. During model refresh, supported providers are processed even when an individual provider fails, after which PetaKerja reports complete or partial success and reloads the provider table. Individual users model preferences are outside this use case. The current refresh handler also expects model-refresh fields that are absent from the live ai_provider_credentials snapshot, so that schema mismatch must be resolved before the refresh path is deployable.',
        ms: 'Carta alir ini menunjukkan cara pentadbir PetaKerja melihat dan mengurus konfigurasi penyedia AI. Selepas bahagian AI Providers dipilih, PetaKerja membaca kelayakan platform, menggabungkannya dengan daftar penyedia dan memaparkan nama penyedia, status kunci, bilangan model serta status pengambilan. Kegagalan permintaan memaparkan ralat pemuatan penyedia. Pentadbir boleh melihat maklumat ini dalam mod baca sahaja, manakala owner boleh menyimpan kunci platform bersama atau menyegarkan semula senarai model penyedia. Kunci yang dihantar disahkan, dienkripsi dan disimpan sebelum rekod audit serta hasil kejayaan direkodkan; kegagalan pengesahan dan permintaan melalui laluan ralat yang berasingan. Semasa segar semula model, penyedia yang disokong terus diproses walaupun satu penyedia gagal, kemudian PetaKerja melaporkan kejayaan penuh atau separa dan memuatkan semula jadual penyedia. Pilihan model pengguna individu berada di luar kes guna ini. Pengendali segar semula semasa turut menjangkakan medan metadata model yang tiada dalam snapshot langsung ai_provider_credentials, maka ketidakpadanan skema itu perlu diselesaikan sebelum laluan segar semula boleh digunakan dalam produksi.',
      },
      columns: [['pentadbir'], ['admin-ui'], ['admin-manager'], ['admin-api-client'], ['admin-ai-providers-api'], ['user-profile', 'ai-provider-registry'], ['ai-credential-entity', 'audit-log-entity', 'ai-provider', 'supabase-db']],
    },
    {
      id: 'admin-manage-ai-configuration-flowchart-original', title: 'Carta alir pentadbir mengurus konfigurasi chatbot AI — Asal', category: 'Carta Alir', status: 'current', reference: 'assets/diagrams/flowchart-admin-manage-ai-configuration-original.svg',
      description: 'Susun atur asal untuk perbandingan dengan varian dikemas.',
      flowchartAudience: 'administrator', flowchartOrder: 4,
      variantFamily: 'admin-manage-ai-configuration-flowchart', variantKind: 'original', variantOrder: 2, canonicalDiagramId: 'admin-manage-ai-configuration-flowchart',
      columns: [['pentadbir'], ['admin-ui'], ['admin-manager'], ['admin-api-client'], ['admin-ai-providers-api'], ['user-profile', 'ai-provider-registry'], ['ai-credential-entity', 'audit-log-entity', 'ai-provider', 'supabase-db']],
    },
    {
      id: 'admin-sign-out-flowchart', title: 'Carta alir pentadbir log keluar', category: 'Carta Alir', status: 'current', reference: 'assets/diagrams/flowchart-admin-sign-out.svg',
      description: 'Log keluar Better Auth yang menyelaraskan keadaan pengguna dan akses papan pemuka, termasuk kegagalan yang mengekalkan sesi.',
      flowchartAudience: 'administrator', flowchartOrder: 5,
      variantFamily: 'admin-sign-out-flowchart', variantKind: 'polished', variantOrder: 1, canonicalDiagramId: 'admin-sign-out-flowchart',
      reportExplanation: {
        en: 'This flow chart shows how a signed-in PetaKerja administrator signs out. The flow begins when the administrator selects Sign Out, after which the available control is disabled and the request is sent to Better Auth. If sign-out fails, the current session is preserved and the Sign Out control is re-enabled; the current implementation records the failure in the console rather than displaying a dedicated user-facing error. If sign-out succeeds, Better Auth invalidates the session and clears its cookie. PetaKerja then clears the current user state, notifies authentication subscribers and updates any open administrator dashboard to its signed-out access state while the user menu returns to guest mode.',
        ms: 'Carta alir ini menunjukkan cara pentadbir PetaKerja yang telah log masuk keluar daripada sistem. Aliran bermula apabila pentadbir memilih Sign Out, kemudian kawalan yang tersedia dinyahaktifkan dan permintaan dihantar kepada Better Auth. Jika log keluar gagal, sesi semasa dikekalkan dan kawalan Sign Out diaktifkan semula; pelaksanaan semasa merekodkan kegagalan pada konsol dan tidak memaparkan ralat khusus kepada pengguna. Jika log keluar berjaya, Better Auth membatalkan sesi dan mengosongkan kukinya. PetaKerja kemudian mengosongkan keadaan pengguna semasa, memaklumkan pelanggan pengesahan dan mengemas kini mana-mana papan pemuka pentadbir yang terbuka kepada keadaan akses signed-out, manakala menu pengguna kembali ke mod tetamu.',
      },
      columns: [['pentadbir'], ['user-menu-manager'], ['auth-manager'], ['auth-client'], ['better-auth'], ['admin-manager', 'admin-ui']],
    },
    {
      id: 'admin-sign-out-flowchart-original', title: 'Carta alir pentadbir log keluar — Asal', category: 'Carta Alir', status: 'current', reference: 'assets/diagrams/flowchart-admin-sign-out-original.svg',
      description: 'Susun atur asal untuk perbandingan dengan varian dikemas.',
      flowchartAudience: 'administrator', flowchartOrder: 5,
      variantFamily: 'admin-sign-out-flowchart', variantKind: 'original', variantOrder: 2, canonicalDiagramId: 'admin-sign-out-flowchart',
      columns: [['pentadbir'], ['user-menu-manager'], ['auth-manager'], ['auth-client'], ['better-auth'], ['admin-manager', 'admin-ui']],
    },
    {
      id: 'user-explore-3d-map-sequence', title: 'Jujukan pengguna meneroka peta 3D', category: 'Jujukan', status: 'current', reference: 'assets/diagrams/sequence-user-explore-3d-map.svg',
      description: 'Aliran awam daripada preset Malaysia kepada workspace MapLibre, POI, kategori, terrain dan bangunan 3D.',
      sequenceAudience: 'user', sequenceOrder: 3,
      columns: [['pengguna'], ['workspace-ui'], ['mypeta-app'], ['map-manager'], ['maplibre-gl'], ['poi-manager', 'category-manager'], ['supabase-module'], ['supabase-db']],
    },
    {
      id: 'user-sign-out-sequence', title: 'Jujukan pengguna log keluar', category: 'Jujukan', status: 'current', reference: 'assets/diagrams/sequence-user-sign-out.svg',
      description: 'Aliran log keluar pengguna melalui Better Auth, termasuk pembersihan keadaan dan kegagalan yang mengekalkan sesi semasa.',
      sequenceAudience: 'user', sequenceOrder: 4,
      columns: [['pengguna'], ['user-menu-manager'], ['auth-manager'], ['auth-client'], ['better-auth'], ['user-dashboard'], ['workspace-ui']],
    },
    {
      id: 'admin-access-dashboard-sequence', title: 'Jujukan pentadbir mengakses papan pemuka', category: 'Jujukan', status: 'current', reference: 'assets/diagrams/sequence-admin-access-dashboard.svg',
      description: 'Pengesahan sesi dan role sebelum data Overview penyedia, penggunaan AI dan pengguna dimuat secara selari.',
      sequenceAudience: 'administrator', sequenceOrder: 1,
      columns: [['pentadbir'], ['admin-ui'], ['auth-manager'], ['admin-manager'], ['admin-api-client'], ['admin-dashboard-api'], ['better-auth'], ['supabase-db', 'user-profile']],
    },
    {
      id: 'admin-monitor-activity-sequence', title: 'Jujukan pentadbir memantau aktiviti sistem', category: 'Jujukan', status: 'current', reference: 'assets/diagrams/sequence-admin-monitor-activity.svg',
      description: 'Paparan Usage membaca sehingga 100 rekod penggunaan pembantu AI terkini; ia bukan log pelayan umum atau log audit pentadbir.',
      sequenceAudience: 'administrator', sequenceOrder: 2,
      columns: [['pentadbir'], ['admin-ui'], ['admin-manager'], ['admin-api-client'], ['admin-usage-api'], ['better-auth'], ['ai-usage-entity', 'supabase-db']],
    },
    {
      id: 'admin-manage-users-sequence', title: 'Jujukan pentadbir mengurus pengguna', category: 'Jujukan', status: 'current', reference: 'assets/diagrams/sequence-admin-manage-users.svg',
      description: 'Aliran baca sahaja untuk mengesahkan pentadbir dan memaparkan 100 profil pengguna terkini bersama peranan.',
      sequenceAudience: 'administrator', sequenceOrder: 3,
      columns: [['pentadbir'], ['admin-ui'], ['admin-manager'], ['admin-api-client'], ['admin-users-api'], ['better-auth'], ['supabase-db', 'user-profile']],
    },
    {
      id: 'admin-manage-ai-configuration-sequence', title: 'Jujukan pentadbir mengurus konfigurasi chatbot AI', category: 'Jujukan', status: 'current', reference: 'assets/diagrams/sequence-admin-manage-ai-configuration.svg',
      description: 'Aliran lihat konfigurasi penyedia untuk admin/owner serta simpanan kekunci platform dan segar semula model yang dihadkan kepada owner. Nota amaran merekodkan ketidakselarasan skema refresh semasa.',
      sequenceAudience: 'administrator', sequenceOrder: 4,
      columns: [['pentadbir'], ['admin-ui'], ['admin-manager'], ['admin-api-client'], ['admin-ai-providers-api'], ['better-auth'], ['user-profile', 'ai-provider-registry', 'ai-credential-entity', 'audit-log-entity', 'supabase-db'], ['ai-provider']],
    },
    {
      id: 'admin-sign-out-sequence', title: 'Jujukan pentadbir log keluar', category: 'Jujukan', status: 'current', reference: 'assets/diagrams/sequence-admin-sign-out.svg',
      description: 'Aliran log keluar pentadbir melalui Better Auth dan pemulihan paparan papan pemuka kepada keadaan signed-out.',
      sequenceAudience: 'administrator', sequenceOrder: 5,
      columns: [['pentadbir'], ['user-menu-manager'], ['auth-manager'], ['auth-client'], ['better-auth'], ['admin-manager'], ['admin-ui']],
    },
    {
      id: 'domain', title: 'Kelas domain teras', category: 'Kelas', status: 'current', reference: 'assets/diagrams/class-domain.svg',
      description: 'Entiti Supabase, kontrak TypeScript dan servis domain tanpa mendakwa adanya ORM.',
      variantFamily: 'domain', variantKind: 'polished', variantOrder: 1, canonicalDiagramId: 'domain',
      columns: [
        ['auth-identity', 'user-profile', 'state-entity'],
        ['data-source-entity', 'poi-group-entity', 'poi-category-entity', 'poi-entity', 'highlight-entity', 'open-data-api'],
        ['job-entity', 'job-state-entity'],
        ['ai-credential-entity', 'ai-preference-entity', 'ai-usage-entity', 'audit-log-entity'],
      ],
    },
    {
      id: 'domain-original', title: 'Kelas domain teras — Asal', category: 'Kelas', status: 'current', reference: 'assets/diagrams/class-domain-original.svg',
      description: 'Susun atur asal untuk perbandingan dengan varian dikemas.',
      variantFamily: 'domain', variantKind: 'original', variantOrder: 2, canonicalDiagramId: 'domain',
      columns: [
        ['auth-identity', 'user-profile', 'state-entity'],
        ['data-source-entity', 'poi-group-entity', 'poi-category-entity', 'poi-entity', 'highlight-entity', 'open-data-api'],
        ['job-entity', 'job-state-entity'],
        ['ai-credential-entity', 'ai-preference-entity', 'ai-usage-entity', 'audit-log-entity'],
      ],
    },
    {
      id: 'implementation', title: 'Kebergantungan kelas pelaksanaan', category: 'Kelas', status: 'current', reference: 'assets/diagrams/class-implementation.svg',
      description: 'Composition MyPetaApp, constructor association dan dependency modul sebenar.',
      columns: [
        ['app-state', 'mypeta-app'],
        ['auth-manager', 'map-manager', 'poi-manager', 'search-manager', 'category-manager', 'insights-manager', 'national-data-cube-manager', 'highlight-manager', 'job-manager', 'chatbot-manager', 'admin-manager'],
        ['supabase-module', 'jobs-api', 'assistant-stream', 'open-data-api', 'shared-types'],
        ['supabase-db', 'express-app', 'better-auth'],
      ],
    },
    {
      id: 'architecture', title: 'Seni bina berlapis', category: 'Reka bentuk', status: 'current', reference: 'assets/diagrams/architecture-layered.svg',
      description: 'Frontend browser, lapisan manager, servis, backend Express serta data dan perkhidmatan luar.',
      variantFamily: 'architecture', variantKind: 'polished', variantOrder: 1, canonicalDiagramId: 'architecture',
      columns: [['browser', 'index-html', 'main-ts', 'ui-templates'], ['mypeta-app', 'map-manager', 'poi-manager', 'job-manager', 'insights-manager', 'chatbot-manager'], ['supabase-module', 'jobs-api', 'open-data-api'], ['express-app', 'better-auth'], ['supabase-db', 'data-gov']],
    },
    {
      id: 'architecture-original', title: 'Seni bina berlapis — Asal', category: 'Reka bentuk', status: 'current', reference: 'assets/diagrams/architecture-layered-original.svg',
      description: 'Rekreasi Draw.io neutral bagi kandungan D2 asal.',
      variantFamily: 'architecture', variantKind: 'original', variantOrder: 2, canonicalDiagramId: 'architecture',
      columns: [['browser', 'index-html', 'main-ts', 'ui-templates'], ['mypeta-app', 'map-manager', 'poi-manager', 'job-manager', 'insights-manager', 'chatbot-manager'], ['supabase-module', 'jobs-api', 'open-data-api'], ['express-app', 'better-auth'], ['supabase-db', 'data-gov']],
    },
    {
      id: 'modules', title: 'Hierarki modul', category: 'Reka bentuk', status: 'current', reference: 'assets/diagrams/module-hierarchy.svg',
      description: 'Tanggungjawab modul teras, carian pekerjaan, analitik dan akaun serta hubungan antara modul.',
      variantFamily: 'modules', variantKind: 'polished', variantOrder: 1, canonicalDiagramId: 'modules',
      columns: [
        ['mypeta-app'],
        ['map-manager', 'poi-manager', 'job-manager', 'insights-manager', 'chatbot-manager', 'auth-manager'],
        ['pipeline-service', 'user-dashboard', 'gmail-service', 'watchlist-service', 'extractor-service'],
        ['blog-manager', 'blog-editor', 'intel-manager', 'kopi-manager', 'event-manager'],
      ],
    },
    {
      id: 'modules-original', title: 'Hierarki modul — Asal', category: 'Reka bentuk', status: 'current', reference: 'assets/diagrams/module-hierarchy-original.svg',
      description: 'Rekreasi Draw.io neutral bagi kandungan D2 asal.',
      variantFamily: 'modules', variantKind: 'original', variantOrder: 2, canonicalDiagramId: 'modules',
      columns: [
        ['mypeta-app'],
        ['map-manager', 'poi-manager', 'job-manager', 'insights-manager', 'chatbot-manager', 'auth-manager'],
        ['pipeline-service', 'user-dashboard', 'gmail-service', 'watchlist-service', 'extractor-service'],
        ['blog-manager', 'blog-editor', 'intel-manager', 'kopi-manager', 'event-manager'],
      ],
    },
    {
      id: 'map-routing-responsibility-stack', title: 'Tanggungjawab penghalaan A-ke-B', category: 'Peta & Penghalaan', status: 'current', reference: 'assets/diagrams/petakerja-map-routing-responsibility-stack.svg',
      description: 'Pembahagian tanggungjawab semasa antara input pelayar, MapLibre, orkestrasi pelayar, GeoGateway, penyedia geo dan cache.',
      columns: [
        ['browser', 'search-manager', 'maplibre-gl'],
        ['express-app'],
        ['supabase-db'],
      ],
    },
    {
      id: 'erd', title: 'ERD teras', category: 'Data', status: 'current', reference: 'assets/diagrams/erd-core.svg',
      description: 'Hubungan identiti, profil, POI, pekerjaan dan modul pengguna. public.job_listings ditanda tidak tersedia.',
      columns: [
        ['auth-identity', 'user-profile', 'state-entity'],
        ['data-source-entity', 'poi-group-entity', 'poi-category-entity', 'poi-entity'],
        ['job-entity', 'job-listings-legacy', 'job-state-entity'],
        ['pipeline-runs-entity', 'pipeline-items-entity', 'gmail-entity', 'watchlist-entity', 'extractor-entity'],
        ['blog-data', 'newsletter-data', 'community-data'],
      ],
    },
    {
      id: 'data-flow', title: 'Aliran data', category: 'Data', status: 'current', reference: 'assets/diagrams/data-flow.svg',
      description: 'Sumber, ingestion/query, storage dan paparan untuk POI, jobs, AI serta modul lanjutan.',
      columns: [
        ['data-gov', 'extractor-service', 'better-auth'],
        ['open-data-api', 'jobs-api', 'supabase-module', 'pipeline-service', 'blog-routes', 'gmail-service', 'watchlist-service'],
        ['express-app', 'supabase-db'],
        ['poi-manager', 'job-manager', 'insights-manager', 'chatbot-manager', 'blog-manager', 'user-dashboard'],
        ['map-manager', 'pengguna'],
      ],
    },
    {
      id: 'etl-pipeline', title: 'Pipeline ETL operasi & penyampaian PetaKerja', category: 'ETL Pipeline', status: 'current', reference: 'assets/diagrams/etl-pipeline.svg',
      description: 'Ingest kelompok, penormalan, storan operasi dan penyampaian aplikasi semasa merentasi GitHub Actions, Vercel, Supabase dan DigitalOcean.',
      columns: [
        ['github-actions', 'vercel-daily-cron', 'valhalla-tile-builder'],
        ['extractor-service', 'kopi-manager', 'event-manager', 'watchlist-service'],
        ['supabase-db', 'digitalocean-geo-host', 'valhalla', 'nominatim'],
        ['vercel-runtime', 'express-app', 'geo-gateway'],
        ['browser', 'job-manager', 'map-manager'],
      ],
    },
    {
      id: 'deployment-infrastructure', title: 'Deployment & Infrastruktur PetaKerja — Produksi', category: 'Deployment & Infra', status: 'current', reference: 'assets/diagrams/deployment-infrastructure.svg',
      description: 'Laluan produksi daripada domain dan automasi kepada binaan Vercel, runtime same-origin, Supabase, origin geo DigitalOcean serta pengguna.',
      columns: [
        ['exabytes-registrar', 'cloudflare-dns'],
        ['github-repository', 'github-actions', 'vercel-daily-cron'],
        ['vercel-build-pipeline'],
        ['vercel-runtime', 'vercel-edge-delivery', 'vercel-node-function', 'express-app', 'geo-gateway'],
        ['supabase-db', 'supabase-storage', 'better-auth', 'supabase-module'],
        ['valhalla-tile-builder', 'digitalocean-geo-host', 'valhalla', 'nominatim'],
        ['browser', 'pengguna', 'google-cloud-services', 'email-platforms', 'ai-provider', 'external-data-platforms'],
      ],
    },
    {
      id: 'jobops', title: 'JobOps, Gmail & Watchlist', category: 'Modul lanjutan', status: 'current', reference: null,
      description: 'Pipeline saved jobs, integrasi Gmail, watchlist syarikat, extractor dan notifikasi.',
      columns: [['pengguna', 'user-dashboard'], ['job-manager', 'pipeline-service', 'gmail-service', 'watchlist-service'], ['extractor-service'], ['pipeline-runs-entity', 'pipeline-items-entity', 'gmail-entity', 'watchlist-entity', 'extractor-entity'], ['supabase-db']],
    },
    {
      id: 'blog', title: 'Blog & newsletter', category: 'Modul lanjutan', status: 'current', reference: null,
      description: 'Boot blog berasingan, editor, route, entiti kandungan, analytics dan delivery newsletter.',
      columns: [['browser', 'main-ts'], ['blog-manager', 'blog-editor'], ['blog-routes'], ['blog-data', 'newsletter-data'], ['supabase-db']],
    },
    {
      id: 'community', title: 'Community & intel', category: 'Modul lanjutan', status: 'current', reference: null,
      description: 'Intel, kopi, event dan data komuniti yang dipaparkan pada map dan catalog.',
      columns: [['mypeta-app'], ['intel-manager', 'kopi-manager', 'event-manager'], ['community-data', 'supabase-db'], ['map-manager', 'pengguna']],
    },
    {
      id: 'supabase', title: 'Peta penuh Supabase', category: 'Data', status: 'current', reference: 'assets/diagrams/supabase-full.svg',
      description: 'Snapshot langsung 73 jadual public dan 86 foreign key. Pilih jadual untuk melihat hubungan satu hop.',
      layout: 'schema', columns: [],
    },
    {
      id: 'v2-geo-usecase', title: 'Kes guna georouting V2', category: 'V2 Georouting', status: 'current', reference: 'assets/diagrams/v2-georouting/usecase.svg',
      description: 'Semua kes guna Navigator, GPS, profil, alternatif, manuver, analisis perjalanan, laluan kerja, Studio Geo dan sandaran.',
      collectionId: 'v2-georouting', collectionGroupId: 'use-cases', collectionOrder: 1, versionTag: 'V2', basedOnDiagramId: 'usecase',
      columns: [['pengguna'], ['map-tools-manager', 'geo-navigation-manager'], ['geo-service', 'geo-api', 'geo-gateway'], ['valhalla', 'nominatim', 'geo-studio']],
    },
    {
      id: 'v2-geo-map-flowchart', title: 'Carta alir peta dan navigasi V2', category: 'V2 Georouting', status: 'current', reference: 'assets/diagrams/v2-georouting/map-flowchart.svg',
      description: 'Aliran daripada kesediaan MapLibre kepada A/B, penghalaan dan tindakan analitik pilihan.',
      collectionId: 'v2-georouting', collectionGroupId: 'flowcharts', collectionOrder: 2, versionTag: 'V2', basedOnDiagramId: 'user-explore-3d-map-flowchart',
      columns: [['pengguna'], ['map-manager', 'map-tools-manager'], ['geo-navigation-manager'], ['geo-route-renderer', 'maplibre-gl']],
    },
    {
      id: 'v2-geo-route-sequence', title: 'Jujukan laluan A-ke-B V2', category: 'V2 Georouting', status: 'current', reference: 'assets/diagrams/v2-georouting/route-sequence.svg',
      description: 'Cache hit/miss, Valhalla, alternatif, pemaparan dan sandaran garis lurus yang tidak mendakwa navigasi.',
      collectionId: 'v2-georouting', collectionGroupId: 'sequences', collectionOrder: 3, versionTag: 'V2', basedOnDiagramId: 'user-explore-3d-map-sequence', sequenceAudience: 'georouting', sequenceOrder: 1,
      columns: [['pengguna'], ['map-tools-manager', 'geo-navigation-manager'], ['geo-service', 'geo-api', 'geo-gateway'], ['geo-route-cache', 'valhalla'], ['geo-route-renderer', 'maplibre-gl']],
    },
    {
      id: 'v2-geo-travel-analysis-sequence', title: 'Jujukan analisis perjalanan V2', category: 'V2 Georouting', status: 'current', reference: 'assets/diagrams/v2-georouting/travel-analysis-sequence.svg',
      description: 'Matriks, isokron dan aliran sempadan/POI-dalam yang kini dihentikan oleh geokod Nominatim yang dinyahaktifkan.',
      collectionId: 'v2-georouting', collectionGroupId: 'sequences', collectionOrder: 4, versionTag: 'V2', sequenceAudience: 'georouting', sequenceOrder: 2,
      columns: [['pengguna'], ['map-tools-manager', 'geo-navigation-manager'], ['geo-service', 'geo-api', 'geo-gateway'], ['geo-route-cache', 'geo-geocode-cache'], ['valhalla', 'nominatim', 'maplibre-gl']],
    },
    {
      id: 'v2-geo-job-route-sequence', title: 'Jujukan laluan ke tempat kerja V2', category: 'V2 Georouting', status: 'current', reference: 'assets/diagrams/v2-georouting/job-route-sequence.svg',
      description: 'Penyelesaian lokasi kerja berautentikasi, cache keyakinan, penolakan kerja remote/lokasi lemah dan pengiraan laluan.',
      collectionId: 'v2-georouting', collectionGroupId: 'sequences', collectionOrder: 5, versionTag: 'V2', sequenceAudience: 'georouting', sequenceOrder: 3,
      columns: [['pengguna'], ['job-manager'], ['job-location-resolver', 'job-location-resolution'], ['geo-navigation-manager', 'geo-service', 'geo-gateway'], ['valhalla', 'maplibre-gl']],
    },
    {
      id: 'v2-geo-domain', title: 'Domain georouting V2', category: 'V2 Georouting', status: 'current', reference: 'assets/diagrams/v2-georouting/domain.svg',
      description: 'Model domain sedia ada bersama kontrak tempat, laluan, alternatif, manuver, matriks, isokron dan resolusi lokasi kerja.',
      collectionId: 'v2-georouting', collectionGroupId: 'classes', collectionOrder: 6, versionTag: 'V2', basedOnDiagramId: 'domain',
      columns: [['geo-location', 'geo-place'], ['geo-route', 'geo-route-alternative', 'geo-maneuver'], ['geo-matrix', 'geo-isochrone'], ['job-entity', 'job-location-resolution']],
    },
    {
      id: 'v2-geo-implementation', title: 'Pelaksanaan georouting V2', category: 'V2 Georouting', status: 'current', reference: 'assets/diagrams/v2-georouting/implementation.svg',
      description: 'Kebergantungan Map Tools, Navigator, pemapar, rupa laluan, klien geo, API, gateway, cache dan penyedia.',
      collectionId: 'v2-georouting', collectionGroupId: 'classes', collectionOrder: 7, versionTag: 'V2', basedOnDiagramId: 'implementation',
      columns: [['mypeta-app', 'map-manager'], ['map-tools-manager', 'geo-navigation-manager', 'geo-route-renderer', 'route-appearance-manager'], ['geo-service', 'geo-api', 'geo-gateway'], ['valhalla', 'nominatim', 'supabase-db']],
    },
    {
      id: 'v2-geo-architecture', title: 'Seni bina georouting V2', category: 'V2 Georouting', status: 'current', reference: 'assets/diagrams/v2-georouting/architecture.svg',
      description: 'Lapisan tanggungjawab gaya stacked-Doritos daripada UI pelayar kepada penyedia, cache dan aplikasi analitik.',
      collectionId: 'v2-georouting', collectionGroupId: 'architecture-modules', collectionOrder: 8, versionTag: 'V2', basedOnDiagramId: 'architecture',
      columns: [['browser', 'map-tools-manager'], ['geo-navigation-manager', 'geo-route-renderer'], ['geo-service', 'geo-api'], ['geo-gateway'], ['valhalla', 'nominatim', 'supabase-db', 'geo-studio']],
    },
    {
      id: 'v2-geo-modules', title: 'Modul georouting V2', category: 'V2 Georouting', status: 'current', reference: 'assets/diagrams/v2-georouting/modules.svg',
      description: 'Hierarki orkestrasi frontend, pemaparan, gateway, penyedia dan laluan tempat kerja.',
      collectionId: 'v2-georouting', collectionGroupId: 'architecture-modules', collectionOrder: 9, versionTag: 'V2', basedOnDiagramId: 'modules',
      columns: [['mypeta-app'], ['map-tools-manager', 'geo-navigation-manager', 'geo-route-renderer', 'route-appearance-manager'], ['geo-service', 'geo-api', 'geo-gateway'], ['job-location-resolver', 'geo-studio']],
    },
    {
      id: 'v2-geo-data-flow', title: 'Aliran data georouting V2', category: 'V2 Georouting', status: 'current', reference: 'assets/diagrams/v2-georouting/data-flow.svg',
      description: 'Browser ke API same-origin, gateway, cache/penyedia, GeoJSON ternormal dan MapLibre.',
      collectionId: 'v2-georouting', collectionGroupId: 'data', collectionOrder: 10, versionTag: 'V2', basedOnDiagramId: 'data-flow',
      columns: [['browser'], ['geo-service'], ['geo-api'], ['geo-gateway'], ['geo-route-cache', 'geo-geocode-cache', 'valhalla', 'nominatim'], ['maplibre-gl']],
    },
    {
      id: 'v2-geo-erd', title: 'ERD penghalaan V2', category: 'V2 Georouting', status: 'current', reference: 'assets/diagrams/v2-georouting/erd.svg',
      description: 'ERD fokus bagi cache geokod, cache laluan, resolusi lokasi kerja dan hubungannya dengan scraped_jobs.',
      collectionId: 'v2-georouting', collectionGroupId: 'data', collectionOrder: 11, versionTag: 'V2', basedOnDiagramId: 'erd',
      columns: [['geo-geocode-cache', 'geo-route-cache'], ['job-location-resolution', 'job-entity']],
    },
    {
      id: 'v2-geo-routing-stack', title: 'Tindanan tanggungjawab penghalaan V2', category: 'V2 Georouting', status: 'current', reference: 'assets/diagrams/v2-georouting/routing-stack.svg',
      description: 'Valhalla operasi, Nominatim berpagar, MapLibre sebagai pemapar dan Haversine sebagai sandaran bukan navigasi.',
      collectionId: 'v2-georouting', collectionGroupId: 'architecture-modules', collectionOrder: 12, versionTag: 'V2', basedOnDiagramId: 'map-routing-responsibility-stack',
      columns: [['map-tools-manager', 'geo-navigation-manager'], ['geo-service', 'geo-api'], ['geo-gateway'], ['geo-route-cache', 'valhalla', 'nominatim'], ['geo-route-renderer', 'maplibre-gl']],
    },
    {
      id: 'v2-geo-supabase', title: 'Snapshot Supabase georouting V2', category: 'V2 Georouting', status: 'current', reference: 'assets/diagrams/v2-georouting/supabase.svg',
      description: 'Snapshot bertarikh 19 Julai 2026 bagi 87 jadual public dan 119 foreign key, dengan lima jadual berkaitan geo dikenal pasti.',
      collectionId: 'v2-georouting', collectionGroupId: 'data', collectionOrder: 13, versionTag: 'V2', basedOnDiagramId: 'supabase',
      columns: [['geo-geocode-cache', 'geo-route-cache', 'job-location-resolution'], ['geo-studio'], ['supabase-db']],
    },
  ];

  const rawTables = `
account|auth|id|id,provider_id|1
ai_admin_audit_logs|ai|id|id|1
ai_provider_credentials|ai|id|id,owner_type,provider_id,enabled|1
ai_usage_events|ai|id|id,provider_id,status|1
ai_user_model_preferences|ai|user_id|user_id|1
blog_analytics_events|blog|id|id|1
blog_author_profiles|blog|id|id|1
blog_broadcast_recipients|blog|broadcast_id+subscriber_id|broadcast_id,subscriber_id,status|1
blog_broadcast_redirects|blog|id|id|1
blog_broadcasts|blog|id|id,status|1
blog_categories|blog|id|id,name|1
blog_comments|blog|id|id,status|1
blog_cron_runs|blog|id|id|1
blog_email_events|blog|id|id,email|1
blog_email_suppressions|blog|email|email|1
blog_media|blog|id|id|1
blog_newsletters|blog|id|id,name|1
blog_post_bookmarks|blog|post_id+user_id|post_id,user_id|1
blog_post_reactions|blog|post_id+user_id+reaction|post_id,user_id,reaction|1
blog_post_revisions|blog|id|id|1
blog_post_tags|blog|post_id+tag_id|post_id,tag_id|1
blog_post_views|blog|id|id|1
blog_post_views_daily|blog|bucket_date+post_id|bucket_date,post_id|1
blog_post_views_daily_dim|blog|bucket_date+post_id+dim_kind+dim_value|bucket_date,post_id,dim_kind,dim_value|1
blog_posts|blog|id|id,status,title|1
blog_reading_history|blog|user_id+post_id|user_id,post_id|1
blog_recommendations|blog|id|id,title|1
blog_subscriber_events|blog|id|id|1
blog_subscriber_newsletters|blog|subscriber_id+newsletter_id|subscriber_id,newsletter_id|1
blog_subscribers|blog|id|id,email,status,source|1
blog_tags|blog|id|id,name|1
blog_views_rollup_state|blog|id|id|1
coffee_shops|community|id|id,name,state|1
company_address_cache|jobops|company_key|company_key,source|1
data_sources|core|id|id,name,is_active|1
events|community|id|id,name,state|1
extractor_jobs|jobops|run_id+scraped_jobs_id|run_id,scraped_jobs_id,source,title|1
extractor_runs|jobops|id|id,status|1
geocode_cache|infra|query_key|query_key,source|1
map_styles|core|id|id|1
notifications|jobops|id|id,title|1
pipeline_run_items|jobops|id|id,status|1
pipeline_runs|jobops|id|id,status|1
poi_bookmarks|core|id|id|1
poi_categories|core|id|id,name|1
poi_category_groups|core|id|id,name|1
poi_reviews|core|id|id|1
pois|core|id|id,name,category|1
poll_options|community|id|id|1
polls|community|id|id,category,is_active|1
rc_masjids|community|id|id,name|1
rc_submissions|community|id|id,title|1
scraped_jobs|core|id|id,source_platform,job_title,company_name,state|1
session|auth|id|id|1
spatial_ref_sys|infra|srid|srid|0
states|core|id|id,name|1
transit_routes|core|id|id,source|1
user|auth|id|id,name,email|1
user_api_tokens|infra|id|id,name|1
user_company_watchlist|jobops|id|id,enabled|1
user_gmail_integrations|jobops|id|id,email,status|1
user_gmail_messages|jobops|id|id|1
user_gmail_sync_runs|jobops|id|id,status|1
user_job_states|core|id|id,source,state,job_title,company_name,source_platform|1
user_marker_purchases|core|user_id+marker_id|user_id,marker_id|1
user_notification_prefs|infra|user_id|user_id|1
user_pipeline_settings|jobops|user_id|user_id|1
user_privacy_prefs|infra|user_id|user_id|1
users|core|id|id,email,role|1
verification|auth|id|id|1
votes|community|id|id|1
watchlist_discovered_jobs|jobops|id|id,job_title|1
watchlist_polls|jobops|id|id,status|1`.trim();

  const schemaTables = rawTables.split('\n').map((line) => {
    const [name, group, pk, columns, rls] = line.split('|');
    return { name, group, pk: pk.split('+'), columns: columns.split(','), rls: rls === '1' };
  });

  const rawForeignKeys = `
account.user_id>user.id
ai_admin_audit_logs.actor_user_id>users.id
ai_provider_credentials.user_id>users.id
ai_usage_events.user_id>users.id
ai_user_model_preferences.user_id>users.id
blog_analytics_events.post_id>blog_posts.id
blog_analytics_events.user_id>users.id
blog_author_profiles.user_id>users.id
blog_broadcast_recipients.broadcast_id>blog_broadcasts.id
blog_broadcast_recipients.subscriber_id>blog_subscribers.id
blog_broadcast_redirects.broadcast_id>blog_broadcasts.id
blog_broadcasts.newsletter_id>blog_newsletters.id
blog_broadcasts.post_id>blog_posts.id
blog_broadcasts.created_by>users.id
blog_comments.parent_id>blog_comments.id
blog_comments.post_id>blog_posts.id
blog_comments.user_id>users.id
blog_email_events.broadcast_id>blog_broadcasts.id
blog_email_suppressions.source_broadcast_id>blog_broadcasts.id
blog_email_suppressions.source_event_id>blog_email_events.provider_event_id
blog_media.owner_user_id>users.id
blog_post_bookmarks.post_id>blog_posts.id
blog_post_bookmarks.user_id>users.id
blog_post_reactions.post_id>blog_posts.id
blog_post_reactions.user_id>users.id
blog_post_revisions.post_id>blog_posts.id
blog_post_revisions.editor_user_id>users.id
blog_post_tags.post_id>blog_posts.id
blog_post_tags.tag_id>blog_tags.id
blog_post_views.post_id>blog_posts.id
blog_post_views.viewer_user_id>users.id
blog_post_views_daily.post_id>blog_posts.id
blog_posts.author_id>blog_author_profiles.id
blog_posts.category_id>blog_categories.id
blog_posts.newsletter_id>blog_newsletters.id
blog_reading_history.post_id>blog_posts.id
blog_reading_history.user_id>users.id
blog_recommendations.created_by>users.id
blog_subscriber_events.source_post_id>blog_posts.id
blog_subscriber_events.subscriber_id>blog_subscribers.id
blog_subscriber_newsletters.newsletter_id>blog_newsletters.id
blog_subscriber_newsletters.subscriber_id>blog_subscribers.id
blog_subscribers.source_post_id>blog_posts.id
blog_subscribers.user_id>users.id
extractor_jobs.run_id>extractor_runs.id
map_styles.category_id>poi_categories.id
map_styles.group_id>poi_category_groups.id
notifications.user_id>users.id
pipeline_run_items.run_id>pipeline_runs.id
pipeline_run_items.job_state_id>user_job_states.id
pipeline_runs.user_id>users.id
poi_bookmarks.poi_id>pois.id
poi_bookmarks.user_id>users.id
poi_categories.group_id>poi_category_groups.id
poi_reviews.poi_id>pois.id
poi_reviews.user_id>users.id
pois.data_source_id>data_sources.id
pois.category>poi_categories.id
pois.state_id>states.id
poll_options.poll_id>polls.id
polls.created_by>users.id
rc_submissions.masjid_id>rc_masjids.id
session.user_id>user.id
user_api_tokens.user_id>users.id
user_company_watchlist.user_id>users.id
user_gmail_integrations.user_id>users.id
user_gmail_messages.integration_id>user_gmail_integrations.id
user_gmail_messages.matched_job_state_id>user_job_states.id
user_gmail_messages.user_id>users.id
user_gmail_sync_runs.integration_id>user_gmail_integrations.id
user_gmail_sync_runs.user_id>users.id
user_job_states.user_id>users.id
user_marker_purchases.user_id>users.id
user_notification_prefs.user_id>users.id
user_pipeline_settings.user_id>users.id
user_privacy_prefs.user_id>users.id
users.selected_state>states.id
votes.poll_option_id>poll_options.id
votes.poll_id>polls.id
votes.user_id>users.id
watchlist_discovered_jobs.watchlist_entry_id>user_company_watchlist.id
watchlist_discovered_jobs.saved_job_state_id>user_job_states.id
watchlist_discovered_jobs.user_id>users.id
watchlist_polls.notification_id>notifications.id
watchlist_polls.watchlist_entry_id>user_company_watchlist.id
watchlist_polls.user_id>users.id`.trim();

  const schemaForeignKeys = rawForeignKeys.split('\n').map((line, index) => {
    const [sourceSide, targetSide] = line.split('>');
    const sourceSplit = sourceSide.split('.');
    const targetSplit = targetSide.split('.');
    return {
      id: `fk-${index + 1}`,
      sourceTable: sourceSplit[0], sourceColumn: sourceSplit.slice(1).join('.'),
      targetTable: targetSplit[0], targetColumn: targetSplit.slice(1).join('.'),
    };
  });

  const logicalLinks = [
    { id: 'logical-auth-bridge', sourceTable: 'user', sourceColumn: 'id', targetTable: 'users', targetColumn: 'better_auth_user_id', label: 'Better Auth bridge' },
  ];

  const hotspots = [
    { id: 'start-workspaces', view: 'start', label: 'Pilihan ruang kerja', x: 18.5, y: 34.5, w: 61, h: 34, nodes: ['mypeta-app', 'ui-templates', 'pengguna'] },
    { id: 'start-map-preset', view: 'start', label: 'Malaysia Map', x: 18.5, y: 36, w: 20, h: 10, nodes: ['map-manager', 'mypeta-app'] },
    { id: 'map-search', view: 'map', label: 'Carian POI', x: 42, y: 2.5, w: 25, h: 4.5, nodes: ['search-manager', 'poi-entity'] },
    { id: 'ribbon', view: 'map', label: 'Ribbon aplikasi', x: 0.5, y: 7, w: 99, h: 10, nodes: ['panel-manager', 'ui-templates', 'mypeta-app'] },
    { id: 'ribbon-map', view: 'map', label: 'Kawalan peta', x: 0.5, y: 8, w: 54, h: 9, nodes: ['map-manager', 'panel-manager'] },
    { id: 'ribbon-data', view: 'map', label: 'Dataset nasional', x: 63, y: 8, w: 25, h: 9, nodes: ['insights-manager', 'open-data-api'] },
    { id: 'contents-pane', view: 'map', label: 'Contents pane', x: 0, y: 18, w: 21, h: 78, nodes: ['panel-manager', 'category-manager', 'intel-manager'] },
    { id: 'contents-poi', view: 'map', label: 'Kategori dan kiraan POI', x: 0, y: 72, w: 21, h: 20, nodes: ['category-manager', 'poi-category-entity', 'poi-group-entity'] },
    { id: 'contents-intel', view: 'map', label: 'Layer intel', x: 0, y: 25, w: 21, h: 48, nodes: ['intel-manager', 'kopi-manager', 'event-manager'] },
    { id: 'map-canvas', view: 'map', label: 'MapLibre map', x: 21, y: 22, w: 55, h: 75, nodes: ['map-manager', 'poi-manager', 'poi-entity', 'state-entity', 'highlight-manager'] },
    { id: 'catalog-pane', view: 'map', label: 'Catalog pane', x: 76, y: 18, w: 24, h: 79, nodes: ['panel-manager', 'insights-manager', 'chatbot-manager'] },
    { id: 'catalog-national', view: 'map', label: 'Analitik nasional', x: 76.5, y: 22, w: 23, h: 12, nodes: ['insights-manager', 'open-data-api', 'state-entity'] },
    { id: 'user-menu', view: 'map', label: 'Menu pengguna', x: 92, y: 2, w: 3.5, h: 5.5, nodes: ['auth-manager', 'user-profile', 'user-dashboard', 'admin-manager'] },
    { id: 'auth-modal', view: 'auth', label: 'Google OAuth', x: 34.5, y: 38, w: 31, h: 24, nodes: ['auth-manager', 'auth-identity', 'user-profile', 'better-auth', 'admin-manager'] },
    { id: 'assistant-panel', view: 'assistant', label: 'PetaKerja Assistant', x: 76.5, y: 23, w: 23, h: 73, nodes: ['chatbot-manager', 'assistant-stream', 'ai-provider', 'ai-preference-entity', 'ai-usage-entity'] },
    { id: 'assistant-highlight', view: 'assistant', label: 'Highlight tool', x: 78.5, y: 76, w: 18, h: 7, nodes: ['highlight-manager', 'highlight-entity', 'chatbot-manager'] },
    { id: 'jobs-search', view: 'jobs', label: 'Borang carian pekerjaan', x: 29, y: 25, w: 68, h: 8, nodes: ['job-manager', 'jobs-api', 'supa-jobs-route', 'job-search-relevance', 'job-entity'] },
    { id: 'jobs-cards', view: 'jobs', label: 'Kad dan status pekerjaan', x: 1.5, y: 35, w: 22, h: 55, nodes: ['job-manager', 'job-search-relevance', 'job-entity', 'job-state-entity', 'user-dashboard'] },
    { id: 'jobs-map', view: 'jobs', label: 'Marker pekerjaan', x: 25, y: 34, w: 74, h: 63, nodes: ['job-manager', 'job-entity', 'map-manager'] },
    { id: 'blog-search', view: 'blog', label: 'Carian dan filter blog', x: 57, y: 1.5, w: 24, h: 5, nodes: ['blog-manager', 'blog-routes'] },
    { id: 'blog-write', view: 'blog', label: 'Write post', x: 85, y: 1.5, w: 7, h: 5, nodes: ['blog-editor', 'blog-routes'] },
    { id: 'blog-posts', view: 'blog', label: 'Senarai post', x: 13, y: 10, w: 49, h: 16, nodes: ['blog-manager', 'blog-data'] },
    { id: 'blog-subscribe', view: 'blog', label: 'Newsletter subscribe', x: 13, y: 28, w: 74, h: 15, nodes: ['newsletter-data', 'blog-routes'] },
  ];

  const uiViews = [
    { id: 'start', label: 'Start page', image: 'assets/ui/start-page.png', scope: 'core', description: 'Pemilihan ruang kerja sebelum map dimulakan.' },
    { id: 'map', label: 'Peta & POI', image: 'assets/ui/map-workspace.png', scope: 'core', description: 'Workspace utama dengan ribbon, contents, map dan catalog.' },
    { id: 'auth', label: 'Google sign-in', image: 'assets/ui/google-sign-in.png', scope: 'infra', description: 'Gate Better Auth tanpa data peribadi.' },
    { id: 'assistant', label: 'Analitik & assistant', image: 'assets/ui/analysis-assistant.png', scope: 'core', description: 'Assistant, tools spatial dan konteks map.' },
    { id: 'jobs', label: 'Jobs workspace', image: 'assets/ui/jobs-workspace.png', scope: 'core', description: 'Carian, kad pekerjaan dan marker peta.' },
    { id: 'blog', label: 'Blog', image: 'assets/ui/blog.png', scope: 'blog', description: 'Carian post, author action dan newsletter.' },
  ].map((view) => ({ ...view, hotspots: hotspots.filter((hotspot) => hotspot.view === view.id).map((hotspot) => hotspot.id) }));

  const mappings = Object.fromEntries(nodeList.map((node) => [node.id, {
    hotspots: hotspots.filter((hotspot) => hotspot.nodes.includes(node.id)).map((hotspot) => hotspot.id),
    relatedNodes: edges.filter((item) => item.from === node.id || item.to === node.id).map((item) => item.from === node.id ? item.to : item.from),
  }]));

  window.PETAKERJA_ARCHITECTURE = {
    meta: {
      title: 'PetaKerja Architecture Explorer',
      generatedAt: '14 Julai 2026',
      codeRoot: ROOT,
      branch: 'main',
      schema: { tables: 73, foreignKeys: 86, logicalLinks: 1 },
      notes: ['Tiada ORM aplikasi; supabase-js dan pg.Pool digunakan secara langsung.', 'public.job_listings tidak wujud dalam snapshot langsung.'],
    },
    scopeGroups,
    diagrams,
    nodes,
    edges,
    uiViews,
    hotspots,
    mappings,
    sourceRefs: {
      useCase: 'assets/editor/use-case-petakerja.drawio',
      domainClassDiagram: 'assets/editor/class-domain-petakerja-original.drawio',
      domainClassDiagramPolished: 'assets/editor/class-domain-petakerja.drawio',
      classDiagram: 'assets/editor/class-diagram-petakerja.drawio',
      searchJobsSequence: 'assets/editor/sequence-job-search.drawio',
      manageUsersSequence: 'assets/editor/sequence-admin-manage-users.drawio',
      manageAIConfigurationSequence: 'assets/editor/sequence-admin-manage-ai-configuration.drawio',
      accessAdminDashboardSequence: 'assets/editor/sequence-admin-access-dashboard.drawio',
      monitorSystemActivitySequence: 'assets/editor/sequence-admin-monitor-activity.drawio',
      administratorSignOutSequence: 'assets/editor/sequence-admin-sign-out.drawio',
      explore3DMapSequence: 'assets/editor/sequence-user-explore-3d-map.drawio',
      userSignOutSequence: 'assets/editor/sequence-user-sign-out.drawio',
      googleSignInFlowChart: 'assets/editor/flowchart-user-google-sign-in-original.drawio',
      googleSignInFlowChartPolished: 'assets/editor/flowchart-user-google-sign-in.drawio',
      searchJobsFlowChart: 'assets/editor/flowchart-user-search-jobs-original.drawio',
      searchJobsFlowChartPolished: 'assets/editor/flowchart-user-search-jobs.drawio',
      explore3DMapFlowChart: 'assets/editor/flowchart-user-explore-3d-map-original.drawio',
      explore3DMapFlowChartPolished: 'assets/editor/flowchart-user-explore-3d-map.drawio',
      userSignOutFlowChart: 'assets/editor/flowchart-user-sign-out-original.drawio',
      userSignOutFlowChartPolished: 'assets/editor/flowchart-user-sign-out.drawio',
      layeredArchitectureDrawio: 'assets/editor/architecture-layered.drawio',
      moduleHierarchyDrawio: 'assets/editor/module-hierarchy.drawio',
      manageUsersFlowChart: 'assets/editor/flowchart-admin-manage-users.drawio',
      reportDiagrams: 'exports/diagrams/',
    },
    schemaTables,
    schemaForeignKeys,
    logicalLinks,
  };
}());
