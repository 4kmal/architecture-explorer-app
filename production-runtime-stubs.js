(function () {
  'use strict';

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

  window.PETAKERJA_AGENT = Object.freeze({ DiagramAgent: DisabledDiagramAgent });
}());
