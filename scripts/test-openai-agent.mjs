import assert from 'node:assert/strict';
import { createServer } from 'node:http';
import { mkdtemp, readFile, rm } from 'node:fs/promises';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import { spawn } from 'node:child_process';
import vm from 'node:vm';

await import('../openai-model-policy.js');
const runtimeSource = await readFile(new URL('../agent-runtime.js', import.meta.url), 'utf8');
const sandbox = {
  window: { PETAKERJA_OPENAI_POLICY: globalThis.PETAKERJA_OPENAI_POLICY },
  console, URL, setTimeout, clearTimeout, AbortController, fetch,
};
vm.createContext(sandbox);
vm.runInContext(runtimeSource, sandbox, { filename: 'agent-runtime.js' });
const api = sandbox.window.PETAKERJA_AGENT;

const request = api.buildOpenAIResponsesRequest('gpt-5.6-terra', 'system', 'user');
assert.equal(request.model, 'gpt-5.6-terra');
assert.deepEqual({ ...request.reasoning }, { effort: 'medium' });
assert.equal(request.store, false);
assert.equal(request.text.format.type, 'json_schema');
assert.equal(request.text.format.strict, true);
assert.equal(request.text.format.name, 'diagram_plan');

const compatibleAgent = new api.DiagramAgent({});
compatibleAgent.configure({ provider: 'compatible', baseURL: 'http://127.0.0.1', model: 'gpt-4o-2024-05-13', apiKey: 'test' });
assert.doesNotThrow(() => compatibleAgent.assertOpenAIModelAllowed());
const openAIAgent = new api.DiagramAgent({});
openAIAgent.configure({ provider: 'openai', model: 'gpt-4o-2024-05-13', apiKey: 'test' });
assert.throws(() => openAIAgent.assertOpenAIModelAllowed(), /Blocked deprecated OpenAI model/);

assert.throws(() => api.extractResponsesText({ status: 'incomplete', incomplete_details: { reason: 'max_output_tokens' }, output: [] }), /incomplete/i);
assert.throws(() => api.extractResponsesText({ output: [{ content: [{ type: 'refusal', refusal: 'No.' }] }] }), /refusal/i);

const upstreamRequests = [];
const examplePlan = { id: 'mock', title: 'Mock', diagramType: 'auth-sequence', summary: 'Mock plan', warnings: [], operations: [] };
const mock = createServer(async (incoming, response) => {
  const chunks = [];
  for await (const chunk of incoming) chunks.push(chunk);
  const raw = Buffer.concat(chunks).toString('utf8');
  const body = raw ? JSON.parse(raw) : null;
  upstreamRequests.push({ method: incoming.method, path: incoming.url, authorization: incoming.headers.authorization, body });
  const payload = incoming.url === '/models'
    ? { object: 'list', data: [{ id: 'gpt-5.6-terra', object: 'model' }] }
    : { status: 'completed', output: [{ type: 'message', content: [{ type: 'output_text', text: JSON.stringify(examplePlan) }] }] };
  const json = JSON.stringify(payload);
  response.writeHead(200, { 'Content-Type': 'application/json', 'Content-Length': Buffer.byteLength(json) });
  response.end(json);
});
await new Promise((resolve) => mock.listen(0, '127.0.0.1', resolve));
const mockPort = mock.address().port;
const temporary = await mkdtemp(join(tmpdir(), 'petakerja-openai-test-'));
const host = spawn(process.execPath, ['scripts/explorer-host.mjs'], {
  cwd: new URL('..', import.meta.url),
  env: {
    ...process.env,
    PETAKERJA_OPENAI_BASE_URL: `http://127.0.0.1:${mockPort}`,
    PETAKERJA_EXPLORER_PORT_START: '8091',
    PETAKERJA_EXPLORER_PORT_END: '8091',
    PETAKERJA_EXPLORER_RUNTIME_FILE: join(temporary, 'host.json'),
  },
  stdio: ['ignore', 'pipe', 'pipe'],
});

try {
  const hostURL = await new Promise((resolve, reject) => {
    let stderr = '';
    const timer = setTimeout(() => reject(new Error(stderr || 'Timed out starting the test Explorer host.')), 10000);
    host.stderr.on('data', (chunk) => { stderr += String(chunk); });
    host.stdout.on('data', (chunk) => {
      const match = String(chunk).match(/http:\/\/127\.0\.0\.1:\d+\//);
      if (match) { clearTimeout(timer); resolve(match[0]); }
    });
    host.once('error', reject);
    host.once('exit', (code) => { if (code) reject(new Error(stderr || `Test host exited with ${code}.`)); });
  });

  const models = await fetch(new URL('/api/agent/openai/models', hostURL), {
    method: 'POST', headers: { 'Content-Type': 'application/json', Origin: hostURL.replace(/\/$/, '') }, body: JSON.stringify({ apiKey: 'sk-test-only' }),
  });
  assert.equal(models.status, 200);
  assert.equal((await models.json()).data[0].id, 'gpt-5.6-terra');

  const response = await fetch(new URL('/api/agent/openai/responses', hostURL), {
    method: 'POST', headers: { 'Content-Type': 'application/json', Origin: hostURL.replace(/\/$/, '') },
    body: JSON.stringify({ apiKey: 'sk-test-only', request }),
  });
  assert.equal(response.status, 200);
  assert.equal(api.extractResponsesText(await response.json()), JSON.stringify(examplePlan));
  const forwarded = upstreamRequests.find((entry) => entry.path === '/responses');
  assert.ok(forwarded);
  assert.equal(forwarded.body.model, 'gpt-5.6-terra');
  assert.equal(forwarded.body.reasoning.effort, 'medium');
  assert.equal(forwarded.body.store, false);
  assert.equal(forwarded.body.text.format.strict, true);
  assert.ok(upstreamRequests.every((entry) => entry.path !== '/chat/completions'));

  const beforeBlocked = upstreamRequests.length;
  const blocked = await fetch(new URL('/api/agent/openai/responses', hostURL), {
    method: 'POST', headers: { 'Content-Type': 'application/json', Origin: hostURL.replace(/\/$/, '') },
    body: JSON.stringify({ apiKey: 'sk-test-only', request: { ...request, model: 'gpt-4o-2024-05-13' } }),
  });
  assert.equal(blocked.status, 400);
  assert.match((await blocked.json()).error.message, /Blocked deprecated model/);
  assert.equal(upstreamRequests.length, beforeBlocked, 'A blocked model must never reach the upstream provider.');

  console.log(JSON.stringify({
    passed: true,
    model: request.model,
    endpoint: '/responses',
    strictStructuredOutput: request.text.format.strict,
    blockedBeforeUpstream: true,
    compatibleProviderExempt: true,
    upstreamPaths: upstreamRequests.map((entry) => entry.path),
  }, null, 2));
} finally {
  host.kill('SIGTERM');
  await new Promise((resolve) => host.once('exit', resolve));
  await new Promise((resolve) => mock.close(resolve));
  await rm(temporary, { recursive: true, force: true });
}
