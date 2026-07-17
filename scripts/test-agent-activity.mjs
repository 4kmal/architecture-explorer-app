import { readFileSync } from 'node:fs';
import { dirname, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

const root = resolve(dirname(fileURLToPath(import.meta.url)), '..');
const read = (name) => readFileSync(resolve(root, name), 'utf8');
const html = read('index.html');
const css = `${read('styles.css')}\n${read('enterprise.css')}`;
const app = read('app.js');

const checks = {
  singleOverlay: (html.match(/id="agent-canvas-activity"/g) || []).length === 1,
  accessibleState: /id="agent-state"[^>]*role="status"[^>]*aria-live="polite"/.test(html),
  pointerTransparent: /\.agent-canvas-activity\s*\{[^}]*pointer-events:\s*none/s.test(css),
  runningState: /data-agent-state="running"/.test(css),
  stoppingState: /data-agent-state="stopping"/.test(css),
  solidOutline: /\.agent-canvas-activity\s*\{[^}]*border:\s*2px solid transparent/s.test(css)
    && /data-agent-state="running"[^}]*\{[^}]*border-color:\s*var\(--focus\)/s.test(css),
  noActivityAnimation: !/agent-canvas-(?:pulse|glow)/.test(css)
    && !/\.agent-canvas-activity\s*\{[^}]*box-shadow/s.test(css),
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
