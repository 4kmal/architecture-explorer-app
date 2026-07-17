import assert from 'node:assert/strict';
import { readFile } from 'node:fs/promises';

const root = new URL('../', import.meta.url);
const [html, baseCSS, enterpriseCSS, slidesCSS, appJS] = await Promise.all([
  readFile(new URL('index.html', root), 'utf8'),
  readFile(new URL('styles.css', root), 'utf8'),
  readFile(new URL('enterprise.css', root), 'utf8'),
  readFile(new URL('slides.css', root), 'utf8'),
  readFile(new URL('app.js', root), 'utf8'),
]);
const css = `${baseCSS}\n${enterpriseCSS}`;

for (const marker of [
  'class="header-primary-controls"',
  'class="header-context-controls"',
  'class="header-choice-control language-control"',
  'id="language-select"',
  'id="language-value"',
  'data-bp-icon="languages"',
  'data-theme-icon="system"',
  'data-theme-icon="light"',
  'data-theme-icon="dark"',
  'id="learning-link" class="header-learning-link"',
  'id="slides-link" class="header-learning-link"',
  'class="compact-field scope-field"',
]) assert.ok(html.includes(marker), `responsive header marker missing: ${marker}`);

for (const marker of [
  '--app-header-height: 50px',
  '--app-mobile-tabs-height: 0px',
  '@media (max-width: 1199px)',
  '@media (max-width: 900px)',
  '@media (max-width: 767px)',
  '@media (max-width: 480px)',
  'grid-template-areas: "brand primary" "context context"',
  '"brand learn slides language"',
  '"diagram diagram search search"',
  'height: calc(100dvh - var(--app-header-height) - var(--app-mobile-tabs-height))',
  'container: diagram-workspace / inline-size',
  '@container diagram-workspace (max-width: 1100px)',
  '@container diagram-workspace (max-width: 900px)',
  'grid-template-columns: minmax(0, 1fr) auto',
  'flex-wrap: wrap',
  'overflow-x: auto',
  '.header-learning-link { display: inline-grid;',
  '.header-choice-control {',
  '.header-choice-value {',
  'html[data-theme-preference="system"] .header-choice-icons',
  '.brand-block { min-width: 0; max-width: none; }',
]) assert.ok(css.includes(marker), `responsive CSS contract missing: ${marker}`);

assert.ok(slidesCSS.includes('inset: var(--app-header-height) 0 0'), 'Slides Studio must follow the shared header height');
assert.ok(!css.includes('calc(100dvh - 54px)'), 'Explorer must not use the old fixed desktop header offset');
assert.ok(!slidesCSS.includes('inset: 54px 0 0'), 'Slides Studio must not use the old fixed header offset');
assert.ok(!css.includes('.status-chip, #open-reference { display: none; }'), 'the workspace status must remain visible at narrow widths');
assert.ok(appJS.includes('function syncSelectTitle(select)'), 'select tooltip synchronizer is missing');
assert.ok(appJS.includes('syncSelectTitle(els.diagramPicker)') && appJS.includes('syncSelectTitle(els.scope)'), 'responsive select tooltips are not synchronized');
assert.ok(appJS.includes('function syncHeaderChoiceControls()'), 'compact theme/language control synchronizer is missing');
assert.ok(appJS.includes('function applyLanguagePreference(language)'), 'shared language setter is missing');
assert.ok(appJS.includes("els.languageSelect.addEventListener('change'"), 'native language selector listener is missing');
assert.ok(appJS.includes("state.themePreference === 'system'"), 'dynamic System theme tooltip contract is missing');
assert.ok(!appJS.includes("document.querySelectorAll('[data-language]')"), 'legacy BM/EN segmented-button wiring must be removed');

console.log('Responsive Architecture Explorer header contract: OK');
