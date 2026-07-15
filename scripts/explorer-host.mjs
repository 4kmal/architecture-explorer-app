import { createServer } from 'node:http';
import { copyFileSync, createReadStream, existsSync, mkdirSync, readFileSync, renameSync, statSync, writeFileSync } from 'node:fs';
import { extname, isAbsolute, join, normalize, relative, resolve, sep } from 'node:path';
import { createHash, randomBytes, randomUUID } from 'node:crypto';

await import('../openai-model-policy.js');

const root = resolve(import.meta.dirname, '..');
const runtimeDirectory = join(root, '.runtime');
const runtimeFile = process.env.PETAKERJA_EXPLORER_RUNTIME_FILE || join(runtimeDirectory, 'host.json');
const token = randomBytes(24).toString('hex');
const commands = [];
const results = new Map();
let sequence = 0;
let mcpLastSeen = 0;
const openAIBaseURL = String(process.env.PETAKERJA_OPENAI_BASE_URL || 'https://api.openai.com/v1').replace(/\/+$/, '');
const openAIPolicy = globalThis.PETAKERJA_OPENAI_POLICY;
const workspaceManifest = JSON.parse(readFileSync(join(root, 'workspace-manifest.json'), 'utf8'));
const allowedOrigins = new Set(String(process.env.PETAKERJA_EXPLORER_ALLOWED_ORIGINS || 'http://127.0.0.1:3000,http://localhost:3000')
  .split(',').map((entry) => entry.trim()).filter(Boolean));
const deniedStaticSegments = new Set(['.git', '.runtime', 'bridge', 'node_modules', 'scripts']);

const contentTypes = {
  '.html': 'text/html; charset=utf-8', '.js': 'text/javascript; charset=utf-8', '.css': 'text/css; charset=utf-8',
  '.json': 'application/json; charset=utf-8', '.svg': 'image/svg+xml', '.png': 'image/png', '.jpg': 'image/jpeg',
  '.drawio': 'application/xml; charset=utf-8', '.xml': 'application/xml; charset=utf-8', '.woff2': 'font/woff2',
};

function json(response, status, value) {
  const body = JSON.stringify(value);
  response.writeHead(status, { 'Content-Type': 'application/json; charset=utf-8', 'Content-Length': Buffer.byteLength(body), 'Cache-Control': 'no-store' });
  response.end(body);
}

async function readJSON(request) {
  const chunks = [];
  let size = 0;
  for await (const chunk of request) {
    size += chunk.length;
    if (size > 25 * 1024 * 1024) throw new Error('Request body exceeds the 25 MB limit.');
    chunks.push(chunk);
  }
  return chunks.length ? JSON.parse(Buffer.concat(chunks).toString('utf8')) : {};
}

function authorized(request) { return request.headers.authorization === `Bearer ${token}`; }

function sameOrigin(request, port) {
  const origin = request.headers.origin;
  return !origin || origin === `http://127.0.0.1:${port}` || origin === `http://localhost:${port}` || allowedOrigins.has(origin);
}

function workspaceAuthorized(request) {
  return request.headers['x-petakerja-workspace-token'] === token;
}

function sha256(xml, svg) {
  return createHash('sha256').update(xml).update('\0').update(svg).digest('hex');
}

function safeWorkspacePath(entry, field) {
  const path = resolve(root, entry[field]);
  const location = relative(root, path);
  if (!location || location.startsWith(`..${sep}`) || location === '..' || isAbsolute(location)) {
    throw new Error(`Unsafe workspace ${field} path.`);
  }
  return path;
}

function diagramPattern(pageId) {
  const escaped = String(pageId).replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
  return new RegExp(`<diagram\\b(?=[^>]*\\bid=["']${escaped}["'])[^>]*>[\\s\\S]*?<\\/diagram>`, 'i');
}

function extractWorkspacePage(xml, entry) {
  if (!entry.sharedSource) return xml;
  const match = xml.match(diagramPattern(entry.pageId));
  if (!match) throw new Error(`Page ${entry.pageId} was not found in the shared Draw.io source.`);
  const mxfile = xml.match(/<mxfile\b([^>]*)>/i);
  return `<mxfile${mxfile?.[1] || ''}>${match[0]}</mxfile>`;
}

function mergeWorkspacePage(currentXml, incomingXml, entry) {
  if (!entry.sharedSource) return incomingXml;
  const incoming = incomingXml.match(diagramPattern(entry.pageId));
  if (!incoming) throw new Error(`Saved XML does not contain page ${entry.pageId}.`);
  const pattern = diagramPattern(entry.pageId);
  if (!pattern.test(currentXml)) throw new Error(`Canonical source does not contain page ${entry.pageId}.`);
  return currentXml.replace(pattern, incoming[0]);
}

function workspaceDocument(diagramId) {
  const entry = workspaceManifest.diagrams?.[diagramId];
  if (!entry) return null;
  const xmlPath = safeWorkspacePath(entry, 'xml');
  const svgPath = safeWorkspacePath(entry, 'svg');
  if (!existsSync(xmlPath) || !existsSync(svgPath)) throw new Error(`Workspace files for ${diagramId} are unavailable.`);
  const fullXml = readFileSync(xmlPath, 'utf8');
  const xml = extractWorkspacePage(fullXml, entry);
  const svg = readFileSync(svgPath, 'utf8');
  const modifiedAt = new Date(Math.max(statSync(xmlPath).mtimeMs, statSync(svgPath).mtimeMs)).toISOString();
  return { entry, xmlPath, svgPath, xml, svg, revision: sha256(xml, svg), modifiedAt };
}

function atomicWrite(path, value) {
  const temporary = `${path}.${process.pid}.${randomUUID()}.tmp`;
  writeFileSync(temporary, value, 'utf8');
  renameSync(temporary, path);
}

function backupWorkspaceDocument(diagramId, document) {
  const stamp = new Date().toISOString().replace(/[:.]/g, '-');
  const directory = join(runtimeDirectory, 'backups', diagramId);
  mkdirSync(directory, { recursive: true });
  copyFileSync(document.xmlPath, join(directory, `${stamp}.drawio`));
  copyFileSync(document.svgPath, join(directory, `${stamp}.svg`));
}

function staticPathAllowed(path) {
  const location = relative(root, path);
  if (!location || location.startsWith(`..${sep}`) || location === '..' || isAbsolute(location)) return false;
  const segments = location.split(/[\\/]+/).map((segment) => segment.toLocaleLowerCase());
  return !segments.some((segment) => deniedStaticSegments.has(segment) || segment.startsWith('.env'));
}

async function forwardOpenAI(response, path, apiKey, body, timeout = 120000) {
  if (!apiKey || typeof apiKey !== 'string') { json(response, 400, { error: { message: 'An in-memory OpenAI API key is required.' } }); return; }
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), timeout);
  try {
    const upstream = await fetch(`${openAIBaseURL}${path}`, {
      method: body == null ? 'GET' : 'POST',
      headers: { Authorization: `Bearer ${apiKey}`, ...(body == null ? {} : { 'Content-Type': 'application/json' }) },
      body: body == null ? undefined : JSON.stringify(body),
      signal: controller.signal,
    });
    const raw = await upstream.text();
    let payload;
    try { payload = raw ? JSON.parse(raw) : {}; } catch (_error) { payload = { error: { message: raw || upstream.statusText } }; }
    json(response, upstream.status, payload);
  } catch (error) {
    const message = error.name === 'AbortError' ? 'The OpenAI request timed out.' : 'The OpenAI upstream request failed.';
    json(response, 502, { error: { message } });
  } finally {
    clearTimeout(timer);
  }
}

function configSnippet(port) {
  const serverPath = join(root, 'bridge', 'mcp-server.mjs');
  return JSON.stringify({ mcpServers: { 'petakerja-explorer': { command: 'node', args: [serverPath], env: { PETAKERJA_EXPLORER_RUNTIME: runtimeFile } } } }, null, 2);
}

function createRequestHandler(port) {
  return async (request, response) => {
    try {
      const url = new URL(request.url, `http://127.0.0.1:${port}`);
      if (url.pathname === '/api/bridge/status' && request.method === 'GET') {
        json(response, 200, { port, sequence, mcpConnected: Date.now() - mcpLastSeen < 5000, configSnippet: configSnippet(port), workspace: { writable: true, diagrams: Object.keys(workspaceManifest.diagrams || {}).length } });
        return;
      }
      if (url.pathname === '/api/workspace/session' && request.method === 'GET') {
        if (!sameOrigin(request, port)) { json(response, 403, { error: { message: 'Origin rejected.' } }); return; }
        json(response, 200, { token, diagrams: Object.keys(workspaceManifest.diagrams || {}) });
        return;
      }
      if (url.pathname.startsWith('/api/workspace/diagrams/') && request.method === 'GET') {
        if (!sameOrigin(request, port)) { json(response, 403, { error: { message: 'Origin rejected.' } }); return; }
        const diagramId = decodeURIComponent(url.pathname.slice('/api/workspace/diagrams/'.length));
        const document = workspaceDocument(diagramId);
        if (!document) { json(response, 404, { error: { message: 'Diagram is not registered for workspace persistence.' } }); return; }
        json(response, 200, { diagramId, xml: document.xml, svg: document.svg, revision: document.revision, modifiedAt: document.modifiedAt });
        return;
      }
      if (url.pathname.startsWith('/api/workspace/diagrams/') && request.method === 'PUT') {
        if (!sameOrigin(request, port)) { json(response, 403, { error: { message: 'Origin rejected.' } }); return; }
        if (!workspaceAuthorized(request)) { json(response, 401, { error: { message: 'Workspace token rejected.' } }); return; }
        const diagramId = decodeURIComponent(url.pathname.slice('/api/workspace/diagrams/'.length));
        const current = workspaceDocument(diagramId);
        if (!current) { json(response, 404, { error: { message: 'Diagram is not registered for workspace persistence.' } }); return; }
        const body = await readJSON(request);
        if (body.revision !== current.revision) {
          json(response, 409, { error: { message: 'A newer workspace revision exists. Reload before saving.' }, revision: current.revision, modifiedAt: current.modifiedAt });
          return;
        }
        const xml = String(body.xml || '');
        const svg = String(body.svg || '');
        if (!xml.includes('<mxfile') || !svg.includes('<svg')) { json(response, 400, { error: { message: 'Valid Draw.io XML and SVG are required.' } }); return; }
        if (Buffer.byteLength(xml) > 20 * 1024 * 1024 || Buffer.byteLength(svg) > 20 * 1024 * 1024) {
          json(response, 413, { error: { message: 'Workspace diagram exceeds the 20 MB per-file limit.' } }); return;
        }
        const fullXml = readFileSync(current.xmlPath, 'utf8');
        const mergedXml = mergeWorkspacePage(fullXml, xml, current.entry);
        backupWorkspaceDocument(diagramId, current);
        atomicWrite(current.xmlPath, mergedXml);
        atomicWrite(current.svgPath, svg);
        const saved = workspaceDocument(diagramId);
        json(response, 200, { diagramId, revision: saved.revision, modifiedAt: saved.modifiedAt });
        return;
      }
      if (url.pathname === '/api/agent/openai/models' && request.method === 'POST') {
        if (!sameOrigin(request, port)) { json(response, 403, { error: { message: 'Origin rejected.' } }); return; }
        const body = await readJSON(request);
        await forwardOpenAI(response, '/models', body.apiKey, null, 30000);
        return;
      }
      if (url.pathname === '/api/agent/openai/responses' && request.method === 'POST') {
        if (!sameOrigin(request, port)) { json(response, 403, { error: { message: 'Origin rejected.' } }); return; }
        const body = await readJSON(request);
        const inference = body.request || {};
        const deprecated = openAIPolicy?.deprecated?.[inference.model];
        if (deprecated) {
          json(response, 400, { error: { message: `Blocked deprecated model ${inference.model}. Use ${deprecated.replacement}; shutdown date ${deprecated.shutdownDate}.` } });
          return;
        }
        if (!inference.model || inference.stream === true) { json(response, 400, { error: { message: 'A non-streaming OpenAI model request is required.' } }); return; }
        inference.store = false;
        await forwardOpenAI(response, '/responses', body.apiKey, inference);
        return;
      }
      if (url.pathname === '/api/bridge/commands' && request.method === 'GET') {
        const since = Number(url.searchParams.get('since') || 0);
        json(response, 200, { commands: commands.filter((command) => command.sequence > since).slice(0, 20) });
        return;
      }
      if (url.pathname === '/api/bridge/result' && request.method === 'POST') {
        const body = await readJSON(request);
        if (!body.id) throw new Error('Command result ID is required.');
        results.set(body.id, { ...body, receivedAt: Date.now() });
        json(response, 200, { accepted: true });
        return;
      }
      if (url.pathname === '/api/mcp/command' && request.method === 'POST') {
        if (!authorized(request)) { json(response, 401, { error: 'Unauthorized.' }); return; }
        mcpLastSeen = Date.now();
        const body = await readJSON(request);
        const command = { id: randomUUID(), sequence: ++sequence, tool: body.tool, arguments: body.arguments || {}, createdAt: Date.now() };
        commands.push(command);
        while (commands.length > 200) commands.shift();
        json(response, 202, command);
        return;
      }
      if (url.pathname.startsWith('/api/mcp/result/') && request.method === 'GET') {
        if (!authorized(request)) { json(response, 401, { error: 'Unauthorized.' }); return; }
        mcpLastSeen = Date.now();
        const id = decodeURIComponent(url.pathname.slice('/api/mcp/result/'.length));
        const result = results.get(id);
        json(response, result ? 200 : 202, result || { pending: true });
        if (result) results.delete(id);
        return;
      }
      if (request.method !== 'GET' && request.method !== 'HEAD') { json(response, 405, { error: 'Method not allowed.' }); return; }
      const relative = decodeURIComponent(url.pathname === '/' ? 'index.html' : url.pathname.slice(1));
      const path = normalize(resolve(root, relative));
      if (!staticPathAllowed(path) || !existsSync(path) || !statSync(path).isFile()) { json(response, 404, { error: 'Not found.' }); return; }
      const headers = { 'Content-Type': contentTypes[extname(path).toLocaleLowerCase()] || 'application/octet-stream', 'Cache-Control': 'no-store' };
      response.writeHead(200, headers);
      if (request.method === 'HEAD') response.end(); else createReadStream(path).pipe(response);
    } catch (error) {
      json(response, 400, { error: error.message });
    }
  };
}

function listen(port) {
  return new Promise((resolveListen, reject) => {
    const server = createServer(createRequestHandler(port));
    server.once('error', reject);
    server.listen(port, '127.0.0.1', () => resolveListen(server));
  });
}

let server;
let port;
const configuredPort = Number(process.env.PETAKERJA_EXPLORER_PORT || 8082);
const portStart = Number(process.env.PETAKERJA_EXPLORER_PORT_START || configuredPort);
const portEnd = Number(process.env.PETAKERJA_EXPLORER_PORT_END || process.env.PETAKERJA_EXPLORER_PORT_START || configuredPort);
for (let candidate = portStart; candidate <= portEnd; candidate += 1) {
  try { server = await listen(candidate); port = candidate; break; } catch (error) { if (error.code !== 'EADDRINUSE') throw error; }
}
if (!server) throw new Error(`No free Explorer port was found between ${portStart} and ${portEnd}.`);
mkdirSync(resolve(runtimeFile, '..'), { recursive: true });
writeFileSync(runtimeFile, JSON.stringify({ port, token, pid: process.pid, root, startedAt: new Date().toISOString() }, null, 2));
process.stdout.write(`PetaKerja Architecture Explorer: http://127.0.0.1:${port}/\n`);

const cleanup = () => { try { if (existsSync(runtimeFile) && JSON.parse(readFileSync(runtimeFile, 'utf8')).pid === process.pid) writeFileSync(runtimeFile, ''); } catch {} };
process.on('SIGINT', () => { cleanup(); server.close(() => process.exit(0)); });
process.on('SIGTERM', () => { cleanup(); server.close(() => process.exit(0)); });
