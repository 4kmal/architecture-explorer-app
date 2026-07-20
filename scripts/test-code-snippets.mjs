import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import vm from 'node:vm';
import { fileURLToPath } from 'node:url';

const appRoot = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const repoRoot = path.resolve(appRoot, '..', '..');

function read(file) {
  return fs.readFileSync(path.join(appRoot, file), 'utf8');
}

const dataSandbox = { window: {} };
vm.runInNewContext(read('architecture-data.js'), dataSandbox, { filename: 'architecture-data.js' });
const snippets = dataSandbox.window.PETAKERJA_ARCHITECTURE.diagrams.filter((diagram) => diagram.layout === 'code');

const expected = [
  ['code-geo-routing', 'a. Algoritma Penghalaan Geo A-ke-B PetaKerja', 'a. PetaKerja A-to-B Geo Routing Algorithm', 'Rajah 3.33 Algoritma penghalaan geo A-ke-B PetaKerja', 'Figure 3.33 PetaKerja A-to-B geo routing algorithm'],
  ['code-job-scraping', 'b. Algoritma Pengikisan Data Pekerjaan', 'b. Job Data Scraping Algorithm', 'Rajah 3.34 Algoritma pengikisan data pekerjaan', 'Figure 3.34 Job data scraping algorithm'],
  ['code-poi-search', 'c. Algoritma Carian POI Hibrid', 'c. Hybrid POI Search Algorithm', 'Rajah 3.35 Algoritma carian POI hibrid', 'Figure 3.35 Hybrid POI search algorithm'],
  ['code-poi-clustering', 'd. Algoritma Pengelompokan Penanda POI', 'd. POI Marker Clustering Algorithm', 'Rajah 3.36 Algoritma pengelompokan penanda POI', 'Figure 3.36 POI marker clustering algorithm'],
  ['code-live-job-search', 'e. Algoritma Carian Pekerjaan Langsung PetaKerja', 'e. PetaKerja Live Job Search Algorithm', 'Rajah 3.37 Algoritma carian pekerjaan langsung PetaKerja', 'Figure 3.37 PetaKerja live job search algorithm'],
];

assert.equal(snippets.length, 5, 'Exactly five code snippets must be published.');
assert.deepEqual(Array.from(snippets, ({ id, reportHeading, reportHeadingEn, caption, captionEn }) => [id, reportHeading, reportHeadingEn, caption, captionEn]), expected);
assert.ok(snippets.every((snippet) => snippet.category === 'Code Snippets'), 'All snippets must use the Code Snippets category.');
assert.ok(snippets.every((snippet) => snippet.snippetGroup === 'Algorithms'), 'All snippets must use the Algorithms subgroup.');
assert.ok(snippets.every((snippet) => Array.isArray(snippet.columns) && snippet.columns.length === 0), 'Code snippets must remain visible in every architecture scope.');
assert.ok(snippets.every((snippet) => typeof snippet.code === 'string' && snippet.code.trim().length > 100), 'Every snippet must contain substantive pseudocode.');
assert.ok(snippets.every((snippet) => typeof snippet.codeEn === 'string' && snippet.codeEn.trim().length > 100), 'Every snippet must contain substantive English pseudocode.');
assert.deepEqual(Array.from(snippets, (snippet) => snippet.codeEn.split('\n')[0]), [
  'Function CalculateAndDisplayRoute(pointA, pointB, profile)',
  'Function RunJobScraping()',
  'Function SearchPOI(searchText)',
  'Function PreparePOIClusterMarkers(poiList)',
  'Function SearchLiveJobs(searchText, location, filters)',
]);

for (const snippet of snippets) {
  assert.ok(Array.isArray(snippet.sourceFiles) && snippet.sourceFiles.length > 0, `${snippet.id} must cite source files.`);
  for (const sourceFile of snippet.sourceFiles) {
    assert.ok(fs.existsSync(path.join(repoRoot, sourceFile)), `${snippet.id} has a missing source path: ${sourceFile}`);
  }
}

const liveSearch = snippets.find((snippet) => snippet.id === 'code-live-job-search');
assert.ok(liveSearch, 'The Live Search algorithm must be published after the existing report snippets.');
for (const requiredTerm of ['Maukerja', 'Hiredly', 'Ricebowl', 'Graduan', 'Jora', 'JobStreet', 'Jobstore', 'Careerjet', '/api/search-jobs', 'Scrapling', 'CAREERJET_AFFID', 'lima minit', 'sedang berjalan', 'isDemoMode']) {
  assert.match(liveSearch.code, new RegExp(requiredTerm.replace(/[.*+?^${}()|[\]\\]/g, '\\$&'), 'i'), `Live Search pseudocode must explain ${requiredTerm}.`);
}
assert.doesNotMatch(liveSearch.code, /scraped_jobs|scraped_at|Upsert|60 hari|kron harian/i, 'Live Search must remain distinct from the daily indexed-job ingestion algorithm.');
assert.doesNotMatch(liveSearch.codeEn, /scraped_jobs|scraped_at|Upsert|60 days|daily cron|stale-row/i, 'English Live Search must remain distinct from the daily indexed-job ingestion algorithm.');

const upstreamSources = liveSearch.upstreamSources;
assert.ok(Array.isArray(upstreamSources), 'Live Search must include a verified upstreamSources contract.');
assert.equal(upstreamSources.length, 8, 'Live Search must document exactly eight upstream sources.');
assert.equal(new Set(upstreamSources.map(({ name }) => name)).size, 8, 'Every upstream source name must be unique.');
assert.deepEqual(Array.from(upstreamSources, ({ name }) => name), [
  'Maukerja', 'Hiredly', 'Ricebowl', 'GRADUAN', 'Jora Malaysia', 'JobStreet Malaysia', 'Jobstore', 'Careerjet Malaysia',
]);
assert.equal(upstreamSources.filter(({ kind }) => kind === 'html').length, 5, 'Five sources must use Axios/Cheerio HTML access.');
assert.equal(upstreamSources.filter(({ kind }) => kind === 'scrapling').length, 2, 'Two sources must use Scrapling.');
assert.equal(upstreamSources.filter(({ kind }) => kind === 'api').length, 1, 'Careerjet must be documented as the sole optional API source.');
for (const source of upstreamSources) {
  assert.match(source.website, /^https:\/\//, `${source.name} must link to an HTTPS official website.`);
  assert.ok(source.method && source.methodEn && source.requestScope && source.requestScopeEn, `${source.name} must have bilingual method and request-scope text.`);
  assert.ok(fs.existsSync(path.join(repoRoot, source.implementationFile)), `${source.name} has a missing implementation path: ${source.implementationFile}`);
}
assert.match(upstreamSources.find(({ name }) => name === 'Jobstore').requestScopeEn, /redirect.*generic browse page/i, 'Jobstore must document the observed generic browse-page redirect.');
assert.match(upstreamSources.find(({ name }) => name === 'Careerjet Malaysia').methodEn, /API.*not HTML scraping/i, 'Careerjet must be clearly distinguished from HTML scraping.');

const copiedReportContent = snippets.map((snippet) => `${snippet.code}\n${snippet.caption}\n${snippet.codeEn}\n${snippet.captionEn}`).join('\n');
assert.doesNotMatch(copiedReportContent, /Google\s*Maps|EV[-\s]?charging|pengecas|stesen\s+pengecas|mikro[-\s]*survei|ulasan/i, 'Copied content contains terminology from the obsolete project.');

const highlighterSandbox = { window: {} };
vm.runInNewContext(read('code-snippet-highlighter.js'), highlighterSandbox, { filename: 'code-snippet-highlighter.js' });
const highlighterAPI = highlighterSandbox.window.PETAKERJA_CODE_SNIPPET_HIGHLIGHTER;
assert.ok(highlighterAPI, 'Pseudocode highlighting helpers must be exported to the Explorer.');

for (const snippet of snippets) {
  for (const [language, code] of [['BM', snippet.code], ['English', snippet.codeEn]]) {
    const tokens = highlighterAPI.tokenize(code);
    assert.equal(tokens.map((token) => token.value).join(''), code, `${snippet.id} ${language} highlighting must preserve every visible character.`);
    const tokenTypes = new Set(tokens.map((token) => token.type));
    for (const requiredType of ['control', 'function', 'system']) {
      assert.ok(tokenTypes.has(requiredType), `${snippet.id} ${language} must contain ${requiredType} highlighting.`);
    }
    if (/(["']).*?\1/.test(code)) assert.ok(tokenTypes.has('message'), `${snippet.id} ${language} quoted text must be highlighted as a message.`);
    assert.match(highlighterAPI.highlightHTML(code), /class="pseudo-token pseudo-token--control"/);
  }
}

const tokenizerFixture = `Parallel For each source in SCRAPER_SOURCES
    If response = "<unsafe & value>" Then
        result = SendRequest(POST /api/geo/route(source))
        Upsert result into scraped_jobs
    End If`;
const fixtureTokens = highlighterAPI.tokenize(tokenizerFixture);
assert.equal(fixtureTokens.map((token) => token.value).join(''), tokenizerFixture, 'Tokenizer fixtures must retain exact indentation and line breaks.');
assert.ok(fixtureTokens.some(({ type, value }) => type === 'control' && value === 'Parallel For each'), 'Multiword control structures must remain one semantic token.');
assert.ok(fixtureTokens.some(({ type, value }) => type === 'message' && value === '"<unsafe & value>"'), 'Quoted strings must be recognized before inner text.');
assert.ok(fixtureTokens.some(({ type, value }) => type === 'system' && value === '/api/geo/route'), 'API paths must be highlighted as system/data tokens.');
assert.ok(fixtureTokens.some(({ type, value }) => type === 'function' && value === 'SendRequest'), 'Function calls must be highlighted semantically.');
assert.ok(fixtureTokens.some(({ type, value }) => type === 'system' && value === 'scraped_jobs'), 'Identifiers containing underscores must be highlighted as system/data tokens.');
const liveSystemTokens = highlighterAPI.tokenize('Maukerja Hiredly Ricebowl Graduan Jora JobStreet Jobstore Careerjet Scrapling CAREERJET_AFFID GET /api/search-jobs');
for (const expectedSystem of ['Maukerja', 'Hiredly', 'Ricebowl', 'Graduan', 'Jora', 'JobStreet', 'Jobstore', 'Careerjet', 'Scrapling', 'CAREERJET_AFFID', 'GET', '/api/search-jobs']) {
  assert.ok(liveSystemTokens.some(({ type, value }) => type === 'system' && value === expectedSystem), `${expectedSystem} must use system/data highlighting.`);
}
const escapedFixture = highlighterAPI.highlightHTML(tokenizerFixture);
assert.match(escapedFixture, /&quot;&lt;unsafe &amp; value&gt;&quot;/, 'Highlighted strings must be safely HTML escaped.');
assert.doesNotMatch(escapedFixture, /"<unsafe & value>"/, 'Highlighted output must not contain unsafe source HTML.');

const clipboardSandbox = { window: { PETAKERJA_CODE_SNIPPET_HIGHLIGHTER: highlighterAPI } };
vm.runInNewContext(read('code-snippet-clipboard.js'), clipboardSandbox, { filename: 'code-snippet-clipboard.js' });
const clipboardAPI = clipboardSandbox.window.PETAKERJA_CODE_SNIPPET_CLIPBOARD;
assert.ok(clipboardAPI, 'Clipboard helpers must be exported to the Explorer.');

const indentedCode = 'Function Uji()\n    Return "A&B"\nEnd Function';
const codeHTML = clipboardAPI.codeHTML(indentedCode);
assert.match(codeHTML, /font-family:Consolas,'Cascadia Mono','Courier New',monospace/);
assert.match(codeHTML, /font-size:10pt/);
assert.match(codeHTML, /background-color:#f3f4f6/);
assert.match(codeHTML, /color:#1D4ED8;font-weight:700/, 'Word HTML must include the print-safe control-flow colour and weight.');
assert.match(codeHTML, /color:#6D28D9;font-weight:600/, 'Word HTML must include the print-safe function colour and weight.');
assert.match(codeHTML, /color:#92400E;font-weight:400/, 'Word HTML must include the print-safe message colour.');
assert.match(clipboardAPI.codeHTML(tokenizerFixture), /color:#0F766E;font-weight:600/, 'Word HTML must include the print-safe system/data colour and weight.');
const liveSearchHTML = clipboardAPI.codeHTML(liveSearch.codeEn);
assert.match(liveSearchHTML, /color:#0F766E;font-weight:600;[^>]*>\/api\/search-jobs<\/span>/, 'Word HTML must preserve Live Search system/data highlighting.');
assert.match(liveSearchHTML, /font-family:Consolas,'Cascadia Mono','Courier New',monospace/);
assert.match(codeHTML, /\n    <span[^>]+>Return<\/span> <span[^>]+>&quot;A&amp;B&quot;<\/span>\n/, 'Rich HTML must preserve indentation and escape report content.');

const captionHTML = clipboardAPI.captionHTML('Rajah 3.33 Algoritma & ujian');
assert.match(captionHTML, /text-align:center/);
assert.match(captionHTML, /font-family:'Times New Roman',serif/);
assert.match(captionHTML, /font-size:10pt/);
assert.match(captionHTML, /Algoritma &amp; ujian/);

let richItems = null;
class TestClipboardItem {
  constructor(payload) { this.payload = payload; }
}
const richRuntime = {
  Blob,
  ClipboardItem: TestClipboardItem,
  navigator: { clipboard: { write: async (items) => { richItems = items; } } },
};
assert.equal(await clipboardAPI.writeClipboardPayload(indentedCode, codeHTML, richRuntime), 'rich');
assert.equal(richItems.length, 1);
assert.deepEqual(Object.keys(richItems[0].payload).sort(), ['text/html', 'text/plain']);
assert.equal(await richItems[0].payload['text/plain'].text(), indentedCode);
assert.equal(await richItems[0].payload['text/html'].text(), codeHTML);

let plainFallback = null;
const plainRuntime = {
  navigator: { clipboard: { writeText: async (value) => { plainFallback = value; } } },
};
assert.equal(await clipboardAPI.writeClipboardPayload(indentedCode, codeHTML, plainRuntime), 'plain');
assert.equal(plainFallback, indentedCode);

let selected = false;
let selectionFallback = null;
const selectionRuntime = {
  navigator: {},
  document: {
    createElement: () => ({
      value: '', style: {}, setAttribute() {}, select() { selected = true; }, remove() {},
    }),
    body: { appendChild: (element) => { selectionFallback = element; } },
    execCommand: (command) => command === 'copy',
  },
};
assert.equal(await clipboardAPI.writeClipboardPayload(indentedCode, codeHTML, selectionRuntime), 'selection');
assert.equal(selectionFallback.value, indentedCode);
assert.equal(selected, true);

const appSource = read('app.js');
const styles = read('styles.css');
assert.match(appSource, /petakerja-explorer-code-snippet-folders/);
assert.match(appSource, /petakerja-explorer-code-snippet-language/);
assert.match(appSource, /data-nav-family="code-snippets"/);
assert.match(appSource, /data-snippet-language="ms"/);
assert.match(appSource, /data-snippet-language="en"/);
assert.match(appSource, /codeSnippetText\(diagram\)/);
assert.match(appSource, /codeSnippetHighlighter\.highlightHTML\(snippet\.code\)/);
assert.match(appSource, /Kawalan aliran/);
assert.match(appSource, /Control flow/);
assert.match(appSource, /Sistem\/data/);
assert.match(appSource, /System\/data/);
assert.match(appSource, /data-copy-snippet-code/);
assert.match(appSource, /data-copy-snippet-caption/);
assert.match(appSource, /diagram\.upstreamSources/);
assert.match(appSource, /Verified Live Search sources/);
assert.match(appSource, /Sumber Carian Langsung yang disahkan/);
assert.match(appSource, /target="_blank" rel="noopener noreferrer"/);
for (const heading of ['Source', 'Website', 'Method', 'Request scope', 'Sumber', 'Laman', 'Kaedah', 'Skop permintaan']) assert.match(appSource, new RegExp(heading));
assert.match(appSource, /isCodeDiagram\(\)/);
assert.match(styles, /body\.is-code-snippet-mode \.context-column/);
assert.match(styles, /font: 10pt\/1\.45 Consolas, "Cascadia Mono", "Courier New", monospace/);
assert.match(styles, /user-select: text !important/);
assert.match(styles, /--code-control: #1d4ed8/);
assert.match(styles, /--code-control: #7dd3fc/);
assert.match(styles, /\.pseudo-token--function/);
assert.match(styles, /\.code-snippet-legend/);
assert.match(styles, /\.code-upstream-table-wrap/);
assert.match(styles, /overflow-x: auto/);
assert.match(styles, /min-width: 760px/);

console.log('Five code snippets, the verified Live Search source table, bilingual semantic highlighting, copy payloads, fallbacks and presentation contract passed.');
