# PetaKerja Architecture Explorer

Offline-first architecture documentation built with vanilla HTML, CSS and JavaScript. The actual Draw.io page is the default view, with the generated interactive map available as a second mode. English is the default for a browser with no saved preference; an explicit BM or EN choice remains stored in `localStorage`.

The native Explorer shell uses a locally bundled Blueprint-derived 16px solid SVG icon subset. Icons keep each control's complete bilingual accessible name, and the Explorer makes no CDN or runtime network request for them.

Dokumentasi seni bina offline-first yang dibina dengan vanilla HTML, CSS dan JavaScript. Rajah Draw.io sebenar ialah paparan lalai, manakala peta interaktif yang dijana kekal sebagai mod kedua. English ialah bahasa lalai bagi browser tanpa pilihan tersimpan; pilihan BM atau EN yang dibuat pengguna terus disimpan dalam `localStorage`.

## Cara membuka / How to open

1. Dwiklik `Start-Explorer.cmd` untuk mod editor penuh. / Double-click `Start-Explorer.cmd` for the full editor mode.
2. The launcher uses loopback port `8082` by default, records runtime metadata under the ignored `.runtime/` folder, and opens the correct URL automatically. Set `PETAKERJA_EXPLORER_PORT` to use another port.
3. Atau jalankan pelayan statik dari folder ini: / Or run a static server from this folder:

   ```powershell
   python -m http.server 8080
   ```

   Kemudian buka / Then open `http://localhost:8080/`.
4. `index.html` masih boleh dibuka terus melalui `file://`, tetapi mod itu baca sahaja kerana browser menyekat integrasi editor lokal. / `index.html` can still be opened through `file://`, but that mode is read-only because the browser blocks the local editor integration.

Jika butang `Edit` dibuka dalam mod `file://`, Explorer kini memaparkan arahan pelancar dan bukannya mengabaikan klik. Import Draw.io menggunakan panduan yang sama. / If `Edit` is clicked in `file://` mode, Explorer now shows the launcher instructions instead of ignoring the click. Draw.io import uses the same guidance.

## Interaksi / Interactions

- Tukar `Rajah sebenar / Peta interaktif` untuk membandingkan rajah asal dengan peta yang dijana. / Switch `Actual diagram / Interactive map` to compare the source diagram with the generated map.
- Pilih `BM | EN`; pilihan disimpan dalam `localStorage`. / Choose `BM | EN`; the choice persists in `localStorage`.
- Pilih `Sistem / System`, `Cerah / Light` atau `Gelap / Dark`. Sistem ialah lalai dan mengikut tema Windows; pilihan manual disimpan dalam `localStorage`. / Choose System, Light or Dark. System is the default and follows the Windows theme; a manual preference persists in `localStorage`.
- Hover atau fokus menunjukkan hubungan terus. Klik mengunci pilihan dan menambah konteks tahap kedua; `Escape` mengosongkannya. / Hover or focus shows direct relationships. Click pins the selection and adds second-level context; `Escape` clears it.
- Gunakan senarai `Bergantung pada`, `Digunakan oleh` dan `Hubungan data` untuk berpindah antara komponen. / Use the `Depends on`, `Used by` and `Data relations` lists to move between components.
- Gunakan `Muat / Fit`, zoom, roda tetikus dan drag-to-pan. Drag boleh bermula di atas teks atau komponen tanpa memilih teks rajah. / Use Fit, zoom, the mouse wheel and drag-to-pan. Drag can start over text or components without selecting diagram text.
- Carian mengindeks nama BM dan English, kelas, fail, route, RPC, jadual dan label UI. / Search indexes BM and English labels, classes, files, routes, RPCs, tables and UI labels.
- Pada tablet dan telefon, gunakan tab `Rajah/Diagram`, `UI` dan `Butiran/Details`. / On tablets and phones, use the Diagram, UI and Details tabs.
- Pilih `Edit` untuk membuka editor Draw.io penuh. Perubahan dihantar kepada validator selepas kira-kira 300 ms; perubahan geometri tidak dianggap sebagai ralat logik. / Choose `Edit` to open the full Draw.io editor. Changes reach the validator after about 300 ms; geometry-only changes are not treated as logical errors.
- Returning to `View` commits the active text edit, exports the current Draw.io page as SVG, sanitises it, and immediately replaces the bundled canvas. The latest valid SVG remains visible if a later export fails.
- Registered canonical diagrams also provide **Save to workspace** in Edit or Agent mode. The local host writes the current XML and SVG atomically, keeps ignored backups, and uses SHA-256 revisions to prevent one browser from silently overwriting a newer save. Reloading Chrome or Edge hydrates the same saved workspace layout.
- Seret fail `.drawio` atau `.xml` ke Explorer untuk preflight halaman dan pemetaan semantik. Fail asal tidak diubah; gunakan `Simpan sebagai / Save as` untuk memuat turun salinan. / Drag a `.drawio` or `.xml` file onto the Explorer for page and semantic-mapping preflight. The original is untouched; use Save as to download a copy.
- Padanan menggunakan `petakerjaKey`, ID sel, nama teknikal/stereotaip dan konteks hubungan. Isu UML memberi amaran tetapi tidak menyekat editor kecuali XML tidak boleh dibaca. / Matching uses `petakerjaKey`, cell IDs, technical names/stereotypes and relationship context. UML issues warn without blocking the editor unless the XML cannot be read.
- Import preflight detects canonical PetaKerja Use Case, Domain, Implementation, Supabase and Flow Chart pages, or safely classifies generic class, use-case, ERD, activity, sequence and flow-chart pages. Ambiguous results require confirmation; unrelated pages remain session-only and receive no false PetaKerja UI mappings.
- The dedicated `Sequence / Jujukan` sidebar uses persistent, accessible `User / Pengguna` and `Administrator / Pentadbir` folders. User sequences contain Google OAuth sign-in, Daily Index job search, Explore the 3D Map and Sign Out. Administrator sequences contain Access Administrator Dashboard, Monitor System Activity Logs, Manage Users, Manage AI Chatbot Configuration and Sign Out.
- The dedicated `Flow Chart / Carta Alir` sidebar has independent persistent User and Administrator folders. Google sign-in, Search Jobs, Explore the 3D Map, User Sign Out and every Administrator use case have nested folders containing `Polished / Dikemas` (recommended and canonical) plus `Original / Asal` (reference) views. Each flow chart keeps its bilingual report paragraph outside the canvas with a copy control.
- `Classes / Kelas` uses the same nested variant pattern for Core domain classes. The polished group-coloured UML presentation is canonical, while the corrected reorganized source remains available as the Original reference with identical component and relationship mappings.
- The job-search View and Edit source now use a proper UML sequence with eight participants, activation bars, cache/query/result fragments and stable `petakerjaKey` mappings to `JobFinderManager`, `supa-api.ts`, `server/routes/intel-jobs.ts`, `shared/jobSearchRelevance.ts`, `public.scraped_jobs`, job cards and MapLibre markers.
- Supported sequences show a global `Simple | Code` / `Ringkas | Kod` control in View and Edit modes. Simple is the persisted default; Code exposes exact selectors, function names, routes and queries without changing the shared Draw.io geometry or dirty state.
- Every registered editable diagram stores native `labelEn`/`labelMs` metadata. This includes Use Case, Domain, Implementation, the full Supabase map, all User and Administrator sequences, every Original/Polished flow chart, Layered Architecture and Module Hierarchy. Sequence messages additionally keep bilingual Simple/Code fields. Switching BM/EN or Ringkas/Kod projects those labels into the same Draw.io geometry, preserves the active page, selection and zoom, and does not create a dirty document or cloud revision by itself. Manual text edits update only the active language.
- The Manage Users sequence documents the current read-only implementation: session verification, `admin|owner` authorization and the newest 100 `public.users` rows. It does not imply role editing, suspension or deletion.
- The Manage AI Chatbot Configuration sequence distinguishes read-only administrator access from owner-only shared-key and model-refresh operations. Its visible implementation note records that `custom_headers`, `fetched_models`, `models_fetched_at` and `fetch_error` are expected by the refresh backend but absent from the current live `ai_provider_credentials` snapshot; the Explorer performs no migration.
- Access Administrator Dashboard documents the real parallel load of provider, AI-usage and user overview data after Better Auth and `admin|owner` authorization. Monitor System Activity Logs is deliberately scoped to the latest AI-assistant usage events from `public.ai_usage_events`; it does not imply a general server-log or `ai_admin_audit_logs` viewer.
- The User Explore the 3D Map sequence follows the Malaysia preset through `MyPetaApp`, `MapManager`, MapLibre, POI/category RPCs, terrain and the 3D-building toggle. Separate User and Administrator Sign Out sequences show Better Auth invalidation and the actual protected-view cleanup behavior.

### V2 Georouting collection

The persisted **V2 Georouting** sidebar folder contains 13 independent, bilingual and editable Draw.io diagrams. Six nested subcategories separate Use Case Diagrams, Flowcharts, Sequence Diagrams, Class Diagrams, Architecture & Modules, and Data Diagrams. Only the subgroup containing the active diagram opens on a fresh load; subgroup choices then persist independently under `petakerja-explorer-diagram-collection-groups`. Paired views expose **Open vanilla / Open V2** in Details; the three additive sequences remain standalone. The historical Draw.io and SVG assets outside `v2-georouting/` are comparison references and must not be rewritten by this collection.

The three V2 sequence diagrams extract their actor, participant, activation, fragment, call, return, divider and actor-stem styles directly from `templates/Sequence Diagram Template.drawio`. They retain nine 200-pixel-pitch lanes, use one 20x40 human actor plus eight 100x60 system participants, and place messages on a 50-pixel row grid. Template `alt` and `opt` frames distinguish cache, provider, geocoder, remote-work, confidence and fallback behavior instead of presenting mutually exclusive paths as one linear exchange.

The V2 Domain and Implementation diagrams use `templates/Class Diagram Template.drawio` as their read-only UML style authority. The generator validates and copies its package, swimlane header, member, divider, relationship and multiplicity-label styles. Every class has a 46-pixel header, a typed attribute compartment, an optional 8-pixel divider and public-operation compartment, with variable heights rounded to the 10-pixel template grid. Parent classes keep the Explorer's stable component keys; child compartments use deterministic `/attributes`, `/divider` and `/operations` keys. Associations, dashed dependencies and hollow-diamond aggregations use orthogonal connector gutters with role labels and endpoint multiplicities.

The V2 Georouting Architecture and Routing Responsibility Stack use `templates/Stack Template.drawio` as a third read-only visual authority. Both keep its exact `1900 x 1180` canvas, five progressively wider foreground trapezoids, five 12-pixel-offset depth copies, fourteen fixed card slots, 480-pixel explanation column, source footer, invisible anchors and separate request/normalized-response rails. Architecture remains the broad capability overview for routing, travel analysis, workplace navigation and Geo Studio; Routing Responsibility Stack remains the focused A-to-B operational flow. Every internal connector has explicit orthogonal gutter points, and the dedicated fallback branch states that a straight line has no ETA, maneuvers or navigable-route claim. Template colors are projected through `light-dark(...)` so the same structural palette remains legible in both Explorer themes.

The runtime note is dated **19 July 2026**: Valhalla routing and shared geo cache were enabled and available, while Nominatim geocoding was disabled and unavailable. Nominatim-dependent boundary and POI-within flows are therefore marked feature-gated. The Haversine fallback is documented only as a straight-line result with no ETA, maneuvers or navigable-route claim. The Supabase snapshot records 87 public tables and 119 foreign keys and identifies `geo_geocode_cache`, `geo_route_cache`, `job_location_resolutions`, `geo_workspaces` and `geo_workspace_assets`.

To regenerate only the owned source collection and then rebuild Explorer previews:

```powershell
python .\scripts\generate-v2-georouting-diagrams.py
python .\scripts\build-diagram-assets.py
python .\scripts\test-v2-georouting-collection.py
```

The generator rewrites the 13 owned V2 sources deterministically. For a class-only visual refresh, export only `domain.drawio` and `implementation.drawio`; for a stack-only refresh, export only `architecture.drawio` and `routing-stack.drawio` to their matching `assets/diagrams/v2-georouting/` SVG files. Then run the asset builder with `PETAKERJA_REUSE_DIAGRAM_EXPORTS=1`; the regression test confirms the remaining V2 and historical vanilla assets did not drift.

Update the date and counts only after a fresh runtime/status and schema verification. The generator writes solely to `assets/editor/v2-georouting/`; generated previews are published under `assets/diagrams/v2-georouting/` by the shared asset builder.

## For Dummies / Panduan Pemula

Choose the locally bundled `book-open` button in the header, or open `#learn` directly. The learning workspace is a bilingual, interactive diagram textbook with ten chapters: orientation, connector notation, Use Case, Sequence, sequence fragments, Activity, Class, ERD/data, architecture/data flow, and State Diagram essentials.

- Direct lesson links use `#learn/<chapter>/<topic>` and work through `file://` as well as localhost.
- Each notation includes a keyboard-accessible SVG, plain-language reading guidance, appropriate use, common mistakes and real PetaKerja examples where available.
- The right-side practice area contains connector, fragment, multiplicity, activity, architecture and state labs plus no-penalty chapter quizzes.
- `Open in Explorer` returns to the referenced diagram and pins the mapped component or connector, preserving the Explorer's diagram, scope and view state.
- Completed topics, quiz attempts and best scores are stored only in `petakerja-explorer-learning-progress:v1`. Use **Reset progress** to remove them.
- Search includes BM/English titles and aliases such as `u-turn`, `self-call`, `dashed line`, `alt`, `opt`, `diamond` and `crow's foot`.
- External standards and draw.io guides are optional links; the page itself makes no runtime network request.

Pada paparan kecil, pilih topik melalui pemilih pelajaran kemudian tukar tab `Belajar / Contoh / Kuiz`. Semua panel kekal di dalam satu viewport dan hanya panel dalaman yang menatal.

Run the dependency-free contract check with `node .\scripts\test-learning-page.mjs`.

## Slides Studio / Studio Slaid

Open `#slides` (or use the **Slides / Slaid** header button) to browse recent
private presentations, search or sort the library and create a UKM deck. Open
`#slides/<deckId>` for the fixed 16:9 workspace
includes a slide filmstrip, Fabric.js canvas, layouts/elements/diagram panels,
speaker notes, timing, a presentation checker and fullscreen rehearsal mode.

- **UKM FYP Presentation 2026** creates 12 Bahasa Melayu slides with suggested
  timings totalling 9 minutes 15 seconds.
- Every registered Explorer diagram can be filtered and inserted as a
  sanitised SVG snapshot. Linked objects keep their diagram ID, language,
  variant, label mode and SHA-256 source revision.
- **Save** writes the deck atomically under ignored `.runtime/presentations/`;
  **Save as copy** creates a separate deck ID; `.slides.json` remains the
  portable source format.
- Local revisions return `409` rather than overwriting a newer browser save.
  Local presentation assets are stored under ignored
  `.runtime/presentation-assets/`.
- Through the integrated PetaKerja origin, **Sync** uses Better Auth-protected,
  administrator-only Express routes and private Supabase storage. Unsigned-in or offline work
  remains safe locally and is queued in IndexedDB for retry.
- Export options include editable `.pptx`, source JSON, one PNG, a PNG ZIP and
  browser Print/Save as PDF. Speaker notes are included in PowerPoint exports.
- On desktop, scrolling vertically over the empty stage around the Fabric
  canvas selects the previous or next slide. Wheel input over the canvas,
  filmstrip, zoom controls, inspector or notes keeps its existing behaviour.
  Trackpad deltas are normalised and throttled, navigation includes hidden
  slides, stops at the deck boundaries, keeps the active thumbnail visible and
  announces the selected slide to assistive technology.
- Every cloud deck has a stable title, a default `main` branch and immutable
  numbered versions. Autosave changes only the branch working copy; use
  **Create Version** for a named checkpoint. History can create, switch, rename
  and archive lightweight branches, preview versions and restore an old version
  as a new head without deleting later history.
- Production includes the browser Draw.io editor, imports, validation, private
  cloud diagrams, branches, versions, collaborators, learning and Slides
  Studio for every signed-in user. Administrators and owners additionally
  maintain the canonical diagram library. Agent Mode, MCP, Draw.io Desktop and
  direct local workspace saving remain local-only authority surfaces.
- IndexedDB is written first. Cloud snapshots are revision checked and stored
  through Better Auth-protected PetaKerja APIs in private Supabase Storage.
  Stale saves return `409`, active-writer leases return `423`, and pending work
  can be recovered on a new branch without overwriting the cloud head.

Cloud sync requires migration
`supabase/migrations/20260716061519_architecture_slides_studio.sql` to be applied
to the linked project, followed by
`supabase/migrations/20260716171818_architecture_slides_version_history.sql`.
The browser never receives a Supabase secret key. Direct Google Slides API
editing and simultaneous collaboration are intentionally out of scope.

Run the Slides Studio contract and local persistence checks with:

```powershell
node .\scripts\test-slides-studio.mjs
node .\scripts\test-workspace-host.mjs
```

## Agent Mode

`Agent` keeps Draw.io visible beside a compact plan and activity panel. It is a constrained diagram agent, not a generic browser operator:

1. Choose `OpenAI`, `OpenAI-compatible`, or `Codex bridge`.
2. OpenAI mode uses the localhost proxy, the Responses API, `gpt-5.6-terra`, medium reasoning, `store: false`, and strict `DiagramPlan` Structured Outputs. The bundled policy blocks known deprecated OpenAI IDs before a request and displays its review date.
3. OpenAI-compatible mode retains a configurable base URL and Chat Completions without applying OpenAI's model policy to the third-party provider.
4. API keys are session-only. Codex bridge mode does not require a browser API key.
5. Use **Test connection** to surface authentication, endpoint, model-availability or CORS errors before planning.
6. Enter a request and choose **Create plan**. The model can return only the documented `DiagramPlan` operations.
7. Review the operation count, affected keys and warnings, then choose **Run plan**.
8. Each operation focuses or creates its target in Draw.io, refreshes validation and appears in the activity log. **Stop** preserves completed work; **Revert run** restores the pre-run XML snapshot.

While operations are being applied, a solid 2px activity outline surrounds only the Draw.io canvas. It remains visible while a safe stop is finishing, then clears when the run completes, stops or fails. The same state is announced through the Agent status region, so activity is never communicated by colour alone. This behavior is inspired by Page Agent's running-only `MotionOverlay`, but is implemented locally with dependency-free CSS and does not bundle `ai-motion`.

Run the dependency-free activity regression check with `node .\scripts\test-agent-activity.mjs`.

Allowed operations are `createPage`, `createComponent`, `updateComponent`, `moveResize`, `connect`, `delete` and `applyLayout`. Native sequence support includes lifelines, actor/boundary/control/entity/object participants, activation bars, combined fragments, synchronous/asynchronous/return/self messages, and sequence layout. The runtime rejects generic clicks, navigation and arbitrary JavaScript. Credentials exist only in page memory, are redacted from activity messages and disappear on reload.

The OpenAI model-policy snapshot is in `openai-model-policy.js`; its official source and review date are shown in Agent Mode. Run the mock endpoint regression test with `node .\scripts\test-openai-agent.mjs`.

Corak reflection-before-action, sejarah aktiviti, retry terhad, pembatalan dan simulator cursor diadaptasi daripada Page Agent di bawah lesen MIT. Explorer tidak menyemat UI DOM-clicking Page Agent. Lihat `THIRD_PARTY_NOTICES.md` dan `licenses/PAGE_AGENT_LICENSE.txt`.

## Optional Codex MCP bridge

The Node launcher also hosts an authenticated loopback command queue. The Agent panel shows connection status and a copyable MCP configuration; the Explorer never changes `.mcp.json` automatically.

Install or refresh the local bridge dependencies only when needed:

```powershell
npm.cmd install --prefix .\bridge
```

The bundled server exposes:

- `get_explorer_status`
- `get_diagram_context`
- `start_new_diagram_session`
- `propose_diagram_plan`
- `await_plan_decision`
- `apply_diagram_operations`
- `validate_active_diagram`
- `export_active_diagram`

Both embedded Agent Mode and Codex use the same validated operations, visible Draw.io plugin, validation feedback, Stop behavior and revert snapshot. Commands are consumed only by an active, ready Agent workspace; reloading the page establishes a fresh queue baseline so old commands are not replayed.

The included authentication demonstration creates a fresh diagram session and then applies 71 visible operations. Run `node .\scripts\run-auth-sequence-demo.mjs` while Agent Mode is open. It writes the canonical `.drawio` and `.svg`; `node .\scripts\export-auth-sequence-png.mjs` produces a light, high-resolution PNG from the adaptive SVG.

## Jana semula aset / Regenerate assets

Skrip tanpa dependency membaca fail Draw.io asal, mengeksport halaman menggunakan indeks satu berasaskan halaman, membuang fallback imej base64, menghasilkan varian BM/EN dan membina `diagram-assets.js`:

The dependency-free script reads the original Draw.io files, exports one-based page indexes, removes base64 image fallbacks, generates BM/EN variants and rebuilds `diagram-assets.js` with unique component keys and directed connector metadata:

```powershell
python .\scripts\build-google-oauth-sequence.py
python .\scripts\build-google-sign-in-flowchart.py
python .\scripts\build-admin-manage-users-flowchart.py
python .\scripts\build-admin-flowcharts.py
python .\scripts\build-polished-admin-flowcharts.py
python .\scripts\build-polished-core-variants.py
python .\scripts\build-job-search-sequence.py
python .\scripts\build-admin-manage-users-sequence.py
python .\scripts\build-admin-manage-ai-configuration-sequence.py
python .\scripts\build-admin-dashboard-sequences.py
python .\scripts\generate-v2-georouting-diagrams.py
python .\scripts\build-diagram-assets.py
```

Portable sources / Sumber mudah alih:

- `assets/editor/` contains every registered canonical Draw.io source used by Edit mode and workspace saving. No active generator depends on a Desktop, Semester or user-profile directory.
- `assets/diagrams/` contains generated interactive SVG assets used by View mode.
- `assets/editor/v2-georouting/` and `assets/diagrams/v2-georouting/` isolate the 13 V2 georouting sources and previews from all historical vanilla assets.
- `templates/Flow Chart Template.drawio`, `templates/Sequence Diagram Template.drawio`, `templates/Use Case Template.drawio`, `templates/Class Diagram Template.drawio` and `templates/Stack Template.drawio` are the read-only visual authorities for the V2 layout system. The generator keeps their 10-pixel grid, UML dimensions, compartment rules, exact responsibility-stack geometry, depth offsets, card/callout slots and connector semantics.
- `exports/diagrams/` is the ignored local destination for report-ready Draw.io, SVG and PNG exports.
- `workspace-manifest.json` is the single allowlist mapping writable diagram IDs to their repository-relative XML and SVG paths. Arbitrary imports remain session-only and download-only until deliberately registered.
- `scripts\build-admin-manage-users-flowchart.py` and `scripts\build-admin-flowcharts.py`: generate the five verified original Administrator flow charts from the read-only template, validate branch coverage and reachability, and preserve their editor copies with the `-original.drawio` suffix.
- `scripts\build-polished-admin-flowcharts.py`: applies the shared semantic palette and tidy presentation rules to all five Administrator flows without changing their labels, branches, stable keys or endpoints. It validates each graph, runs `drawio-ai validate --strict` and `drawio-ai audit`, exports report-ready Draw.io/SVG/PNG files beside the template, and makes the polished sources canonical in Edit mode.
- `scripts\build-polished-core-variants.py`: creates the polished Core Domain and Google sign-in variants, preserves Original hashes, resolves only audited connector fan-ins, produces light report PNGs plus theme-aware Draw.io/SVG files, and publishes matching Original/Polished editor assets.
- `scripts\build-user-flowcharts-and-designs.py` and `scripts\build-polished-user-flowcharts.py`: generate, validate and export the three User flowchart pairs plus editable Layered Architecture and Module Hierarchy Draw.io pairs. The polished variants are canonical; Original variants retain identical logic, stable keys and relationship counts.
- `assets\editor\flowchart-admin-*.drawio`: canonical polished editor sources. Matching `flowchart-admin-*-original.drawio` files remain available through each use case's Original view. `build-diagram-assets.py` produces interactive BM/EN SVGs for both variants.
- `assets\editor\class-domain-petakerja*.drawio` and `flowchart-user-google-sign-in*.drawio`: canonical polished sources and their unchanged Original copies. Both variants retain the same stable keys, UI hotspots and relationship manifests.
- `assets\editor\flowchart-user-search-jobs*.drawio`, `flowchart-user-explore-3d-map*.drawio`, `flowchart-user-sign-out*.drawio`, `architecture-layered*.drawio` and `module-hierarchy*.drawio`: editable Original/Polished sources for the new User and Design variant folders. The older D2 SVGs remain reference artifacts and are not modified.
- The optional development CLI is pinned to `drawio-ai-kit` v1.0.0: `npm.cmd install -g "github:sparklabx/drawio-ai-kit#v1.0.0"`. Its generic workflow and diagram-principle rules are used; cloud-provider and BPMN-specific rules are deliberately not applied to these UML-style flow charts.
- `templates/Sequence Diagram Template.drawio`: read-only visual source for all dedicated Google OAuth, Search Jobs, administrator-dashboard, map-exploration and Sign Out sequence generators.
- `assets\editor\sequence-google-oauth.drawio` and `sequence-job-search.drawio`: generated bilingual editor sources with stable participant, message, operand and fragment keys. Draw.io displays the selected BM/EN and Simple/Code projection without maintaining separate layouts.
- `assets\editor\sequence-admin-manage-users.drawio`: generated simplified-English editor source with stable keys and non-visual bilingual Simple/Code message labels.
- `assets\editor\sequence-admin-manage-ai-configuration.drawio`: generated simplified-English editor source for provider visibility, owner-only shared-key management and model refresh, with stable keys and bilingual Simple/Code message labels.
- `assets\editor\sequence-admin-access-dashboard.drawio`, `sequence-admin-monitor-activity.drawio` and `sequence-admin-sign-out.drawio`: generated administrator sequence sources with stable participant, activation, message, operand and fragment keys.
- `assets\editor\sequence-user-explore-3d-map.drawio` and `sequence-user-sign-out.drawio`: generated bilingual User sequence sources for the public map workspace and Better Auth sign-out cleanup. They share the same native projection and language-specific editing behavior as the Google OAuth and Job Search sequences.
- Local report exports are written under the ignored `exports/diagrams/` directory.

The generator reads the corrected Domain source and copies it into the local editor bundle; it does not rewrite any source diagram. / Penjana membaca sumber Domain yang telah dibetulkan dan menyalinnya ke bundle editor lokal tanpa menulis semula mana-mana rajah sumber.

## Runtime editor lokal / Local editor runtime

- Runtime vendored berada di `vendor/drawio/` dan menambah kira-kira 143 MB.
- `plugins/petakerja-explorer.js` ialah bridge pemilihan/fokus/pengesahan khusus Explorer.
- Lesen dan atribusi disimpan dalam `vendor/drawio/LICENSE` dan `THIRD_PARTY_NOTICES.md`.
- `scripts/sync-drawio-runtime.ps1` boleh menyalin semula runtime daripada repo rujukan. Selepas penyegerakan, daftarkan semula plugin `pkx` seperti diterangkan oleh skrip.
- The vendored runtime lives in `vendor/drawio/`, adds about 143 MB, and remains fully local.
- `Start-Explorer.ps1 -NoOpen` starts or reuses the Node host and prints the selected URL without opening a browser, which is useful for local tests.
- Registered canonical diagrams can be persisted with **Save to workspace** and are restored from their repository-relative workspace files after reload. Unknown imports remain in memory until **Save as** and are never silently registered.
- Theme changes finish the active text edit and reload Draw.io with the current in-memory XML, page and selection, so unsaved diagram work is preserved.
- BM/EN and Ringkas/Kod changes use the same safe reload handshake. Before reload, the bridge commits active text editing and returns the latest XML, page, selection and scale. The controller canonicalises bilingual wrapper labels and native `mxCell value` labels, then reloads the requested projection and restores the editor view.
- Canonical XML and hashes do not contain a transient visible-language projection. Therefore a presentation-only language or label-mode switch does not mark the diagram dirty or advance cloud history. **Save as** projects the selected language into the visible `label` values while retaining the hidden bilingual metadata for Draw.io Desktop.
- `scripts/test-bilingual-diagram-editor.py` inventories the workspace manifest and protects the all-diagram contract: 51 registered diagrams, 50 source files, complete BM/EN fields and unchanged geometry, styles and connector endpoints.
- `scripts/test-v2-georouting-collection.py` verifies nested paths, six subgroup counts, bilingual navigation labels, stable keys, connected edges, exact sequence/class/stack template styles, fixed UML and stack geometry, 12-pixel depth offsets, explicit non-crossing stack gutters, request/response rails, fallback semantics, ordered collection metadata, comparison links, runtime claims and the 87-table/119-FK snapshot.

## PetaKerja mini-app integration

When this repository is checked out as `apps/architecture-explorer` inside PetaKerja, use the parent commands:

```powershell
npm run explorer:setup
npm run dev:explorer
```

PetaKerja serves the mini-app at `http://localhost:3000/architecture-explorer/` and proxies its local APIs to the Explorer host. The standalone host remains available through `npm start` in this directory. The production build includes the full browser Draw.io runtime and cloud diagram client, but excludes Agent Mode, MCP, Draw.io Desktop integration and filesystem workspace saving. Local canonical assets can still be updated explicitly with **Save to workspace** during development.

## Snapshot dan batasan / Snapshot and limitations

- Snapshot Supabase: 73 jadual/tables `public`, 86 foreign keys dan/and one logical Better Auth link (`user.id` → `users.better_auth_user_id`).
- PetaKerja uses `supabase-js` and raw `pg.Pool`, not an application ORM layer.
- `public.job_listings` is expected by selected legacy ETL paths but is absent from the current schema; active Supabase job data is in `public.scraped_jobs`.
- `public.spatial_ref_sys` is a PostGIS system table with RLS disabled in the current snapshot. The explorer does not modify the database. See the [Supabase Row Level Security guide](https://supabase.com/docs/guides/database/postgres/row-level-security).
- Screenshot di/in `assets/ui/` ialah tangkapan tetamu yang dianonimkan / anonymised guest captures with no email, name, avatar, token or API key.
