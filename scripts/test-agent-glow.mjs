import { readFileSync } from 'node:fs';
import { dirname, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

const root = resolve(dirname(fileURLToPath(import.meta.url)), '..');
const read = (name) => readFileSync(resolve(root, name), 'utf8');
const html = read('index.html');
const css = read('styles.css');
const app = read('app.js');

const checks = {
  singleOverlay: (html.match(/id="agent-canvas-activity"/g) || []).length === 1,
  accessibleState: /id="agent-state"[^>]*role="status"[^>]*aria-live="polite"/.test(html),
  pointerTransparent: /\.agent-canvas-activity\s*\{[^}]*pointer-events:\s*none/s.test(css),
  runningState: /data-agent-state="running"/.test(css),
  stoppingState: /data-agent-state="stopping"/.test(css),
  reducedMotion: /@media\s*\(prefers-reduced-motion:\s*reduce\)[\s\S]*animation:\s*none\s*!important/.test(css),
  noGradients: !/(?:linear|radial|conic)-gradient\s*\(/.test(css),
  lifecycleSync: /editorSurface\.dataset\.agentState\s*=\s*value/.test(app),
  ariaBusy: /editorSurface\.setAttribute\('aria-busy',\s*String\(value === 'running' \|\| value === 'stopping'\)\)/.test(app),
  deferredThemeReload: /diagramAgent\?\.running[\s\S]*pendingEditorThemePreference/.test(app)
    && /onRunEnd\(event\)[\s\S]*syncEditorThemePreference\(nextPreference\)/.test(app),
};

const failures = Object.entries(checks).filter(([, passed]) => !passed).map(([name]) => name);
if (failures.length) {
  process.stderr.write(`${JSON.stringify({ passed: false, failures, checks }, null, 2)}\n`);
  process.exit(1);
}

process.stdout.write(`${JSON.stringify({ passed: true, checks }, null, 2)}\n`);
