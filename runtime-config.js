(function () {
  'use strict';

  const integratedPrefix = '/architecture-explorer';
  const integrated = window.location.pathname === integratedPrefix
    || window.location.pathname.startsWith(`${integratedPrefix}/`);
  const apiBase = integrated ? `${integratedPrefix}/api` : '/api';

  window.PETAKERJA_EXPLORER_RUNTIME = Object.freeze({
    integrated,
    lite: false,
    edition: 'local-full',
    capabilities: Object.freeze({
      editor: true,
      import: true,
      cloudDiagrams: true,
      localWorkspace: true,
      agent: true,
      mcp: true,
      realtime: false,
    }),
    apiBase,
    cloudApiBase: '/api/architecture-explorer',
    api(path) {
      const suffix = String(path || '').replace(/^\/+/, '');
      return `${apiBase}/${suffix}`;
    },
  });
}());
