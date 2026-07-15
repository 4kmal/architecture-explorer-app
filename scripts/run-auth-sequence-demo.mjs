import { existsSync, mkdirSync, readFileSync, writeFileSync } from 'node:fs';
import { dirname, join, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';
import authSequencePlan from './auth-sequence-plan.mjs';

const root = resolve(dirname(fileURLToPath(import.meta.url)), '..');
const runtimePath = join(root, '.runtime', 'host.json');
if (!existsSync(runtimePath)) throw new Error('Start the Explorer host before running the visible Agent demo.');
const runtime = JSON.parse(readFileSync(runtimePath, 'utf8'));
if (!runtime.port || !runtime.token) throw new Error('Explorer runtime metadata is incomplete.');
const baseURL = `http://127.0.0.1:${runtime.port}`;

async function invoke(tool, argumentsValue = {}, timeout = 240000) {
  const response = await fetch(`${baseURL}/api/mcp/command`, {
    method: 'POST',
    headers: { Authorization: `Bearer ${runtime.token}`, 'Content-Type': 'application/json' },
    body: JSON.stringify({ tool, arguments: argumentsValue }),
  });
  if (!response.ok) throw new Error(`Bridge rejected ${tool} (${response.status}).`);
  const command = await response.json();
  const deadline = Date.now() + timeout;
  while (Date.now() < deadline) {
    await new Promise((resolveWait) => setTimeout(resolveWait, 300));
    const resultResponse = await fetch(`${baseURL}/api/mcp/result/${encodeURIComponent(command.id)}`, { headers: { Authorization: `Bearer ${runtime.token}` } });
    if (resultResponse.status === 202) continue;
    const result = await resultResponse.json();
    if (!resultResponse.ok || !result.ok) throw new Error(result.error || `${tool} failed.`);
    return result.result;
  }
  throw new Error(`${tool} timed out. Keep Agent Mode visible in the Explorer browser tab.`);
}

const session = await invoke('start_new_diagram_session', {
  name: authSequencePlan.title,
  diagramType: 'auth-sequence',
  pageId: 'petakerja_auth_sequence',
  filename: 'Sequence Diagram - PetaKerja User Login Logout.drawio',
});
await invoke('propose_diagram_plan', { plan: authSequencePlan });
const run = await invoke('apply_diagram_operations', { plan: authSequencePlan });
const validation = await invoke('validate_active_diagram');
const exported = await invoke('export_active_diagram');

const outputDirectory = resolve(root, '..');
const baseName = 'Sequence Diagram - PetaKerja User Login Logout';
const drawioPath = join(outputDirectory, `${baseName}.drawio`);
const svgPath = join(outputDirectory, `${baseName}.svg`);
const editorAssetPath = join(root, 'assets', 'editor', 'auth-sequence.drawio');
const svgAssetPath = join(root, 'assets', 'diagrams', 'auth-sequence.svg');
const inlineAssetPath = join(root, 'auth-sequence-svg.js');
mkdirSync(dirname(editorAssetPath), { recursive: true });
mkdirSync(dirname(svgAssetPath), { recursive: true });
writeFileSync(drawioPath, exported.xml, 'utf8');
writeFileSync(svgPath, exported.svg, 'utf8');
writeFileSync(editorAssetPath, exported.xml, 'utf8');
writeFileSync(svgAssetPath, exported.svg, 'utf8');
writeFileSync(inlineAssetPath, `window.PETAKERJA_AUTH_SEQUENCE_SVG = ${JSON.stringify(exported.svg)};\n`, 'utf8');

process.stdout.write(`${JSON.stringify({ session, run, validation, outputs: { drawioPath, svgPath, editorAssetPath, svgAssetPath, inlineAssetPath } }, null, 2)}\n`);
