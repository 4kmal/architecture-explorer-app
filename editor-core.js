(function () {
  'use strict';

  const EDITABLE_DIAGRAMS = ['usecase', 'domain', 'domain-original', 'implementation', 'supabase', 'sequence', 'auth-sequence', 'google-oauth-sequence', 'user-google-sign-in-flowchart', 'user-google-sign-in-flowchart-original', 'user-search-jobs-flowchart', 'user-search-jobs-flowchart-original', 'user-explore-3d-map-flowchart', 'user-explore-3d-map-flowchart-original', 'user-sign-out-flowchart', 'user-sign-out-flowchart-original', 'admin-access-dashboard-flowchart', 'admin-monitor-activity-flowchart', 'admin-manage-users-flowchart', 'admin-manage-ai-configuration-flowchart', 'admin-sign-out-flowchart', 'admin-access-dashboard-flowchart-original', 'admin-monitor-activity-flowchart-original', 'admin-manage-users-flowchart-original', 'admin-manage-ai-configuration-flowchart-original', 'admin-sign-out-flowchart-original', 'user-explore-3d-map-sequence', 'user-sign-out-sequence', 'admin-access-dashboard-sequence', 'admin-monitor-activity-sequence', 'admin-manage-users-sequence', 'admin-manage-ai-configuration-sequence', 'admin-sign-out-sequence', 'architecture-visual-stack', 'architecture', 'architecture-original', 'modules', 'modules-original', 'modules-layered-stack', 'map-routing-responsibility-stack', 'nominatim-valhalla-workflow', 'nominatim-maplibre-workflow', 'valhalla-maplibre-workflow', 'geo-server-communication-workflow', 'etl-pipeline', 'daily-index-workflow', 'live-search-workflow', 'deployment-infrastructure', 'v2-geo-usecase', 'v2-geo-map-flowchart', 'v2-geo-route-sequence', 'v2-geo-travel-analysis-sequence', 'v2-geo-job-route-sequence', 'v2-geo-domain', 'v2-geo-implementation', 'v2-geo-architecture', 'v2-geo-modules', 'v2-geo-data-flow', 'v2-geo-erd', 'v2-geo-routing-stack', 'v2-geo-supabase'];
  const SOURCE_FILES = {
    usecase: { url: 'assets/editor/use-case-petakerja.drawio', pageId: 'petakerja-use-case', filename: 'Rajah Kes Guna PetaKerja.drawio' },
    domain: { url: 'assets/editor/class-domain-petakerja.drawio?v=20260720-1', pageId: 'petakerja_domain', filename: 'Class Diagram PetaKerja - Polished.drawio' },
    'domain-original': { url: 'assets/editor/class-domain-petakerja-original.drawio?v=20260715-3', pageId: 'petakerja_domain', filename: 'Class Diagram PetaKerja.drawio' },
    implementation: { url: 'assets/editor/class-diagram-petakerja.drawio', pageId: 'petakerja_implementation', filename: 'Kebergantungan Kelas PetaKerja.drawio' },
    supabase: { url: 'assets/editor/class-diagram-petakerja.drawio', pageId: 'petakerja_supabase', filename: 'Peta Entiti Supabase PetaKerja.drawio' },
    sequence: { url: 'assets/editor/sequence-job-search.drawio?v=20260717-1', pageId: 'petakerja_job_search_sequence', filename: 'Sequence Diagram PetaKerja - Search Jobs.drawio' },
    'auth-sequence': { url: 'assets/editor/auth-sequence.drawio', pageId: 'petakerja_auth_sequence', filename: 'Sequence Diagram - PetaKerja User Login Logout.drawio' },
    'google-oauth-sequence': { url: 'assets/editor/sequence-google-oauth.drawio?v=20260717-1', pageId: 'petakerja_google_oauth_sequence', filename: 'Sequence Diagram PetaKerja - Sign in Google OAuth.drawio' },
    'user-google-sign-in-flowchart': { url: 'assets/editor/flowchart-user-google-sign-in.drawio?v=20260715-3', pageId: 'petakerja_flow_google_sign_in', filename: 'Flow Chart PetaKerja - Sign in with Google - Polished.drawio' },
    'user-google-sign-in-flowchart-original': { url: 'assets/editor/flowchart-user-google-sign-in-original.drawio?v=20260715-3', pageId: 'petakerja_flow_google_sign_in', filename: 'Flow Chart PetaKerja - Sign in with Google.drawio' },
    'user-search-jobs-flowchart': { url: 'assets/editor/flowchart-user-search-jobs.drawio?v=20260715-1', pageId: 'petakerja_flow_user_search_jobs', filename: 'Flow Chart PetaKerja - Search Jobs - Polished.drawio' },
    'user-search-jobs-flowchart-original': { url: 'assets/editor/flowchart-user-search-jobs-original.drawio?v=20260715-1', pageId: 'petakerja_flow_user_search_jobs', filename: 'Flow Chart PetaKerja - Search Jobs.drawio' },
    'user-explore-3d-map-flowchart': { url: 'assets/editor/flowchart-user-explore-3d-map.drawio?v=20260720-2', pageId: 'petakerja_flow_user_explore_3d_map', filename: 'Flow Chart PetaKerja - Explore the 3D Map - Polished.drawio' },
    'user-explore-3d-map-flowchart-original': { url: 'assets/editor/flowchart-user-explore-3d-map-original.drawio?v=20260715-1', pageId: 'petakerja_flow_user_explore_3d_map', filename: 'Flow Chart PetaKerja - Explore the 3D Map.drawio' },
    'user-sign-out-flowchart': { url: 'assets/editor/flowchart-user-sign-out.drawio?v=20260715-1', pageId: 'petakerja_flow_user_sign_out', filename: 'Flow Chart PetaKerja - User Sign Out - Polished.drawio' },
    'user-sign-out-flowchart-original': { url: 'assets/editor/flowchart-user-sign-out-original.drawio?v=20260715-1', pageId: 'petakerja_flow_user_sign_out', filename: 'Flow Chart PetaKerja - User Sign Out.drawio' },
    'admin-access-dashboard-flowchart': { url: 'assets/editor/flowchart-admin-access-dashboard.drawio?v=20260715-2', pageId: 'petakerja_flow_admin_access_dashboard', filename: 'Flow Chart PetaKerja - Access Administrator Dashboard - Polished.drawio' },
    'admin-monitor-activity-flowchart': { url: 'assets/editor/flowchart-admin-monitor-activity.drawio?v=20260715-2', pageId: 'petakerja_flow_admin_monitor_activity', filename: 'Flow Chart PetaKerja - Monitor System Activity Logs - Polished.drawio' },
    'admin-manage-users-flowchart': { url: 'assets/editor/flowchart-admin-manage-users.drawio?v=20260715-2', pageId: 'petakerja_flow_admin_manage_users', filename: 'Flow Chart PetaKerja - Manage Users - Polished.drawio' },
    'admin-manage-ai-configuration-flowchart': { url: 'assets/editor/flowchart-admin-manage-ai-configuration.drawio?v=20260715-2', pageId: 'petakerja_flow_admin_manage_ai_configuration', filename: 'Flow Chart PetaKerja - Manage AI Chatbot Configuration - Polished.drawio' },
    'admin-sign-out-flowchart': { url: 'assets/editor/flowchart-admin-sign-out.drawio?v=20260715-2', pageId: 'petakerja_flow_admin_sign_out', filename: 'Flow Chart PetaKerja - Administrator Sign Out - Polished.drawio' },
    'admin-access-dashboard-flowchart-original': { url: 'assets/editor/flowchart-admin-access-dashboard-original.drawio?v=20260715-2', pageId: 'petakerja_flow_admin_access_dashboard', filename: 'Flow Chart PetaKerja - Access Administrator Dashboard.drawio' },
    'admin-monitor-activity-flowchart-original': { url: 'assets/editor/flowchart-admin-monitor-activity-original.drawio?v=20260715-2', pageId: 'petakerja_flow_admin_monitor_activity', filename: 'Flow Chart PetaKerja - Monitor System Activity Logs.drawio' },
    'admin-manage-users-flowchart-original': { url: 'assets/editor/flowchart-admin-manage-users-original.drawio?v=20260715-2', pageId: 'petakerja_flow_admin_manage_users', filename: 'Flow Chart PetaKerja - Manage Users.drawio' },
    'admin-manage-ai-configuration-flowchart-original': { url: 'assets/editor/flowchart-admin-manage-ai-configuration-original.drawio?v=20260715-2', pageId: 'petakerja_flow_admin_manage_ai_configuration', filename: 'Flow Chart PetaKerja - Manage AI Chatbot Configuration.drawio' },
    'admin-sign-out-flowchart-original': { url: 'assets/editor/flowchart-admin-sign-out-original.drawio?v=20260715-2', pageId: 'petakerja_flow_admin_sign_out', filename: 'Flow Chart PetaKerja - Administrator Sign Out.drawio' },
    'admin-manage-users-sequence': { url: 'assets/editor/sequence-admin-manage-users.drawio', pageId: 'petakerja_admin_manage_users_sequence', filename: 'Sequence Diagram PetaKerja - Manage Users.drawio' },
    'admin-manage-ai-configuration-sequence': { url: 'assets/editor/sequence-admin-manage-ai-configuration.drawio', pageId: 'petakerja_admin_manage_ai_configuration_sequence', filename: 'Sequence Diagram PetaKerja - Manage AI Chatbot Configuration.drawio' },
    'admin-access-dashboard-sequence': { url: 'assets/editor/sequence-admin-access-dashboard.drawio', pageId: 'petakerja_admin_access_dashboard_sequence', filename: 'Sequence Diagram PetaKerja - Access Administrator Dashboard.drawio' },
    'admin-monitor-activity-sequence': { url: 'assets/editor/sequence-admin-monitor-activity.drawio', pageId: 'petakerja_admin_monitor_activity_sequence', filename: 'Sequence Diagram PetaKerja - Monitor System Activity Logs.drawio' },
    'admin-sign-out-sequence': { url: 'assets/editor/sequence-admin-sign-out.drawio', pageId: 'petakerja_administrator_sign_out_sequence', filename: 'Sequence Diagram PetaKerja - Administrator Sign Out.drawio' },
    'user-explore-3d-map-sequence': { url: 'assets/editor/sequence-user-explore-3d-map.drawio?v=20260717-1', pageId: 'petakerja_user_explore_3d_map_sequence', filename: 'Sequence Diagram PetaKerja - Explore the 3D Map.drawio' },
    'user-sign-out-sequence': { url: 'assets/editor/sequence-user-sign-out.drawio?v=20260717-1', pageId: 'petakerja_user_sign_out_sequence', filename: 'Sequence Diagram PetaKerja - User Sign Out.drawio' },
    'architecture-visual-stack': { url: 'assets/editor/architecture-visual-stack.drawio?v=20260722-1', pageId: 'petakerja_layered_architecture_visual_stack', filename: 'PetaKerja Layered Architecture - Visual Stack.drawio' },
    architecture: { url: 'assets/editor/architecture-layered.drawio?v=20260722-1', pageId: 'petakerja_layered_architecture', filename: 'PetaKerja Layered Architecture - Detailed Layers.drawio' },
    'architecture-original': { url: 'assets/editor/architecture-layered-original.drawio?v=20260721-1', pageId: 'petakerja_layered_architecture', filename: 'PetaKerja Layered Architecture - Original.drawio' },
    modules: { url: 'assets/editor/module-hierarchy.drawio?v=20260722-1', pageId: 'petakerja_module_hierarchy', filename: 'PetaKerja Module Hierarchy - Polished.drawio' },
    'modules-original': { url: 'assets/editor/module-hierarchy-original.drawio?v=20260721-1', pageId: 'petakerja_module_hierarchy', filename: 'PetaKerja Module Hierarchy - Original.drawio' },
    'modules-layered-stack': { url: 'assets/editor/module-hierarchy-layered-stack.drawio?v=20260722-1', pageId: 'petakerja_module_hierarchy_layered_stack', filename: 'PetaKerja Module Hierarchy - Layered Stack.drawio' },
    'map-routing-responsibility-stack': { url: 'assets/editor/petakerja-map-routing-responsibility-stack.drawio?v=20260722-1', pageId: 'petakerja_map_routing_stack', filename: 'PetaKerja Map Routing Responsibility Stack.drawio' },
    'nominatim-valhalla-workflow': { url: 'assets/editor/map-routing/nominatim-valhalla-workflow.drawio?v=20260722-1', pageId: 'petakerja_nominatim_valhalla_workflow', filename: 'PetaKerja Nominatim and Valhalla Workflow.drawio' },
    'nominatim-maplibre-workflow': { url: 'assets/editor/map-routing/nominatim-maplibre-workflow.drawio?v=20260722-1', pageId: 'petakerja_nominatim_maplibre_workflow', filename: 'PetaKerja Nominatim and MapLibre Workflow.drawio' },
    'valhalla-maplibre-workflow': { url: 'assets/editor/map-routing/valhalla-maplibre-workflow.drawio?v=20260722-1', pageId: 'petakerja_valhalla_maplibre_workflow', filename: 'PetaKerja Valhalla and MapLibre Workflow.drawio' },
    'geo-server-communication-workflow': { url: 'assets/editor/map-routing/geo-server-communication-workflow.drawio?v=20260722-1', pageId: 'petakerja_geo_server_communication_workflow', filename: 'PetaKerja Geo Server Communication.drawio' },
    'etl-pipeline': { url: 'assets/editor/etl-pipeline.drawio?v=20260720-1', pageId: 'petakerja_etl_pipeline', filename: 'PetaKerja Operational ETL and Serving Pipeline.drawio' },
    'daily-index-workflow': { url: 'assets/editor/daily-index-workflow.drawio?v=20260722-1', pageId: 'petakerja_daily_index_workflow', filename: 'PetaKerja Daily Index Workflow.drawio' },
    'live-search-workflow': { url: 'assets/editor/live-search-workflow.drawio?v=20260722-1', pageId: 'petakerja_live_search_workflow', filename: 'PetaKerja Live Search Workflow.drawio' },
    'deployment-infrastructure': { url: 'assets/editor/deployment-infrastructure.drawio?v=20260720-1', pageId: 'petakerja_deployment_infrastructure', filename: 'PetaKerja Production Deployment and Infrastructure.drawio' },
    'v2-geo-usecase': { url: 'assets/editor/v2-georouting/usecase.drawio?v=20260719-1', pageId: 'v2_geo_usecase', filename: 'PetaKerja V2 Georouting - Use Cases.drawio' },
    'v2-geo-map-flowchart': { url: 'assets/editor/v2-georouting/map-flowchart.drawio?v=20260719-1', pageId: 'v2_geo_map_flowchart', filename: 'PetaKerja V2 Georouting - Map Flowchart.drawio' },
    'v2-geo-route-sequence': { url: 'assets/editor/v2-georouting/route-sequence.drawio?v=20260719-1', pageId: 'v2_geo_route_sequence', filename: 'PetaKerja V2 Georouting - Route Sequence.drawio' },
    'v2-geo-travel-analysis-sequence': { url: 'assets/editor/v2-georouting/travel-analysis-sequence.drawio?v=20260719-1', pageId: 'v2_geo_travel_analysis_sequence', filename: 'PetaKerja V2 Georouting - Travel Analysis Sequence.drawio' },
    'v2-geo-job-route-sequence': { url: 'assets/editor/v2-georouting/job-route-sequence.drawio?v=20260719-1', pageId: 'v2_geo_job_route_sequence', filename: 'PetaKerja V2 Georouting - Job Route Sequence.drawio' },
    'v2-geo-domain': { url: 'assets/editor/v2-georouting/domain.drawio?v=20260719-1', pageId: 'v2_geo_domain', filename: 'PetaKerja V2 Georouting - Domain.drawio' },
    'v2-geo-implementation': { url: 'assets/editor/v2-georouting/implementation.drawio?v=20260719-1', pageId: 'v2_geo_implementation', filename: 'PetaKerja V2 Georouting - Implementation.drawio' },
    'v2-geo-architecture': { url: 'assets/editor/v2-georouting/architecture.drawio?v=20260719-1', pageId: 'v2_geo_architecture', filename: 'PetaKerja V2 Georouting - Architecture.drawio' },
    'v2-geo-modules': { url: 'assets/editor/v2-georouting/modules.drawio?v=20260719-1', pageId: 'v2_geo_modules', filename: 'PetaKerja V2 Georouting - Modules.drawio' },
    'v2-geo-data-flow': { url: 'assets/editor/v2-georouting/data-flow.drawio?v=20260719-1', pageId: 'v2_geo_data_flow', filename: 'PetaKerja V2 Georouting - Data Flow.drawio' },
    'v2-geo-erd': { url: 'assets/editor/v2-georouting/erd.drawio?v=20260719-1', pageId: 'v2_geo_erd', filename: 'PetaKerja V2 Georouting - ERD.drawio' },
    'v2-geo-routing-stack': { url: 'assets/editor/v2-georouting/routing-stack.drawio?v=20260719-1', pageId: 'v2_geo_routing_stack', filename: 'PetaKerja V2 Georouting - Routing Stack.drawio' },
    'v2-geo-supabase': { url: 'assets/editor/v2-georouting/supabase.drawio?v=20260719-1', pageId: 'v2_geo_supabase', filename: 'PetaKerja V2 Georouting - Supabase Snapshot.drawio' },
  };

  const parser = new DOMParser();
  const serializer = new XMLSerializer();

  function bilingual(ms, en) { return { ms, en }; }

  function cleanLabel(value) {
    const holder = document.createElement('div');
    holder.innerHTML = String(value || '').replace(/<br\s*\/?\s*>/gi, ' ');
    return (holder.textContent || holder.innerText || '').replace(/\s+/g, ' ').trim();
  }

  function localizedLabelPairs(xml) {
    const documentNode = normaliseDocument(xml);
    const pairs = [];
    const seen = new Set();
    const addPair = (en, ms) => {
      const cleanEn = cleanLabel(en);
      const cleanMs = cleanLabel(ms);
      if (!cleanEn || !cleanMs || cleanEn === cleanMs) return;
      const key = `${cleanEn}\u0000${cleanMs}`;
      if (seen.has(key)) return;
      seen.add(key);
      pairs.push({ en: cleanEn, ms: cleanMs });
    };
    const segments = (value) => String(value || '')
      .replace(/<br\s*\/?\s*>/gi, '\n')
      .replace(/<\/div>\s*<div[^>]*>/gi, '\n')
      .split(/\r?\n/).map(cleanLabel).filter(Boolean);
    bilingualElements(documentNode).forEach((element) => {
      const labelEn = element.getAttribute('labelEn');
      const labelMs = element.getAttribute('labelMs');
      addPair(labelEn, labelMs);
      const enSegments = segments(labelEn);
      const msSegments = segments(labelMs);
      if (enSegments.length === msSegments.length) {
        enSegments.forEach((segment, index) => addPair(segment, msSegments[index]));
      }
    });
    return pairs.sort((left, right) => Math.max(right.en.length, right.ms.length) - Math.max(left.en.length, left.ms.length));
  }

  function normaliseText(value) {
    return cleanLabel(value).normalize('NFKD').replace(/[\u0300-\u036f]/g, '')
      .toLocaleLowerCase().replace(/[^a-z0-9_]+/g, ' ').trim().replace(/\s+/g, ' ');
  }

  function firstIdentifier(value) {
    const match = cleanLabel(value).match(/^[A-Za-z_][A-Za-z0-9_.:-]*/);
    return match ? match[0].toLocaleLowerCase() : '';
  }

  function isTechnicalAlias(value) {
    return /^[A-Za-z_][A-Za-z0-9_.:-]*$/.test(cleanLabel(value));
  }

  function cellValue(cell) {
    if (!cell) return '';
    const own = cell.getAttribute('value');
    if (own != null && own !== '') return own;
    const wrapper = cell.parentElement;
    return wrapper && wrapper.tagName.toLocaleLowerCase() !== 'root'
      ? (wrapper.getAttribute('label') || wrapper.getAttribute('value') || '') : '';
  }

  function cellId(cell) {
    if (!cell) return '';
    const own = cell.getAttribute('id');
    if (own) return own;
    const wrapper = cell.parentElement;
    return wrapper && wrapper.tagName.toLocaleLowerCase() !== 'root' ? (wrapper.getAttribute('id') || '') : '';
  }

  function cellStyle(cell) { return cell?.getAttribute('style') || ''; }

  function readStableKey(cell) {
    return cell?.getAttribute('petakerjaKey') || cell?.parentElement?.getAttribute('petakerjaKey') || '';
  }

  function writeStableKey(cell, key) {
    if (!cell) return;
    const wrapper = cell.parentElement;
    if (wrapper && wrapper.tagName.toLocaleLowerCase() !== 'root') wrapper.setAttribute('petakerjaKey', key);
    else cell.setAttribute('petakerjaKey', key);
  }

  function binaryString(bytes) {
    let result = '';
    const chunk = 0x8000;
    for (let index = 0; index < bytes.length; index += chunk) {
      result += String.fromCharCode.apply(null, bytes.subarray(index, index + chunk));
    }
    return result;
  }

  function decodeDiagramText(text) {
    const value = String(text || '').trim();
    if (!value) throw new Error('The diagram page is empty.');
    if (value.startsWith('<')) return value;
    if (!window.pako) throw new Error('The local Draw.io compression codec is unavailable.');
    const binary = atob(value);
    const bytes = Uint8Array.from(binary, (character) => character.charCodeAt(0));
    return decodeURIComponent(window.pako.inflateRaw(bytes, { to: 'string' }));
  }

  function parseXML(xml) {
    const documentNode = parser.parseFromString(String(xml || ''), 'application/xml');
    const error = documentNode.querySelector('parsererror');
    if (error) throw new Error(cleanLabel(error.textContent) || 'Invalid XML.');
    return documentNode;
  }

  function normaliseDocument(xml) {
    let documentNode = parseXML(xml);
    let root = documentNode.documentElement;

    if (root.tagName === 'mxGraphModel') {
      const model = root.cloneNode(true);
      documentNode = document.implementation.createDocument('', 'mxfile', null);
      root = documentNode.documentElement;
      root.setAttribute('compressed', 'false');
      const diagram = documentNode.createElement('diagram');
      diagram.setAttribute('id', 'imported-page');
      diagram.setAttribute('name', 'Imported diagram');
      diagram.appendChild(documentNode.importNode(model, true));
      root.appendChild(diagram);
    } else if (root.tagName !== 'mxfile') {
      throw new Error('Expected an mxfile or mxGraphModel root element.');
    }

    const diagrams = [...root.children].filter((child) => child.tagName === 'diagram');
    if (!diagrams.length) throw new Error('No Draw.io pages were found.');

    diagrams.forEach((diagram) => {
      let model = [...diagram.children].find((child) => child.tagName === 'mxGraphModel');
      if (!model) {
        const decoded = parseXML(decodeDiagramText(diagram.textContent));
        if (decoded.documentElement.tagName !== 'mxGraphModel') {
          throw new Error(`Page ${diagram.getAttribute('name') || diagram.getAttribute('id') || ''} has no mxGraphModel.`);
        }
        model = documentNode.importNode(decoded.documentElement, true);
        while (diagram.firstChild) diagram.removeChild(diagram.firstChild);
        diagram.appendChild(model);
      }
    });
    root.setAttribute('compressed', 'false');
    return documentNode;
  }

  function hashText(value) {
    let hash = 2166136261;
    for (let index = 0; index < value.length; index += 1) {
      hash ^= value.charCodeAt(index);
      hash = Math.imul(hash, 16777619);
    }
    return (hash >>> 0).toString(16).padStart(8, '0');
  }

  function createBlankDocument(options = {}) {
    const pageId = options.pageId || `petakerja-${Date.now()}`;
    const pageName = options.pageName || 'PetaKerja Diagram';
    const escapedId = String(pageId).replace(/[&<>"']/g, '');
    const escapedName = String(pageName).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
    return `<mxfile host="PetaKerja Architecture Explorer" modified="${new Date().toISOString()}" agent="PetaKerja Explorer" version="28.2.8" type="device"><diagram id="${escapedId}" name="${escapedName}"><mxGraphModel dx="1800" dy="1000" grid="1" gridSize="10" guides="1" tooltips="1" connect="1" arrows="1" fold="1" page="1" pageScale="1" pageWidth="2200" pageHeight="1800" math="0" shadow="0"><root><mxCell id="0"/><mxCell id="1" parent="0"/></root></mxGraphModel></diagram></mxfile>`;
  }

  function pageFingerprint(model, includeGeometry) {
    const clone = model.cloneNode(true);
    if (!includeGeometry) {
      clone.querySelectorAll('mxGeometry, mxPoint, Array[as="points"]').forEach((node) => node.remove());
      clone.querySelectorAll('mxCell').forEach((cell) => {
        const style = cell.getAttribute('style');
        if (style) cell.setAttribute('style', style.replace(/(?:^|;)entryX=[^;]*/g, '').replace(/(?:^|;)entryY=[^;]*/g, ''));
      });
    }
    return hashText(serializer.serializeToString(clone));
  }

  function pageLogicFingerprint(model) {
    const cells = [...model.querySelectorAll('mxCell')];
    const records = cells.map((cell) => {
      const record = {
        id: cellId(cell),
        vertex: cell.getAttribute('vertex') === '1',
        edge: cell.getAttribute('edge') === '1',
        value: cleanLabel(cellValue(cell)),
      };
      if (record.edge) {
        record.source = cell.getAttribute('source') || '';
        record.target = cell.getAttribute('target') || '';
        record.kind = connectionKind(cell, record.value);
      }
      return record;
    }).sort((left, right) => left.id.localeCompare(right.id));
    return hashText(JSON.stringify(records));
  }

  function componentTarget(component) {
    if (component.tableName) return `table:${component.tableName}`;
    return component.nodeIds?.[0] || component.id || null;
  }

  function buildCanonicalManifests(data, assets, translations) {
    const result = {};
    EDITABLE_DIAGRAMS.forEach((diagramId) => {
      const asset = assets[diagramId];
      if (!asset) return;
      const identities = (asset.components || []).map((component) => {
        const target = componentTarget(component);
        const node = target?.startsWith('table:') ? null : data.nodes[target];
        const aliases = new Set([
          component.label, component.labelEn, component.tableName,
          node?.label, translations.en?.nodeLabels?.[node?.id],
          component.id?.startsWith('table:') ? component.id.slice(6) : component.id,
        ].filter(Boolean).map(cleanLabel));
        const technical = [...aliases].find(isTechnicalAlias) || '';
        return {
          key: `${diagramId}/${component.componentKey}`,
          diagramId,
          componentKey: component.componentKey,
          target,
          tableName: component.tableName || null,
          label: component.label || component.tableName || node?.label || component.id,
          labelEn: component.labelEn || translations.en?.nodeLabels?.[node?.id] || component.label || component.tableName || component.id,
          aliases: [...aliases],
          aliasKeys: new Set([...aliases].map(normaliseText)),
          technical: technical.toLocaleLowerCase(),
          cellIds: component.cellIds || [],
          nodeIds: component.nodeIds || [],
          uiHotspots: component.uiHotspots || [],
        };
      });
      const byComponent = new Map(identities.map((identity) => [identity.componentKey, identity]));
      const connections = (asset.connections || []).filter((connection) => connection.visual !== false).map((connection) => ({
        id: connection.id,
        sourceKey: byComponent.get(connection.sourceComponentKey)?.key,
        targetKey: byComponent.get(connection.targetComponentKey)?.key,
        kind: connection.kind || 'association',
        label: connection.label || bilingual('', ''),
      })).filter((connection) => connection.sourceKey && connection.targetKey);
      result[diagramId] = {
        id: diagramId,
        identities,
        byKey: new Map(identities.map((identity) => [identity.key, identity])),
        // The first Draw.io cell is the component root. Remaining IDs belong to
        // compartments such as attributes and operations and must not be matched
        // as independent UML components by the validator.
        byCellId: new Map(identities.flatMap((identity) => identity.cellIds.slice(0, 1).map((cellId) => [cellId, identity]))),
        connections,
      };
    });
    return result;
  }

  function isComponentCandidate(cell, cellsByParent) {
    if (!cell || cell.getAttribute('vertex') !== '1') return false;
    const label = cleanLabel(cellValue(cell));
    if (!label || /^[-+]\s/.test(label) || /^(?:0|1|\*|0\.\.1|0\.\.\*|1\.\.\*)$/.test(label)) return false;
    const style = cellStyle(cell);
    if (/^text(?:;|$)/i.test(style)) return false;
    const hasCompartments = (cellsByParent.get(cellId(cell)) || []).some((child) => child.getAttribute('vertex') === '1');
    return hasCompartments || /childLayout=stackLayout|shape=umlActor|ellipse(?:;|$)|shape=umlFrame/i.test(style)
      || /<<\s*(?:entity|service|interface|class)/i.test(label);
  }

  function semanticCandidates(cell, manifest) {
    const value = cleanLabel(cellValue(cell));
    const normalised = normaliseText(value);
    const identifier = firstIdentifier(value);
    const shortIdentifier = identifier.split('.').pop();
    return manifest.identities.filter((identity) => identity.aliasKeys.has(normalised)
      || (identity.technical && identifier && (identity.technical === identifier || identity.technical === shortIdentifier))
      || (shortIdentifier && identity.aliasKeys.has(normaliseText(shortIdentifier))));
  }

  function identityLabelMatches(cell, identity) {
    const value = cleanLabel(cellValue(cell));
    const normalized = normaliseText(value);
    const compact = normalized.replace(/\s+/g, '');
    const identifier = firstIdentifier(value);
    const shortIdentifier = identifier.split('.').pop();
    return identity.aliasKeys.has(normalized)
      || [...identity.aliasKeys].some((alias) => alias.replace(/\s+/g, '') === compact)
      || [...identity.aliasKeys].some((alias) => alias.length >= 4 && normalized.startsWith(`${alias} `))
      || [...identity.aliasKeys].some((alias) => {
        const compactAlias = alias.replace(/\s+/g, '');
        return compactAlias.length >= 4 && compact.startsWith(compactAlias);
      })
      || (identity.technical && identifier && (identity.technical === identifier || identity.technical === shortIdentifier))
      || (identifier && identity.aliasKeys.has(normaliseText(identifier)))
      || (shortIdentifier && identity.aliasKeys.has(normaliseText(shortIdentifier)));
  }

  function issue(ruleId, severity, cellIds, ms, en, meta = {}) {
    return { ruleId, severity, cellIds: [...new Set((cellIds || []).filter(Boolean))], message: bilingual(ms, en), ...meta };
  }

  function edgeLabel(edge, cells) {
    const labels = [cleanLabel(cellValue(edge))];
    cells.filter((cell) => cell.getAttribute('parent') === cellId(edge)).forEach((cell) => labels.push(cleanLabel(cellValue(cell))));
    return [...new Set(labels.filter(Boolean))].join(' · ');
  }

  function connectionKind(edge, label) {
    const style = cellStyle(edge);
    const lower = label.toLocaleLowerCase();
    if (lower.includes('include')) return 'include';
    if (lower.includes('extend')) return 'extend';
    if (style.includes('startArrow=diamond') && style.includes('startFill=1')) return 'composition';
    if (style.includes('startArrow=diamond')) return 'aggregation';
    // Sequence messages use the UML lifeline message style. Ordinary
    // orthogonal class associations can also contain entryY/exitY routing
    // hints, so those coordinates alone are not evidence of a sequence edge.
    if (style.includes('verticalAlign=bottom') && style.includes('exitY=') && style.includes('entryY=')) {
      if (style.includes('loopSize=') || edge.getAttribute('source') === edge.getAttribute('target')) return 'sequence-self';
      if (style.includes('dashed=1')) return 'sequence-return';
      if (style.includes('endArrow=open')) return 'sequence-async';
      return 'sequence-sync';
    }
    if (style.includes('dashed=1') && style.includes('endArrow=open')) return 'dependency';
    if (style.includes('dashed=1')) return 'logical';
    return 'association';
  }

  function relationSignature(kind, sourceKey, targetKey) {
    if (kind === 'association' || kind === 'logical') {
      return `${kind}:${[sourceKey, targetKey].sort().join('|')}`;
    }
    return `${kind}:${sourceKey}>${targetKey}`;
  }

  function genericDiagramType(cells, pageName = '') {
    const vertices = cells.filter((cell) => cell.getAttribute('vertex') === '1');
    const styles = vertices.map(cellStyle).join(';').toLocaleLowerCase();
    const labels = vertices.map((cell) => cleanLabel(cellValue(cell))).join(' ').toLocaleLowerCase();
    const edges = cells.filter((cell) => cell.getAttribute('edge') === '1');
    const name = normaliseText(pageName);
    if (/\b(?:agile|sprint|kanban)\b/.test(name)) return 'unknown';
    if (/\bsequence\b|\bjujukan\b/.test(name)) return 'generic-sequence';
    if (/\buse case\b|\busecase\b|\bkes guna\b/.test(name)) return 'generic-usecase';
    if (/\bactivity\b|\baktiviti\b/.test(name)) return 'generic-activity';
    if (/\bflow\s*chart\b|\bflowchart\b|\bcarta\s+alir\b/.test(name)) return 'generic-flowchart';
    if (/\berd\b|\bentity relation/.test(name)) return 'generic-erd';
    if (/\bclass diagram\b|\brajah kelas\b/.test(name)) return 'generic-class';
    if (/lifeline|sequence|participant|activation/.test(`${styles} ${labels}`)) return 'generic-sequence';
    if (/shape=umlactor|<<\s*(?:include|extend)\s*>>/.test(`${styles} ${labels}`)) return 'generic-usecase';
    if (/\b(?:pk|fk)\b|<<\s*entity|table\s*:|entityrelation/.test(`${styles} ${labels}`)) return 'generic-erd';
    if (/childlayout=stacklayout|<<\s*(?:class|interface|service)|[+-]\s*[a-z_][a-z0-9_]*\s*(?:\(|:)/.test(`${styles} ${labels}`)) return 'generic-class';
    if (/rhombus|activity|startstate|endstate/.test(`${styles} ${labels}`)) return 'generic-activity';
    if (/mxgraph\.flowchart\.(?:start_1|decision)|\b(?:yes|no|ya|tidak)\b/.test(`${styles} ${labels}`)) return 'generic-flowchart';
    if (edges.length && vertices.length > 1) return 'generic-class';
    return 'unknown';
  }

  function detectionForCandidates(candidateResults, cells, pageName) {
    const candidates = candidateResults.map((result) => {
      const matched = result.counts.exact + result.counts.semantic;
      const denominator = Math.max(3, Math.min(result.manifest.identities.length, Math.max(3, result.componentCandidates)));
      const confidence = Math.min(0.99, (result.counts.exact + result.counts.semantic * 0.75) / denominator);
      return {
        diagramType: result.manifest.id,
        confidence: Number(confidence.toFixed(3)),
        exact: result.counts.exact,
        semantic: result.counts.semantic,
        matched,
        score: result.score,
      };
    }).sort((left, right) => right.confidence - left.confidence || right.score - left.score);
    const best = candidates[0] || { diagramType: 'unknown', confidence: 0, exact: 0, semantic: 0, matched: 0 };
    const runnerUp = candidates[1] || { confidence: 0 };
    const lead = best.confidence - runnerUp.confidence;
    const recognized = best.exact >= 3 || (best.confidence >= 0.70 && lead >= 0.15);
    const ambiguous = !recognized && (best.matched >= 2 || best.confidence >= 0.35) && lead < 0.15;
    const genericType = genericDiagramType(cells, pageName);
    return {
      diagramType: recognized || ambiguous ? best.diagramType : genericType,
      confidence: best.confidence,
      status: recognized ? 'recognized' : ambiguous ? 'ambiguous' : 'generic',
      evidence: [
        `${best.exact} stable/exact matches`,
        `${best.semantic} semantic matches`,
        `${Math.round(lead * 100)}% lead over next candidate`,
      ],
      candidates,
    };
  }

  function analysePage(diagram, manifests, hintId) {
    const model = [...diagram.children].find((child) => child.tagName === 'mxGraphModel');
    const cells = [...model.querySelectorAll('mxCell')];
    const cellById = new Map();
    const duplicates = [];
    cells.forEach((cell) => {
      const id = cellId(cell);
      if (!id) return;
      if (cellById.has(id)) duplicates.push(id);
      cellById.set(id, cell);
    });
    const cellsByParent = new Map();
    cells.forEach((cell) => {
      const parent = cell.getAttribute('parent');
      if (!cellsByParent.has(parent)) cellsByParent.set(parent, []);
      cellsByParent.get(parent).push(cell);
    });

    const candidateManifests = hintId && manifests[hintId] ? [manifests[hintId]] : Object.values(manifests);
    let selected = null;
    const candidateResults = [];
    candidateManifests.forEach((manifest) => {
      const matches = [];
      const matchedIdentityKeys = new Set();
      const identityUsage = new Map();
      cells.forEach((cell) => {
        if (cell.getAttribute('vertex') !== '1') return;
        // Activation bars are sequence-diagram notation, not architecture
        // components.  They carry a stable operation key so they must be
        // excluded before the stable-key matcher runs.
        if (cellStyle(cell).includes('targetShapes=umlLifeline')) return;
        const stableKey = readStableKey(cell);
        const id = cellId(cell);
        const knownIdentity = manifest.byCellId.get(id);
        const stableIdentity = stableKey ? manifest.byKey.get(stableKey) : null;
        // Sequence documents deliberately attach petakerjaKey metadata to
        // messages, guards, operand labels and notes.  Those cells are UML
        // notation, not architecture components, so do not feed them into the
        // component matcher merely because they have a stable key.
        if ((manifest.id.includes('sequence') || manifest.id.includes('flowchart')) && stableKey && !stableIdentity && !knownIdentity) return;
        if (!stableKey && !knownIdentity && !isComponentCandidate(cell, cellsByParent)) return;
        let identity = stableIdentity;
        let confidence = identity ? 'exact' : null;
        if (!identity) {
          identity = knownIdentity;
          if (identity) confidence = 'exact';
        }
        let candidates = [];
        if (!identity) {
          candidates = semanticCandidates(cell, manifest);
          if (candidates.length === 1) { identity = candidates[0]; confidence = 'semantic'; }
          else if (candidates.length > 1) confidence = 'ambiguous';
        }
        if (identity) {
          identityUsage.set(identity.key, (identityUsage.get(identity.key) || 0) + 1);
          matchedIdentityKeys.add(identity.key);
          matches.push({ cellId: id, pageId: diagram.getAttribute('id'), componentKey: identity.key, stableKey, confidence, identity, candidates: [] });
        } else if (confidence === 'ambiguous') {
          matches.push({ cellId: id, pageId: diagram.getAttribute('id'), componentKey: null, stableKey, confidence, identity: null, candidates });
        } else if (stableKey || isComponentCandidate(cell, cellsByParent)) {
          matches.push({ cellId: id, pageId: diagram.getAttribute('id'), componentKey: null, stableKey, confidence: 'unmapped', identity: null, candidates: [] });
        }
      });
      matches.forEach((match) => {
        if (match.identity && identityUsage.get(match.identity.key) > 1) {
          match.confidence = 'ambiguous';
          match.candidates = [match.identity];
          match.componentKey = null;
          match.identity = null;
        }
      });
      const counts = {
        exact: matches.filter((match) => match.confidence === 'exact').length,
        semantic: matches.filter((match) => match.confidence === 'semantic').length,
        ambiguous: matches.filter((match) => match.confidence === 'ambiguous').length,
        unmapped: matches.filter((match) => match.confidence === 'unmapped').length,
      };
      const score = counts.exact * 12 + counts.semantic * 7 - counts.ambiguous * 2 - counts.unmapped;
      const result = { manifest, matches, counts, score, matchedIdentityKeys, componentCandidates: matches.length };
      candidateResults.push(result);
      if (!selected || score > selected.score) selected = result;
    });

    const forced = hintId && manifests[hintId] ? hintId : null;
    const detection = detectionForCandidates(candidateResults, cells, diagram.getAttribute('name') || '');
    if (forced) {
      detection.diagramType = forced;
      detection.status = 'recognized';
      detection.confidence = 1;
      detection.evidence.unshift('Diagram type confirmed by the user or active workspace.');
    }
    const mappingEnabled = detection.status === 'recognized';
    const manifest = selected.manifest;
    const matches = mappingEnabled ? selected.matches : selected.matches.map((match) => ({
      ...match, componentKey: null, identity: null,
      confidence: match.confidence === 'ambiguous' ? 'ambiguous' : 'unmapped',
    }));
    const matchByCell = new Map(matches.filter((match) => match.identity).map((match) => [match.cellId, match]));
    // Sequence messages attach to activation bars rather than participant
    // headers. Resolve each stable activation key back to its participant so
    // relationship direction and highlighting survive Edit -> View exports.
    const connectionMatchByCell = new Map(matchByCell);
    cells.filter((cell) => cell.getAttribute('vertex') === '1' && cellStyle(cell).includes('targetShapes=umlLifeline')).forEach((cell) => {
      const stableKey = readStableKey(cell);
      if (!stableKey?.endsWith('-activation')) return;
      const participantKey = stableKey.slice(0, -'-activation'.length);
      // Component keys are deliberately semantic (for example
      // ``participant-pengguna``), while stable Draw.io keys retain the
      // technical participant name (``participant-user``).  Locate the root
      // through its stable key first so actors and specialised dashboard
      // lifelines remain mapped after imports or layout changes.
      const participantCell = cells.find((candidate) => readStableKey(candidate) === participantKey);
      const canonicalIdentity = manifest.identities.find((identity) => identity.cellIds.includes(cellId(cell)));
      const participantMatch = participantCell
        ? matchByCell.get(cellId(participantCell))
        : matches.find((match) => match.identity?.key === participantKey)
          || (canonicalIdentity
            ? matches.find((match) => match.identity?.key === canonicalIdentity.key)
            : null);
      if (participantMatch) {
        connectionMatchByCell.set(cellId(cell), { ...participantMatch, cellId: cellId(cell) });
        // Canonicalise the activation key together with its participant root.
        // This keeps repeated autosave validation stable after the root key is
        // rewritten from a technical alias such as ``participant-administrator``.
        writeStableKey(cell, `${participantMatch.identity.key}-activation`);
      }
    });
    const issues = [];
    duplicates.forEach((id) => issues.push(issue('duplicate-cell-id', 'error', [id],
      `ID sel pendua: ${id}.`, `Duplicate cell ID: ${id}.`)));
    matches.filter((match) => match.confidence === 'ambiguous').forEach((match) => issues.push(issue('ambiguous-component', 'warning', [match.cellId],
      'Komponen ini mempunyai lebih daripada satu padanan PetaKerja.', 'This component has more than one PetaKerja match.')));
    matches.filter((match) => match.confidence === 'unmapped').forEach((match) => issues.push(issue('unmapped-component', 'info', [match.cellId],
      'Komponen ini belum dipetakan kepada seni bina PetaKerja.', 'This component is not mapped to the PetaKerja architecture.')));
    matches.filter((match) => {
      if (!match.identity) return false;
      const cell = cellById.get(match.cellId);
      const label = cleanLabel(cellValue(cell));
      // A sequence frame is labelled alt/opt/loop while its manifest identity
      // describes the frame's purpose. Empty actor roots likewise use a
      // separate visible label cell. Neither is a rename.
      if (!label || cellStyle(cell).includes('shape=umlFrame')) return false;
      return !identityLabelMatches(cell, match.identity);
    }).forEach((match) => issues.push(issue('renamed-component', 'warning', [match.cellId],
      `Label komponen tidak lagi sepadan dengan ${match.identity.label}.`,
      `The component label no longer matches ${match.identity.labelEn}.`, { componentKey: match.identity.key })));

    const matchedKeys = new Set(matches.filter((match) => match.identity).map((match) => match.identity.key));
    if (mappingEnabled) manifest.identities.filter((identity) => !matchedKeys.has(identity.key)).forEach((identity) => issues.push(issue('missing-component', 'warning', [],
      `Komponen kanonik tidak ditemui: ${identity.label}.`, `Canonical component not found: ${identity.labelEn}.`, { componentKey: identity.key })));

    const actualRelations = [];
    cells.filter((cell) => cell.getAttribute('edge') === '1'
      && cell.parentElement?.getAttribute('petakerjaRelation') !== 'structural').forEach((edge) => {
      const sourceId = edge.getAttribute('source');
      const targetId = edge.getAttribute('target');
      const sourceCell = cellById.get(sourceId);
      const targetCell = cellById.get(targetId);
      if (!sourceId || !targetId || !sourceCell || !targetCell) {
        const style = cellStyle(edge);
        // Dashed, endpoint-free lines inside alt/opt/loop frames are operand
        // dividers, not broken sequence messages.
        if (manifest.id.includes('sequence') && !sourceId && !targetId
            && style.includes('dashed=1') && style.includes('endArrow=none')) return;
        issues.push(issue('dangling-connector', 'error', [cellId(edge), sourceId, targetId],
          'Connector tidak mempunyai source dan target yang sah.', 'Connector does not have valid source and target cells.'));
        return;
      }
      const sourceMatch = connectionMatchByCell.get(sourceId);
      const targetMatch = connectionMatchByCell.get(targetId);
      const label = edgeLabel(edge, cells);
      const kind = manifest.id.includes('flowchart')
        ? (/^(?:yes|no|ya|tidak)$/i.test(label.trim()) ? 'flow-decision' : 'flow')
        : connectionKind(edge, label);
      if ((kind === 'include' || kind === 'extend') && !(cellStyle(edge).includes('dashed=1') && cellStyle(edge).includes('endArrow=open'))) {
        issues.push(issue('invalid-usecase-connector-style', 'warning', [cellId(edge)],
          `Hubungan <<${kind}>> mesti menggunakan garisan putus-putus dan anak panah terbuka.`,
          `The <<${kind}>> relationship must use a dashed line and an open arrowhead.`));
      }
      if (!sourceMatch || !targetMatch) {
        if (sourceMatch || targetMatch) {
          const other = sourceMatch ? targetCell : sourceCell;
          issues.push(issue('connector-to-noncomponent', 'warning', [cellId(edge), cellId(other)],
            'Connector ini bersambung kepada container atau label, bukan terus kepada komponen UML.',
            'This connector is attached to a container or label instead of a UML component.'));
        }
        return;
      }
      const signature = relationSignature(kind, sourceMatch.identity.key, targetMatch.identity.key);
      actualRelations.push({ edge, sourceMatch, targetMatch, kind, signature });
      if ((kind === 'association' || kind === 'aggregation' || kind === 'composition') && (diagram.getAttribute('id') || '').includes('domain')) {
        const multiplicities = cells.filter((cell) => cell.getAttribute('parent') === cellId(edge))
          .map((cell) => cleanLabel(cellValue(cell))).filter((value) => /^(?:0|1|\*|0\.\.1|0\.\.\*|1\.\.\*)$/.test(value));
        if (multiplicities.length < 2) issues.push(issue('missing-multiplicity', 'info', [cellId(edge)],
          'Multiplicity tidak lengkap pada kedua-dua hujung hubungan.', 'Multiplicity is not complete at both relationship ends.'));
      }
    });

    const actualSignatures = new Set(actualRelations.map((relation) => relation.signature));
    const expectedSignatures = new Map(manifest.connections.map((connection) => [relationSignature(connection.kind, connection.sourceKey, connection.targetKey), connection]));
    if (mappingEnabled) manifest.connections.forEach((connection) => {
      const signature = relationSignature(connection.kind, connection.sourceKey, connection.targetKey);
      if (!actualSignatures.has(signature)) {
        const source = manifest.byKey.get(connection.sourceKey);
        const target = manifest.byKey.get(connection.targetKey);
        const cellIds = matches.filter((match) => match.identity && (match.identity.key === connection.sourceKey || match.identity.key === connection.targetKey)).map((match) => match.cellId);
        issues.push(issue('missing-relation', 'warning', cellIds,
          `Hubungan kanonik tiada: ${source?.label || connection.sourceKey} → ${target?.label || connection.targetKey} (${connection.kind}).`,
          `Canonical relationship missing: ${source?.labelEn || connection.sourceKey} → ${target?.labelEn || connection.targetKey} (${connection.kind}).`));
      }
    });
    if (mappingEnabled) actualRelations.filter((relation) => !expectedSignatures.has(relation.signature)).forEach((relation) => issues.push(issue('unexpected-relation', 'info', [cellId(relation.edge)],
      'Hubungan ini tidak terdapat dalam snapshot kanonik PetaKerja.', 'This relationship is not present in the canonical PetaKerja snapshot.')));

    if (mappingEnabled) matches.filter((match) => match.identity && match.confidence !== 'ambiguous').forEach((match) => writeStableKey(cellById.get(match.cellId), match.identity.key));
    return {
      id: diagram.getAttribute('id') || '', name: diagram.getAttribute('name') || 'Page', diagramId: detection.diagramType,
      model, cells, cellById, matches, issues, counts: selected.counts, score: selected.score,
      detection,
      componentCount: matches.length,
      relationshipCount: cells.filter((cell) => cell.getAttribute('edge') === '1').length,
      relations: actualRelations.map((relation) => ({
        id: cellId(relation.edge),
        sourceCellId: relation.sourceMatch.cellId,
        targetCellId: relation.targetMatch.cellId,
        sourceComponentKey: relation.sourceMatch.identity?.componentKey || null,
        targetComponentKey: relation.targetMatch.identity?.componentKey || null,
        kind: relation.kind,
        label: edgeLabel(relation.edge, cells),
        petakerjaKey: readStableKey(relation.edge),
        labels: {
          simple: {
            en: cleanLabel(relation.edge.parentElement?.getAttribute('simpleLabelEn') || edgeLabel(relation.edge, cells)),
            ms: cleanLabel(relation.edge.parentElement?.getAttribute('simpleLabelMs') || edgeLabel(relation.edge, cells)),
          },
          code: {
            en: cleanLabel(relation.edge.parentElement?.getAttribute('codeLabelEn') || edgeLabel(relation.edge, cells)),
            ms: cleanLabel(relation.edge.parentElement?.getAttribute('codeLabelMs') || edgeLabel(relation.edge, cells)),
          },
        },
      })),
      logicFingerprint: pageLogicFingerprint(model), geometryFingerprint: pageFingerprint(model, true),
    };
  }

  function analyseXML(xml, manifests, options = {}) {
    try {
      const documentNode = normaliseDocument(xml);
      const diagrams = [...documentNode.documentElement.children].filter((child) => child.tagName === 'diagram');
      const pages = diagrams.map((diagram) => analysePage(diagram, manifests, options.diagramHint));
      let selectedPage = options.pageId ? pages.find((page) => page.id === options.pageId) : null;
      if (!selectedPage && options.diagramHint) selectedPage = pages.filter((page) => page.diagramId === options.diagramHint).sort((a, b) => b.score - a.score)[0];
      if (!selectedPage) selectedPage = pages.slice().sort((a, b) => b.score - a.score)[0];
      return {
        fatal: false, document: documentNode, xml: serializer.serializeToString(documentNode), pages, selectedPage,
        issues: pages.flatMap((page) => page.issues.map((entry) => ({ ...entry, pageId: page.id, diagramId: page.diagramId }))),
      };
    } catch (error) {
      return {
        fatal: true, xml: String(xml || ''), pages: [], selectedPage: null,
        issues: [issue('invalid-drawio-xml', 'fatal', [], `Fail tidak boleh dibaca: ${error.message}`, `The file cannot be read: ${error.message}`)],
      };
    }
  }

  function extractSinglePage(xml, pageId) {
    const documentNode = normaliseDocument(xml);
    const diagrams = [...documentNode.documentElement.children].filter((child) => child.tagName === 'diagram');
    const selected = diagrams.find((diagram) => diagram.getAttribute('id') === pageId) || diagrams[0];
    diagrams.filter((diagram) => diagram !== selected).forEach((diagram) => diagram.remove());
    return serializer.serializeToString(documentNode);
  }

  const PROJECTION_LANGUAGE_ATTR = 'petakerjaProjectionLanguage';
  const PROJECTION_LABEL_MODE_ATTR = 'petakerjaDiagramLabelMode';
  const LEGACY_PROJECTION_LABEL_MODE_ATTR = 'petakerjaSequenceLabelMode';

  function validLanguage(value, fallback = 'en') { return value === 'ms' ? 'ms' : value === 'en' ? 'en' : fallback; }
  function validDiagramLabelMode(value, fallback = 'simple') { return value === 'code' ? 'code' : value === 'simple' ? 'simple' : fallback; }

  function projectedLabelField(language, labelMode) {
    const prefix = validDiagramLabelMode(labelMode) === 'code' ? 'code' : 'simple';
    return `${prefix}Label${validLanguage(language) === 'ms' ? 'Ms' : 'En'}`;
  }

  function isBilingualElement(element) {
    return element?.hasAttribute('labelEn') || element?.hasAttribute('labelMs')
      || element?.hasAttribute('simpleLabelEn') || element?.hasAttribute('simpleLabelMs');
  }

  function bilingualElements(documentNode) {
    const wrappers = [...documentNode.querySelectorAll('object')].filter(isBilingualElement);
    const directCells = [...documentNode.querySelectorAll('mxCell')].filter((cell) => (
      cell.parentElement?.tagName !== 'object' && isBilingualElement(cell)
    ));
    return [...wrappers, ...directCells];
  }

  function visibleLabelAttribute(element) {
    return element.tagName === 'mxCell' ? 'value' : 'label';
  }

  function hasBilingualMetadata(documentNode) {
    return bilingualElements(documentNode).length > 0;
  }

  function projectLocalizedXML(xml, language = 'en', labelMode = 'simple') {
    const documentNode = normaliseDocument(xml);
    if (!hasBilingualMetadata(documentNode)) return serializer.serializeToString(documentNode);
    const activeLanguage = validLanguage(language);
    const activeMode = validDiagramLabelMode(labelMode);
    documentNode.documentElement.setAttribute(PROJECTION_LANGUAGE_ATTR, activeLanguage);
    documentNode.documentElement.setAttribute(PROJECTION_LABEL_MODE_ATTR, activeMode);
    documentNode.documentElement.removeAttribute(LEGACY_PROJECTION_LABEL_MODE_ATTR);
    bilingualElements(documentNode).forEach((element) => {
      const messageField = projectedLabelField(activeLanguage, activeMode);
      const genericField = activeLanguage === 'ms' ? 'labelMs' : 'labelEn';
      const visible = element.getAttribute(messageField) ?? element.getAttribute(genericField);
      if (visible != null) element.setAttribute(visibleLabelAttribute(element), visible);
    });
    return serializer.serializeToString(documentNode);
  }

  function canonicalizeLocalizedXML(xml, options = {}) {
    const documentNode = normaliseDocument(xml);
    const root = documentNode.documentElement;
    const bilingual = hasBilingualMetadata(documentNode);
    const language = validLanguage(root.getAttribute(PROJECTION_LANGUAGE_ATTR), validLanguage(options.fallbackLanguage || 'en'));
    const labelMode = validDiagramLabelMode(
      root.getAttribute(PROJECTION_LABEL_MODE_ATTR) || root.getAttribute(LEGACY_PROJECTION_LABEL_MODE_ATTR),
      validDiagramLabelMode(options.fallbackLabelMode || 'simple'),
    );
    let translationChanged = false;
    if (bilingual) {
      bilingualElements(documentNode).forEach((element) => {
        const isMessage = element.hasAttribute('simpleLabelEn') || element.hasAttribute('codeLabelEn');
        const activeField = isMessage
          ? projectedLabelField(language, labelMode)
          : (language === 'ms' ? 'labelMs' : 'labelEn');
        const visibleAttribute = visibleLabelAttribute(element);
        const visible = element.getAttribute(visibleAttribute);
        const expected = element.getAttribute(activeField);
        if (options.captureEdits !== false && visible != null && expected != null && visible !== expected) {
          element.setAttribute(activeField, visible);
          translationChanged = true;
        }
        const canonicalLabel = isMessage
          ? (element.getAttribute('simpleLabelEn') ?? element.getAttribute('codeLabelEn'))
          : element.getAttribute('labelEn');
        if (canonicalLabel != null) element.setAttribute(visibleAttribute, canonicalLabel);
      });
    }
    root.removeAttribute(PROJECTION_LANGUAGE_ATTR);
    root.removeAttribute(PROJECTION_LABEL_MODE_ATTR);
    root.removeAttribute(LEGACY_PROJECTION_LABEL_MODE_ATTR);
    return {
      xml: serializer.serializeToString(documentNode), bilingual, language, labelMode, translationChanged,
    };
  }

  function canonicalDocumentFingerprint(xml) {
    const documentNode = normaliseDocument(xml);
    // Draw.io rewrites host/version metadata, XML whitespace and attribute order
    // when a document is loaded, even when the user changed nothing. Those
    // serialization details must not turn a language projection into a content
    // edit or a cloud revision.
    [...documentNode.documentElement.attributes].forEach((attribute) => {
      documentNode.documentElement.removeAttribute(attribute.name);
    });
    documentNode.querySelectorAll('mxGraphModel').forEach((model) => {
      // Draw.io derives these from the current editor viewport, not from the
      // diagram's page or cell geometry.
      model.removeAttribute('dx');
      model.removeAttribute('dy');
    });
    documentNode.querySelectorAll('mxGeometry').forEach((geometry) => {
      // Draw.io omits explicit zero origins when it serializes a loaded cell.
      // Missing x/y and x="0"/y="0" are the same mxGeometry value.
      if (Number(geometry.getAttribute('x')) === 0) geometry.removeAttribute('x');
      if (Number(geometry.getAttribute('y')) === 0) geometry.removeAttribute('y');
    });
    [...documentNode.querySelectorAll('*')].forEach((element) => {
      const attributes = [...element.attributes]
        .map((attribute) => [attribute.name, attribute.value])
        .sort(([left], [right]) => left.localeCompare(right));
      [...element.attributes].forEach((attribute) => element.removeAttribute(attribute.name));
      attributes.forEach(([name, value]) => element.setAttribute(name, value));
    });
    const walker = document.createTreeWalker(documentNode, NodeFilter.SHOW_TEXT);
    const whitespace = [];
    while (walker.nextNode()) {
      if (!walker.currentNode.nodeValue?.trim()) whitespace.push(walker.currentNode);
    }
    whitespace.forEach((node) => node.remove());
    return serializer.serializeToString(documentNode);
  }

  function localizedIssue(entry, language) { return entry.message?.[language] || entry.message?.ms || entry.ruleId; }

  class EditorController {
    constructor(options) {
      this.iframe = options.iframe;
      this.data = options.data;
      this.assets = options.assets;
      this.translations = options.translations;
      this.manifests = buildCanonicalManifests(this.data, this.assets, this.translations);
      this.language = options.language || 'en';
      this.diagramLabelMode = validDiagramLabelMode(options.diagramLabelMode || options.sequenceLabelMode || 'simple');
      this.themePreference = ['light', 'dark', 'system'].includes(options.themePreference) ? options.themePreference : 'system';
      this.callbacks = options.callbacks || {};
      this.workingXml = '';
      this.filename = 'PetaKerja Diagram.drawio';
      this.analysis = null;
      this.diagramId = null;
      this.pageId = null;
      this.dirty = false;
      this.ready = false;
      this.frameStarted = false;
      this.pendingLoad = false;
      this.validationTimer = null;
      this.exportRequest = null;
      this.reloadRequest = null;
      this.operationRequests = new Map();
      this.selectedCellIds = [];
      this.editorScale = null;
      this.lastLogicFingerprint = null;
      this.lastDocumentFingerprint = null;
      this.boundMessage = (event) => this.onMessage(event);
      window.addEventListener('message', this.boundMessage);
    }

    get available() {
      if (window.PETAKERJA_EXPLORER_RUNTIME?.lite) return false;
      return window.location.protocol === 'http:' || window.location.protocol === 'https:';
    }

    editorURL() {
      const params = new URLSearchParams({
        embed: '1', proto: 'json', dev: '1', p: 'pkx', plugins: '1', local: '1', pages: '1',
        picker: '0', gapi: '0', db: '0', od: '0', gh: '0', tr: '0', prefetchFonts: '0',
        noSaveBtn: '1', saveAndExit: '0', noExitBtn: '1', lang: this.language,
        dark: this.themePreference === 'dark' ? '1' : this.themePreference === 'light' ? '0' : 'auto',
      });
      return `vendor/drawio/index.html?${params.toString()}`;
    }

    startFrame(force = false) {
      if (!this.available) return false;
      if (!this.frameStarted || force) {
        this.ready = false;
        this.frameStarted = true;
        this.pendingLoad = Boolean(this.workingXml);
        if (force) this.callbacks.onFrameReload?.();
        this.iframe.src = this.editorURL();
      } else if (this.workingXml && this.ready) {
        this.loadIntoEditor();
      }
      return true;
    }

    async openCanonical(diagramId) {
      const source = SOURCE_FILES[diagramId];
      if (!source) throw new Error('This diagram has no editable Draw.io source.');
      const response = await fetch(source.url, { cache: 'no-store' });
      if (!response.ok) throw new Error(`Unable to load ${source.url} (${response.status}).`);
      const fullXml = await response.text();
      return this.openXML(extractSinglePage(fullXml, source.pageId), {
        filename: source.filename, diagramHint: diagramId, pageId: source.pageId,
      });
    }

    newSession(options = {}) {
      const diagramId = options.diagramType || 'unknown';
      const pageId = options.pageId || `petakerja-${diagramId}-${Date.now()}`;
      const filename = options.filename || `${options.name || 'PetaKerja Diagram'}.drawio`;
      return this.openXML(createBlankDocument({ pageId, pageName: options.name || 'PetaKerja Diagram' }), {
        filename, diagramHint: EDITABLE_DIAGRAMS.includes(diagramId) ? diagramId : null, pageId, dirty: true,
      });
    }

    openXML(xml, options = {}) {
      const localized = canonicalizeLocalizedXML(xml, {
        fallbackLanguage: 'en', fallbackLabelMode: 'simple', captureEdits: true,
      });
      const analysis = analyseXML(localized.xml, this.manifests, { diagramHint: options.diagramHint, pageId: options.pageId });
      if (analysis.fatal) return analysis;
      this.analysis = analysis;
      this.workingXml = analysis.xml;
      this.filename = options.filename || this.filename;
      this.diagramId = analysis.selectedPage?.diagramId || options.diagramHint || null;
      this.pageId = options.pageId && analysis.pages.some((page) => page.id === options.pageId)
        ? options.pageId : (analysis.selectedPage?.id || null);
      this.dirty = Boolean(options.dirty);
      this.lastLogicFingerprint = analysis.selectedPage?.logicFingerprint || null;
      this.lastDocumentFingerprint = canonicalDocumentFingerprint(this.workingXml);
      this.pendingLoad = true;
      this.startFrame();
      this.callbacks.onAnalysis?.(analysis, { changeKind: 'load' });
      this.callbacks.onDirtyChange?.(this.dirty);
      this.callbacks.onWorkingDocument?.(this.documentSnapshot());
      return analysis;
    }

    preflight(xml) { return analyseXML(xml, this.manifests); }

    loadIntoEditor() {
      if (!this.ready || !this.workingXml) return;
      const visibleXml = projectLocalizedXML(this.workingXml, this.language, this.diagramLabelMode);
      this.post({ action: 'load', xml: visibleXml, autosave: 1, modified: '0', saveAndExit: 0, noSaveBtn: 1 });
      this.pendingLoad = false;
    }

    captureWorkingXML(xml, options = {}) {
      if (!xml) return false;
      const localized = canonicalizeLocalizedXML(xml, {
        fallbackLanguage: this.language,
        fallbackLabelMode: this.diagramLabelMode,
        captureEdits: options.captureEdits !== false,
      });
      const nextFingerprint = canonicalDocumentFingerprint(localized.xml);
      const previousFingerprint = this.lastDocumentFingerprint || canonicalDocumentFingerprint(this.workingXml);
      const changed = nextFingerprint !== previousFingerprint;
      this.workingXml = localized.xml;
      this.lastDocumentFingerprint = nextFingerprint;
      if (!changed) return false;
      if (options.markDirty !== false) {
        this.dirty = true;
        this.callbacks.onDirtyChange?.(true);
      }
      this.scheduleValidation();
      this.callbacks.onWorkingDocument?.(this.documentSnapshot());
      return true;
    }

    post(message) {
      if (!this.iframe.contentWindow || !this.available) return;
      this.iframe.contentWindow.postMessage(JSON.stringify(message), window.location.origin);
    }

    restoreEditorFocus() {
      this.post({
        action: 'petakerja-restore-view',
        pageId: this.pageId,
        cellId: this.selectedCellIds[0] || null,
        scale: this.editorScale,
      });
    }

    onMessage(event) {
      if (event.source !== this.iframe.contentWindow || event.origin !== window.location.origin) return;
      let message = event.data;
      if (typeof message === 'string') {
        try { message = JSON.parse(message); } catch (_error) { return; }
      }
      if (!message || typeof message !== 'object') return;
      if (message.event === 'init') {
        this.ready = true;
        this.loadIntoEditor();
      } else if (message.event === 'load') {
        this.ready = true;
        this.callbacks.onReady?.();
        this.restoreEditorFocus();
        this.sendIssues();
      } else if (message.event === 'autosave' || message.event === 'save') {
        if (message.xml) this.captureWorkingXML(message.xml);
        if (message.event === 'save') this.saveAs();
      } else if (message.event === 'export') {
        if (message.xml) {
          this.captureWorkingXML(message.xml);
          this.validateNow({ notifyDocument: false });
        }
        if (this.exportRequest) {
          const request = this.exportRequest;
          this.exportRequest = null;
          window.clearTimeout(request.timer);
          if (message.data) request.resolve({ svg: message.data, xml: this.workingXml, pageId: this.pageId });
          else request.reject(new Error('Draw.io returned an empty SVG export.'));
        }
      } else if (message.event === 'petakerja-committed') {
        if (this.exportRequest) this.post({
          action: 'export', format: 'svg', asText: true, embedCellMetadata: true,
          pageId: this.pageId, spin: 'Exporting current diagram',
        });
      } else if (message.event === 'petakerja-reload-ready') {
        const request = this.reloadRequest;
        if (!request) return;
        this.reloadRequest = null;
        window.clearTimeout(request.timer);
        if (message.xml) this.captureWorkingXML(message.xml);
        if (message.pageId) this.pageId = message.pageId;
        if (Number.isFinite(Number(message.scale)) && Number(message.scale) > 0) this.editorScale = Number(message.scale);
        if (request.reload) this.startFrame(true);
        request.resolve();
      } else if (message.event === 'petakerja-operation-result') {
        const request = this.operationRequests.get(message.requestId);
        if (request) {
          this.operationRequests.delete(message.requestId);
          window.clearTimeout(request.timer);
          if (message.ok) {
            if (message.xml) this.captureWorkingXML(message.xml);
            if (request.operation?.type === 'createPage' && message.pageId) {
              this.pageId = message.pageId;
              this.diagramId = request.operation.diagramType || null;
            }
            request.resolve(message);
          }
          else request.reject(new Error(message.error || 'Draw.io operation failed.'));
        }
      } else if (message.event === 'petakerja-ready') {
        this.callbacks.onReady?.();
        this.restoreEditorFocus();
        this.sendIssues();
      } else if (message.event === 'petakerja-selection') {
        if (Number.isFinite(Number(message.scale)) && Number(message.scale) > 0) this.editorScale = Number(message.scale);
        const page = this.analysis?.pages.find((item) => item.id === (message.pageId || this.pageId)) || this.analysis?.selectedPage;
        const selectedIds = message.cellIds || [];
        this.selectedCellIds = selectedIds.slice();
        let match = page?.matches.find((item) => selectedIds.includes(item.cellId)) || null;
        if (!match && page) {
          selectedIds.some((selectedId) => {
            let cell = page.cellById.get(selectedId);
            const visited = new Set();
            while (cell && !visited.has(cellId(cell))) {
              visited.add(cellId(cell));
              match = page.matches.find((item) => item.cellId === cellId(cell)) || null;
              if (match) return true;
              cell = page.cellById.get(cell.getAttribute('parent'));
            }
            return false;
          });
        }
        this.callbacks.onSelection?.(match, message);
      }
    }

    scheduleValidation() {
      window.clearTimeout(this.validationTimer);
      this.validationTimer = window.setTimeout(() => this.validateNow(), 300);
    }

    validateNow(options = {}) {
      const previous = this.analysis?.selectedPage;
      const analysis = analyseXML(this.workingXml, this.manifests, { diagramHint: this.diagramId, pageId: this.pageId });
      const current = analysis.selectedPage;
      const changeKind = previous && current && previous.logicFingerprint === current.logicFingerprint
        && previous.geometryFingerprint !== current.geometryFingerprint ? 'geometry' : 'logic';
      this.analysis = analysis;
      this.workingXml = analysis.xml;
      this.lastLogicFingerprint = current?.logicFingerprint || null;
      this.callbacks.onAnalysis?.(analysis, { changeKind });
      if (options.notifyDocument !== false) this.callbacks.onWorkingDocument?.(this.documentSnapshot());
      this.sendIssues();
      return analysis;
    }

    documentSnapshot() {
      return {
        xml: this.workingXml,
        pageId: this.pageId,
        filename: this.filename,
        diagramId: this.diagramId,
        analysis: this.analysis,
        dirty: this.dirty,
      };
    }

    exportRuntimeSVG() {
      if (!this.available || !this.ready || !this.workingXml) {
        return Promise.reject(new Error('The Draw.io editor is not ready to export the current diagram.'));
      }
      if (this.exportRequest) return this.exportRequest.promise;
      let resolveRequest;
      let rejectRequest;
      const promise = new Promise((resolve, reject) => { resolveRequest = resolve; rejectRequest = reject; });
      const timer = window.setTimeout(() => {
        const pending = this.exportRequest;
        this.exportRequest = null;
        pending?.reject(new Error('Timed out while exporting the current Draw.io page.'));
      }, 15000);
      this.exportRequest = { promise, resolve: resolveRequest, reject: rejectRequest, timer };
      this.post({ action: 'petakerja-commit-edit' });
      return promise;
    }

    applyOperation(operation, options = {}) {
      if (!this.available || !this.ready) return Promise.reject(new Error('The Draw.io editor is not ready.'));
      const requestId = `op-${Date.now()}-${Math.random().toString(36).slice(2)}`;
      return new Promise((resolve, reject) => {
        const timer = window.setTimeout(() => {
          this.operationRequests.delete(requestId);
          reject(new Error(`Operation timed out: ${operation.type}`));
        }, options.timeout || 12000);
        this.operationRequests.set(requestId, { resolve, reject, timer, operation });
        this.post({ action: 'petakerja-apply-operation', requestId, operation });
      });
    }

    restoreXML(xml, options = {}) {
      return this.openXML(xml, {
        filename: options.filename || this.filename,
        diagramHint: options.diagramHint || this.diagramId,
        pageId: options.pageId || this.pageId,
        dirty: options.dirty !== false,
      });
    }

    sendIssues() {
      if (!this.analysis) return;
      const issues = this.analysis.issues.map((entry) => ({
        severity: entry.severity, ruleId: entry.ruleId, cellIds: entry.cellIds,
        message: localizedIssue(entry, this.language), pageId: entry.pageId,
      }));
      this.post({ action: 'petakerja-validation', issues });
    }

    focusMatch(match) {
      if (!match) return;
      if (match.pageId) this.post({ action: 'petakerja-focus-page', pageId: match.pageId });
      this.post({ action: 'petakerja-focus-cell', cellId: match.cellId });
    }

    focusComponent(componentKey) {
      const page = this.analysis?.pages.find((item) => item.matches.some((match) => match.identity?.key === componentKey));
      const match = page?.matches.find((item) => item.identity?.key === componentKey);
      this.focusMatch(match);
    }

    resolveMatch(pageId, cellId, componentKey) {
      if (!this.workingXml) return;
      const documentNode = normaliseDocument(this.workingXml);
      const diagram = [...documentNode.documentElement.children].find((item) => item.tagName === 'diagram' && item.getAttribute('id') === pageId);
      const cell = diagram?.querySelector(`mxCell[id="${CSS.escape(cellId)}"]`);
      if (!cell) return;
      if (componentKey) writeStableKey(cell, componentKey); else cell.removeAttribute('petakerjaKey');
      this.workingXml = serializer.serializeToString(documentNode);
      this.dirty = true;
      this.validateNow();
      this.loadIntoEditor();
      this.callbacks.onDirtyChange?.(true);
    }

    captureLatestEditorXML(options = {}) {
      if (!this.frameStarted) return Promise.resolve();
      if (!this.ready) {
        if (options.reload) this.startFrame(true);
        return Promise.resolve();
      }
      if (this.reloadRequest) return this.reloadRequest.promise;
      let resolveRequest;
      let rejectRequest;
      const promise = new Promise((resolve, reject) => { resolveRequest = resolve; rejectRequest = reject; });
      const timer = window.setTimeout(() => {
        const pending = this.reloadRequest;
        if (!pending) return;
        this.reloadRequest = null;
        if (pending.reload) this.startFrame(true);
        pending.reject(new Error('The editor did not confirm its latest document before reloading or exporting.'));
      }, 5000);
      this.reloadRequest = {
        promise, resolve: resolveRequest, reject: rejectRequest, timer, reload: Boolean(options.reload),
      };
      this.post({ action: 'petakerja-prepare-reload' });
      return promise;
    }

    restartFrameSafely() { return this.captureLatestEditorXML({ reload: true }); }

    setLanguage(language) {
      if (language === this.language) return Promise.resolve();
      this.language = language;
      return this.restartFrameSafely();
    }

    setDiagramLabelMode(labelMode) {
      const next = validDiagramLabelMode(labelMode);
      if (next === this.diagramLabelMode) return Promise.resolve();
      this.diagramLabelMode = next;
      return this.restartFrameSafely();
    }

    setSequenceLabelMode(labelMode) { return this.setDiagramLabelMode(labelMode); }

    setThemePreference(preference) {
      const next = ['light', 'dark', 'system'].includes(preference) ? preference : 'system';
      if (next === this.themePreference) return Promise.resolve();
      this.themePreference = next;
      return this.restartFrameSafely();
    }

    async saveAs() {
      await this.captureLatestEditorXML({ reload: false });
      const analysis = this.validateNow();
      if (analysis.fatal) return false;
      const visibleXml = projectLocalizedXML(analysis.xml, this.language, this.diagramLabelMode);
      const blob = new Blob([visibleXml], { type: 'application/vnd.jgraph.mxfile' });
      const url = URL.createObjectURL(blob);
      const link = document.createElement('a');
      const base = (this.filename || 'PetaKerja Diagram.drawio').replace(/\.(?:drawio|xml)$/i, '');
      link.href = url;
      link.download = `${base} - edited.drawio`;
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.setTimeout(() => URL.revokeObjectURL(url), 1000);
      this.dirty = false;
      this.callbacks.onDirtyChange?.(false);
      this.callbacks.onWorkingDocument?.(this.documentSnapshot());
      return true;
    }

    markClean() {
      this.dirty = false;
      this.callbacks.onDirtyChange?.(false);
      this.callbacks.onWorkingDocument?.(this.documentSnapshot());
    }

    dispose() {
      window.removeEventListener('message', this.boundMessage);
      window.clearTimeout(this.validationTimer);
      if (this.exportRequest) window.clearTimeout(this.exportRequest.timer);
      if (this.reloadRequest) window.clearTimeout(this.reloadRequest.timer);
      this.operationRequests.forEach((request) => window.clearTimeout(request.timer));
    }
  }

  window.PETAKERJA_EDITOR = {
    EDITABLE_DIAGRAMS, SOURCE_FILES, buildCanonicalManifests, analyseXML, extractSinglePage, createBlankDocument,
    projectLocalizedXML, canonicalizeLocalizedXML, canonicalDocumentFingerprint, localizedLabelPairs,
    createController(options) { return new EditorController(options); },
  };
}());
