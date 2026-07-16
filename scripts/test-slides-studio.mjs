import assert from 'node:assert/strict';
import { readFile } from 'node:fs/promises';
import vm from 'node:vm';

const root = new URL('..', import.meta.url);
const dataSource = await readFile(new URL('../slides-data.js', import.meta.url), 'utf8');
const context = { window: {} };
vm.runInNewContext(dataSource, context, { filename: 'slides-data.js' });

const config = context.window.PETAKERJA_SLIDES;
assert.equal(config.schemaVersion, 1);
assert.equal(config.defaultLanguage, 'ms');
assert.equal(config.aspectRatio, '16:9');
assert.equal(config.presets[0].slides.length, 12);
assert.equal(config.presets[0].slides.reduce((sum, slide) => sum + slide.durationSeconds, 0), 555);
assert.deepEqual(
  [...config.requiredSections].sort(),
  ['problem', 'methodology', 'solution', 'features', 'demo', 'testing', 'value', 'conclusion'].sort(),
);

const [html, script, css] = await Promise.all([
  readFile(new URL('../index.html', import.meta.url), 'utf8'),
  readFile(new URL('../slides.js', import.meta.url), 'utf8'),
  readFile(new URL('../slides.css', import.meta.url), 'utf8'),
]);

for (const marker of ['id="slides-link"', 'id="slides-shell"', 'id="slides-save-copy"', 'id="slides-library"', 'id="slides-history"', 'id="slides-create-version"', 'id="slides-new-branch"', 'vendor/fabric/fabric.min.js', 'vendor/pptxgenjs/pptxgen.bundle.js']) {
  assert.match(html, new RegExp(marker.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')));
}
for (const marker of ['PETAKERJA_DIAGRAM_ASSETS', 'Fabric.FabricObject.customProperties', 'workspace/presentations', 'architecture-explorer/presentations', 'addNotes', 'IndexedDB', 'syncCloudAssets', 'saveAsCopy', 'handleSlidesStageWheel', 'normalizeSlideWheelDelta', 'SLIDE_WHEEL_THRESHOLD', 'syncActiveThumbnail', 'scrollIntoView', 'loadPresentationLibrary', 'loadBranchesAndVersions', 'syncHistoryAvailability', 'createVersion', 'createBranch', '/restore', 'save local work as a new branch', 'branchHeadHash']) {
  assert.ok(script.toLowerCase().includes(marker.toLowerCase()), `slides.js must include ${marker}`);
}
assert.match(script, /\.slides-stage'\)\.addEventListener\('wheel',\s*handleSlidesStageWheel,\s*\{\s*passive:\s*false\s*\}\)/);
assert.match(script, /Math\.max\(0,\s*Math\.min\(state\.deck\.slides\.length\s*-\s*1,\s*currentIndex\s*\+\s*direction\)\)/);
assert.match(script, /#slides-canvas-wrap, \.slides-zoom/);
assert.doesNotMatch(css, /linear-gradient|radial-gradient|conic-gradient/i);
assert.doesNotMatch(css, /::before[^}]*height:\s*[1-9]px[^}]*background:/is);

process.stdout.write(`${JSON.stringify({ passed: true, presetSlides: 12, targetSeconds: 555 })}\n`);
