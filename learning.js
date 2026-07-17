(function () {
  'use strict';

  const data = window.PETAKERJA_LEARNING;
  if (!data) return;

  const byId = (id) => document.getElementById(id);
  const els = {
    shell: byId('learning-shell'), link: byId('learning-link'), back: byId('learning-back'), navBack: byId('learning-nav-back'),
    nav: byId('learning-nav'), reader: byId('learning-reader'), example: byId('learning-example-panel'), quiz: byId('learning-quiz-panel'),
    search: byId('learning-search'), progressBar: byId('learning-progress-bar'), progressText: byId('learning-progress-text'),
    progressLabel: byId('learning-progress-label'), reset: byId('learning-reset'), live: byId('learning-live'),
    mobileTopic: byId('learning-mobile-topic'), skip: byId('skip-link'),
  };
  if (!els.shell || !els.link) return;

  const STORAGE_KEY = 'petakerja-explorer-learning-progress:v1';
  const state = {
    chapterId: data.chapters[0]?.id || 'orientation', topicId: data.topics[0]?.id || '', mobilePanel: 'lesson',
    previousExplorerHash: '#explorer', quizFeedback: null, query: '',
    progress: { completedTopics: [], quizAttempts: {}, scores: {} },
  };

  function language() { return document.documentElement.lang === 'ms' ? 'ms' : 'en'; }
  function bilingual(en, ms) { return { en, ms }; }
  function local(value) { return typeof value === 'string' ? value : value?.[language()] || value?.en || value?.ms || ''; }
  function escapeHTML(value) { return String(value ?? '').replace(/[&<>'"]/g, (char) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', "'": '&#39;', '"': '&quot;' })[char]); }
  function escapeAttr(value) { return escapeHTML(value).replace(/`/g, '&#96;'); }
  function topicById(id) { return data.topics.find((item) => item.id === id); }
  function chapterById(id) { return data.chapters.find((item) => item.id === id); }
  function activeTopic() { return topicById(state.topicId) || data.topics[0]; }
  function activeChapter() { return chapterById(state.chapterId) || data.chapters[0]; }
  function icon(name) { return `<i data-lucide="${escapeAttr(name)}" aria-hidden="true"></i>`; }

  function loadProgress() {
    try {
      const parsed = JSON.parse(localStorage.getItem(STORAGE_KEY) || 'null');
      if (!parsed || typeof parsed !== 'object') return;
      state.progress.completedTopics = Array.isArray(parsed.completedTopics) ? parsed.completedTopics.filter((id) => topicById(id)) : [];
      state.progress.quizAttempts = parsed.quizAttempts && typeof parsed.quizAttempts === 'object' ? parsed.quizAttempts : {};
      state.progress.scores = parsed.scores && typeof parsed.scores === 'object' ? parsed.scores : {};
    } catch (_error) { /* Learning progress is optional. */ }
  }

  function storeProgress() {
    try { localStorage.setItem(STORAGE_KEY, JSON.stringify(state.progress)); }
    catch (_error) { /* Direct file mode may block storage. */ }
  }

  function setHash(chapterId, topicId, replace = false) {
    const next = `#learn/${encodeURIComponent(chapterId)}/${encodeURIComponent(topicId)}`;
    if (replace) history.replaceState(null, '', next); else location.hash = next;
  }

  function parseRoute() {
    const raw = decodeURIComponent(location.hash.replace(/^#/, ''));
    if (!raw.startsWith('learn')) return { learning: false };
    const [, requestedChapter, requestedTopic] = raw.split('/');
    const chapter = chapterById(requestedChapter) || data.chapters[0];
    const topic = topicById(requestedTopic);
    const validTopic = topic?.chapterId === chapter.id ? topic : topicById(chapter.topicIds[0]);
    return { learning: true, chapterId: chapter.id, topicId: validTopic?.id || data.topics[0]?.id };
  }

  function syncRoute() {
    const route = parseRoute();
    document.body.classList.toggle('is-learning-mode', route.learning);
    els.shell.hidden = !route.learning;
    els.link.classList.toggle('is-active', route.learning);
    if (els.skip) {
      els.skip.href = route.learning ? '#learning-reader' : '#diagram-workspace';
      els.skip.textContent = route.learning ? (language() === 'en' ? 'Skip to lesson' : 'Langkau ke pelajaran') : (language() === 'en' ? 'Skip to diagram' : 'Langkau ke rajah');
    }
    if (route.learning) {
      els.link.setAttribute('aria-current', 'page');
      state.chapterId = route.chapterId; state.topicId = route.topicId; state.quizFeedback = null;
      if (location.hash === '#learn') setHash(state.chapterId, state.topicId, true);
      renderLearning();
    } else {
      els.link.removeAttribute('aria-current');
      document.querySelector('.mobile-tabs')?.removeAttribute('hidden');
    }
  }

  function announce(message) { els.live.textContent = ''; requestAnimationFrame(() => { els.live.textContent = message; }); }
  function refreshIcons() { window.lucide?.createIcons?.({ attrs: { 'aria-hidden': 'true', focusable: 'false', 'stroke-width': '1.8' } }); }

  function part(label, body) {
    return `<g class="notation-part" tabindex="0" role="button" data-learning-part="${escapeAttr(label)}" aria-label="${escapeAttr(label)}"><title>${escapeHTML(label)}</title>${body}</g>`;
  }

  function svgFrame(topic, body, width = 360, height = 190) {
    const prefix = `learn-${topic.id.replace(/[^a-z0-9-]/gi, '-')}`;
    return `<svg class="notation-svg" viewBox="0 0 ${width} ${height}" role="img" aria-label="${escapeAttr(local(topic.title))}" data-prefix="${prefix}">
      <defs>
        <marker id="${prefix}-open" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M 1 1 L 9 5 L 1 9" class="notation-marker-open"/></marker>
        <marker id="${prefix}-filled" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M 0 0 L 10 5 L 0 10 Z" class="notation-marker-filled"/></marker>
        <marker id="${prefix}-triangle" viewBox="0 0 12 12" refX="11" refY="6" markerWidth="9" markerHeight="9" orient="auto-start-reverse"><path d="M 1 1 L 11 6 L 1 11 Z" class="notation-marker-hollow"/></marker>
      </defs>${body}</svg>`;
  }

  function connectorVisual(topic, type) {
    const prefix = `learn-${topic.id.replace(/[^a-z0-9-]/gi, '-')}`;
    let lineClass = 'notation-line'; let marker = ''; let start = ''; let end = '';
    if (['dashed-line', 'dependency', 'realization', 'return-message'].includes(type)) lineClass += ' is-dashed';
    if (['open-arrow', 'dependency', 'async-call', 'return-message', 'include', 'extend'].includes(type)) marker = ` marker-end="url(#${prefix}-open)"`;
    if (['filled-arrow', 'sync-call'].includes(type)) marker = ` marker-end="url(#${prefix}-filled)"`;
    if (['triangle-head', 'generalization', 'realization'].includes(type)) marker = ` marker-end="url(#${prefix}-triangle)"`;
    if (type === 'hollow-diamond' || type === 'aggregation') start = '<path d="M 45 95 L 59 86 L 73 95 L 59 104 Z" class="notation-marker-hollow"/>';
    if (type === 'filled-diamond' || type === 'composition') start = '<path d="M 45 95 L 59 86 L 73 95 L 59 104 Z" class="notation-marker-filled"/>';
    if (type === 'crow-foot') end = '<path d="M 305 95 L 326 78 M 305 95 L 326 95 M 305 95 L 326 112 M 300 78 L 300 112" class="notation-line"/>';
    const label = local(topic.title);
    return svgFrame(topic, `${part(language() === 'en' ? 'Source endpoint' : 'Hujung sumber', '<rect x="12" y="67" width="72" height="56" rx="5" class="notation-node"/><text x="48" y="99" class="notation-text">A</text>')}
      ${part(label, `${start}<path d="M 72 95 L ${type === 'crow-foot' ? 300 : 318} 95" class="${lineClass}"${marker}/>${end}<text x="195" y="76" class="notation-label">${escapeHTML(label)}</text>`)}
      ${part(language() === 'en' ? 'Target endpoint' : 'Hujung sasaran', '<rect x="318" y="67" width="30" height="56" rx="5" class="notation-node"/><text x="333" y="99" class="notation-text">B</text>')}`);
  }

  function useCaseVisual(topic, type) {
    if (type === 'actor') return svgFrame(topic, `${part(local(topic.title), '<circle cx="78" cy="48" r="14" class="notation-node"/><path d="M 78 62 L 78 108 M 45 78 L 111 78 M 78 108 L 50 145 M 78 108 L 106 145" class="notation-line"/><text x="78" y="169" class="notation-label">User</text>')} ${part(language() === 'en' ? 'System goal' : 'Matlamat sistem', '<ellipse cx="248" cy="96" rx="83" ry="34" class="notation-node"/><text x="248" y="100" class="notation-text">Search jobs</text>')}<path d="M 111 78 L 165 91" class="notation-line"/>`);
    if (type === 'system-boundary' || type === 'boundary') return svgFrame(topic, part(local(topic.title), '<rect x="36" y="26" width="288" height="138" class="notation-boundary"/><text x="52" y="48" class="notation-label">PetaKerja System</text><ellipse cx="180" cy="99" rx="75" ry="27" class="notation-node"/><text x="180" y="103" class="notation-text">Use case</text>'));
    if (type === 'usecase') return svgFrame(topic, part(local(topic.title), '<ellipse cx="180" cy="95" rx="110" ry="42" class="notation-node"/><text x="180" y="99" class="notation-text">Search jobs</text>'));
    if (type === 'actor-association') return connectorVisual(topic, 'arrowless-line');
    return connectorVisual(topic, type);
  }

  function sequenceVisual(topic, type) {
    if (['sync-call', 'async-call', 'return-message'].includes(type)) return connectorVisual(topic, type);
    const participant = (x, label) => `${part(label, `<rect x="${x - 48}" y="15" width="96" height="42" class="notation-node"/><text x="${x}" y="40" class="notation-text">${escapeHTML(label)}</text>`)}<path d="M ${x} 57 L ${x} 176" class="notation-lifeline"/>`;
    if (type === 'participant' || type === 'lifeline') return svgFrame(topic, `${participant(100, 'User')} ${participant(260, 'Service')}`);
    if (type === 'activation') return svgFrame(topic, `${participant(100, 'Caller')} ${participant(260, 'Service')} ${part(local(topic.title), '<rect x="253" y="78" width="14" height="75" class="notation-activation"/>')}<path d="M 100 86 L 253 86" class="notation-line" marker-end="url(#learn-activation-filled)"/>`);
    if (type === 'self-message') return svgFrame(topic, `${participant(180, 'Manager')} ${part(local(topic.title), '<path d="M 180 82 L 265 82 L 265 118 L 190 118" class="notation-line"/><path d="M 190 118 L 202 112 L 202 124 Z" class="notation-marker-filled"/><text x="225" y="71" class="notation-label">applyFilters()</text>')}`);
    if (type === 'create-destroy') return svgFrame(topic, `${participant(80, 'Factory')}<path d="M 80 88 L 226 88" class="notation-line"/><path d="M 226 88 L 214 82 L 214 94 Z" class="notation-marker-filled"/><text x="150" y="76" class="notation-label">create()</text>${part(language() === 'en' ? 'Created lifeline' : 'Lifeline dicipta', '<rect x="226" y="65" width="92" height="42" class="notation-node"/><text x="272" y="90" class="notation-text">Object</text><path d="M 272 107 L 272 157" class="notation-lifeline"/><path d="M 262 157 L 282 177 M 282 157 L 262 177" class="notation-line"/>')}`);
    return svgFrame(topic, `${participant(100, 'A')} ${participant(260, 'B')} ${part(local(topic.title), '<path d="M 100 98 L 252 98" class="notation-line"/><text x="176" y="84" class="notation-label">[condition] message</text>')}`);
  }

  function fragmentVisual(topic, type) {
    const label = type.replace('fragment-', '');
    const divider = ['alt', 'par'].includes(label) ? '<path d="M 24 106 L 336 106" class="notation-line is-dashed"/>' : '';
    const secondGuard = label === 'alt' ? '[else]' : label === 'par' ? '[branch 2]' : '';
    return svgFrame(topic, `${part(`${label} frame`, `<rect x="18" y="18" width="324" height="154" class="notation-boundary"/><path d="M 18 18 L 86 18 L 86 48 L 76 58 L 18 58 Z" class="notation-node"/><text x="48" y="39" class="notation-text">${escapeHTML(label)}</text>`)}
      ${part(language() === 'en' ? 'Guarded operand' : 'Operand ber-guard', `<text x="36" y="78" class="notation-label">[condition]</text><path d="M 72 91 L 288 91" class="notation-line" marker-end="url(#learn-${topic.id}-open)"/>${divider}${secondGuard ? `<text x="36" y="128" class="notation-label">${escapeHTML(secondGuard)}</text><path d="M 72 145 L 288 145" class="notation-line" marker-end="url(#learn-${topic.id}-open)"/>` : ''}`)}`);
  }

  function activityVisual(topic, type) {
    if (type === 'flowchart-basics') return svgFrame(topic, `${part(language() === 'en' ? 'Terminator' : 'Terminator', '<ellipse cx="54" cy="95" rx="38" ry="22" class="notation-node"/><text x="54" y="99" class="notation-text">Start</text>')}<path d="M 92 95 L 126 95" class="notation-line" marker-end="url(#learn-flowchart-basics-filled)"/>${part(language() === 'en' ? 'Process' : 'Proses', '<rect x="126" y="70" width="96" height="50" class="notation-node"/><text x="174" y="99" class="notation-text">Sign in</text>')}<path d="M 222 95 L 248 95" class="notation-line" marker-end="url(#learn-flowchart-basics-filled)"/>${part(language() === 'en' ? 'Decision' : 'Keputusan', '<path d="M 294 53 L 340 95 L 294 137 L 248 95 Z" class="notation-node"/><text x="294" y="91" class="notation-small">Session?</text>')}<text x="319" y="55" class="notation-label">Yes</text><text x="315" y="146" class="notation-label">No</text>`);
    if (type === 'activity-start-end') return svgFrame(topic, `${part(language() === 'en' ? 'Initial node' : 'Nod awal', '<circle cx="55" cy="95" r="13" class="notation-marker-filled"/>')}<path d="M 68 95 L 145 95" class="notation-line"/><rect x="145" y="68" width="100" height="54" rx="18" class="notation-node"/><text x="195" y="99" class="notation-text">Action</text><path d="M 245 95 L 300 95" class="notation-line"/>${part(language() === 'en' ? 'Activity final' : 'Activity final', '<circle cx="316" cy="95" r="15" class="notation-node"/><circle cx="316" cy="95" r="9" class="notation-marker-filled"/>')}`);
    if (type === 'activity-action') return svgFrame(topic, part(local(topic.title), '<rect x="90" y="60" width="180" height="70" rx="22" class="notation-node"/><text x="180" y="99" class="notation-text">Validate request</text>'));
    if (type === 'activity-decision') return svgFrame(topic, `${part(language() === 'en' ? 'Decision' : 'Keputusan', '<path d="M 180 48 L 235 95 L 180 142 L 125 95 Z" class="notation-node"/>')}<path d="M 35 95 L 125 95 M 235 95 L 325 55 M 235 95 L 325 135" class="notation-line"/><text x="278" y="54" class="notation-label">[yes]</text><text x="278" y="142" class="notation-label">[no]</text>`);
    if (type === 'activity-fork') return svgFrame(topic, `${part(language() === 'en' ? 'Fork / join bar' : 'Bar fork / join', '<rect x="165" y="28" width="30" height="132" class="notation-marker-filled"/>')}<path d="M 35 95 L 165 95 M 195 60 L 325 38 M 195 130 L 325 152" class="notation-line"/>`);
    if (type === 'activity-swimlane') return svgFrame(topic, `${part('User lane', '<rect x="20" y="20" width="155" height="150" class="notation-boundary"/><text x="34" y="42" class="notation-label">User</text>')} ${part('System lane', '<rect x="175" y="20" width="165" height="150" class="notation-boundary"/><text x="190" y="42" class="notation-label">System</text>')}<rect x="55" y="75" width="92" height="42" rx="14" class="notation-node"/><rect x="215" y="75" width="92" height="42" rx="14" class="notation-node"/><path d="M 147 96 L 215 96" class="notation-line"/>`);
    return svgFrame(topic, `${part(language() === 'en' ? 'Data object' : 'Objek data', '<path d="M 224 42 L 310 42 L 330 62 L 330 128 L 224 128 Z M 310 42 L 310 62 L 330 62" class="notation-node"/><text x="277" y="90" class="notation-text">Job data</text>')}<rect x="35" y="62" width="120" height="64" rx="18" class="notation-node"/><text x="95" y="98" class="notation-text">Action</text><path d="M 155 94 L 224 94" class="notation-line"/>`);
  }

  function classVisual(topic, type) {
    if (['multiplicity', 'navigability', 'dependency', 'realization', 'generalization', 'aggregation', 'composition'].includes(type)) return connectorVisual(topic, type);
    if (type === 'class-visibility') return svgFrame(topic, part(local(topic.title), '<rect x="72" y="28" width="216" height="134" class="notation-node"/><path d="M 72 65 L 288 65 M 72 116 L 288 116" class="notation-line"/><text x="180" y="51" class="notation-text notation-strong">AuthManager</text><text x="88" y="88" class="notation-label">- user: AuthUser?</text><text x="88" y="106" class="notation-label">+ static cache: Map</text><text x="88" y="142" class="notation-label">+ requireAuth(): boolean</text>'));
    if (type === 'stereotype') return svgFrame(topic, part(local(topic.title), '<rect x="72" y="38" width="216" height="114" class="notation-node"/><path d="M 72 91 L 288 91" class="notation-line"/><text x="180" y="62" class="notation-label">«entity: public.users»</text><text x="180" y="82" class="notation-text notation-strong">UserProfile</text><text x="88" y="119" class="notation-label">- id: uuid</text><text x="88" y="138" class="notation-label">- role: user | admin</text>'));
    return svgFrame(topic, part(local(topic.title), '<rect x="72" y="22" width="216" height="146" class="notation-node"/><path d="M 72 60 L 288 60 M 72 118 L 288 118" class="notation-line"/><text x="180" y="47" class="notation-text notation-strong">UserProfile</text><text x="88" y="82" class="notation-label">- id: uuid</text><text x="88" y="101" class="notation-label">- role: string</text><text x="88" y="143" class="notation-label">+ updateProfile()</text>'));
  }

  function erdVisual(topic, type) {
    if (type === 'crow-foot') return connectorVisual(topic, type);
    if (type === 'erd-bridge') return svgFrame(topic, `${part('users', '<rect x="14" y="54" width="92" height="82" class="notation-node"/><text x="60" y="79" class="notation-text notation-strong">users</text><text x="26" y="107" class="notation-label">PK id</text>')} ${part(language() === 'en' ? 'Junction table' : 'Jadual penghubung', '<rect x="132" y="40" width="104" height="110" class="notation-node"/><text x="184" y="66" class="notation-text notation-strong">post_tags</text><text x="144" y="94" class="notation-label">FK post_id</text><text x="144" y="116" class="notation-label">FK tag_id</text>')} ${part('tags', '<rect x="262" y="54" width="84" height="82" class="notation-node"/><text x="304" y="79" class="notation-text notation-strong">tags</text><text x="274" y="107" class="notation-label">PK id</text>')}<path d="M 106 95 L 132 95 M 236 95 L 262 95" class="notation-line"/>`);
    if (type === 'erd-logical') return svgFrame(topic, `${part('Better Auth user', '<rect x="18" y="58" width="128" height="74" class="notation-node"/><text x="82" y="87" class="notation-text">user</text><text x="32" y="112" class="notation-label">PK id</text>')} ${part('PetaKerja profile', '<rect x="214" y="58" width="128" height="74" class="notation-node"/><text x="278" y="87" class="notation-text">users</text><text x="228" y="112" class="notation-label">better_auth_user_id</text>')}<path d="M 146 95 L 214 95" class="notation-line is-dashed"/><text x="180" y="81" class="notation-label">logical</text>`);
    return svgFrame(topic, part(local(topic.title), '<rect x="84" y="26" width="192" height="138" class="notation-node"/><path d="M 84 64 L 276 64" class="notation-line"/><text x="180" y="50" class="notation-text notation-strong">user_job_states</text><text x="100" y="89" class="notation-label">PK id: uuid</text><text x="100" y="111" class="notation-label">FK user_id: uuid</text><text x="100" y="133" class="notation-label">UQ source + job_key</text>'));
  }

  function architectureVisual(topic, type) {
    if (type === 'ownership-dependency') return connectorVisual(topic, 'dependency');
    if (type === 'data-flow') return svgFrame(topic, `${part(language() === 'en' ? 'Data source' : 'Sumber data', '<rect x="18" y="66" width="105" height="58" rx="5" class="notation-node"/><text x="70" y="99" class="notation-text">API</text>')} ${part(language() === 'en' ? 'Consumer' : 'Pengguna data', '<rect x="237" y="66" width="105" height="58" rx="5" class="notation-node"/><text x="289" y="99" class="notation-text">UI</text>')}<path d="M 123 95 L 237 95" class="notation-line" marker-end="url(#learn-${topic.id}-filled)"/><text x="180" y="80" class="notation-label">JSON jobs</text>`);
    if (type === 'architecture-database') return svgFrame(topic, `${part(language() === 'en' ? 'Database' : 'Pangkalan data', '<path d="M 58 48 C 58 30 150 30 150 48 L 150 138 C 150 156 58 156 58 138 Z M 58 48 C 58 66 150 66 150 48" class="notation-node"/><text x="104" y="105" class="notation-text">Supabase</text>')} ${part(language() === 'en' ? 'External system' : 'Sistem luar', '<rect x="216" y="54" width="118" height="82" rx="5" class="notation-node"/><text x="275" y="99" class="notation-text">Google OAuth</text>')}`);
    if (type === 'architecture-layers') return svgFrame(topic, `${part('UI layer', '<rect x="34" y="24" width="292" height="40" rx="5" class="notation-boundary"/><text x="180" y="49" class="notation-text">UI / Managers</text>')} ${part('API layer', '<rect x="34" y="76" width="292" height="40" rx="5" class="notation-boundary"/><text x="180" y="101" class="notation-text">Express API</text>')} ${part('Data layer', '<rect x="34" y="128" width="292" height="40" rx="5" class="notation-boundary"/><text x="180" y="153" class="notation-text">Supabase / PostgreSQL</text>')}`);
    return svgFrame(topic, `${part(language() === 'en' ? 'Module' : 'Modul', '<rect x="32" y="62" width="126" height="72" rx="5" class="notation-node"/><path d="M 32 77 L 18 77 L 18 97 L 32 97 M 32 105 L 18 105 L 18 125 L 32 125" class="notation-line"/><text x="94" y="102" class="notation-text">Manager</text>')} ${part(language() === 'en' ? 'Service' : 'Servis', '<rect x="218" y="62" width="110" height="72" rx="5" class="notation-node"/><text x="273" y="102" class="notation-text">Service</text>')}<path d="M 158 98 L 218 98" class="notation-line is-dashed"/>`);
  }

  function stateVisual(topic, type) {
    if (type === 'state-start-end') return svgFrame(topic, `${part(language() === 'en' ? 'Initial state' : 'Keadaan awal', '<circle cx="42" cy="95" r="12" class="notation-marker-filled"/>')}<path d="M 54 95 L 120 95" class="notation-line"/><rect x="120" y="65" width="100" height="60" rx="18" class="notation-node"/><text x="170" y="99" class="notation-text">Ready</text><path d="M 220 95 L 298 95" class="notation-line"/>${part(language() === 'en' ? 'Final state' : 'Keadaan akhir', '<circle cx="316" cy="95" r="16" class="notation-node"/><circle cx="316" cy="95" r="9" class="notation-marker-filled"/>')}`);
    if (type === 'state-self') return svgFrame(topic, `${part(language() === 'en' ? 'State' : 'Keadaan', '<rect x="118" y="82" width="124" height="62" rx="20" class="notation-node"/><text x="180" y="117" class="notation-text">Searching</text>')} ${part(language() === 'en' ? 'Self-transition' : 'Peralihan kendiri', '<path d="M 145 82 C 100 22 260 22 215 82" class="notation-line"/><path d="M 215 82 L 205 70 L 224 72 Z" class="notation-marker-filled"/><text x="180" y="30" class="notation-label">retry</text>')}`);
    if (type === 'state-label') return svgFrame(topic, `${part('Ready', '<rect x="18" y="67" width="100" height="56" rx="18" class="notation-node"/><text x="68" y="99" class="notation-text">Ready</text>')} ${part(local(topic.title), '<path d="M 118 95 L 242 95" class="notation-line"/><path d="M 242 95 L 230 89 L 230 101 Z" class="notation-marker-filled"/><text x="180" y="72" class="notation-label">save [valid] / persist()</text>')} ${part('Saved', '<rect x="242" y="67" width="100" height="56" rx="18" class="notation-node"/><text x="292" y="99" class="notation-text">Saved</text>')}`);
    if (type === 'state-transition') return stateVisual(topic, 'state-label');
    return svgFrame(topic, part(local(topic.title), '<rect x="100" y="58" width="160" height="78" rx="24" class="notation-node"/><text x="180" y="101" class="notation-text notation-strong">Interviewing</text>'));
  }

  function renderTopicVisual(topic) {
    const type = topic.visualType;
    if (['solid-line', 'dashed-line', 'arrowless-line', 'open-arrow', 'filled-arrow', 'triangle-head', 'hollow-diamond', 'filled-diamond', 'crow-foot'].includes(type)) return connectorVisual(topic, type);
    if (topic.chapterId === 'usecase' || ['boundary'].includes(type)) return useCaseVisual(topic, type);
    if (topic.chapterId === 'sequence' || ['guard'].includes(type)) return sequenceVisual(topic, type);
    if (topic.chapterId === 'fragments' || type === 'operand-divider') return fragmentVisual(topic, type === 'operand-divider' ? 'fragment-alt' : type);
    if (topic.chapterId === 'activity') return activityVisual(topic, type);
    if (topic.chapterId === 'class') return classVisual(topic, type);
    if (topic.chapterId === 'erd') return erdVisual(topic, type);
    if (topic.chapterId === 'architecture') return architectureVisual(topic, type);
    if (topic.chapterId === 'state') return stateVisual(topic, type);
    if (type === 'static-dynamic') return svgFrame(topic, `${part(language() === 'en' ? 'Static structure' : 'Struktur statik', '<rect x="24" y="48" width="120" height="94" class="notation-node"/><path d="M 24 82 L 144 82" class="notation-line"/><text x="84" y="71" class="notation-text">Class</text><text x="84" y="110" class="notation-label">what exists</text>')} ${part(language() === 'en' ? 'Behaviour over time' : 'Tingkah laku mengikut masa', '<rect x="220" y="30" width="96" height="40" class="notation-node"/><path d="M 268 70 L 268 160" class="notation-lifeline"/><path d="M 190 102 L 268 102" class="notation-line"/><text x="252" y="52" class="notation-text">Object</text><text x="224" y="94" class="notation-label">message</text>')}`);
    if (type === 'reading-direction') return svgFrame(topic, `${part(language() === 'en' ? 'Time moves down' : 'Masa bergerak ke bawah', '<path d="M 180 28 L 180 158" class="notation-line"/><path d="M 180 158 L 168 144 L 192 144 Z" class="notation-marker-filled"/><text x="200" y="96" class="notation-label">time</text>')}`);
    return useCaseVisual(topic, type === 'boundary' ? 'boundary' : 'system-boundary');
  }

  function renderNavigation() {
    const query = state.query.trim().toLocaleLowerCase();
    if (query) {
      const results = data.topics.filter((item) => [item.title.en, item.title.ms, item.purpose.en, item.purpose.ms, ...(item.aliases || [])].join(' ').toLocaleLowerCase().includes(query));
      els.nav.innerHTML = `<section class="learning-search-results"><h3>${language() === 'en' ? 'Search results' : 'Hasil carian'}</h3>${results.length ? results.map(topicButton).join('') : `<p>${language() === 'en' ? 'No matching notation.' : 'Tiada notasi sepadan.'}</p>`}</section>`;
      refreshIcons(); return;
    }
    els.nav.innerHTML = data.chapters.map((chapter, index) => {
      const active = chapter.id === state.chapterId;
      const completed = chapter.topicIds.filter((id) => state.progress.completedTopics.includes(id)).length;
      return `<section class="learning-chapter${active ? ' is-active' : ''}"><button type="button" class="learning-chapter__button" data-learning-chapter="${escapeAttr(chapter.id)}" aria-expanded="${String(active)}"><span class="learning-chapter__number">${index + 1}</span>${icon(chapter.icon)}<span><strong>${escapeHTML(local(chapter.title))}</strong><small>${completed}/${chapter.topicIds.length}</small></span>${icon(active ? 'chevron-down' : 'chevron-right')}</button>${active ? `<div class="learning-topic-list">${chapter.topicIds.map((id) => topicButton(topicById(id))).join('')}</div>` : ''}</section>`;
    }).join('');
    refreshIcons();
  }

  function topicButton(item) {
    if (!item) return '';
    const complete = state.progress.completedTopics.includes(item.id);
    return `<button type="button" class="learning-topic-button${item.id === state.topicId ? ' is-active' : ''}" data-learning-topic="${escapeAttr(item.id)}"><span>${escapeHTML(local(item.title))}</span>${icon(complete ? 'circle-check' : 'circle')}</button>`;
  }

  function renderMistakeExercise(topic) {
    const special = {
      'self-message': bilingual('“Catch fetch failure” is drawn as a U-turn self-message. Keep or change it?', '“Catch fetch failure” dilukis sebagai mesej kendiri pusingan U. Kekalkan atau ubah?'),
      'include': bilingual('The arrow points from Sign in toward Save status. Is that correct?', 'Anak panah menunjuk dari Log masuk kepada Simpan status. Adakah itu betul?'),
      'return-message': bilingual('A returned `JobGrepResponse` uses a solid filled arrow. Is that correct?', '`JobGrepResponse` yang dikembalikan menggunakan anak panah pejal berisi. Adakah itu betul?'),
      'composition': bilingual('A separately stored Supabase profile is destroyed whenever the UI manager closes. Is composition correct?', 'Profil Supabase yang disimpan berasingan dimusnahkan apabila manager UI ditutup. Adakah composition betul?'),
      'multiplicity': bilingual('Both `1` and `0..*` labels are placed beside the same class. Can the relationship be read reliably?', 'Kedua-dua label `1` dan `0..*` diletakkan di sebelah kelas sama. Bolehkah hubungan dibaca dengan tepat?'),
    }[topic.id];
    if (!special) return '';
    return `<section class="mistake-exercise"><div><p class="eyebrow">${language() === 'en' ? 'Spot the mistake' : 'Cari kesilapan'}</p><h3>${escapeHTML(local(special))}</h3></div><details><summary>${language() === 'en' ? 'Reveal explanation' : 'Tunjukkan penjelasan'}</summary><p>${escapeHTML(local(topic.commonMistakes))}</p></details></section>`;
  }

  function renderReader() {
    const topic = activeTopic(); const chapter = activeChapter();
    const index = data.topics.indexOf(topic); const previous = data.topics[index - 1]; const next = data.topics[index + 1];
    const complete = state.progress.completedTopics.includes(topic.id);
    const refs = (topic.explorerRefs || []).map((ref) => `<button type="button" class="explorer-example-link" data-explorer-diagram="${escapeAttr(ref.diagramId)}"${ref.componentKey ? ` data-explorer-component="${escapeAttr(ref.componentKey)}"` : ''}${ref.connectionId ? ` data-explorer-connection="${escapeAttr(ref.connectionId)}"` : ''}>${icon('external-link')}<span>${escapeHTML(local(ref.caption))}</span></button>`).join('');
    const sourceRows = (topic.sources || []).map((id) => data.sources[id]).filter(Boolean).map((source) => source.href ? `<a href="${escapeAttr(source.href)}" target="_blank" rel="noreferrer">${escapeHTML(local(source.label))}</a>` : `<span>${escapeHTML(local(source.label))}</span>`).join('');
    els.reader.innerHTML = `<article class="learning-article">
      <header class="learning-article__header"><div><p class="eyebrow">${escapeHTML(local(chapter.title))}</p><h1>${escapeHTML(local(topic.title))}</h1><p>${escapeHTML(local(topic.purpose))}</p></div><button type="button" id="learning-complete" class="completion-button${complete ? ' is-complete' : ''}" aria-pressed="${String(complete)}">${icon(complete ? 'circle-check-big' : 'circle')}<span>${complete ? (language() === 'en' ? 'Completed' : 'Selesai') : (language() === 'en' ? 'Mark complete' : 'Tanda selesai')}</span></button></header>
      <figure class="notation-gallery"><div class="notation-gallery__stage">${renderTopicVisual(topic)}</div><figcaption>${language() === 'en' ? 'Focus or select a part of the illustration to hear its role.' : 'Fokus atau pilih bahagian ilustrasi untuk mendengar peranannya.'}</figcaption></figure>
      <div class="learning-explanation-grid"><section><h2>${language() === 'en' ? 'How to read it' : 'Cara membacanya'}</h2><p>${escapeHTML(local(topic.howToRead))}</p></section><section><h2>${language() === 'en' ? 'When to use it' : 'Bila menggunakannya'}</h2><p>${escapeHTML(local(topic.whenToUse))}</p></section><section class="learning-warning"><h2>${language() === 'en' ? 'Do not confuse it with…' : 'Jangan kelirukannya dengan…'}</h2><p>${escapeHTML(local(topic.commonMistakes))}</p></section></div>
      ${renderMistakeExercise(topic)}
      ${refs ? `<section class="explorer-examples"><h2>${language() === 'en' ? 'See it in PetaKerja' : 'Lihat dalam PetaKerja'}</h2><div>${refs}</div></section>` : ''}
      <section class="learning-sources"><h2>${language() === 'en' ? 'Reference basis' : 'Asas rujukan'}</h2><div>${sourceRows}</div></section>
      <nav class="learning-article__pager" aria-label="${language() === 'en' ? 'Lesson navigation' : 'Navigasi pelajaran'}">${previous ? `<button type="button" data-learning-topic="${escapeAttr(previous.id)}">${icon('arrow-left')}<span><small>${language() === 'en' ? 'Previous' : 'Sebelumnya'}</small>${escapeHTML(local(previous.title))}</span></button>` : '<span></span>'}${next ? `<button type="button" data-learning-topic="${escapeAttr(next.id)}"><span><small>${language() === 'en' ? 'Next' : 'Seterusnya'}</small>${escapeHTML(local(next.title))}</span>${icon('arrow-right')}</button>` : '<span></span>'}</nav>
    </article>`;
    refreshIcons();
  }

  function labType() {
    return ({ orientation: 'reader', connectors: 'connector', usecase: 'usecase', sequence: 'sequence', fragments: 'fragment', activity: 'activity', class: 'multiplicity', erd: 'multiplicity', architecture: 'architecture', state: 'state' })[state.chapterId] || 'connector';
  }

  function optionRows(values, selected) { return values.map((value) => `<option value="${escapeAttr(value)}"${value === selected ? ' selected' : ''}>${escapeHTML(value)}</option>`).join(''); }
  function labText(en, ms) { return language() === 'en' ? en : ms; }

  function renderExamplePanel() {
    const type = labType(); let controls = ''; let title = ''; let body = '';
    if (type === 'connector') {
      title = labText('Connector builder', 'Pembina penyambung');
      controls = `<label>${labText('Relationship', 'Hubungan')}<select data-lab-control="connector">${optionRows(data.labPresets.connector, 'association')}</select></label>`;
      body = labConnector('association');
    } else if (type === 'usecase') {
      title = labText('include vs extend', 'include lwn extend');
      controls = `<label>${labText('Relationship', 'Hubungan')}<select data-lab-control="usecase">${optionRows(['include', 'extend', 'association'], 'include')}</select></label>`;
      body = labConnector('include');
    } else if (type === 'sequence') {
      title = labText('Message comparison', 'Perbandingan mesej');
      controls = `<label>${labText('Message', 'Mesej')}<select data-lab-control="sequence">${optionRows(['synchronous call', 'asynchronous message', 'return message', 'self-message'], 'synchronous call')}</select></label>`;
      body = labSequence('synchronous call');
    } else if (type === 'fragment') {
      title = labText('Fragment simulator', 'Simulator fragmen');
      controls = `<label>${labText('Fragment', 'Fragmen')}<select data-lab-control="fragment">${optionRows(data.labPresets.fragment, 'alt')}</select></label><label>${labText('Guard', 'Guard')}<input data-lab-guard type="text" value="jobs returned" maxlength="48"></label>`;
      body = labFragment('alt', 'jobs returned');
    } else if (type === 'multiplicity') {
      title = labText('Multiplicity builder', 'Pembina multiplicity');
      controls = `<label>A<select data-lab-control="multiplicity-a">${optionRows(data.labPresets.multiplicity, '1')}</select></label><label>B<select data-lab-control="multiplicity-b">${optionRows(data.labPresets.multiplicity, '0..*')}</select></label><label>${labText('Ownership', 'Pemilikan')}<select data-lab-control="ownership">${optionRows(['association', 'aggregation', 'composition'], 'association')}</select></label>`;
      body = labMultiplicity('1', '0..*', 'association');
    } else if (type === 'activity') {
      title = labText('Decision vs parallel flow', 'Keputusan lwn aliran selari');
      controls = `<label>${labText('Node', 'Nod')}<select data-lab-control="activity">${optionRows(['decision', 'fork'], 'decision')}</select></label>`;
      body = labActivity('decision');
    } else if (type === 'architecture') {
      title = labText('Architecture relationship', 'Hubungan seni bina');
      controls = `<label>${labText('Claim', 'Dakwaan')}<select data-lab-control="architecture">${optionRows(['dependency', 'ownership', 'data flow'], 'dependency')}</select></label>`;
      body = labArchitecture('dependency');
    } else if (type === 'state') {
      title = labText('State transition', 'Peralihan keadaan');
      controls = `<label>${labText('Transition', 'Peralihan')}<select data-lab-control="state">${optionRows(['normal', 'self-transition'], 'normal')}</select></label>`;
      body = labState('normal');
    } else {
      title = labText('How to read this diagram', 'Cara membaca rajah ini');
      controls = `<div class="learning-step-controls"><button type="button" data-reader-step="0">1</button><button type="button" data-reader-step="1">2</button><button type="button" data-reader-step="2">3</button></div>`;
      body = labReader(0);
    }
    els.example.innerHTML = `<header><div><p class="eyebrow">${labText('Interactive lab', 'Makmal interaktif')}</p><h2 id="learning-example-title">${escapeHTML(title)}</h2></div>${icon('mouse-pointer-click')}</header><div class="learning-lab-controls">${controls}</div><div id="learning-lab-stage" class="learning-lab-stage">${body}</div><p id="learning-lab-explanation" class="learning-lab-explanation">${labExplanation(type)}</p>`;
    refreshIcons();
  }

  function labConnector(kind) {
    const dashed = ['dependency', 'realization', 'sequence-return', 'include', 'extend'].includes(kind);
    const diamond = kind === 'aggregation' ? '◇' : kind === 'composition' ? '◆' : '';
    const end = kind === 'generalization' || kind === 'realization' ? '△' : kind === 'crow-foot' ? '│&lt;' : kind === 'association' ? '' : '›';
    return `<div class="lab-line-demo"><span class="lab-node">A</span><span class="lab-connector${dashed ? ' is-dashed' : ''}"><b>${diamond}</b><i></i><b>${end}</b><em>${escapeHTML(kind)}</em></span><span class="lab-node">B</span></div>`;
  }
  function labSequence(kind) {
    if (kind === 'self-message') return `<div class="lab-sequence-demo"><span class="lab-lifeline"><b>Manager</b><i></i></span><span class="lab-self-arrow">applyFilters()</span></div>`;
    const dashed = kind === 'return message'; const open = dashed || kind === 'asynchronous message';
    return `<div class="lab-line-demo"><span class="lab-lifeline lab-lifeline--compact"><b>Caller</b><i></i></span><span class="lab-connector${dashed ? ' is-dashed' : ''}"><i></i><b>${open ? '›' : '▶'}</b><em>${escapeHTML(kind)}</em></span><span class="lab-lifeline lab-lifeline--compact"><b>Service</b><i></i></span></div>`;
  }
  function labFragment(kind, guard) { return `<div class="lab-fragment"><strong>${escapeHTML(kind)}</strong><span>[${escapeHTML(guard || 'condition')}]</span><div>message()</div>${['alt', 'par'].includes(kind) ? '<hr><span>[else]</span><div>otherMessage()</div>' : ''}</div>`; }
  function labMultiplicity(a, b, ownership) { const diamond = ownership === 'aggregation' ? '◇' : ownership === 'composition' ? '◆' : ''; return `<div class="lab-line-demo"><span class="lab-node">A<small>${escapeHTML(a)}</small></span><span class="lab-connector"><b>${diamond}</b><i></i><em>${escapeHTML(ownership)}</em></span><span class="lab-node">B<small>${escapeHTML(b)}</small></span></div>`; }
  function labActivity(kind) { return kind === 'fork' ? '<div class="lab-activity"><span class="lab-flow-in"></span><b class="lab-fork"></b><span class="lab-branch one"></span><span class="lab-branch two"></span><em>parallel</em></div>' : '<div class="lab-activity"><span class="lab-flow-in"></span><b class="lab-decision"></b><span class="lab-branch one"></span><span class="lab-branch two"></span><em>[yes] / [no]</em></div>'; }
  function labArchitecture(kind) { return labConnector(kind === 'ownership' ? 'composition' : kind === 'data flow' ? 'sequence-sync' : 'dependency'); }
  function labState(kind) { return kind === 'self-transition' ? '<div class="lab-state"><span>Searching</span><i class="lab-state-loop">retry</i></div>' : '<div class="lab-line-demo"><span class="lab-node">Ready</span><span class="lab-connector"><i></i><b>▶</b><em>save [valid] / persist()</em></span><span class="lab-node">Saved</span></div>'; }
  function labReader(step) { const labels = [labText('1. Identify the diagram family', '1. Kenal pasti keluarga rajah'), labText('2. Find the starting point', '2. Cari titik mula'), labText('3. Interpret line + arrowhead together', '3. Tafsir garisan + kepala bersama')]; return `<ol class="lab-reader">${labels.map((label, index) => `<li class="${index === step ? 'is-active' : ''}">${escapeHTML(label)}</li>`).join('')}</ol>`; }
  function labExplanation(type) {
    return escapeHTML(({ connector: labText('A line pattern is only half the notation; always inspect both endpoints.', 'Corak garisan hanya separuh notasi; sentiasa semak kedua-dua hujung.'), usecase: labText('include points to required shared behaviour; extend points back to the complete base use case.', 'include menunjuk kepada tingkah laku wajib; extend menunjuk kembali kepada kes guna asas.'), sequence: labText('Calls and returns differ by both line pattern and arrowhead.', 'Panggilan dan pulangan berbeza melalui corak garisan serta kepala anak panah.'), fragment: labText('The frame operator tells you how its guarded operands execute.', 'Operator bingkai menerangkan cara operand ber-guard dilaksanakan.'), multiplicity: labText('Read both endpoint labels as one relationship sentence.', 'Baca kedua-dua label hujung sebagai satu ayat hubungan.'), activity: labText('A decision selects one path; a fork starts concurrent paths.', 'Keputusan memilih satu laluan; fork memulakan laluan serentak.'), architecture: labText('Dependency, ownership and data movement make different claims.', 'Dependency, pemilikan dan pergerakan data membuat dakwaan berbeza.'), state: labText('A transition changes or re-enters state after a trigger.', 'Peralihan mengubah atau memasuki semula keadaan selepas pencetus.'), reader: labText('Start with the diagram family before interpreting individual symbols.', 'Mulakan dengan keluarga rajah sebelum mentafsir simbol individu.') })[type] || '');
  }

  function renderQuizPanel() {
    const questions = data.quizQuestions.filter((item) => item.chapterId === state.chapterId);
    const chapter = activeChapter(); const score = state.progress.scores[state.chapterId]; const attempts = state.progress.quizAttempts[state.chapterId] || 0;
    els.quiz.innerHTML = `<header><div><p class="eyebrow">${language() === 'en' ? 'Knowledge check' : 'Semakan pengetahuan'}</p><h2 id="learning-quiz-title">${escapeHTML(local(chapter.title))}</h2></div>${icon('badge-help')}</header><form id="learning-quiz-form">${questions.map((item, questionIndex) => `<fieldset><legend>${questionIndex + 1}. ${escapeHTML(local(item.prompt))}</legend>${item.choices.map((choice, choiceIndex) => `<label><input type="radio" name="${escapeAttr(item.id)}" value="${choiceIndex}"><span>${escapeHTML(local(choice))}</span></label>`).join('')}</fieldset>`).join('')}<button type="submit">${language() === 'en' ? 'Check answers' : 'Semak jawapan'}</button></form><div id="learning-quiz-feedback" class="learning-quiz-feedback" role="status">${state.quizFeedback || (attempts ? `${language() === 'en' ? 'Best score' : 'Skor terbaik'}: ${score || 0}/${questions.length} · ${language() === 'en' ? 'Attempts' : 'Percubaan'}: ${attempts}` : (language() === 'en' ? 'No attempts yet. You can retry without penalty.' : 'Belum ada percubaan. Anda boleh cuba semula tanpa penalti.'))}</div>`;
    refreshIcons();
  }

  function renderProgress() {
    const complete = state.progress.completedTopics.length; const total = data.topics.length; const percent = total ? (complete / total) * 100 : 0;
    els.progressBar.style.width = `${percent}%`; els.progressText.textContent = language() === 'en' ? `${complete} of ${total} topics` : `${complete} daripada ${total} topik`;
    els.progressLabel.textContent = language() === 'en' ? 'Progress' : 'Kemajuan'; els.reset.textContent = language() === 'en' ? 'Reset progress' : 'Set semula kemajuan';
  }

  function renderMobileLabels() {
    const labels = { lesson: language() === 'en' ? 'Learn' : 'Belajar', example: language() === 'en' ? 'Example' : 'Contoh', quiz: language() === 'en' ? 'Quiz' : 'Kuiz' };
    document.querySelectorAll('[data-learning-panel]').forEach((button) => { button.textContent = labels[button.dataset.learningPanel]; });
    els.back.querySelector('span').textContent = language() === 'en' ? 'Back to Explorer' : 'Kembali ke Explorer';
    els.navBack.setAttribute('aria-label', language() === 'en' ? 'Back to Explorer' : 'Kembali ke Explorer');
    els.search.placeholder = language() === 'en' ? 'Search notation...' : 'Cari notasi...';
    byId('learning-title').textContent = language() === 'en' ? 'Diagrams for Dummies' : 'Panduan Rajah untuk Pemula';
    els.link.querySelector('span').textContent = language() === 'en' ? 'For Dummies' : 'Panduan Pemula';
    const linkLabel = language() === 'en' ? 'Open Diagrams for Dummies' : 'Buka Panduan Rajah untuk Pemula';
    els.link.setAttribute('aria-label', linkLabel);
    els.link.title = linkLabel;
    if (els.mobileTopic) {
      els.mobileTopic.setAttribute('aria-label', language() === 'en' ? 'Choose lesson' : 'Pilih pelajaran');
      els.mobileTopic.innerHTML = data.chapters.map((chapter) => `<optgroup label="${escapeAttr(local(chapter.title))}">${chapter.topicIds.map((id) => {
        const topic = topicById(id); return topic ? `<option value="${escapeAttr(topic.id)}"${topic.id === state.topicId ? ' selected' : ''}>${escapeHTML(local(topic.title))}</option>` : '';
      }).join('')}</optgroup>`).join('');
    }
  }

  function renderLearning() {
    renderMobileLabels(); renderNavigation(); renderReader(); renderExamplePanel(); renderQuizPanel(); renderProgress(); updateMobilePanels(); refreshIcons();
  }

  function chooseTopic(id) {
    const topic = topicById(id); if (!topic) return;
    state.chapterId = topic.chapterId; state.topicId = topic.id; state.query = ''; els.search.value = ''; state.quizFeedback = null;
    setHash(topic.chapterId, topic.id); announce(`${local(topic.title)}. ${local(topic.purpose)}`);
  }

  function updateMobilePanels() {
    document.querySelectorAll('[data-learning-region]').forEach((region) => region.classList.toggle('learning-mobile-active', region.dataset.learningRegion === state.mobilePanel));
    document.querySelectorAll('[data-learning-panel]').forEach((button) => { const active = button.dataset.learningPanel === state.mobilePanel; button.classList.toggle('is-active', active); button.setAttribute('aria-selected', String(active)); });
  }

  function updateLab() {
    const stage = byId('learning-lab-stage'); if (!stage) return;
    const type = labType();
    if (type === 'connector') stage.innerHTML = labConnector(document.querySelector('[data-lab-control="connector"]')?.value || 'association');
    else if (type === 'usecase') stage.innerHTML = labConnector(document.querySelector('[data-lab-control="usecase"]')?.value || 'include');
    else if (type === 'sequence') stage.innerHTML = labSequence(document.querySelector('[data-lab-control="sequence"]')?.value || 'synchronous call');
    else if (type === 'fragment') stage.innerHTML = labFragment(document.querySelector('[data-lab-control="fragment"]')?.value || 'alt', document.querySelector('[data-lab-guard]')?.value || 'condition');
    else if (type === 'multiplicity') stage.innerHTML = labMultiplicity(document.querySelector('[data-lab-control="multiplicity-a"]')?.value || '1', document.querySelector('[data-lab-control="multiplicity-b"]')?.value || '0..*', document.querySelector('[data-lab-control="ownership"]')?.value || 'association');
    else if (type === 'activity') stage.innerHTML = labActivity(document.querySelector('[data-lab-control="activity"]')?.value || 'decision');
    else if (type === 'architecture') stage.innerHTML = labArchitecture(document.querySelector('[data-lab-control="architecture"]')?.value || 'dependency');
    else if (type === 'state') stage.innerHTML = labState(document.querySelector('[data-lab-control="state"]')?.value || 'normal');
  }

  els.link.addEventListener('click', () => { if (!location.hash.startsWith('#learn')) state.previousExplorerHash = location.hash && !location.hash.startsWith('#learn') ? location.hash : '#explorer'; });
  [els.back, els.navBack].forEach((button) => button.addEventListener('click', () => { location.hash = state.previousExplorerHash || '#explorer'; }));
  els.search.addEventListener('input', () => { state.query = els.search.value; renderNavigation(); });
  els.nav.addEventListener('click', (event) => {
    const topicButtonElement = event.target.closest('[data-learning-topic]'); if (topicButtonElement) { chooseTopic(topicButtonElement.dataset.learningTopic); return; }
    const chapterButton = event.target.closest('[data-learning-chapter]'); if (!chapterButton) return;
    const chapter = chapterById(chapterButton.dataset.learningChapter); if (chapter) chooseTopic(chapter.topicIds[0]);
  });
  els.reader.addEventListener('click', (event) => {
    const topicButtonElement = event.target.closest('[data-learning-topic]'); if (topicButtonElement) { chooseTopic(topicButtonElement.dataset.learningTopic); return; }
    const complete = event.target.closest('#learning-complete');
    if (complete) {
      const id = state.topicId; const existing = state.progress.completedTopics.indexOf(id);
      if (existing >= 0) state.progress.completedTopics.splice(existing, 1); else state.progress.completedTopics.push(id);
      storeProgress(); renderLearning(); return;
    }
    const example = event.target.closest('[data-explorer-diagram]');
    if (example) {
      window.dispatchEvent(new CustomEvent('petakerja:open-example', { detail: { diagramId: example.dataset.explorerDiagram, componentKey: example.dataset.explorerComponent || null, connectionId: example.dataset.explorerConnection || null } }));
      location.hash = '#explorer';
    }
  });
  els.shell.addEventListener('click', (event) => {
    const partElement = event.target.closest('[data-learning-part]'); if (!partElement) return;
    document.querySelectorAll('[data-learning-part]').forEach((item) => item.classList.toggle('is-active', item === partElement));
    announce(partElement.dataset.learningPart);
  });
  els.shell.addEventListener('focusin', (event) => {
    const partElement = event.target.closest('[data-learning-part]'); if (partElement) announce(partElement.dataset.learningPart);
  });
  document.addEventListener('keydown', (event) => {
    if (!document.body.classList.contains('is-learning-mode')) return;
    const partElement = event.target.closest?.('[data-learning-part]');
    if (partElement && (event.key === 'Enter' || event.key === ' ')) {
      event.preventDefault(); document.querySelectorAll('[data-learning-part]').forEach((item) => item.classList.toggle('is-active', item === partElement)); announce(partElement.dataset.learningPart); return;
    }
    if (event.key === '/' && !/INPUT|TEXTAREA|SELECT/.test(document.activeElement.tagName)) { event.preventDefault(); els.search.focus(); }
  });
  els.example.addEventListener('input', (event) => { if (event.target.matches('[data-lab-control], [data-lab-guard]')) updateLab(); });
  els.example.addEventListener('change', (event) => { if (event.target.matches('[data-lab-control]')) updateLab(); });
  els.example.addEventListener('click', (event) => { const step = event.target.closest('[data-reader-step]'); if (step) byId('learning-lab-stage').innerHTML = labReader(Number(step.dataset.readerStep)); });
  els.quiz.addEventListener('submit', (event) => {
    if (event.target.id !== 'learning-quiz-form') return; event.preventDefault();
    const questions = data.quizQuestions.filter((item) => item.chapterId === state.chapterId); const form = new FormData(event.target); let correct = 0;
    const explanations = questions.map((item, index) => {
      const selected = Number(form.get(item.id)); const isCorrect = selected === item.answer; if (isCorrect) correct += 1;
      return `<li class="${isCorrect ? 'is-correct' : 'is-wrong'}"><strong>${index + 1}. ${isCorrect ? (language() === 'en' ? 'Correct' : 'Betul') : (language() === 'en' ? 'Review' : 'Semak')}</strong><span>${escapeHTML(local(item.explanation))}</span></li>`;
    }).join('');
    state.progress.quizAttempts[state.chapterId] = (state.progress.quizAttempts[state.chapterId] || 0) + 1;
    state.progress.scores[state.chapterId] = Math.max(state.progress.scores[state.chapterId] || 0, correct);
    state.quizFeedback = `<strong>${language() === 'en' ? 'Score' : 'Skor'}: ${correct}/${questions.length}</strong><ol>${explanations}</ol>`;
    storeProgress(); renderQuizPanel(); renderProgress(); announce(`${language() === 'en' ? 'Quiz score' : 'Skor kuiz'} ${correct} ${language() === 'en' ? 'out of' : 'daripada'} ${questions.length}`);
  });
  els.reset.addEventListener('click', () => {
    const okay = window.confirm(language() === 'en' ? 'Reset all learning progress and quiz scores?' : 'Set semula semua kemajuan pembelajaran dan skor kuiz?');
    if (!okay) return; state.progress = { completedTopics: [], quizAttempts: {}, scores: {} }; state.quizFeedback = null; storeProgress(); renderLearning();
  });
  document.querySelectorAll('[data-learning-panel]').forEach((button) => button.addEventListener('click', () => { state.mobilePanel = button.dataset.learningPanel; updateMobilePanels(); }));
  els.mobileTopic?.addEventListener('change', () => chooseTopic(els.mobileTopic.value));
  window.addEventListener('hashchange', syncRoute);
  new MutationObserver((mutations) => {
    if (!mutations.some((mutation) => mutation.attributeName === 'lang' || mutation.attributeName === 'data-theme')) return;
    renderMobileLabels(); if (!els.shell.hidden) renderLearning();
  }).observe(document.documentElement, { attributes: true, attributeFilter: ['lang', 'data-theme'] });

  loadProgress(); renderMobileLabels(); syncRoute();
  window.PETAKERJA_LEARNING_TEST = { state, parseRoute, chooseTopic, renderLearning, labConnector, labFragment };
}());
