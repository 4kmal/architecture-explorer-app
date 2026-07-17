import assert from 'node:assert/strict';
import { readFile } from 'node:fs/promises';

const root = new URL('../', import.meta.url);
const files = await Promise.all([
  'index.html', 'styles.css', 'slides.css', 'enterprise.css', 'app.js', 'learning.js', 'slides.js',
  'vendor/blueprint-icons/blueprint-icons.js', 'THIRD_PARTY_NOTICES.md',
].map((name) => readFile(new URL(name, root), 'utf8')));
const [html, styles, slides, enterprise, app, learning, slidesJS, icons, notices] = files;
const nativeCSS = `${styles}\n${slides}\n${enterprise}`;
const nativeJS = `${app}\n${learning}\n${slidesJS}`;

for (const token of [
  '--bp-grid: 4px',
  '--bp-control-height: 30px',
  '--bp-compact-height: 24px',
  '--app-header-height: 50px',
  '--canvas: #f6f7f9',
  '--surface: #ffffff',
  '--line: #d3d8de',
  '--text: #1c2127',
  '--selected: #2d72d2',
  '--canvas: #111418',
  '--surface: #1c2127',
  '--surface-subtle: #252a31',
  '--line: #404854',
  '--text: #f6f7f9',
]) assert.ok(enterprise.includes(token), `Blueprint token missing: ${token}`);

for (const marker of [
  'data-bp-icon="book-open"',
  'data-bp-icon="presentation"',
  'vendor/blueprint-icons/blueprint-icons.js',
  'window.renderBlueprintIcons = renderBlueprintIcons',
  'window.renderBlueprintIcons?.(document)',
  'window.renderBlueprintIcons?.(els.diagramNav)',
  'licenses/BLUEPRINT_LICENSE.txt',
]) assert.ok(`${html}\n${icons}\n${nativeJS}\n${notices}`.includes(marker), `Blueprint integration marker missing: ${marker}`);

assert.doesNotMatch(`${html}\n${nativeJS}\n${notices}`, /data-lucide|window\.lucide|vendor\/lucide|Lucide icon library/i);
assert.doesNotMatch(nativeCSS, /(?:linear|radial|conic)-gradient\s*\(|drop-shadow\s*\(|agent-glow|agent-canvas-pulse/i);
assert.ok(enterprise.includes('border-radius: 0;'), 'sharp surface radius contract is missing');
assert.ok(enterprise.includes('border-radius: 2px;'), '2px control radius contract is missing');
assert.ok(enterprise.includes('.navigation-panel, .workspace-panel, .ui-panel, .details-panel,'), 'primary surface sharpness contract is missing');
assert.ok(enterprise.includes('.agent-canvas-activity') && enterprise.includes('border-radius: 0;'), 'Agent activity outline must use sharp geometry');

const requestedIcons = new Set();
for (const source of [html, app, learning, slidesJS]) {
  for (const match of source.matchAll(/data-bp-icon=["']([^"'${}]+)["']/g)) requestedIcons.add(match[1]);
}
for (const name of requestedIcons) {
  assert.ok(icons.includes(`"${name}": {`), `Blueprint icon alias missing: ${name}`);
}
for (const dynamicName of ['history']) {
  assert.ok(icons.includes(`"${dynamicName}": {`), `Dynamic Blueprint icon alias missing: ${dynamicName}`);
}

console.log(`Blueprint enterprise design system: OK (${requestedIcons.size} static icon aliases checked)`);
