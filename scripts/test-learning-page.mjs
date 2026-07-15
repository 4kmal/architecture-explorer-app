import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import vm from 'node:vm';
import { fileURLToPath } from 'node:url';

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const read = (name) => fs.readFileSync(path.join(root, name), 'utf8');
const context = vm.createContext({ window: {} });
['architecture-data.js', 'diagram-assets.js', 'learning-data.js'].forEach((name) => vm.runInContext(read(name), context, { filename: name }));

const learning = context.window.PETAKERJA_LEARNING;
const assets = context.window.PETAKERJA_DIAGRAM_ASSETS;
assert.ok(learning, 'window.PETAKERJA_LEARNING must exist');
assert.equal(learning.chapters.length, 10, 'expected ten learning chapters');
assert.ok(learning.topics.length >= 60, 'expected a broad notation gallery');
assert.equal(learning.quizQuestions.length, 20, 'expected two quiz questions per chapter');

const chapterIds = new Set(learning.chapters.map((chapter) => chapter.id));
const topicIds = new Set();
for (const topic of learning.topics) {
  assert.ok(!topicIds.has(topic.id), `duplicate topic ID: ${topic.id}`);
  topicIds.add(topic.id);
  assert.ok(chapterIds.has(topic.chapterId), `${topic.id} has an unknown chapter`);
  for (const key of ['title', 'purpose', 'howToRead', 'whenToUse', 'commonMistakes']) {
    assert.ok(topic[key]?.en && topic[key]?.ms, `${topic.id}.${key} must be bilingual`);
  }
  assert.ok(Array.isArray(topic.aliases), `${topic.id} must provide searchable aliases`);
  (topic.sources || []).forEach((sourceId) => assert.ok(learning.sources[sourceId], `${topic.id} references missing source ${sourceId}`));
  for (const ref of topic.explorerRefs || []) {
    const asset = assets[ref.diagramId];
    assert.ok(asset, `${topic.id} references missing diagram ${ref.diagramId}`);
    if (ref.componentKey) {
      const match = asset.components?.some((component) => component.componentKey === ref.componentKey
        || component.nodeIds?.includes(ref.componentKey)
        || component.tableName === ref.componentKey.replace(/^table:/, ''));
      assert.ok(match, `${topic.id} references missing component ${ref.diagramId}/${ref.componentKey}`);
    }
  }
}

for (const chapter of learning.chapters) {
  assert.ok(chapter.title?.en && chapter.title?.ms && chapter.summary?.en && chapter.summary?.ms, `${chapter.id} must be bilingual`);
  assert.ok(chapter.topicIds.length > 0, `${chapter.id} has no topics`);
  chapter.topicIds.forEach((id) => assert.ok(topicIds.has(id), `${chapter.id} references missing topic ${id}`));
  assert.equal(learning.quizQuestions.filter((question) => question.chapterId === chapter.id).length, 2, `${chapter.id} must have two quiz questions`);
}

const coveredKinds = new Set(learning.topics.flatMap((topic) => topic.covers || []));
const assetKinds = new Set(Object.values(assets).flatMap((asset) => (asset.connections || []).map((connection) => connection.kind)));
assetKinds.forEach((kind) => assert.ok(coveredKinds.has(kind), `Explorer connection kind has no lesson: ${kind}`));

const searchable = learning.topics.flatMap((topic) => [topic.title.en, topic.title.ms, ...topic.aliases]).join(' ').toLocaleLowerCase();
['u-turn', 'self-call', 'dashed line', 'solid line', 'optional', 'alternative', 'opt', 'alt', 'diamond', "crow's foot", 'garisan putus-putus'].forEach((alias) => {
  assert.ok(searchable.includes(alias.toLocaleLowerCase()), `missing search alias: ${alias}`);
});

const html = read('index.html');
const app = read('app.js');
const runtime = read('learning.js');
const css = read('styles.css');
for (const id of ['learning-link', 'learning-shell', 'learning-nav', 'learning-reader', 'learning-example-panel', 'learning-quiz-panel', 'learning-mobile-topic']) {
  assert.ok(html.includes(`id="${id}"`), `index.html is missing #${id}`);
}
assert.ok(html.includes('src="learning-data.js') && html.includes('src="learning.js'), 'learning scripts must be loaded');
assert.ok(runtime.includes("'#learn'") && runtime.includes('petakerja-explorer-learning-progress:v1'), 'hash route and progress store must exist');
assert.ok(runtime.includes('petakerja:open-example') && app.includes('openExplorerExample'), 'Explorer deep-link bridge must exist');
assert.ok(css.includes('body.is-learning-mode') && css.includes('.learning-mobile-tabs'), 'learning and responsive CSS must exist');
assert.ok(!/\bfetch\s*\(/.test(read('learning.js')) && !/\bfetch\s*\(/.test(read('learning-data.js')), 'the learning workspace must not make runtime network requests');
assert.ok(!/linear-gradient|radial-gradient|conic-gradient/i.test(css), 'gradients are not allowed');

console.log(`Learning page contract OK: ${learning.chapters.length} chapters, ${learning.topics.length} topics, ${learning.quizQuestions.length} quiz questions, ${assetKinds.size} Explorer connection kinds.`);
