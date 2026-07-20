(function () {
  'use strict';

  const highlighter = window.PETAKERJA_CODE_SNIPPET_HIGHLIGHTER;

  function escapeHTML(value) {
    return String(value ?? '').replace(/[&<>'"]/g, (character) => ({
      '&': '&amp;', '<': '&lt;', '>': '&gt;', "'": '&#39;', '"': '&quot;',
    }[character]));
  }

  function codeHTML(code) {
    const highlightedCode = highlighter?.highlightHTML(code, { mode: 'word' }) || escapeHTML(code);
    return `<pre style="margin:0;padding:8pt;border:1px solid #d9d9d9;background-color:#f3f4f6;color:#000000;font-family:Consolas,'Cascadia Mono','Courier New',monospace;font-size:10pt;line-height:1.25;white-space:pre-wrap;tab-size:4;">${highlightedCode}</pre>`;
  }

  function captionHTML(caption) {
    return `<p style="margin:0;text-align:center;color:#000000;font-family:'Times New Roman',serif;font-size:10pt;line-height:1.25;">${escapeHTML(caption)}</p>`;
  }

  async function writeClipboardPayload(plainText, htmlText, runtime = window) {
    const clipboard = runtime.navigator?.clipboard;
    if (clipboard?.write && typeof runtime.ClipboardItem === 'function' && typeof runtime.Blob === 'function') {
      try {
        const item = new runtime.ClipboardItem({
          'text/html': new runtime.Blob([htmlText], { type: 'text/html' }),
          'text/plain': new runtime.Blob([plainText], { type: 'text/plain' }),
        });
        await clipboard.write([item]);
        return 'rich';
      } catch (_error) { /* Continue to the plain-text clipboard fallbacks. */ }
    }
    if (clipboard?.writeText) {
      try {
        await clipboard.writeText(plainText);
        return 'plain';
      } catch (_error) { /* Continue to temporary selection copying. */ }
    }
    const textarea = runtime.document.createElement('textarea');
    textarea.value = plainText;
    textarea.setAttribute('readonly', '');
    textarea.style.position = 'fixed';
    textarea.style.inset = '0 auto auto -9999px';
    textarea.style.opacity = '0';
    runtime.document.body.appendChild(textarea);
    textarea.select();
    runtime.document.execCommand('copy');
    textarea.remove();
    return 'selection';
  }

  window.PETAKERJA_CODE_SNIPPET_CLIPBOARD = Object.freeze({
    codeHTML,
    captionHTML,
    writeClipboardPayload,
  });
}());
