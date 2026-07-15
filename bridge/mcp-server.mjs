#!/usr/bin/env node
import { readFileSync } from 'node:fs';
import { resolve } from 'node:path';
import { fileURLToPath } from 'node:url';
import { McpServer } from '@modelcontextprotocol/sdk/server/mcp.js';
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js';
import * as z from 'zod/v4';

const runtimePath = process.env.PETAKERJA_EXPLORER_RUNTIME
  ? resolve(process.env.PETAKERJA_EXPLORER_RUNTIME)
  : fileURLToPath(new URL('../.runtime/host.json', import.meta.url));

function runtime() {
  let value;
  try { value = JSON.parse(readFileSync(runtimePath, 'utf8')); }
  catch (error) { throw new Error(`Explorer host is not running or its runtime file cannot be read: ${runtimePath}. ${error.message}`); }
  if (!value.port || !value.token) throw new Error('Explorer host runtime metadata is incomplete. Start the Explorer launcher again.');
  return value;
}

async function invoke(tool, argumentsValue = {}, timeout = 180000) {
  const active = runtime();
  const base = `http://127.0.0.1:${active.port}`;
  const response = await fetch(`${base}/api/mcp/command`, {
    method: 'POST', headers: { Authorization: `Bearer ${active.token}`, 'Content-Type': 'application/json' },
    body: JSON.stringify({ tool, arguments: argumentsValue }),
  });
  if (!response.ok) throw new Error(`Explorer bridge rejected ${tool} (${response.status}).`);
  const command = await response.json();
  const deadline = Date.now() + timeout;
  while (Date.now() < deadline) {
    await new Promise((resolveWait) => setTimeout(resolveWait, 350));
    const resultResponse = await fetch(`${base}/api/mcp/result/${encodeURIComponent(command.id)}`, { headers: { Authorization: `Bearer ${active.token}` } });
    if (resultResponse.status === 202) continue;
    if (!resultResponse.ok) throw new Error(`Explorer result request failed (${resultResponse.status}).`);
    const result = await resultResponse.json();
    if (!result.ok) throw new Error(result.error || `${tool} failed in the Explorer.`);
    return result.result;
  }
  throw new Error(`${tool} timed out. Keep the Explorer tab open and connected to the local host.`);
}

function content(value) { return { content: [{ type: 'text', text: JSON.stringify(value, null, 2) }] }; }

const server = new McpServer({ name: 'petakerja-architecture-explorer', version: '1.0.0' });
server.registerTool('get_explorer_status', { description: 'Get the visible Explorer workspace, active diagram and dirty state.', inputSchema: {} }, async () => content(await invoke('get_explorer_status')));
server.registerTool('get_diagram_context', { description: 'Read the active diagram components, relations, detection result and validation context.', inputSchema: {} }, async () => content(await invoke('get_diagram_context')));
server.registerTool('start_new_diagram_session', {
  description: 'Start a fresh session-only Draw.io document so Agent operations do not append to an unrelated diagram.',
  inputSchema: {
    name: z.string().describe('Visible Draw.io page and document name.'),
    diagramType: z.string().describe('Detected or canonical diagram type, for example auth-sequence.'),
    pageId: z.string().optional().describe('Stable Draw.io page ID.'),
    filename: z.string().optional().describe('Suggested Save As filename.'),
  },
}, async (args) => content(await invoke('start_new_diagram_session', args)));
server.registerTool('propose_diagram_plan', {
  description: 'Show a structured DiagramPlan in the Explorer for user review. This tool does not apply it.',
  inputSchema: { plan: z.record(z.string(), z.unknown()).describe('A DiagramPlan containing title, diagramType, summary, warnings and allowed operations.') },
}, async ({ plan }) => content(await invoke('propose_diagram_plan', { plan })));
server.registerTool('await_plan_decision', { description: 'Read the current review state for the visible DiagramPlan.', inputSchema: {} }, async () => content(await invoke('await_plan_decision')));
server.registerTool('apply_diagram_operations', {
  description: 'Apply approved, constrained diagram operations visibly through the embedded Draw.io editor.',
  inputSchema: {
    operations: z.array(z.record(z.string(), z.unknown())).optional().describe('Allowed DiagramOperation objects.'),
    plan: z.record(z.string(), z.unknown()).optional().describe('A full DiagramPlan. Takes precedence over operations.'),
  },
}, async (args) => content(await invoke('apply_diagram_operations', args)));
server.registerTool('validate_active_diagram', { description: 'Run the Explorer UML and PetaKerja mapping validator.', inputSchema: {} }, async () => content(await invoke('validate_active_diagram')));
server.registerTool('export_active_diagram', { description: 'Export the active Draw.io page as sanitized SVG plus its current XML.', inputSchema: {} }, async () => content(await invoke('export_active_diagram')));

const transport = new StdioServerTransport();
await server.connect(transport);
console.error('PetaKerja Architecture Explorer MCP bridge connected over stdio.');
