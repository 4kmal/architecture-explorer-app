(function () {
  'use strict';

  const CONTROL_PHRASES = Object.freeze([
    'Parallel For each',
    'End Function',
    'End If',
    'End For',
    'End Try',
    'Else If',
    'For each',
  ]);

  const CONTROL_WORDS = new Set([
    'Function', 'If', 'Then', 'Else', 'Return', 'Try', 'Catch', 'Continue', 'Await', 'When',
    'OR', 'AND', 'Jika', 'Untuk', 'Apabila',
  ]);

  const SYSTEM_WORDS = new Set([
    'MapLibre', 'Valhalla', 'Haversine', 'GeoJSON', 'Supabase', 'Nominatim', 'GeoGateway', 'PetaKerja',
    'POI', 'OSM', 'ETA', 'POST', 'GET', 'Highlight', 'Maukerja', 'Hiredly', 'Ricebowl',
    'Graduan', 'GRADUAN', 'Jora', 'JobStreet', 'Jobstore', 'Careerjet', 'Scrapling', 'Axios',
    'Cheerio', 'CAREERJET_AFFID',
  ]);

  const WORD_STYLES = Object.freeze({
    control: 'color:#1D4ED8;font-weight:700;',
    function: 'color:#6D28D9;font-weight:600;',
    message: 'color:#92400E;font-weight:400;',
    system: 'color:#0F766E;font-weight:600;',
  });

  function escapeHTML(value) {
    return String(value ?? '').replace(/[&<>'"]/g, (character) => ({
      '&': '&amp;', '<': '&lt;', '>': '&gt;', "'": '&#39;', '"': '&quot;',
    }[character]));
  }

  function isIdentifierCharacter(character) {
    return Boolean(character && /[A-Za-z0-9_]/.test(character));
  }

  function controlPhraseAt(source, index) {
    if (isIdentifierCharacter(source[index - 1])) return '';
    for (const phrase of CONTROL_PHRASES) {
      if (!source.startsWith(phrase, index)) continue;
      if (!isIdentifierCharacter(source[index + phrase.length])) return phrase;
    }
    return '';
  }

  function readQuotedString(source, index) {
    const quote = source[index];
    if (quote !== '"' && quote !== "'") return '';
    let cursor = index + 1;
    while (cursor < source.length) {
      if (source[cursor] === '\\') {
        cursor += 2;
        continue;
      }
      if (source[cursor] === quote) return source.slice(index, cursor + 1);
      if (source[cursor] === '\n' || source[cursor] === '\r') break;
      cursor += 1;
    }
    return source.slice(index, cursor);
  }

  function readAPIPath(source, index) {
    if (!source.startsWith('/api/', index)) return '';
    return source.slice(index).match(/^\/api\/[A-Za-z0-9_./-]+/)?.[0] || '';
  }

  function readIdentifier(source, index) {
    return source.slice(index).match(/^[A-Za-z_][A-Za-z0-9_]*(?:\.[A-Za-z_][A-Za-z0-9_]*)*/)?.[0] || '';
  }

  function isFunctionCall(source, indexAfterIdentifier) {
    let cursor = indexAfterIdentifier;
    while (cursor < source.length && /[ \t]/.test(source[cursor])) cursor += 1;
    return source[cursor] === '(';
  }

  function isSystemIdentifier(identifier) {
    if (SYSTEM_WORDS.has(identifier)) return true;
    if (identifier.includes('_')) return true;
    return /^[A-Z][A-Z0-9_]*$/.test(identifier);
  }

  function tokenize(code) {
    const source = String(code ?? '');
    const tokens = [];
    let index = 0;

    function add(type, value) {
      if (!value) return;
      const previous = tokens[tokens.length - 1];
      if (type === 'neutral' && previous?.type === type) previous.value += value;
      else tokens.push({ type, value });
    }

    while (index < source.length) {
      const quotedString = readQuotedString(source, index);
      if (quotedString) {
        add('message', quotedString);
        index += quotedString.length;
        continue;
      }

      const apiPath = readAPIPath(source, index);
      if (apiPath) {
        add('system', apiPath);
        index += apiPath.length;
        continue;
      }

      const controlPhrase = controlPhraseAt(source, index);
      if (controlPhrase) {
        add('control', controlPhrase);
        index += controlPhrase.length;
        continue;
      }

      const identifier = readIdentifier(source, index);
      if (identifier) {
        const indexAfterIdentifier = index + identifier.length;
        if (CONTROL_WORDS.has(identifier)) add('control', identifier);
        else if (isFunctionCall(source, indexAfterIdentifier)) add('function', identifier);
        else if (isSystemIdentifier(identifier)) add('system', identifier);
        else add('neutral', identifier);
        index = indexAfterIdentifier;
        continue;
      }

      add('neutral', source[index]);
      index += 1;
    }

    return tokens;
  }

  function highlightHTML(code, options = {}) {
    const wordMode = options.mode === 'word';
    return tokenize(code).map(({ type, value }) => {
      const escaped = escapeHTML(value);
      if (type === 'neutral') return escaped;
      if (wordMode) return `<span style="${WORD_STYLES[type]}">${escaped}</span>`;
      return `<span class="pseudo-token pseudo-token--${type}">${escaped}</span>`;
    }).join('');
  }

  window.PETAKERJA_CODE_SNIPPET_HIGHLIGHTER = Object.freeze({
    tokenize,
    highlightHTML,
    escapeHTML,
  });
}());
