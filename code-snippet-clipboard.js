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

  function sourceTablePayload(sources, language = 'ms') {
    const english = language === 'en';
    const headings = english
      ? ['Source', 'Website', 'Method', 'Request scope']
      : ['Sumber', 'Laman', 'Kaedah', 'Skop permintaan'];
    const rows = (Array.isArray(sources) ? sources : []).map((source) => {
      const website = /^https:\/\//i.test(String(source.website || '')) ? String(source.website) : '';
      return [
        String(source.name || ''),
        website,
        String(english ? source.methodEn || source.method || '' : source.method || ''),
        String(english ? source.requestScopeEn || source.requestScope || '' : source.requestScope || ''),
      ];
    });
    const plainText = [headings, ...rows].map((row) => row.join('\t')).join('\n');
    const cellStyle = "border:1px solid #b7b7b7;padding:4pt 6pt;text-align:left;vertical-align:top;";
    const headingCells = headings.map((heading) => `<th style="${cellStyle}background-color:#f3f4f6;font-weight:700;">${escapeHTML(heading)}</th>`).join('');
    const bodyRows = rows.map(([name, website, method, requestScope]) => {
      const websiteCell = website
        ? `<a href="${escapeHTML(website)}" style="color:#0563C1;text-decoration:underline;">${escapeHTML(website)}</a>`
        : '';
      return `<tr><th scope="row" style="${cellStyle}font-weight:700;">${escapeHTML(name)}</th><td style="${cellStyle}">${websiteCell}</td><td style="${cellStyle}">${escapeHTML(method)}</td><td style="${cellStyle}">${escapeHTML(requestScope)}</td></tr>`;
    }).join('');
    const htmlText = `<table style="border-collapse:collapse;color:#000000;font-family:'Times New Roman',serif;font-size:10pt;line-height:1.25;"><thead><tr>${headingCells}</tr></thead><tbody>${bodyRows}</tbody></table>`;
    return { plainText, htmlText };
  }

  function markerFlowPayload(title, steps) {
    const safeTitle = String(title || '');
    const safeSteps = (Array.isArray(steps) ? steps : []).map((step) => String(step || ''));
    const plainText = [safeTitle, safeSteps.join('\n        ↓\n')].filter(Boolean).join('\n');
    const titleHTML = safeTitle
      ? `<p style="margin:0 0 6pt;text-align:center;color:#000000;font-family:'Times New Roman',serif;font-size:10pt;line-height:1.25;font-weight:700;">${escapeHTML(safeTitle)}</p>`
      : '';
    const stepStyle = 'border:1px solid #b7b7b7;padding:6pt 8pt;background-color:#f3f4f6;text-align:center;vertical-align:middle;';
    const arrowStyle = 'border:0;padding:2pt 8pt;text-align:center;vertical-align:middle;font-weight:700;';
    const rows = safeSteps.map((step, index) => {
      const stepRow = `<tr><td style="${stepStyle}">${escapeHTML(step)}</td></tr>`;
      const arrowRow = index < safeSteps.length - 1 ? `<tr><td style="${arrowStyle}">↓</td></tr>` : '';
      return `${stepRow}${arrowRow}`;
    }).join('');
    const tableHTML = `<table style="width:100%;border-collapse:collapse;color:#000000;font-family:'Times New Roman',serif;font-size:10pt;line-height:1.25;"><tbody>${rows}</tbody></table>`;
    return { plainText, htmlText: `${titleHTML}${tableHTML}` };
  }

  function reportCellPlain(value) {
    if (Array.isArray(value)) return value.map((item, index) => `${index + 1}. ${String(item || '')}`).join(' ');
    return String(value ?? '');
  }

  function reportCellHTML(value) {
    if (!Array.isArray(value)) return escapeHTML(value);
    const items = value.map((item) => `<li style="margin:0 0 2pt;padding:0;">${escapeHTML(item)}</li>`).join('');
    return `<ol style="margin:0;padding-left:16pt;">${items}</ol>`;
  }

  function reportTablePayload(table) {
    const safeTable = table && typeof table === 'object' ? table : {};
    const title = String(safeTable.title || '');
    const source = String(safeTable.source || '');
    const note = String(safeTable.note || '');
    const sourceLabel = String(safeTable.sourceLabel || 'Sumber');
    const noteLabel = String(safeTable.noteLabel || 'Catatan');
    const columns = (Array.isArray(safeTable.columns) ? safeTable.columns : []).map((column) => ({
      label: String(column?.label || ''),
      width: /^\d+(?:\.\d+)?%$/.test(String(column?.width || '')) ? String(column.width) : '',
    }));
    const rows = (Array.isArray(safeTable.rows) ? safeTable.rows : []).map((row) => Array.isArray(row) ? row : []);
    const rowHeaderIndex = Number.isInteger(safeTable.rowHeaderIndex) ? safeTable.rowHeaderIndex : -1;
    const plainLines = [];
    if (title) plainLines.push(title);
    if (source) plainLines.push(`${sourceLabel}: ${source}`);
    if (columns.length) plainLines.push(columns.map((column) => column.label).join('\t'));
    rows.forEach((row) => plainLines.push(columns.map((_column, index) => reportCellPlain(row[index])).join('\t')));
    if (note) plainLines.push(`${noteLabel}: ${note}`);

    const cellStyle = 'border:1px solid #000000;padding:4pt 5pt;text-align:left;vertical-align:top;color:#000000;background-color:#ffffff;';
    const titleHTML = title
      ? `<p style="margin:0 0 5pt;text-align:center;color:#000000;font-family:'Times New Roman',serif;font-size:10pt;line-height:1.25;font-weight:700;">${escapeHTML(title)}</p>`
      : '';
    const sourceHTML = source
      ? `<p style="margin:0 0 4pt;color:#000000;font-family:'Times New Roman',serif;font-size:9pt;line-height:1.2;"><strong>${escapeHTML(sourceLabel)}:</strong> ${escapeHTML(source)}</p>`
      : '';
    const colgroup = columns.some((column) => column.width)
      ? `<colgroup>${columns.map((column) => `<col${column.width ? ` style="width:${column.width};"` : ''}>`).join('')}</colgroup>`
      : '';
    const headingCells = columns.map((column) => `<th scope="col" style="${cellStyle}font-weight:700;">${escapeHTML(column.label)}</th>`).join('');
    const bodyRows = rows.map((row) => `<tr>${columns.map((_column, index) => {
      const tag = index === rowHeaderIndex ? 'th' : 'td';
      const scope = index === rowHeaderIndex ? ' scope="row"' : '';
      const weight = index === rowHeaderIndex ? 'font-weight:700;' : '';
      return `<${tag}${scope} style="${cellStyle}${weight}">${reportCellHTML(row[index])}</${tag}>`;
    }).join('')}</tr>`).join('');
    const tableHTML = `<table border="1" cellspacing="0" cellpadding="0" style="width:100%;border:1px solid #000000;border-collapse:collapse;table-layout:fixed;color:#000000;background-color:#ffffff;font-family:'Times New Roman',serif;font-size:10pt;line-height:1.25;">${colgroup}<thead><tr>${headingCells}</tr></thead><tbody>${bodyRows}</tbody></table>`;
    const noteHTML = note
      ? `<p style="margin:5pt 0 0;color:#000000;font-family:'Times New Roman',serif;font-size:9pt;line-height:1.2;"><strong>${escapeHTML(noteLabel)}:</strong> ${escapeHTML(note)}</p>`
      : '';
    return { plainText: plainLines.join('\n'), htmlText: `${titleHTML}${sourceHTML}${tableHTML}${noteHTML}` };
  }

  function reportTableFragmentPayload(table, fragment = {}) {
    const safeTable = table && typeof table === 'object' ? table : {};
    const columns = (Array.isArray(safeTable.columns) ? safeTable.columns : []).map((column) => ({
      label: String(column?.label || ''),
    }));
    const rows = (Array.isArray(safeTable.rows) ? safeTable.rows : []).map((row) => Array.isArray(row) ? row : []);
    const rowHeaderIndex = Number.isInteger(safeTable.rowHeaderIndex) ? safeTable.rowHeaderIndex : -1;
    const columnIndex = Number.isInteger(fragment.columnIndex) ? fragment.columnIndex : -1;
    const rowIndex = Number.isInteger(fragment.rowIndex) ? fragment.rowIndex : -1;
    const kind = ['cell', 'row', 'column'].includes(fragment.kind) ? fragment.kind : 'cell';
    const cellStyle = 'border:1px solid #000000;padding:4pt 5pt;text-align:left;vertical-align:top;color:#000000;background-color:#ffffff;';
    const tableStyle = "width:100%;border:1px solid #000000;border-collapse:collapse;table-layout:fixed;color:#000000;background-color:#ffffff;font-family:'Times New Roman',serif;font-size:10pt;line-height:1.25;";
    const cell = (tag, value, scope = '') => `<${tag}${scope} style="${cellStyle}${tag === 'th' ? 'font-weight:700;' : ''}">${reportCellHTML(value)}</${tag}>`;
    let plainText = '';
    let tableRows = '';

    if (kind === 'column' && columnIndex >= 0 && columnIndex < columns.length) {
      plainText = [columns[columnIndex].label, ...rows.map((row) => reportCellPlain(row[columnIndex]))].join('\n');
      const heading = cell('th', columns[columnIndex].label, ' scope="col"');
      const body = rows.map((row) => {
        const tag = columnIndex === rowHeaderIndex ? 'th' : 'td';
        const scope = tag === 'th' ? ' scope="row"' : '';
        return `<tr>${cell(tag, row[columnIndex], scope)}</tr>`;
      }).join('');
      tableRows = `<thead><tr>${heading}</tr></thead><tbody>${body}</tbody>`;
    } else if (kind === 'row') {
      const values = rowIndex < 0 ? columns.map((column) => column.label) : (rows[rowIndex] || []);
      plainText = columns.map((_column, index) => reportCellPlain(values[index])).join('\t');
      const cells = columns.map((_column, index) => {
        const header = rowIndex < 0 || index === rowHeaderIndex;
        const scope = rowIndex < 0 ? ' scope="col"' : (index === rowHeaderIndex ? ' scope="row"' : '');
        return cell(header ? 'th' : 'td', values[index], scope);
      }).join('');
      tableRows = rowIndex < 0 ? `<thead><tr>${cells}</tr></thead>` : `<tbody><tr>${cells}</tr></tbody>`;
    } else {
      const header = rowIndex < 0;
      const value = header ? columns[columnIndex]?.label : rows[rowIndex]?.[columnIndex];
      plainText = reportCellPlain(value);
      const tag = header || columnIndex === rowHeaderIndex ? 'th' : 'td';
      const scope = header ? ' scope="col"' : (columnIndex === rowHeaderIndex ? ' scope="row"' : '');
      tableRows = header ? `<thead><tr>${cell(tag, value, scope)}</tr></thead>` : `<tbody><tr>${cell(tag, value, scope)}</tr></tbody>`;
    }

    return {
      plainText,
      htmlText: `<table border="1" cellspacing="0" cellpadding="0" style="${tableStyle}">${tableRows}</table>`,
    };
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
    sourceTablePayload,
    markerFlowPayload,
    reportTablePayload,
    reportTableFragmentPayload,
    writeClipboardPayload,
  });
}());
