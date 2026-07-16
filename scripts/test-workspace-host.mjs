import assert from 'node:assert/strict';
import { spawn } from 'node:child_process';
import { readFile } from 'node:fs/promises';

const root = new URL('..', import.meta.url);
const port = 8092;
const host = spawn(process.execPath, ['scripts/explorer-host.mjs'], {
  cwd: root,
  env: { ...process.env, PETAKERJA_EXPLORER_PORT: String(port) },
  stdio: ['ignore', 'pipe', 'pipe'],
});

async function waitForHost() {
  for (let attempt = 0; attempt < 80; attempt += 1) {
    try {
      const response = await fetch(`http://127.0.0.1:${port}/api/bridge/status`);
      if (response.ok) return response.json();
    } catch (_error) { /* Host is still starting. */ }
    await new Promise((resolve) => setTimeout(resolve, 50));
  }
  throw new Error('Workspace host did not start.');
}

try {
  const status = await waitForHost();
  assert.equal(status.workspace.writable, true);
  const sessionResponse = await fetch(`http://127.0.0.1:${port}/api/workspace/session`);
  const session = await sessionResponse.json();
  assert.ok(session.diagrams.includes('domain'));

  const domainResponse = await fetch(`http://127.0.0.1:${port}/api/workspace/diagrams/domain`);
  const domain = await domainResponse.json();
  assert.equal(domain.revision.length, 64);
  assert.match(domain.xml, /<mxfile/);
  assert.match(domain.svg, /<svg/);

  const implementationResponse = await fetch(`http://127.0.0.1:${port}/api/workspace/diagrams/implementation`);
  const implementation = await implementationResponse.json();
  assert.equal((implementation.xml.match(/<diagram\b/g) || []).length, 1, 'shared sources must hydrate one page only');
  assert.match(implementation.xml, /petakerja_implementation/);

  const conflictResponse = await fetch(`http://127.0.0.1:${port}/api/workspace/diagrams/domain`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json', 'X-PetaKerja-Workspace-Token': session.token },
    body: JSON.stringify({ revision: 'stale', xml: domain.xml, svg: domain.svg }),
  });
  assert.equal(conflictResponse.status, 409);

  const deckId = `deck-test-${Date.now()}`;
  const deck = {
    schemaVersion: 1,
    id: deckId,
    title: 'Workspace host test deck',
    language: 'ms',
    aspectRatio: '16:9',
    presetId: 'ukm-fyp-2026',
    themeId: 'ukm-neutral',
    slides: [{ id: `slide-test-${Date.now()}`, name: 'Test', hidden: false, layoutId: 'blank', durationSeconds: 45, speakerNotes: 'Test notes', canvasJson: { version: '7.4.0', objects: [] } }],
    assets: {},
    createdAt: new Date().toISOString(),
    updatedAt: new Date().toISOString(),
  };
  const createDeckResponse = await fetch(`http://127.0.0.1:${port}/api/workspace/presentations`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', 'X-PetaKerja-Workspace-Token': session.token },
    body: JSON.stringify({ document: deck }),
  });
  assert.equal(createDeckResponse.status, 201);
  const createdDeck = await createDeckResponse.json();
  assert.equal(createdDeck.revision.length, 64);

  const staleDeckResponse = await fetch(`http://127.0.0.1:${port}/api/workspace/presentations/${deckId}`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json', 'X-PetaKerja-Workspace-Token': session.token },
    body: JSON.stringify({ document: { ...deck, title: 'Stale write' }, revision: 'stale' }),
  });
  assert.equal(staleDeckResponse.status, 409);

  const updateDeckResponse = await fetch(`http://127.0.0.1:${port}/api/workspace/presentations/${deckId}`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json', 'X-PetaKerja-Workspace-Token': session.token },
    body: JSON.stringify({ document: { ...deck, title: 'Updated test deck', updatedAt: new Date().toISOString() }, revision: createdDeck.revision }),
  });
  assert.equal(updateDeckResponse.status, 200);
  const updatedDeck = await updateDeckResponse.json();
  assert.notEqual(updatedDeck.revision, createdDeck.revision);

  const assetId = `asset-test-${Date.now()}`;
  const assetResponse = await fetch(`http://127.0.0.1:${port}/api/workspace/presentations/${deckId}/assets/${assetId}`, {
    method: 'PUT',
    headers: { 'Content-Type': 'image/svg+xml', 'X-PetaKerja-Workspace-Token': session.token },
    body: '<svg xmlns="http://www.w3.org/2000/svg" width="10" height="10"/>',
  });
  assert.equal(assetResponse.status, 201);
  const readAssetResponse = await fetch(`http://127.0.0.1:${port}/api/workspace/presentations/${deckId}/assets/${assetId}`);
  assert.equal(readAssetResponse.status, 200);
  assert.match(await readAssetResponse.text(), /<svg/);

  const deleteDeckResponse = await fetch(`http://127.0.0.1:${port}/api/workspace/presentations/${deckId}`, {
    method: 'DELETE', headers: { 'X-PetaKerja-Workspace-Token': session.token },
  });
  assert.equal(deleteDeckResponse.status, 200);

  for (const path of ['/.runtime/host.json', '/.git/config', '/bridge/package.json', '/scripts/explorer-host.mjs']) {
    const response = await fetch(`http://127.0.0.1:${port}${path}`);
    assert.equal(response.status, 404, `${path} must not be served`);
  }

  const manifest = JSON.parse(await readFile(new URL('../workspace-manifest.json', import.meta.url), 'utf8'));
  assert.equal(session.diagrams.length, Object.keys(manifest.diagrams).length);
  process.stdout.write(`${JSON.stringify({ passed: true, diagrams: session.diagrams.length, sharedPage: 'petakerja_implementation' })}\n`);
} finally {
  host.kill('SIGTERM');
}
