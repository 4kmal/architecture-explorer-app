import { mkdtemp, readFile, rm, writeFile } from 'node:fs/promises';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import { spawn } from 'node:child_process';

const source = 'C:\\Users\\iamal\\Desktop\\Semester 8\\codex\\Sequence Diagram - PetaKerja User Login Logout.svg';
const output = 'C:\\Users\\iamal\\Desktop\\Semester 8\\codex\\Sequence Diagram - PetaKerja User Login Logout.png';
const edge = 'C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe';
const folder = await mkdtemp(join(tmpdir(), 'petakerja-sequence-'));
const htmlPath = join(folder, 'render.html');

try {
  let svg = await readFile(source, 'utf8');
  const viewBox = svg.match(/viewBox="0 0 ([\d.]+) ([\d.]+)"/);
  if (!viewBox) throw new Error('The generated SVG has no usable viewBox.');
  const width = Math.ceil(Number(viewBox[1]));
  const height = Math.ceil(Number(viewBox[2]));
  svg = svg
    .replace('color-scheme: light dark;', 'color-scheme: only light;')
    .replace(/<defs\s*\/>/, '<defs/><rect x="0" y="0" width="100%" height="100%" fill="#ffffff"/>');
  await writeFile(htmlPath, `<!doctype html><html style="color-scheme:only light"><head><meta charset="utf-8"><style>html,body{margin:0;width:${width}px;height:${height}px;overflow:hidden;background:#fff}svg{display:block}</style></head><body>${svg}</body></html>`, 'utf8');

  await new Promise((resolve, reject) => {
    const child = spawn(edge, [
      '--headless=new', '--hide-scrollbars', '--disable-gpu',
      `--user-data-dir=${join(folder, 'profile')}`,
      `--window-size=${width},${height}`,
      `--screenshot=${output}`,
      new URL(`file:///${htmlPath.replace(/\\/g, '/')}`).href,
    ], { stdio: ['ignore', 'pipe', 'pipe'] });
    let stderr = '';
    child.stderr.on('data', (chunk) => { stderr += String(chunk); });
    child.once('error', reject);
    child.once('exit', (code) => code === 0 ? resolve() : reject(new Error(stderr || `Edge exited with ${code}.`)));
  });
  console.log(JSON.stringify({ output, width, height }, null, 2));
} finally {
  await rm(folder, { recursive: true, force: true });
}
