import fs from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const scriptDir = path.dirname(fileURLToPath(import.meta.url));
const explorerRoot = path.resolve(scriptDir, '..');
const blueprintIcons = path.resolve(explorerRoot, '..', '..', 'repo-reference', 'blueprint', 'resources', 'icons', '16px');
const outputDir = path.join(explorerRoot, 'vendor', 'blueprint-icons');
const outputFile = path.join(outputDir, 'blueprint-icons.js');

// Explorer semantic names stay stable even when the upstream Blueprint name differs.
const aliases = Object.freeze({
  'activity': 'timeline-events',
  'arrow-left': 'arrow-left',
  'arrow-right': 'arrow-right',
  'badge-help': 'help',
  'book-open': 'manual',
  'bot': 'predictive-analysis',
  'boxes': 'projects',
  'briefcase-business': 'briefcase',
  'chevron-down': 'chevron-down',
  'chevron-right': 'chevron-right',
  'circle': 'circle',
  'circle-check': 'tick-circle',
  'circle-check-big': 'tick-circle',
  'circle-x': 'error',
  'cloud': 'cloud',
  'cloud-upload': 'cloud-upload',
  'compass': 'compass',
  'copy-plus': 'duplicate',
  'database': 'database',
  'download': 'download',
  'external-link': 'arrow-top-right',
  'file-plus-2': 'new-drawing',
  'file-question-mark': 'help',
  'folder': 'folder-close',
  'folder-tree': 'diagram-tree',
  'git-branch': 'git-branch',
  'git-commit-horizontal': 'git-commit',
  'heading': 'header',
  'history': 'history',
  'image': 'media',
  'languages': 'translate',
  'layers-2': 'layers',
  'layout-dashboard': 'panel-stats',
  'layout-grid': 'layout-grid',
  'list-checks': 'list',
  'list-tree': 'diagram-tree',
  'log-in': 'log-in',
  'log-out': 'log-out',
  'map': 'map',
  'monitor': 'desktop',
  'moon': 'moon',
  'mouse-pointer-click': 'select',
  'network': 'graph',
  'newspaper': 'document',
  'panels-top-left': 'layout-grid',
  'play': 'play',
  'plus': 'plus',
  'presentation': 'presentation',
  'redo-2': 'redo',
  'refresh-cw': 'refresh',
  'repeat-2': 'repeat',
  'save': 'floppy-disk',
  'search': 'search',
  'shield-user': 'shield',
  'sparkles': 'endorsed',
  'square': 'square',
  'sun': 'flash',
  'table-properties': 'panel-table',
  'triangle-alert': 'warning-sign',
  'type': 'new-text-box',
  'undo-2': 'undo',
  'user-plus': 'new-person',
  'user-round': 'person',
  'users': 'people',
  'users-round': 'people',
  'waypoints': 'data-lineage',
  'workflow': 'flow-linear',
  'x': 'cross',
});

async function svgPaths(iconName) {
  const source = await fs.readFile(path.join(blueprintIcons, `${iconName}.svg`), 'utf8');
  const paths = [...source.matchAll(/<path\b[^>]*\bd="([^"]+)"[^>]*\/?\s*>/g)].map((match) => match[1]);
  if (!paths.length) throw new Error(`Blueprint icon has no paths: ${iconName}`);
  return paths;
}

const entries = {};
for (const [semanticName, blueprintName] of Object.entries(aliases)) {
  entries[semanticName] = { blueprintName, paths: await svgPaths(blueprintName) };
}

const source = `/*\n * Local Blueprint icon subset for PetaKerja Architecture Explorer.\n * Derived from @blueprintjs/icons (Apache-2.0). See THIRD_PARTY_NOTICES.md.\n */\n(function () {\n  'use strict';\n\n  const ICONS = Object.freeze(${JSON.stringify(entries, null, 2)});\n  const SVG_NS = 'http://www.w3.org/2000/svg';\n\n  function renderBlueprintIcons(root = document) {\n    const nodes = [];\n    if (root?.matches?.('[data-bp-icon]')) nodes.push(root);\n    root?.querySelectorAll?.('[data-bp-icon]')?.forEach((node) => nodes.push(node));\n    for (const node of nodes) {\n      if (node.dataset.bpIconRendered === 'true') continue;\n      const definition = ICONS[node.dataset.bpIcon];\n      if (!definition) {\n        node.dataset.bpIconMissing = 'true';\n        continue;\n      }\n      const svg = document.createElementNS(SVG_NS, 'svg');\n      svg.setAttribute('viewBox', '0 0 16 16');\n      svg.setAttribute('width', '16');\n      svg.setAttribute('height', '16');\n      svg.setAttribute('fill', 'currentColor');\n      svg.setAttribute('focusable', 'false');\n      svg.setAttribute('aria-hidden', 'true');\n      svg.classList.add('bp-icon');\n      svg.dataset.iconName = node.dataset.bpIcon;\n      for (const pathData of definition.paths) {\n        const pathNode = document.createElementNS(SVG_NS, 'path');\n        pathNode.setAttribute('d', pathData);\n        svg.append(pathNode);\n      }\n      node.replaceChildren(svg);\n      node.dataset.bpIconRendered = 'true';\n    }\n    return nodes.length;\n  }\n\n  window.PETAKERJA_BLUEPRINT_ICONS = ICONS;\n  window.renderBlueprintIcons = renderBlueprintIcons;\n}());\n`;

await fs.mkdir(outputDir, { recursive: true });
await fs.writeFile(outputFile, source, 'utf8');
console.log(`Wrote ${Object.keys(entries).length} Blueprint icon aliases to ${outputFile}`);
