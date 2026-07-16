(function () {
  'use strict';

  class ReadOnlyEditorController {
    constructor(options = {}) {
      this.callbacks = options.callbacks || {};
      this.available = false;
      this.ready = false;
      this.dirty = false;
      this.workingXml = '';
      this.documentSnapshot = null;
      this.analysis = null;
      this.diagramId = null;
      this.pageId = null;
      this.themePreference = options.themePreference || 'system';
    }

    startFrame() {}
    post() {}
    setLanguage() {}
    setThemePreference(preference) { this.themePreference = preference; }
    openCanonical() {}
    openXML() {}
    newSession() {}
    markClean() { this.dirty = false; }
    saveAs() {}
    focusComponent() {}
    focusMatch() {}
    resolveMatch() { return null; }
    preflight() { return { fatal: true, pages: [], selectedPage: null }; }
    validateNow() { return this.analysis || { fatal: false, issues: [], pages: [] }; }
    async exportRuntimeSVG() { return null; }
  }

  class DisabledDiagramAgent {
    constructor() { this.plan = null; }
    configure() {}
    setPlan(plan) { this.plan = plan || null; }
    decision() {}
    stop() {}
    async propose() { throw new Error('Agent Mode is available only in the trusted local Explorer.'); }
    async run() { throw new Error('Agent Mode is available only in the trusted local Explorer.'); }
    async revert() { throw new Error('Agent Mode is available only in the trusted local Explorer.'); }
    async testConnection() { throw new Error('Agent Mode is available only in the trusted local Explorer.'); }
  }

  window.PETAKERJA_EDITOR = Object.freeze({
    createController(options) { return new ReadOnlyEditorController(options); },
  });
  window.PETAKERJA_AGENT = Object.freeze({ DiagramAgent: DisabledDiagramAgent });
}());
