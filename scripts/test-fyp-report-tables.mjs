import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import vm from 'node:vm';
import { fileURLToPath } from 'node:url';

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const read = (filename) => fs.readFileSync(path.join(root, filename), 'utf8');
const runBrowserScript = (filename, extras = {}) => {
  const sandbox = { window: {}, ...extras };
  vm.createContext(sandbox);
  vm.runInContext(read(filename), sandbox, { filename });
  return sandbox;
};

const dataSandbox = runBrowserScript('fyp-report-tables.js');
const registry = dataSandbox.window.PETAKERJA_FYP_REPORT_TABLES;
const localizedText = (value, language) => typeof value === 'object' && value !== null ? value[language] : String(value ?? '');
const assertLocalized = (value, label) => {
  assert.ok(value && typeof value === 'object' && value.ms && value.en, `${label} should contain BM and English text`);
};
assert.ok(registry, 'FYP report-table registry should be exported');
assert.deepEqual(Object.keys(registry.pages).sort(), ['kamus-data', 'use-case-specification']);

const dictionaryPage = registry.pages['kamus-data'];
const dictionaryTables = dictionaryPage.sections.flatMap((section) => section.tables);
assert.equal(dictionaryPage.sections.length, 2, 'Kamus Data should be grouped by two actors');
assert.deepEqual(Array.from(dictionaryPage.sections, (section) => section.title.ms), ['Pengguna', 'Pentadbir']);
assert.deepEqual(Array.from(dictionaryPage.sections, (section) => section.title.en), ['User', 'Administrator']);
assert.equal(dictionaryTables.length, 8, 'Kamus Data should contain eight table blocks');

const expectedFields = {
  'user-profile': ['id', 'username', 'email', 'profile_picture_url', 'selected_state', 'points', 'exp', 'created_at', 'updated_at', 'last_login', 'display_name', 'provider', 'welcomed_at', 'role', 'better_auth_user_id'],
  poi: ['id', 'data_source_id', 'source_id', 'name', 'category', 'state_id', 'lat', 'lng', 'geom', 'address', 'postcode', 'phone', 'website', 'opening_hours', 'operator', 'brand', 'elevation', 'height', 'search_vector', 'is_verified', 'created_at', 'updated_at', 'email', 'social_media'],
  'job-listing': ['id', 'source_platform', 'job_title', 'company_name', 'company_logo', 'location', 'state', 'description', 'salary_raw', 'salary_min', 'salary_max', 'employment_type', 'remote_type', 'experience_level', 'job_category', 'skills', 'job_url', 'apply_link', 'posted_at', 'scraped_at', 'expires_at', 'search_vector', 'created_at', 'updated_at'],
  'user-job-state': ['id', 'user_id', 'source', 'job_key', 'state', 'job_title', 'company_name', 'apply_url', 'location', 'salary_raw', 'source_platform', 'posted_at', 'notes', 'tailoring_json', 'fit_score', 'fit_breakdown', 'saved_at', 'applied_at', 'responded_at', 'closed_at', 'created_at', 'updated_at', 'resume_pdf_path', 'resume_pdf_rendered_at', 'resume_pdf_renderer'],
  'admin-user-view': ['display_name', 'email', 'role', 'created_at', 'last_login'],
  'ai-provider-credential': ['id', 'owner_type', 'user_id', 'provider_id', 'display_name', 'auth_type', 'encrypted_api_key', 'base_url', 'headers', 'metadata', 'enabled', 'created_at', 'updated_at'],
  'ai-usage-event': ['id', 'user_id', 'session_id', 'message_id', 'provider_id', 'model_id', 'credential_owner_type', 'input_tokens', 'output_tokens', 'cache_read_tokens', 'cache_write_tokens', 'estimated_cost_usd', 'context_summary', 'status', 'error_message', 'created_at'],
  'admin-audit-log': ['id', 'actor_user_id', 'action', 'target_type', 'target_id', 'metadata', 'created_at'],
};

for (const table of dictionaryTables) {
  assert.ok(expectedFields[table.id], `Unexpected dictionary table: ${table.id}`);
  assert.deepEqual(Array.from(table.fields, (field) => field.name), expectedFields[table.id], `${table.id} must cover its verified fields exactly`);
  assertLocalized(table.title, `${table.id}.title`);
  assertLocalized(table.operation, `${table.id}.operation`);
  for (const field of table.fields) {
    for (const key of ['type', 'constraints', 'description']) assertLocalized(field[key], `${table.id}.${field.name}.${key}`);
    assert.ok(field.size, `${table.id}.${field.name}.size should be populated`);
    if (field.name !== 'estimated_cost_usd') assert.equal(localizedText(field.size, 'ms'), 'Tidak ditetapkan', `${table.id}.${field.name} should not invent a declared size`);
  }
}

assert.equal(dictionaryTables.find((table) => table.id === 'ai-usage-event').fields.find((field) => field.name === 'estimated_cost_usd').size, '12,6');
const notesField = dictionaryTables.find((table) => table.id === 'user-job-state').fields.find((field) => field.name === 'notes');
assert.equal(notesField.size.ms, 'Tidak ditetapkan');
assert.match(notesField.constraints.ms, /4000 aksara/);
assert.match(notesField.constraints.en, /4000 characters/);
assert.match(dictionaryTables.find((table) => table.id === 'poi').operation.ms, /bacaan/i);
assert.match(dictionaryTables.find((table) => table.id === 'job-listing').operation.en, /read-oriented/i);
assert.match(dictionaryTables.find((table) => table.id === 'user-job-state').operation.ms, /milik sendiri/i);
assert.match(dictionaryTables.find((table) => table.id === 'admin-user-view').operation.en, /does not change roles/i);
assert.match(dictionaryTables.find((table) => table.id === 'ai-provider-credential').operation.en, /Only owners/i);
assert.match(dictionaryTables.find((table) => table.id === 'ai-usage-event').operation.en, /not general server logs/i);
assert.match(dictionaryTables.find((table) => table.id === 'admin-audit-log').operation.en, /not displayed in the Usage section/i);

const useCases = registry.pages['use-case-specification'].useCases;
assert.equal(useCases.length, 15, 'Use Case Specification should contain 15 tables');
assert.deepEqual(Array.from(useCases, (item) => item.id), Array.from({ length: 15 }, (_item, index) => `KP${String(index + 1).padStart(2, '0')}`));
assert.equal(new Set(useCases.map((item) => item.id)).size, 15, 'Use-case IDs should be unique');
for (const useCase of useCases) {
  for (const key of ['name', 'purpose', 'actors']) assertLocalized(useCase[key], `${useCase.id}.${key}`);
  for (const key of ['preconditions', 'mainFlow', 'alternatives', 'postconditions', 'relationships']) {
    assert.ok(useCase[key].length, `${useCase.id}.${key} should be populated`);
    for (const [index, value] of useCase[key].entries()) assertLocalized(value, `${useCase.id}.${key}[${index}]`);
  }
}

const relationships = Object.fromEntries(useCases.map((item) => [item.id, item.relationships.map((value) => value.ms).join(' ')]));
for (const id of ['KP03', 'KP04', 'KP05', 'KP06']) assert.match(relationships[id], /KP02.*<<extend>>/);
assert.match(relationships.KP08, /KP07.*<<extend>>/);
assert.match(relationships.KP09, /KP08.*<<extend>>/);
assert.match(relationships.KP09, /KP01.*<<include>>/);
assert.match(relationships.KP10, /KP02.*<<extend>>/);
assert.match(relationships.KP10, /KP01.*<<include>>/);
assert.match(relationships.KP12, /KP01.*<<include>>/);
assert.match(relationships.KP14, /baca sahaja/i);
assert.match(useCases.find((item) => item.id === 'KP15').alternatives.map((value) => value.ms).join(' '), /medan model yang tiada/i);
assert.match(useCases.find((item) => item.id === 'KP15').alternatives.map((value) => value.en).join(' '), /fields absent from the live/i);

const assetSandbox = runBrowserScript('diagram-assets.js');
const useCaseAsset = assetSandbox.window.PETAKERJA_DIAGRAM_ASSETS.usecase;
const assetKeys = new Set(useCaseAsset.components.map((component) => component.componentKey));
assert.ok(assetKeys.has('drawio:actor-user') && assetKeys.has('drawio:actor-admin'));
for (const useCase of useCases) assert.ok(assetKeys.has(useCase.componentKey), `${useCase.id} should map to a current diagram component`);
const connectedKeys = new Set(useCaseAsset.connections.flatMap((connection) => [connection.sourceComponentKey, connection.targetComponentKey]));
for (const useCase of useCases) assert.ok(connectedKeys.has(useCase.componentKey), `${useCase.id} should be connected by the current use-case registry`);
for (const connection of useCaseAsset.connections.filter((item) => ['include', 'extend'].includes(item.kind))) {
  const label = connection.label.ms;
  assert.equal(label, `<<${connection.kind}>>`, `${connection.id} should keep its relationship label`);
}

const clipboardSandbox = runBrowserScript('code-snippet-highlighter.js');
vm.runInContext(read('code-snippet-clipboard.js'), clipboardSandbox, { filename: 'code-snippet-clipboard.js' });
const clipboard = clipboardSandbox.window.PETAKERJA_CODE_SNIPPET_CLIPBOARD;
assert.equal(typeof clipboard.reportTablePayload, 'function');
assert.equal(typeof clipboard.reportTableFragmentPayload, 'function');

const samplePayload = clipboard.reportTablePayload({
  title: 'KP99 — Test <safe>', source: 'Source & schema', note: 'Test "note"', sourceLabel: 'Source', noteLabel: 'Note', rowHeaderIndex: 0,
  columns: [{ label: 'Item', width: '24%' }, { label: 'Specification', width: '76%' }],
  rows: [['Senario Utama', ['Langkah <satu>', 'Langkah & dua']]],
});
assert.match(samplePayload.plainText, /Source: Source & schema/);
assert.match(samplePayload.plainText, /Item\tSpecification/);
assert.match(samplePayload.plainText, /Note: Test "note"/);
assert.match(samplePayload.plainText, /1\. Langkah <satu> 2\. Langkah & dua/);
assert.match(samplePayload.htmlText, /<table border="1" cellspacing="0" cellpadding="0"/);
assert.match(samplePayload.htmlText, /border-collapse:collapse/);
assert.match(samplePayload.htmlText, /table-layout:fixed/);
assert.match(samplePayload.htmlText, /font-family:'Times New Roman'/);
assert.match(samplePayload.htmlText, /<ol style=/);
assert.doesNotMatch(samplePayload.htmlText, /<safe>|Langkah <satu>|Source & schema/);
assert.match(samplePayload.htmlText, /&lt;safe&gt;|Langkah &lt;satu&gt;|Source &amp; schema/);
assert.match(samplePayload.htmlText, /<strong>Source:<\/strong>/);
assert.match(samplePayload.htmlText, /<strong>Note:<\/strong>/);
const cellTags = samplePayload.htmlText.match(/<(?:th|td)\b[^>]*>/g) || [];
assert.ok(cellTags.length >= 4 && cellTags.every((tag) => tag.includes('border:1px solid #000000')), 'Every copied header and data cell should have a black border');

const fragmentTable = {
  rowHeaderIndex: 0,
  columns: [{ label: 'Medan' }, { label: 'Huraian' }],
  rows: [['id', 'Kunci <utama>'], ['name', ['Nama pertama', 'Nama kedua']]],
};
const cellPayload = clipboard.reportTableFragmentPayload(fragmentTable, { kind: 'cell', rowIndex: 0, columnIndex: 1 });
assert.equal(cellPayload.plainText, 'Kunci <utama>');
assert.match(cellPayload.htmlText, /Kunci &lt;utama&gt;/);
assert.match(cellPayload.htmlText, /border:1px solid #000000/);
const rowPayload = clipboard.reportTableFragmentPayload(fragmentTable, { kind: 'row', rowIndex: 1, columnIndex: 0 });
assert.match(rowPayload.plainText, /^name\t1\. Nama pertama 2\. Nama kedua$/);
assert.match(rowPayload.htmlText, /<tbody><tr><th scope="row"/);
assert.match(rowPayload.htmlText, /<ol style=/);
const columnPayload = clipboard.reportTableFragmentPayload(fragmentTable, { kind: 'column', rowIndex: 0, columnIndex: 1 });
assert.equal(columnPayload.plainText, 'Huraian\nKunci <utama>\n1. Nama pertama 2. Nama kedua');
assert.match(columnPayload.htmlText, /<thead><tr><th scope="col"/);
assert.equal((columnPayload.htmlText.match(/<tr>/g) || []).length, 3, 'Copied column should contain one heading and two data rows');

const indexHTML = read('index.html');
const appJS = read('app.js');
const stylesCSS = read('styles.css');
const architectureData = read('architecture-data.js');
const translations = read('translations.js');
assert.match(indexHTML, /fyp-report-tables\.js/);
assert.match(architectureData, /category: 'Laporan FYP'/);
assert.match(architectureData, /collectionId: 'fyp-report', collectionGroupId: 'report-tables'/);
assert.match(architectureData, /layout: 'report-table'/);
assert.match(appJS, /renderReportTables/);
assert.match(appJS, /data-copy-report-table/);
assert.match(appJS, /addEventListener\('contextmenu', openReportContextMenu\)/);
assert.match(appJS, /data-report-context-copy/);
assert.match(appJS, /reportTableFragmentPayload/);
assert.match(appJS, /data-report-column-index/);
assert.match(appJS, /data-report-row-index/);
assert.match(appJS, /reportColumnSelection: null/);
assert.match(appJS, /data-report-column-select=/);
assert.match(appJS, /data-bp-icon="chevron-down"/);
assert.match(appJS, /aria-pressed="false"/);
assert.match(appJS, /function toggleReportColumnSelection/);
assert.match(appJS, /function applyReportColumnSelection/);
assert.match(appJS, /function clearReportColumnSelection/);
assert.match(appJS, /function selectedReportColumnCopyData/);
assert.match(appJS, /kind: 'column'/);
assert.match(appJS, /addEventListener\('copy'/);
assert.match(appJS, /clipboardData\.setData\('text\/plain'/);
assert.match(appJS, /clipboardData\.setData\('text\/html'/);
assert.match(appJS, /editableTarget \|\| selectedReportText\(\)/);
assert.match(appJS, /nextLanguage !== state\.reportTableLanguage/);
assert.match(appJS, /nextColumnMode !== state\.dictionaryColumnMode/);
assert.match(appJS, /petakerja-explorer-report-table-language/);
assert.match(appJS, /petakerja-explorer-data-dictionary-column/);
assert.match(appJS, /data-report-language="ms"/);
assert.match(appJS, /data-report-language="en"/);
assert.match(appJS, /data-report-column-mode="constraints"/);
assert.match(appJS, /data-report-column-mode="size"/);
assert.match(appJS, /showSize \? field\.size : field\.constraints/);
assert.match(architectureData, /id: 'fyp-use-case-specification', title: 'Spesifikasi Kes Guna'/);
assert.match(translations, /'fyp-kamus-data': \['Data Dictionary'/);
assert.match(translations, /'fyp-use-case-specification': \['Use Case Specification'/);
assert.match(stylesCSS, /body\.is-report-table-mode \.context-column/);
assert.match(stylesCSS, /\.fyp-report-table th,[\s\S]*border: 1px solid #000000/);
assert.match(stylesCSS, /\.fyp-report-view__tools/);
assert.match(stylesCSS, /body\.is-report-table-mode \.graph-canvas \*[\s\S]*user-select: text !important/);
assert.match(stylesCSS, /\.fyp-report-context-menu/);
assert.match(stylesCSS, /\.fyp-report-column-heading/);
assert.match(stylesCSS, /\.fyp-report-column-heading button\[aria-pressed="true"\]/);
assert.match(stylesCSS, /\.fyp-report-table th\.is-report-column-selected,[\s\S]*background: var\(--selected-bg\)/);

console.log('FYP report-table verification passed: bilingual dictionaries and use cases, declared-size mode, selectable columns, keyboard and context copying, and rich clipboard HTML.');
