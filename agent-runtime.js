(function () {
  'use strict';

  const policy = window.PETAKERJA_OPENAI_POLICY || { reviewedAt: '1970-01-01', defaultModel: 'gpt-5.6-terra', deprecated: {} };
  const ALLOWED_TYPES = new Set(['createPage', 'createComponent', 'updateComponent', 'moveResize', 'connect', 'delete', 'applyLayout']);
  const COMPONENT_TYPES = new Set(['class', 'entity', 'interface', 'service', 'actor', 'usecase', 'table', 'note', 'lifeline', 'activation', 'combinedFragment']);
  const PARTICIPANT_TYPES = new Set(['actor', 'boundary', 'control', 'entity', 'object']);
  const RELATION_KINDS = new Set(['association', 'dependency', 'aggregation', 'composition', 'logical', 'include', 'extend', 'sequence-sync', 'sequence-async', 'sequence-return', 'sequence-self']);
  const LAYOUTS = new Set(['hierarchical', 'circle', 'sequence']);
  const PROVIDERS = new Set(['openai', 'compatible', 'codex']);
  const localAPI = (path) => window.PETAKERJA_EXPLORER_RUNTIME?.api(path) || `/api/${String(path || '').replace(/^\/+/, '')}`;

  function endpoint(baseURL, path) {
    const clean = String(baseURL || '').trim().replace(/\/+$/, '');
    if (!clean) throw new Error('Base URL is required.');
    return `${clean}${path}`;
  }

  function compact(value) {
    if (Array.isArray(value)) return value.map(compact);
    if (!value || typeof value !== 'object') return value;
    return Object.fromEntries(Object.entries(value).filter(([, entry]) => entry !== null).map(([key, entry]) => [key, compact(entry)]));
  }

  function safePlan(value) {
    if (!value || typeof value !== 'object' || !Array.isArray(value.operations)) throw new Error('The model did not return a DiagramPlan.');
    const plan = {
      id: String(value.id || `plan-${Date.now()}`),
      title: String(value.title || 'Diagram plan'),
      diagramType: String(value.diagramType || 'unknown'),
      summary: String(value.summary || ''),
      warnings: Array.isArray(value.warnings) ? value.warnings.map(String) : [],
      operations: value.operations.map((operation, index) => validateOperation(compact(operation), index)),
    };
    if (!plan.operations.length) throw new Error('The DiagramPlan contains no operations.');
    if (plan.operations.length > 160) throw new Error('The DiagramPlan exceeds the 160-operation safety limit.');
    return plan;
  }

  function validGeometry(value, requirePosition = false) {
    if (!value || typeof value !== 'object') return false;
    if (requirePosition && (!Number.isFinite(Number(value.x)) || !Number.isFinite(Number(value.y)))) return false;
    return ['x', 'y', 'width', 'height'].every((key) => value[key] == null || Number.isFinite(Number(value[key])));
  }

  function validateOperation(operation, index = 0) {
    if (!operation || !ALLOWED_TYPES.has(operation.type)) throw new Error(`Operation ${index + 1} has an unsupported type.`);
    const result = JSON.parse(JSON.stringify(operation));
    if (result.type === 'createPage') {
      if (!result.name || !result.diagramType) throw new Error(`Operation ${index + 1} needs a page name and diagramType.`);
    } else if (result.type === 'createComponent') {
      if (!result.key || result.label == null) throw new Error(`Operation ${index + 1} needs key and label.`);
      if (!COMPONENT_TYPES.has(result.componentType)) throw new Error(`Operation ${index + 1} has an unsupported componentType.`);
      if (!validGeometry(result.geometry, true)) throw new Error(`Operation ${index + 1} needs valid geometry.`);
      if (result.componentType === 'lifeline' && result.participantType && !PARTICIPANT_TYPES.has(result.participantType)) throw new Error(`Operation ${index + 1} has an unsupported participantType.`);
    } else if (result.type === 'updateComponent') {
      if (!result.key) throw new Error(`Operation ${index + 1} needs a component key.`);
    } else if (result.type === 'moveResize') {
      if (!result.key || !validGeometry(result.geometry)) throw new Error(`Operation ${index + 1} needs a component key and geometry.`);
    } else if (result.type === 'connect') {
      if (!result.key || !result.sourceKey || !result.targetKey || !RELATION_KINDS.has(result.relationKind)) throw new Error(`Operation ${index + 1} has an invalid connection.`);
      if (result.geometry && !validGeometry(result.geometry)) throw new Error(`Operation ${index + 1} has invalid connection geometry.`);
    } else if (result.type === 'delete') {
      if (!Array.isArray(result.keys) || !result.keys.length) throw new Error(`Operation ${index + 1} needs keys to delete.`);
    } else if (result.type === 'applyLayout' && !LAYOUTS.has(result.algorithm)) {
      throw new Error(`Operation ${index + 1} has an unsupported layout.`);
    }
    return result;
  }

  function nullable(type) { return { type: [type, 'null'] }; }
  const operationProperties = {
    type: { type: 'string', enum: [...ALLOWED_TYPES] },
    name: nullable('string'), diagramType: nullable('string'), key: nullable('string'),
    componentType: { type: ['string', 'null'], enum: [...COMPONENT_TYPES, null] },
    participantType: { type: ['string', 'null'], enum: [...PARTICIPANT_TYPES, null] },
    label: nullable('string'), stylePreset: nullable('string'), sourceKey: nullable('string'), targetKey: nullable('string'),
    relationKind: { type: ['string', 'null'], enum: [...RELATION_KINDS, null] },
    algorithm: { type: ['string', 'null'], enum: [...LAYOUTS, null] },
    compartments: { type: ['array', 'null'], items: { type: 'string' } },
    geometry: {
      type: ['object', 'null'],
      properties: { x: nullable('number'), y: nullable('number'), width: nullable('number'), height: nullable('number') },
      required: ['x', 'y', 'width', 'height'], additionalProperties: false,
    },
    multiplicities: {
      type: ['object', 'null'], properties: { source: nullable('string'), target: nullable('string') },
      required: ['source', 'target'], additionalProperties: false,
    },
    keys: { type: ['array', 'null'], items: { type: 'string' } },
  };
  const DIAGRAM_PLAN_SCHEMA = {
    type: 'object', additionalProperties: false,
    properties: {
      id: { type: 'string' }, title: { type: 'string' }, diagramType: { type: 'string' }, summary: { type: 'string' },
      warnings: { type: 'array', items: { type: 'string' } },
      operations: { type: 'array', minItems: 1, maxItems: 160, items: { type: 'object', properties: operationProperties, required: Object.keys(operationProperties), additionalProperties: false } },
    },
    required: ['id', 'title', 'diagramType', 'summary', 'warnings', 'operations'],
  };

  function extractJSON(text) {
    const source = String(text || '').trim().replace(/^```(?:json)?\s*/i, '').replace(/\s*```$/, '');
    try { return JSON.parse(source); } catch (_error) {
      const start = source.indexOf('{'); const end = source.lastIndexOf('}');
      if (start >= 0 && end > start) return JSON.parse(source.slice(start, end + 1));
      throw new Error('The model response is not valid JSON.');
    }
  }

  function extractResponsesText(payload) {
    if (payload?.status === 'incomplete') {
      const reason = payload.incomplete_details?.reason || 'unknown reason';
      throw new Error(`OpenAI returned an incomplete response (${reason}).`);
    }
    let refusal = '';
    const text = [];
    (payload?.output || []).forEach((item) => (item?.content || []).forEach((content) => {
      if (content?.type === 'output_text' && typeof content.text === 'string') text.push(content.text);
      if (content?.type === 'refusal') refusal = content.refusal || content.text || 'The model refused the request.';
    }));
    if (refusal) throw new Error(`OpenAI refusal: ${refusal}`);
    if (!text.length) throw new Error('OpenAI returned no output_text content.');
    return text.join('');
  }

  function buildOpenAIResponsesRequest(model, systemPrompt, userContent) {
    return {
      model,
      reasoning: { effort: 'medium' },
      store: false,
      input: [{ role: 'system', content: systemPrompt }, { role: 'user', content: userContent }],
      text: { format: { type: 'json_schema', name: 'diagram_plan', strict: true, schema: DIAGRAM_PLAN_SCHEMA } },
    };
  }

  function redact(value, secret) {
    const text = String(value || '');
    return secret ? text.split(secret).join('[redacted]') : text;
  }

  function policyAgeDays() { return Math.floor((Date.now() - new Date(`${policy.reviewedAt}T00:00:00Z`).getTime()) / 86400000); }
  function policyStatus(model) {
    const deprecated = policy.deprecated?.[model];
    return deprecated ? { state: 'blocked', ...deprecated } : { state: 'unknown', id: model, replacement: null, shutdownDate: null };
  }

  async function responseError(response, fallback) {
    let payload = null;
    try { payload = await response.json(); } catch (_error) { /* Fall through to status text. */ }
    const message = payload?.error?.message || payload?.error || `${response.status} ${response.statusText}`;
    const prefix = response.status === 401 ? 'Authentication failed' : response.status === 429 ? 'Rate limit reached' : fallback;
    return new Error(`${prefix}: ${message}`);
  }

  class DiagramAgent {
    constructor(options) {
      this.editor = options.editor; this.getContext = options.getContext; this.callbacks = options.callbacks || {};
      this.plan = null; this.decision = 'none'; this.preRunXml = ''; this.preRunDocument = null;
      this.running = false; this.stopRequested = false;
      this.credentials = { provider: 'openai', baseURL: 'https://api.openai.com/v1', model: policy.defaultModel, apiKey: '' };
      this.availableModels = new Set();
    }

    configure(credentials) {
      const provider = PROVIDERS.has(credentials.provider) ? credentials.provider : 'openai';
      this.credentials = {
        provider,
        baseURL: provider === 'openai' ? 'https://api.openai.com/v1' : String(credentials.baseURL || '').trim(),
        model: String(credentials.model || (provider === 'openai' ? policy.defaultModel : '')).trim(),
        apiKey: String(credentials.apiKey || ''),
      };
      this.emitProviderStatus();
    }

    headers() {
      const headers = { 'Content-Type': 'application/json' };
      if (this.credentials.apiKey) headers.Authorization = `Bearer ${this.credentials.apiKey}`;
      return headers;
    }

    log(kind, message, meta = {}) { this.callbacks.onLog?.({ time: new Date().toISOString(), kind, message: redact(message, this.credentials.apiKey), meta }); }
    setState(value) { this.callbacks.onState?.(value); }

    emitProviderStatus(remoteStatus) {
      const provider = this.credentials.provider;
      let model = provider === 'openai' ? policyStatus(this.credentials.model) : { state: provider === 'codex' ? 'bridge' : 'unverified', id: this.credentials.model };
      if (provider === 'openai' && model.state !== 'blocked' && remoteStatus) model = { ...model, state: remoteStatus };
      const status = { provider, endpoint: this.credentials.baseURL || 'Local Codex bridge', model, policyDate: policy.reviewedAt, policyAgeDays: policyAgeDays(), stale: policyAgeDays() > 30 };
      this.callbacks.onProviderStatus?.(status);
      return status;
    }

    assertOpenAIModelAllowed() {
      if (this.credentials.provider !== 'openai') return;
      const status = policyStatus(this.credentials.model);
      if (status.state === 'blocked') throw new Error(`Blocked deprecated OpenAI model ${status.id}. Use ${status.replacement || policy.defaultModel}; shutdown date ${status.shutdownDate}.`);
    }

    async testConnection() {
      this.setState('testing');
      try {
        if (this.credentials.provider === 'codex') {
          const response = await fetch(localAPI('bridge/status'), { cache: 'no-store' });
          if (!response.ok) throw new Error('The local Codex bridge host is unavailable.');
          this.log('success', 'Codex bridge host is ready.'); this.emitProviderStatus('bridge'); this.setState('idle'); return true;
        }
        if (!this.credentials.model) throw new Error('Model is required.');
        if (!this.credentials.apiKey) throw new Error('Enter an API key for this session before testing the provider.');
        this.assertOpenAIModelAllowed();
        const response = this.credentials.provider === 'openai'
          ? await fetch(localAPI('agent/openai/models'), { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ apiKey: this.credentials.apiKey }) })
          : await fetch(endpoint(this.credentials.baseURL, '/models'), { headers: this.headers() });
        if (!response.ok) throw await responseError(response, 'Connection failed');
        const payload = await response.json();
        this.availableModels = new Set((payload.data || []).map((item) => item.id).filter(Boolean));
        const present = this.availableModels.has(this.credentials.model);
        if (!present) throw new Error(`Model ${this.credentials.model} was not returned by /models for this account.`);
        this.log('success', `Connection succeeded. ${this.credentials.model} is available.`);
        this.emitProviderStatus('current'); this.setState('idle'); return true;
      } catch (error) {
        const message = error instanceof TypeError ? `${error.message}. The endpoint may be offline or blocking this local origin.` : error.message;
        this.log('error', message); this.emitProviderStatus('error'); this.setState('error'); throw new Error(message);
      }
    }

    systemPrompt() {
      return [
        'You are a UML diagram planning agent for the PetaKerja Architecture Explorer.',
        'Return one DiagramPlan that conforms exactly to the supplied JSON Schema.',
        `Allowed operation types: ${[...ALLOWED_TYPES].join(', ')}.`,
        `Allowed component types: ${[...COMPONENT_TYPES].join(', ')}.`,
        `Allowed participant types: ${[...PARTICIPANT_TYPES].join(', ')}.`,
        `Allowed relation kinds: ${[...RELATION_KINDS].join(', ')}.`,
        'Use existing stable component keys where possible. Every createComponent needs key, componentType, label and geometry.',
        'For sequence messages, put the absolute message Y coordinate in geometry.y and use native sequence relation kinds.',
        'Do not issue browser clicks, navigation, JavaScript, filesystem or network operations.',
        'Preserve logical architecture. Layout-only requests must use moveResize or applyLayout.',
      ].join('\n');
    }

    async propose(prompt) {
      if (!String(prompt || '').trim()) throw new Error('Enter a diagram request first.');
      if (this.credentials.provider === 'codex') throw new Error('Codex bridge mode receives a reviewed DiagramPlan through the local MCP bridge; use its propose_diagram_plan tool.');
      if (!this.credentials.model) throw new Error('Model is required.');
      if (!this.credentials.apiKey) throw new Error('Enter an API key for this session before creating a plan.');
      this.assertOpenAIModelAllowed();
      this.setState('planning'); this.log('reflection', 'Reviewing the current diagram before proposing actions.');
      const context = await this.getContext();
      const userContent = `Current diagram context:\n${JSON.stringify(context)}\n\nUser request:\n${String(prompt).trim()}`;
      let payload;
      if (this.credentials.provider === 'openai') {
        const response = await fetch(localAPI('agent/openai/responses'), {
          method: 'POST', headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            apiKey: this.credentials.apiKey,
            request: buildOpenAIResponsesRequest(this.credentials.model, this.systemPrompt(), userContent),
          }),
        });
        if (!response.ok) throw await responseError(response, 'OpenAI plan request failed');
        payload = await response.json();
        this.plan = safePlan(extractJSON(extractResponsesText(payload)));
      } else {
        const response = await fetch(endpoint(this.credentials.baseURL, '/chat/completions'), {
          method: 'POST', headers: this.headers(),
          body: JSON.stringify({ model: this.credentials.model, temperature: 0.1, response_format: { type: 'json_object' }, messages: [{ role: 'system', content: this.systemPrompt() }, { role: 'user', content: userContent }] }),
        });
        if (!response.ok) throw await responseError(response, 'Compatible-provider plan request failed');
        payload = await response.json();
        const content = payload.choices?.[0]?.message?.content ?? payload.output_text ?? payload.plan;
        this.plan = safePlan(typeof content === 'object' ? content : extractJSON(content));
      }
      this.decision = 'pending'; this.log('plan', `Plan ready: ${this.plan.operations.length} operations.`); this.setState('review'); this.callbacks.onPlan?.(this.plan); return this.plan;
    }

    setPlan(plan) { this.plan = safePlan(plan); this.decision = 'pending'; this.callbacks.onPlan?.(this.plan); this.setState('review'); return this.plan; }

    async run(plan = this.plan) {
      if (this.running) throw new Error('An agent run is already active.');
      const approved = safePlan(plan); this.decision = 'approved'; this.preRunDocument = this.editor.documentSnapshot?.() || null;
      this.preRunXml = this.preRunDocument?.xml || this.editor.workingXml; this.running = true; this.stopRequested = false; this.setState('running'); this.callbacks.onRunStart?.(approved);
      let completed = 0;
      try {
        for (let index = 0; index < approved.operations.length; index += 1) {
          if (this.stopRequested) break;
          const operation = approved.operations[index]; this.log('action', `${index + 1}/${approved.operations.length}: ${operation.type}`, { operation });
          let lastError = null;
          for (let attempt = 1; attempt <= 2; attempt += 1) {
            try { const result = await this.editor.applyOperation(operation); completed += 1; this.editor.validateNow(); this.callbacks.onOperation?.({ index, operation, result, completed, total: approved.operations.length }); lastError = null; break; }
            catch (error) { lastError = error; this.log('retry', `Operation failed on attempt ${attempt}: ${error.message}`); }
          }
          if (lastError) throw lastError;
          await new Promise((resolve) => window.setTimeout(resolve, 220));
        }
        if (this.stopRequested) { this.log('stopped', `Run stopped after ${completed} operations. Completed changes were preserved.`); this.setState('stopped'); this.decision = 'stopped'; }
        else { this.log('success', `Run completed: ${completed} operations applied.`); this.setState('complete'); this.decision = 'applied'; }
        return { completed, stopped: this.stopRequested };
      } catch (error) { this.log('error', `Run failed after ${completed} completed operations: ${error.message}`); this.setState('error'); this.decision = 'error'; throw error; }
      finally { this.running = false; this.callbacks.onRunEnd?.({ completed, stopped: this.stopRequested, canRevert: Boolean(this.preRunXml) }); }
    }

    stop() { if (!this.running) return false; this.stopRequested = true; this.log('stopping', 'Stop requested. The current operation will finish safely.'); this.setState('stopping'); return true; }
    revert() {
      if (!this.preRunXml) throw new Error('There is no agent run to revert.');
      this.editor.restoreXML(this.preRunXml, { dirty: true, filename: this.preRunDocument?.filename, pageId: this.preRunDocument?.pageId, diagramHint: this.preRunDocument?.diagramId });
      this.log('revert', 'Restored the diagram snapshot from before the last run.'); this.setState('idle'); this.decision = 'reverted'; this.callbacks.onRevert?.(); return true;
    }
  }

  window.PETAKERJA_AGENT = {
    DiagramAgent, safePlan, validateOperation, DIAGRAM_PLAN_SCHEMA,
    ALLOWED_TYPES: [...ALLOWED_TYPES], COMPONENT_TYPES: [...COMPONENT_TYPES], RELATION_KINDS: [...RELATION_KINDS], LAYOUTS: [...LAYOUTS],
    policyStatus, extractResponsesText, buildOpenAIResponsesRequest,
  };
}());
