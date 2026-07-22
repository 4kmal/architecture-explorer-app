#!/usr/bin/env python3
"""Export, slim and bundle PetaKerja diagrams for offline interactive use.

The script uses only the Python standard library. Draw.io Desktop exports the
registered source pages, while the generator also keeps their non-visual BM/EN
editor metadata aligned with the View dictionaries. Geometry and relationships
are not rewritten by the localization pass.
"""

from __future__ import annotations

import html
import json
import os
import re
import shutil
import subprocess
import tempfile
import time
import xml.etree.ElementTree as ET
from pathlib import Path

from sequence_label_catalog import apply_all
from paths import ASSET_DIAGRAMS, DRAWIO, EDITOR, ROOT

CLASS_SOURCE = EDITOR / "class-diagram-petakerja.drawio"
DOMAIN_SOURCE = EDITOR / "class-domain-petakerja.drawio"
USECASE_SOURCE = EDITOR / "use-case-petakerja.drawio"
GOOGLE_OAUTH_SEQUENCE_SOURCE = ROOT / "assets" / "editor" / "sequence-google-oauth.drawio"
GOOGLE_SIGN_IN_FLOWCHART_SOURCE = ROOT / "assets" / "editor" / "flowchart-user-google-sign-in.drawio"
GOOGLE_SIGN_IN_FLOWCHART_ORIGINAL_SOURCE = ROOT / "assets" / "editor" / "flowchart-user-google-sign-in-original.drawio"
USER_SEARCH_JOBS_FLOWCHART_SOURCE = ROOT / "assets" / "editor" / "flowchart-user-search-jobs.drawio"
USER_SEARCH_JOBS_FLOWCHART_ORIGINAL_SOURCE = ROOT / "assets" / "editor" / "flowchart-user-search-jobs-original.drawio"
USER_EXPLORE_3D_MAP_FLOWCHART_SOURCE = ROOT / "assets" / "editor" / "flowchart-user-explore-3d-map.drawio"
USER_EXPLORE_3D_MAP_FLOWCHART_ORIGINAL_SOURCE = ROOT / "assets" / "editor" / "flowchart-user-explore-3d-map-original.drawio"
USER_SIGN_OUT_FLOWCHART_SOURCE = ROOT / "assets" / "editor" / "flowchart-user-sign-out.drawio"
USER_SIGN_OUT_FLOWCHART_ORIGINAL_SOURCE = ROOT / "assets" / "editor" / "flowchart-user-sign-out-original.drawio"
ADMIN_MANAGE_USERS_FLOWCHART_SOURCE = ROOT / "assets" / "editor" / "flowchart-admin-manage-users.drawio"
ADMIN_ACCESS_DASHBOARD_FLOWCHART_SOURCE = ROOT / "assets" / "editor" / "flowchart-admin-access-dashboard.drawio"
ADMIN_MONITOR_ACTIVITY_FLOWCHART_SOURCE = ROOT / "assets" / "editor" / "flowchart-admin-monitor-activity.drawio"
ADMIN_MANAGE_AI_CONFIGURATION_FLOWCHART_SOURCE = ROOT / "assets" / "editor" / "flowchart-admin-manage-ai-configuration.drawio"
ADMIN_SIGN_OUT_FLOWCHART_SOURCE = ROOT / "assets" / "editor" / "flowchart-admin-sign-out.drawio"
ADMIN_MANAGE_USERS_FLOWCHART_ORIGINAL_SOURCE = ROOT / "assets" / "editor" / "flowchart-admin-manage-users-original.drawio"
ADMIN_ACCESS_DASHBOARD_FLOWCHART_ORIGINAL_SOURCE = ROOT / "assets" / "editor" / "flowchart-admin-access-dashboard-original.drawio"
ADMIN_MONITOR_ACTIVITY_FLOWCHART_ORIGINAL_SOURCE = ROOT / "assets" / "editor" / "flowchart-admin-monitor-activity-original.drawio"
ADMIN_MANAGE_AI_CONFIGURATION_FLOWCHART_ORIGINAL_SOURCE = ROOT / "assets" / "editor" / "flowchart-admin-manage-ai-configuration-original.drawio"
ADMIN_SIGN_OUT_FLOWCHART_ORIGINAL_SOURCE = ROOT / "assets" / "editor" / "flowchart-admin-sign-out-original.drawio"
JOB_SEARCH_SEQUENCE_SOURCE = ROOT / "assets" / "editor" / "sequence-job-search.drawio"
ADMIN_MANAGE_USERS_SEQUENCE_SOURCE = ROOT / "assets" / "editor" / "sequence-admin-manage-users.drawio"
ADMIN_MANAGE_AI_CONFIGURATION_SEQUENCE_SOURCE = ROOT / "assets" / "editor" / "sequence-admin-manage-ai-configuration.drawio"
ADMIN_ACCESS_DASHBOARD_SEQUENCE_SOURCE = ROOT / "assets" / "editor" / "sequence-admin-access-dashboard.drawio"
ADMIN_MONITOR_ACTIVITY_SEQUENCE_SOURCE = ROOT / "assets" / "editor" / "sequence-admin-monitor-activity.drawio"
ADMIN_SIGN_OUT_SEQUENCE_SOURCE = ROOT / "assets" / "editor" / "sequence-admin-sign-out.drawio"
USER_EXPLORE_3D_MAP_SEQUENCE_SOURCE = ROOT / "assets" / "editor" / "sequence-user-explore-3d-map.drawio"
USER_SIGN_OUT_SEQUENCE_SOURCE = ROOT / "assets" / "editor" / "sequence-user-sign-out.drawio"
REPORT_DIAGRAMS = ASSET_DIAGRAMS
OUTPUT = ROOT / "diagram-assets.js"
DOMAIN_EDITOR_ASSET = ROOT / "assets" / "editor" / "class-domain-petakerja.drawio"
DOMAIN_ORIGINAL_SOURCE = ROOT / "assets" / "editor" / "class-domain-petakerja-original.drawio"
LAYERED_ARCHITECTURE_SOURCE = ROOT / "assets" / "editor" / "architecture-layered.drawio"
LAYERED_ARCHITECTURE_ORIGINAL_SOURCE = ROOT / "assets" / "editor" / "architecture-layered-original.drawio"
ARCHITECTURE_VISUAL_STACK_SOURCE = ROOT / "assets" / "editor" / "architecture-visual-stack.drawio"
MODULE_HIERARCHY_SOURCE = ROOT / "assets" / "editor" / "module-hierarchy.drawio"
MODULE_HIERARCHY_ORIGINAL_SOURCE = ROOT / "assets" / "editor" / "module-hierarchy-original.drawio"
MODULE_HIERARCHY_LAYERED_STACK_SOURCE = ROOT / "assets" / "editor" / "module-hierarchy-layered-stack.drawio"
MAP_ROUTING_STACK_SOURCE = ROOT / "assets" / "editor" / "petakerja-map-routing-responsibility-stack.drawio"
MAP_ROUTING_WORKFLOW_EDITOR = ROOT / "assets" / "editor" / "map-routing"
NOMINATIM_VALHALLA_WORKFLOW_SOURCE = MAP_ROUTING_WORKFLOW_EDITOR / "nominatim-valhalla-workflow.drawio"
NOMINATIM_MAPLIBRE_WORKFLOW_SOURCE = MAP_ROUTING_WORKFLOW_EDITOR / "nominatim-maplibre-workflow.drawio"
VALHALLA_MAPLIBRE_WORKFLOW_SOURCE = MAP_ROUTING_WORKFLOW_EDITOR / "valhalla-maplibre-workflow.drawio"
GEO_SERVER_COMMUNICATION_WORKFLOW_SOURCE = MAP_ROUTING_WORKFLOW_EDITOR / "geo-server-communication-workflow.drawio"
ETL_PIPELINE_SOURCE = ROOT / "assets" / "editor" / "etl-pipeline.drawio"
DAILY_INDEX_WORKFLOW_SOURCE = ROOT / "assets" / "editor" / "daily-index-workflow.drawio"
LIVE_SEARCH_WORKFLOW_SOURCE = ROOT / "assets" / "editor" / "live-search-workflow.drawio"
DEPLOYMENT_INFRASTRUCTURE_SOURCE = ROOT / "assets" / "editor" / "deployment-infrastructure.drawio"
V2_GEOROUTING_EDITOR = EDITOR / "v2-georouting"

V2_GEOROUTING_EXPORTS = {
    "v2-geo-usecase": ("usecase.drawio", "v2_geo_usecase", "usecase.svg"),
    "v2-geo-map-flowchart": ("map-flowchart.drawio", "v2_geo_map_flowchart", "map-flowchart.svg"),
    "v2-geo-route-sequence": ("route-sequence.drawio", "v2_geo_route_sequence", "route-sequence.svg"),
    "v2-geo-travel-analysis-sequence": ("travel-analysis-sequence.drawio", "v2_geo_travel_analysis_sequence", "travel-analysis-sequence.svg"),
    "v2-geo-job-route-sequence": ("job-route-sequence.drawio", "v2_geo_job_route_sequence", "job-route-sequence.svg"),
    "v2-geo-domain": ("domain.drawio", "v2_geo_domain", "domain.svg"),
    "v2-geo-implementation": ("implementation.drawio", "v2_geo_implementation", "implementation.svg"),
    "v2-geo-architecture": ("architecture.drawio", "v2_geo_architecture", "architecture.svg"),
    "v2-geo-modules": ("modules.drawio", "v2_geo_modules", "modules.svg"),
    "v2-geo-data-flow": ("data-flow.drawio", "v2_geo_data_flow", "data-flow.svg"),
    "v2-geo-erd": ("erd.drawio", "v2_geo_erd", "erd.svg"),
    "v2-geo-routing-stack": ("routing-stack.drawio", "v2_geo_routing_stack", "routing-stack.svg"),
    "v2-geo-supabase": ("supabase.drawio", "v2_geo_supabase", "supabase.svg"),
}
V2_GEOROUTING_IDS = frozenset(V2_GEOROUTING_EXPORTS)
MAP_ROUTING_WORKFLOW_IDS = frozenset({
    "nominatim-valhalla-workflow", "nominatim-maplibre-workflow",
    "valhalla-maplibre-workflow", "geo-server-communication-workflow",
})
EMBEDDED_BILINGUAL_IDS = frozenset({
    "etl-pipeline", "daily-index-workflow", "live-search-workflow",
    "deployment-infrastructure", "modules-layered-stack", "architecture-visual-stack", *MAP_ROUTING_WORKFLOW_IDS,
})
WORKFLOW_SOURCES = frozenset({
    DAILY_INDEX_WORKFLOW_SOURCE, LIVE_SEARCH_WORKFLOW_SOURCE,
    ARCHITECTURE_VISUAL_STACK_SOURCE,
    NOMINATIM_VALHALLA_WORKFLOW_SOURCE, NOMINATIM_MAPLIBRE_WORKFLOW_SOURCE,
    VALHALLA_MAPLIBRE_WORKFLOW_SOURCE, GEO_SERVER_COMMUNICATION_WORKFLOW_SOURCE,
})
V2_GEOROUTING_SEQUENCE_IDS = frozenset({
    "v2-geo-route-sequence", "v2-geo-travel-analysis-sequence", "v2-geo-job-route-sequence",
})


DRAWIO_EXPORTS = {
    "usecase": (USECASE_SOURCE, 1, "use-case.svg"),
    "domain": (DOMAIN_EDITOR_ASSET, 1, "class-domain.svg"),
    "domain-original": (DOMAIN_ORIGINAL_SOURCE, 1, "class-domain-original.svg"),
    "implementation": (CLASS_SOURCE, 2, "class-implementation.svg"),
    "supabase": (CLASS_SOURCE, 3, "supabase-full.svg"),
    "sequence": (JOB_SEARCH_SEQUENCE_SOURCE, 1, "sequence-job-search.svg"),
    "google-oauth-sequence": (GOOGLE_OAUTH_SEQUENCE_SOURCE, 1, "sequence-google-oauth.svg"),
    "user-google-sign-in-flowchart": (GOOGLE_SIGN_IN_FLOWCHART_SOURCE, 1, "flowchart-user-google-sign-in.svg"),
    "user-google-sign-in-flowchart-original": (GOOGLE_SIGN_IN_FLOWCHART_ORIGINAL_SOURCE, 1, "flowchart-user-google-sign-in-original.svg"),
    "user-search-jobs-flowchart": (USER_SEARCH_JOBS_FLOWCHART_SOURCE, 1, "flowchart-user-search-jobs.svg"),
    "user-search-jobs-flowchart-original": (USER_SEARCH_JOBS_FLOWCHART_ORIGINAL_SOURCE, 1, "flowchart-user-search-jobs-original.svg"),
    "user-explore-3d-map-flowchart": (USER_EXPLORE_3D_MAP_FLOWCHART_SOURCE, 1, "flowchart-user-explore-3d-map.svg"),
    "user-explore-3d-map-flowchart-original": (USER_EXPLORE_3D_MAP_FLOWCHART_ORIGINAL_SOURCE, 1, "flowchart-user-explore-3d-map-original.svg"),
    "user-sign-out-flowchart": (USER_SIGN_OUT_FLOWCHART_SOURCE, 1, "flowchart-user-sign-out.svg"),
    "user-sign-out-flowchart-original": (USER_SIGN_OUT_FLOWCHART_ORIGINAL_SOURCE, 1, "flowchart-user-sign-out-original.svg"),
    "admin-manage-users-flowchart": (ADMIN_MANAGE_USERS_FLOWCHART_SOURCE, 1, "flowchart-admin-manage-users.svg"),
    "admin-access-dashboard-flowchart": (ADMIN_ACCESS_DASHBOARD_FLOWCHART_SOURCE, 1, "flowchart-admin-access-dashboard.svg"),
    "admin-monitor-activity-flowchart": (ADMIN_MONITOR_ACTIVITY_FLOWCHART_SOURCE, 1, "flowchart-admin-monitor-activity.svg"),
    "admin-manage-ai-configuration-flowchart": (ADMIN_MANAGE_AI_CONFIGURATION_FLOWCHART_SOURCE, 1, "flowchart-admin-manage-ai-configuration.svg"),
    "admin-sign-out-flowchart": (ADMIN_SIGN_OUT_FLOWCHART_SOURCE, 1, "flowchart-admin-sign-out.svg"),
    "admin-manage-users-flowchart-original": (ADMIN_MANAGE_USERS_FLOWCHART_ORIGINAL_SOURCE, 1, "flowchart-admin-manage-users-original.svg"),
    "admin-access-dashboard-flowchart-original": (ADMIN_ACCESS_DASHBOARD_FLOWCHART_ORIGINAL_SOURCE, 1, "flowchart-admin-access-dashboard-original.svg"),
    "admin-monitor-activity-flowchart-original": (ADMIN_MONITOR_ACTIVITY_FLOWCHART_ORIGINAL_SOURCE, 1, "flowchart-admin-monitor-activity-original.svg"),
    "admin-manage-ai-configuration-flowchart-original": (ADMIN_MANAGE_AI_CONFIGURATION_FLOWCHART_ORIGINAL_SOURCE, 1, "flowchart-admin-manage-ai-configuration-original.svg"),
    "admin-sign-out-flowchart-original": (ADMIN_SIGN_OUT_FLOWCHART_ORIGINAL_SOURCE, 1, "flowchart-admin-sign-out-original.svg"),
    "admin-manage-users-sequence": (ADMIN_MANAGE_USERS_SEQUENCE_SOURCE, 1, "sequence-admin-manage-users.svg"),
    "admin-manage-ai-configuration-sequence": (ADMIN_MANAGE_AI_CONFIGURATION_SEQUENCE_SOURCE, 1, "sequence-admin-manage-ai-configuration.svg"),
    "admin-access-dashboard-sequence": (ADMIN_ACCESS_DASHBOARD_SEQUENCE_SOURCE, 1, "sequence-admin-access-dashboard.svg"),
    "admin-monitor-activity-sequence": (ADMIN_MONITOR_ACTIVITY_SEQUENCE_SOURCE, 1, "sequence-admin-monitor-activity.svg"),
    "admin-sign-out-sequence": (ADMIN_SIGN_OUT_SEQUENCE_SOURCE, 1, "sequence-admin-sign-out.svg"),
    "user-explore-3d-map-sequence": (USER_EXPLORE_3D_MAP_SEQUENCE_SOURCE, 1, "sequence-user-explore-3d-map.svg"),
    "user-sign-out-sequence": (USER_SIGN_OUT_SEQUENCE_SOURCE, 1, "sequence-user-sign-out.svg"),
    "architecture-visual-stack": (ARCHITECTURE_VISUAL_STACK_SOURCE, 0, "architecture-visual-stack.svg"),
    "architecture": (LAYERED_ARCHITECTURE_SOURCE, 1, "architecture-layered.svg"),
    "architecture-original": (LAYERED_ARCHITECTURE_ORIGINAL_SOURCE, 1, "architecture-layered-original.svg"),
    "modules": (MODULE_HIERARCHY_SOURCE, 1, "module-hierarchy.svg"),
    "modules-original": (MODULE_HIERARCHY_ORIGINAL_SOURCE, 1, "module-hierarchy-original.svg"),
    "modules-layered-stack": (MODULE_HIERARCHY_LAYERED_STACK_SOURCE, 0, "module-hierarchy-layered-stack.svg"),
    "map-routing-responsibility-stack": (MAP_ROUTING_STACK_SOURCE, 1, "petakerja-map-routing-responsibility-stack.svg"),
    "nominatim-valhalla-workflow": (NOMINATIM_VALHALLA_WORKFLOW_SOURCE, 0, "map-routing/nominatim-valhalla-workflow.svg"),
    "nominatim-maplibre-workflow": (NOMINATIM_MAPLIBRE_WORKFLOW_SOURCE, 0, "map-routing/nominatim-maplibre-workflow.svg"),
    "valhalla-maplibre-workflow": (VALHALLA_MAPLIBRE_WORKFLOW_SOURCE, 0, "map-routing/valhalla-maplibre-workflow.svg"),
    "geo-server-communication-workflow": (GEO_SERVER_COMMUNICATION_WORKFLOW_SOURCE, 0, "map-routing/geo-server-communication-workflow.svg"),
    "etl-pipeline": (ETL_PIPELINE_SOURCE, 1, "etl-pipeline.svg"),
    "daily-index-workflow": (DAILY_INDEX_WORKFLOW_SOURCE, 0, "daily-index-workflow.svg"),
    "live-search-workflow": (LIVE_SEARCH_WORKFLOW_SOURCE, 0, "live-search-workflow.svg"),
    "deployment-infrastructure": (DEPLOYMENT_INFRASTRUCTURE_SOURCE, 1, "deployment-infrastructure.svg"),
    **{
        diagram_id: (V2_GEOROUTING_EDITOR / source_name, 1, f"v2-georouting/{svg_name}")
        for diagram_id, (source_name, _page_id, svg_name) in V2_GEOROUTING_EXPORTS.items()
    },
}

REPORT_EXPORTS = {
    "activity": "activity-job-search.svg",
    "erd": "erd-core.svg",
    "data-flow": "data-flow.svg",
}


CLASS_NODE_MAP = {
    "AuthIdentity": "auth-identity",
    "UserProfile": "user-profile",
    "State": "state-entity",
    "DataSource": "data-source-entity",
    "POICategoryGroup": "poi-group-entity",
    "POICategory": "poi-category-entity",
    "POI": "poi-entity",
    "HighlightArea": "highlight-entity",
    "OpenDataAPI": "open-data-api",
    "JobListing": "job-entity",
    "UserJobState": "job-state-entity",
    "AIProviderCredential": "ai-credential-entity",
    "AIModelPreference": "ai-preference-entity",
    "AIUsageEvent": "ai-usage-entity",
    "AdminAuditLog": "audit-log-entity",
    "AppState": "app-state",
    "MyPetaApp": "mypeta-app",
    "AuthManager": "auth-manager",
    "MapManager": "map-manager",
    "POIManager": "poi-manager",
    "SearchManager": "search-manager",
    "CategoryManager": "category-manager",
    "InsightsManager": "insights-manager",
    "HighlightManager": "highlight-manager",
    "JobFinderManager": "job-manager",
    "ChatbotManager": "chatbot-manager",
    "AdminDashboardManager": "admin-manager",
    "NationalDataCubeManager": "national-data-cube-manager",
    "supabase.ts": "supabase-module",
    "auth-client.ts": "better-auth",
    "Jobs API modules": "jobs-api",
    "assistantStream.ts": "assistant-stream",
    "aiProviderApi.ts / admin API": "ai-provider",
    "Jenis Kongsi": "shared-types",
}

USECASE_NODE_MAP = {
    "actor-user": "pengguna",
    "actor-admin": "pentadbir",
    "uc-login": "auth-manager",
    "uc-explore": "map-manager",
    "uc-search-poi": "search-manager",
    "uc-filter-poi": "category-manager",
    "uc-poi-details": "poi-manager",
    "uc-open-data": "insights-manager",
    "uc-search-jobs": "job-manager",
    "uc-job-details": "job-manager",
    "uc-save-status": "job-state-entity",
    "uc-logout": "auth-manager",
    "uc-admin-dashboard": "admin-manager",
    "uc-admin-usage": "audit-log-entity",
    "uc-admin-users": "user-profile",
    "uc-admin-ai": "ai-credential-entity",
    "EQjXTwZ-n2oy3b9Xs3Cg-3": "chatbot-manager",
}

TABLE_NODE_MAP = {
    "user": "auth-identity",
    "users": "user-profile",
    "states": "state-entity",
    "data_sources": "data-source-entity",
    "poi_category_groups": "poi-group-entity",
    "poi_categories": "poi-category-entity",
    "pois": "poi-entity",
    "scraped_jobs": "job-entity",
    "user_job_states": "job-state-entity",
    "ai_provider_credentials": "ai-credential-entity",
    "ai_user_model_preferences": "ai-preference-entity",
    "ai_usage_events": "ai-usage-entity",
    "ai_admin_audit_logs": "audit-log-entity",
    "pipeline_runs": "pipeline-runs-entity",
    "pipeline_run_items": "pipeline-items-entity",
    "spatial_ref_sys": "spatial-ref",
}

HOTSPOTS = {
    "pengguna": ["start-workspaces"],
    "pentadbir": ["user-menu"],
    "auth-manager": ["auth-modal", "user-menu"],
    "map-manager": ["map-canvas", "ribbon-map", "start-map-preset"],
    "poi-manager": ["map-canvas", "contents-poi"],
    "search-manager": ["map-search"],
    "category-manager": ["contents-poi"],
    "insights-manager": ["ribbon-data", "catalog-national"],
    "national-data-cube-manager": ["ribbon-data", "catalog-national", "map-canvas"],
    "highlight-manager": ["assistant-highlight", "map-canvas"],
    "highlight-entity": ["assistant-highlight"],
    "job-manager": ["jobs-search", "jobs-cards", "jobs-map"],
    "job-entity": ["jobs-search", "jobs-cards", "jobs-map"],
    "job-state-entity": ["jobs-cards"],
    "chatbot-manager": ["assistant-panel", "assistant-highlight"],
    "admin-manager": ["user-menu", "auth-modal"],
    "admin-ui": ["admin-entry", "admin-users-tab", "admin-users-table"],
    "admin-api-client": ["admin-users-tab", "admin-users-table"],
    "admin-users-api": ["admin-users-tab", "admin-users-table"],
    "user-profile": ["user-menu", "auth-modal"],
    "poi-entity": ["map-search", "map-canvas"],
    "state-entity": ["map-canvas", "catalog-national"],
    "ai-preference-entity": ["assistant-panel"],
    "ai-usage-entity": ["assistant-panel"],
    "mypeta-app": ["start-workspaces", "ribbon"],
    "supabase-module": [],
    "jobs-api": ["jobs-search"],
    "supa-jobs-route": ["jobs-search"],
    "job-search-relevance": ["jobs-search", "jobs-cards"],
    "assistant-stream": ["assistant-panel"],
    "ai-provider": ["assistant-panel"],
    "shared-types": [],
}


USECASE_EN = {
    "Rajah Kes Guna Sistem PetaKerja": "PetaKerja System Use Case Diagram",
    "Sistem PetaKerja": "PetaKerja System",
    "Pengguna": "User",
    "Pentadbir": "Administrator",
    "Log masuk menggunakan Google Oauth": "Sign in with Google OAuth",
    "Teroka peta 3D": "Explore the 3D map",
    "Cari POI": "Search POIs",
    "Tapis kategori POI": "Filter POI categories",
    "Lihat butiran POI": "View POI details",
    "Lihat analitik data terbuka": "View open-data analytics",
    "Cari pekerjaan": "Search jobs",
    "Lihat butiran pekerjaan": "View job details",
    "Simpan dan kemas kini": "Save and update",
    "status &amp; carian pekerjaan": "job status &amp; search",
    "Log keluar": "Sign out",
    "Akses papan pemuka pentadbir": "Access the administrator dashboard",
    "Memantau Log Aktiviti Sistem": "Monitor system activity logs",
    "Mengurus Pengguna": "Manage users",
    "Mengurus Konfigurasi AI Chatbot": "Manage AI chatbot configuration",
    "Bertanya AI Chatbot": "Ask the AI chatbot",
}

GOOGLE_OAUTH_SEQUENCE_MS = {
    "PetaKerja Sign in with Google OAuth Sequence": "Jujukan Log Masuk PetaKerja dengan Google OAuth",
    "User": "Pengguna",
    "PetaKerja Profile API": "API Profil PetaKerja",
    "Select Sign in": "Pilih Log masuk",
    "Display Google sign-in prompt": "Paparkan prompt log masuk Google",
    "Select Continue with Google": "Pilih Teruskan dengan Google",
    "Redirect to Google OAuth": "Ubah hala ke Google OAuth",
    "Show account selection and consent": "Paparkan pemilihan akaun dan persetujuan",
    "Select account and grant consent": "Pilih akaun dan beri persetujuan",
    "Create or update user, account and session": "Cipta atau kemas kini pengguna, akaun dan sesi",
    "Account and session persisted": "Akaun dan sesi disimpan",
    "Set session cookie and redirect to PetaKerja": "Tetapkan kuki sesi dan ubah hala ke PetaKerja",
    "OAuth rejected, cancelled or failed": "OAuth ditolak, dibatalkan atau gagal",
    "Remain in guest state / show sign-in error": "Kekal sebagai tetamu / paparkan ralat log masuk",
    "Read Better Auth session and user": "Baca sesi dan pengguna Better Auth",
    "Session and user": "Sesi dan pengguna",
    "Better Auth session": "Sesi Better Auth",
    "Session user": "Pengguna sesi",
    "No authenticated session": "Tiada sesi disahkan",
    "render guest sign-in": "paparkan log masuk tetamu",
    "Verified Better Auth user": "Pengguna Better Auth disahkan",
    "Find by better_auth_user_id": "Cari melalui better_auth_user_id",
    "Linked public.users profile": "Profil public.users yang dipaut",
    "Find existing user by email": "Cari pengguna sedia ada melalui e-mel",
    "Update better_auth_user_id and profile fields": "Kemas kini better_auth_user_id dan medan profil",
    "Created application profile": "Profil aplikasi dicipta",
    "AuthUser profile": "Profil AuthUser",
    "Notify subscribers": "Maklumkan pelanggan state",
    "Render authenticated user menu": "Paparkan menu pengguna disahkan",
    "alt [OAuth authorization]": "alt [pengesahan OAuth]",
    "alt [Better Auth session]": "alt [sesi Better Auth]",
    "alt [application profile mapping]": "alt [pemetaan profil aplikasi]",
    "[OAuth authorized]": "[OAuth dibenarkan]",
    "[else: rejected / cancelled / error]": "[selainnya: ditolak / dibatalkan / ralat]",
    "[session user exists]": "[pengguna sesi wujud]",
    "[else: no session]": "[selainnya: tiada sesi]",
    "[better_auth_user_id found]": "[better_auth_user_id ditemui]",
    "[else: email match]": "[selainnya: e-mel sepadan]",
    "[else: no profile]": "[selainnya: tiada profil]",
    "Google OAuth only. Password sign-in is intentionally unavailable in PetaKerja.": "Google OAuth sahaja. Log masuk kata laluan sengaja tidak disediakan dalam PetaKerja.",
}

GOOGLE_OAUTH_SEQUENCE_COMPONENTS = [
    # Frame hitboxes are generated first so the narrower participant hitboxes are
    # layered above them in View mode. This keeps every lifeline selectable even
    # where an alt frame spans the same part of the canvas.
    ("fragment-oauth", ["google-oauth-sequence/fragment-oauth", "google-oauth-sequence/oauth-"], ["auth-modal-manager", "auth-manager", "better-auth", "google-oauth"], ["auth-modal"], "Alternatif OAuth", "OAuth alternative"),
    ("fragment-session", ["google-oauth-sequence/fragment-session", "google-oauth-sequence/session-"], ["auth-manager", "auth-client", "better-auth"], ["auth-modal", "user-menu"], "Alternatif sesi", "Session alternative"),
    ("fragment-profile", ["google-oauth-sequence/fragment-profile", "google-oauth-sequence/profile-"], ["profile-bridge", "user-profile"], ["user-menu"], "Alternatif pemetaan profil", "Profile-mapping alternative"),
    ("participant-user", ["google-oauth-sequence/participant-user"], ["pengguna"], ["auth-modal", "user-menu"], "Pengguna", "User"),
    ("participant-ui", ["google-oauth-sequence/participant-ui"], ["user-menu-manager", "auth-modal-manager"], ["auth-modal", "user-menu"], "UI PetaKerja", "PetaKerja UI"),
    ("participant-auth-manager", ["google-oauth-sequence/participant-auth-manager"], ["auth-manager"], ["auth-modal", "user-menu"], "AuthManager", "AuthManager"),
    ("participant-auth-client", ["google-oauth-sequence/participant-auth-client"], ["auth-client"], ["auth-modal"], "authClient", "authClient"),
    ("participant-better-auth", ["google-oauth-sequence/participant-better-auth"], ["better-auth"], ["auth-modal"], "API Better Auth", "Better Auth API"),
    ("participant-google-oauth", ["google-oauth-sequence/participant-google-oauth"], ["google-oauth"], ["auth-modal"], "Google OAuth", "Google OAuth"),
    ("participant-profile-api", ["google-oauth-sequence/participant-profile-api"], ["profile-bridge"], ["user-menu"], "API Profil PetaKerja", "PetaKerja Profile API"),
    ("participant-database", ["google-oauth-sequence/participant-database"], ["supabase-db", "auth-identity", "user-profile"], ["user-menu"], "Supabase / PostgreSQL", "Supabase / PostgreSQL"),
]

GOOGLE_SIGN_IN_FLOWCHART_MS = {
    "PetaKerja Sign in with Google Flow Chart": "Carta Alir Log Masuk PetaKerja dengan Google",
    "Google-only authentication; password sign-in, registration and password reset are not part of this flow.": "Pengesahan Google sahaja; log masuk kata laluan, pendaftaran dan tetapan semula kata laluan tidak termasuk dalam aliran ini.",
    "Start": "Mula",
    "End": "Tamat",
    "User selects Sign in": "Pengguna memilih Log Masuk",
    "Display the Google sign-in prompt": "Paparkan prompt log masuk Google",
    "User selects Continue with Google": "Pengguna memilih Teruskan dengan Google",
    "Start Google OAuth": "Mulakan Google OAuth",
    "Google authorization completed?": "Pengesahan Google selesai?",
    "Display cancellation or sign-in error": "Paparkan pembatalan atau ralat log masuk",
    "Remain in guest state and display Sign in": "Kekal dalam keadaan tetamu dan paparkan Log Masuk",
    "Create or update identity, account and session": "Cipta atau kemas kini identiti, akaun dan sesi",
    "Redirect to PetaKerja": "Ubah hala ke PetaKerja",
    "Check the active session": "Semak sesi aktif",
    "Active session found?": "Sesi aktif ditemui?",
    "Request the PetaKerja profile": "Minta profil PetaKerja",
    "Linked profile found?": "Profil terpaut ditemui?",
    "Load the linked profile": "Muatkan profil terpaut",
    "Matching email profile found?": "Profil dengan e-mel sepadan ditemui?",
    "Link the existing profile": "Pautkan profil sedia ada",
    "Create a new PetaKerja profile": "Cipta profil PetaKerja baharu",
    "Profile obtained successfully?": "Profil berjaya diperoleh?",
    "Return the profile to the application": "Pulangkan profil kepada aplikasi",
    "Update the signed-in user state": "Kemas kini keadaan pengguna yang log masuk",
    "Display the authenticated user menu": "Paparkan menu pengguna yang disahkan",
    "Yes": "Ya",
    "No": "Tidak",
}

GOOGLE_SIGN_IN_FLOWCHART_COMPONENTS = {
    "start": (["pengguna"], ["user-menu"], "Mula", "Start"),
    "select-sign-in": (["pengguna", "user-menu-manager"], ["user-menu"], "Pengguna memilih Log Masuk", "User selects Sign in"),
    "show-google-prompt": (["auth-modal-manager"], ["auth-modal"], "Paparkan prompt log masuk Google", "Display the Google sign-in prompt"),
    "select-google": (["pengguna", "auth-modal-manager", "auth-manager"], ["auth-modal"], "Pengguna memilih Teruskan dengan Google", "User selects Continue with Google"),
    "start-google-oauth": (["auth-manager", "auth-client", "better-auth", "google-oauth"], ["auth-modal"], "Mulakan Google OAuth", "Start Google OAuth"),
    "authorization-completed": (["better-auth", "google-oauth"], ["auth-modal"], "Pengesahan Google selesai?", "Google authorization completed?"),
    "display-auth-error": (["auth-modal-manager", "auth-manager"], ["auth-modal"], "Paparkan pembatalan atau ralat", "Display cancellation or sign-in error"),
    "guest-state": (["auth-manager", "user-menu-manager"], ["user-menu"], "Kekal dalam keadaan tetamu dan paparkan Log Masuk", "Remain in guest state and display Sign in"),
    "save-auth-session": (["better-auth", "auth-identity", "supabase-db"], ["auth-modal"], "Cipta atau kemas kini identiti, akaun dan sesi", "Create or update identity, account and session"),
    "redirect-petakerja": (["better-auth", "auth-client"], ["auth-modal"], "Ubah hala ke PetaKerja", "Redirect to PetaKerja"),
    "check-active-session": (["auth-manager", "auth-client", "better-auth"], ["user-menu"], "Semak sesi aktif", "Check the active session"),
    "active-session-found": (["auth-manager", "better-auth"], ["user-menu"], "Sesi aktif ditemui?", "Active session found?"),
    "request-profile": (["auth-manager", "profile-bridge"], ["user-menu"], "Minta profil PetaKerja", "Request the PetaKerja profile"),
    "linked-profile-found": (["profile-bridge", "user-profile"], ["user-menu"], "Profil terpaut ditemui?", "Linked profile found?"),
    "load-linked-profile": (["profile-bridge", "user-profile", "supabase-db"], ["user-menu"], "Muatkan profil terpaut", "Load the linked profile"),
    "matching-email-found": (["profile-bridge", "user-profile"], ["user-menu"], "Profil e-mel sepadan ditemui?", "Matching email profile found?"),
    "link-existing-profile": (["profile-bridge", "user-profile", "supabase-db"], ["user-menu"], "Pautkan profil sedia ada", "Link the existing profile"),
    "create-new-profile": (["profile-bridge", "user-profile", "supabase-db"], ["user-menu"], "Cipta profil PetaKerja baharu", "Create a new PetaKerja profile"),
    "profile-obtained": (["profile-bridge", "user-profile"], ["user-menu"], "Profil berjaya diperoleh?", "Profile obtained successfully?"),
    "return-profile": (["profile-bridge", "auth-manager"], ["user-menu"], "Pulangkan profil", "Return the profile"),
    "update-user-state": (["auth-manager"], ["user-menu"], "Kemas kini keadaan pengguna", "Update the signed-in user state"),
    "display-authenticated-menu": (["user-menu-manager", "user-profile"], ["user-menu"], "Paparkan menu pengguna disahkan", "Display the authenticated user menu"),
    "end": (["pengguna", "user-menu-manager"], ["user-menu"], "Tamat", "End"),
}

USER_SEARCH_JOBS_FLOWCHART_MS = {
    "PetaKerja Search Jobs Flow Chart": "Carta Alir Carian Pekerjaan PetaKerja",
    "Public Daily Index search with fresh-cache, database, stale-cache, empty and failure outcomes.": "Carian Daily Index awam dengan hasil cache baharu, pangkalan data, cache lama, kosong dan gagal.",
    "Start": "Mula", "End": "Tamat", "Yes": "Ya", "No": "Tidak",
    "Open the Job Finder": "Buka Job Finder",
    "Enter a job title, location and filters": "Masukkan tajuk pekerjaan, lokasi dan penapis",
    "Select Search": "Pilih Cari",
    "Clear previous results and display the loading state": "Kosongkan hasil terdahulu dan paparkan keadaan pemuatan",
    "Request matching jobs from the Daily Index": "Minta pekerjaan sepadan daripada Daily Index",
    "Fresh cached response available?": "Respons cache baharu tersedia?",
    "Use the fresh cached job results": "Gunakan hasil pekerjaan daripada cache baharu",
    "Retrieve matching jobs from the database": "Dapatkan pekerjaan sepadan daripada pangkalan data",
    "Job request successful?": "Permintaan pekerjaan berjaya?",
    "Filter, rank and paginate the job results": "Tapis, susun dan bahagikan hasil pekerjaan kepada halaman",
    "Stale cached response available?": "Respons cache lama tersedia?",
    "Use the stale cached job results": "Gunakan hasil pekerjaan daripada cache lama",
    "Clear loading and display the Daily Index error": "Tamatkan pemuatan dan paparkan ralat Daily Index",
    "Apply profile matching and selected filters": "Gunakan pemadanan profil dan penapis yang dipilih",
    "Matching jobs returned?": "Pekerjaan sepadan dipulangkan?",
    "Display No matching jobs": "Paparkan Tiada pekerjaan sepadan",
    "Display job cards, result count, sources and map markers": "Paparkan kad pekerjaan, jumlah hasil, sumber dan marker peta",
    "Clear the loading state": "Tamatkan keadaan pemuatan",
}

USER_SEARCH_JOBS_COMPONENTS = {
    "start": (["pengguna"], ["jobs-search"]),
    "open-job-finder": (["pengguna", "job-manager"], ["jobs-search"]),
    "enter-criteria": (["pengguna", "job-manager"], ["jobs-search"]),
    "select-search": (["pengguna", "job-manager"], ["jobs-search"]),
    "prepare-search": (["job-manager"], ["jobs-search", "jobs-cards"]),
    "request-daily-index": (["job-manager", "jobs-api", "supa-jobs-route"], ["jobs-search"]),
    "fresh-cache": (["supa-jobs-route"], ["jobs-search"]),
    "use-fresh-cache": (["supa-jobs-route", "job-manager"], ["jobs-cards"]),
    "retrieve-jobs": (["supa-jobs-route", "supabase-db", "job-entity"], ["jobs-search"]),
    "request-successful": (["supa-jobs-route"], ["jobs-search"]),
    "filter-rank": (["supa-jobs-route", "job-search-relevance"], ["jobs-search", "jobs-cards"]),
    "stale-cache": (["supa-jobs-route"], ["jobs-search"]),
    "use-stale-cache": (["supa-jobs-route", "job-manager"], ["jobs-cards"]),
    "display-error": (["job-manager", "jobs-api"], ["jobs-search"]),
    "apply-client-filters": (["job-manager", "job-search-relevance"], ["jobs-search", "jobs-cards"]),
    "jobs-returned": (["job-manager", "job-entity"], ["jobs-cards"]),
    "empty-state": (["job-manager"], ["jobs-cards"]),
    "display-results": (["job-manager", "job-entity", "map-manager"], ["jobs-cards", "jobs-map"]),
    "clear-loading": (["job-manager"], ["jobs-search"]),
    "end": (["pengguna"], ["jobs-cards", "jobs-map"]),
}

USER_EXPLORE_3D_MAP_FLOWCHART_MS = {
    "PetaKerja Explore the 3D Map Flow Chart": "Carta Alir Meneroka Peta 3D PetaKerja",
    "Public Malaysia workspace, POI loading, optional 3D terrain and building controls.": "Ruang kerja Malaysia awam dengan pemuatan POI serta kawalan terrain dan bangunan 3D pilihan.",
    "Start": "Mula", "End": "Tamat", "Yes": "Ya", "No": "Tidak",
    "Select the Malaysia Map workspace": "Pilih ruang kerja Peta Malaysia",
    "Open the map workspace": "Buka ruang kerja peta",
    "Wait for the base map to become ready": "Tunggu peta asas sedia digunakan",
    "Move the camera to Malaysia": "Gerakkan kamera ke Malaysia",
    "Start map exploration": "Mulakan penerokaan peta",
    "Request visible POIs and category counts": "Minta POI yang kelihatan dan bilangan kategori",
    "POI data available?": "Data POI tersedia?",
    "Render POIs and category counts": "Paparkan POI dan bilangan kategori",
    "Continue with the base map without unavailable POIs": "Teruskan dengan peta asas tanpa POI yang tidak tersedia",
    "Display the interactive Malaysia map": "Paparkan peta Malaysia interaktif",
    "3D Terrain selected?": "Terrain 3D dipilih?",
    "Viewport wider than 768px?": "Paparan lebih lebar daripada 768px?",
    "Enable satellite imagery and 3D terrain": "Aktifkan imej satelit dan terrain 3D",
    "Use satellite imagery without terrain elevation": "Gunakan imej satelit tanpa ketinggian terrain",
    "Keep the selected standard basemap": "Kekalkan peta asas standard yang dipilih",
    "3D Buildings toggled?": "Paparan Bangunan 3D ditukar?",
    "Update 3D building visibility": "Kemas kini keterlihatan bangunan 3D",
    "Keep the current building state": "Kekalkan keadaan bangunan semasa",
    "Display the updated interactive map": "Paparkan peta interaktif yang dikemas kini",
}

USER_EXPLORE_3D_MAP_COMPONENTS = {
    "start": (["pengguna"], ["start-map-preset"]),
    "select-map": (["pengguna", "workspace-ui"], ["start-map-preset"]),
    "open-workspace": (["workspace-ui", "mypeta-app"], ["map-canvas"]),
    "wait-map": (["map-manager", "maplibre-gl"], ["map-canvas"]),
    "focus-malaysia": (["map-manager", "maplibre-gl"], ["map-canvas"]),
    "start-exploration": (["mypeta-app", "map-manager"], ["map-canvas"]),
    "request-pois": (["poi-manager", "category-manager", "supabase-module"], ["contents-poi", "map-canvas"]),
    "data-available": (["poi-manager", "category-manager", "supabase-db"], ["contents-poi"]),
    "render-pois": (["poi-manager", "category-manager", "maplibre-gl"], ["contents-poi", "map-canvas"]),
    "base-map-only": (["map-manager", "maplibre-gl"], ["map-canvas"]),
    "display-map": (["map-manager", "maplibre-gl"], ["map-canvas"]),
    "terrain-selected": (["pengguna", "workspace-ui", "map-manager"], ["ribbon-map", "map-canvas"]),
    "wide-viewport": (["map-manager"], ["map-canvas"]),
    "enable-terrain": (["map-manager", "maplibre-gl"], ["ribbon-map", "map-canvas"]),
    "satellite-only": (["map-manager", "maplibre-gl"], ["ribbon-map", "map-canvas"]),
    "keep-basemap": (["map-manager", "maplibre-gl"], ["ribbon-map", "map-canvas"]),
    "buildings-toggled": (["pengguna", "workspace-ui", "map-manager"], ["ribbon-map", "map-canvas"]),
    "update-buildings": (["map-manager", "maplibre-gl"], ["ribbon-map", "map-canvas"]),
    "keep-buildings": (["map-manager", "maplibre-gl"], ["map-canvas"]),
    "display-final-map": (["map-manager", "poi-manager", "maplibre-gl"], ["map-canvas"]),
    "end": (["pengguna"], ["map-canvas"]),
}

USER_SIGN_OUT_FLOWCHART_MS = {
    "PetaKerja User Sign Out Flow Chart": "Carta Alir Pengguna PetaKerja Log Keluar",
    "Better Auth sign-out followed by application-state and dashboard cleanup.": "Log keluar Better Auth diikuti pembersihan keadaan aplikasi dan Dashboard.",
    "Start": "Mula", "End": "Tamat", "Yes": "Ya", "No": "Tidak",
    "User selects Sign Out": "Pengguna memilih Sign Out",
    "Disable the Sign Out control": "Nyahaktifkan kawalan Sign Out",
    "Submit the sign-out request": "Hantar permintaan log keluar",
    "Sign-out successful?": "Log keluar berjaya?",
    "Keep the current session": "Kekalkan sesi semasa",
    "Re-enable Sign Out and display the error": "Aktifkan semula Sign Out dan paparkan ralat",
    "Invalidate the session and clear its cookie": "Batalkan sesi dan kosongkan kukinya",
    "Clear the signed-in user state": "Kosongkan keadaan pengguna yang log masuk",
    "Notify authentication subscribers": "Maklumkan pelanggan pengesahan",
    "User Dashboard open?": "User Dashboard terbuka?",
    "Close the dashboard and clear per-user caches": "Tutup Dashboard dan kosongkan cache khusus pengguna",
    "Display the guest Sign in control": "Paparkan kawalan Log Masuk tetamu",
}

USER_SIGN_OUT_COMPONENTS = {
    "start": (["pengguna"], ["user-menu"]),
    "select-sign-out": (["pengguna", "user-menu-manager"], ["user-menu"]),
    "disable-control": (["user-menu-manager"], ["user-menu"]),
    "request-sign-out": (["user-menu-manager", "auth-manager", "auth-client", "better-auth"], ["user-menu"]),
    "sign-out-successful": (["auth-manager", "auth-client", "better-auth"], ["user-menu"]),
    "keep-session": (["auth-manager", "user-menu-manager"], ["user-menu"]),
    "display-error": (["user-menu-manager"], ["user-menu"]),
    "invalidate-session": (["better-auth", "auth-client"], ["user-menu"]),
    "clear-user": (["auth-manager"], ["user-menu"]),
    "notify-subscribers": (["auth-manager", "user-dashboard"], ["user-menu"]),
    "dashboard-open": (["user-dashboard"], ["user-menu"]),
    "close-dashboard": (["user-dashboard"], ["user-menu"]),
    "display-guest": (["user-menu-manager", "workspace-ui"], ["user-menu"]),
    "end": (["pengguna"], ["user-menu"]),
}

USER_FLOWCHART_SPECS = {
    "user-search-jobs-flowchart": (USER_SEARCH_JOBS_FLOWCHART_SOURCE, USER_SEARCH_JOBS_FLOWCHART_MS, USER_SEARCH_JOBS_COMPONENTS, "user-search-jobs-flowchart"),
    "user-search-jobs-flowchart-original": (USER_SEARCH_JOBS_FLOWCHART_ORIGINAL_SOURCE, USER_SEARCH_JOBS_FLOWCHART_MS, USER_SEARCH_JOBS_COMPONENTS, "user-search-jobs-flowchart"),
    "user-explore-3d-map-flowchart": (USER_EXPLORE_3D_MAP_FLOWCHART_SOURCE, USER_EXPLORE_3D_MAP_FLOWCHART_MS, USER_EXPLORE_3D_MAP_COMPONENTS, "user-explore-3d-map-flowchart"),
    "user-explore-3d-map-flowchart-original": (USER_EXPLORE_3D_MAP_FLOWCHART_ORIGINAL_SOURCE, USER_EXPLORE_3D_MAP_FLOWCHART_MS, USER_EXPLORE_3D_MAP_COMPONENTS, "user-explore-3d-map-flowchart"),
    "user-sign-out-flowchart": (USER_SIGN_OUT_FLOWCHART_SOURCE, USER_SIGN_OUT_FLOWCHART_MS, USER_SIGN_OUT_COMPONENTS, "user-sign-out-flowchart"),
    "user-sign-out-flowchart-original": (USER_SIGN_OUT_FLOWCHART_ORIGINAL_SOURCE, USER_SIGN_OUT_FLOWCHART_MS, USER_SIGN_OUT_COMPONENTS, "user-sign-out-flowchart"),
}

LAYERED_ARCHITECTURE_MS = {
    "PetaKerja Layered Architecture": "Seni Bina Berlapis PetaKerja",
    "Current SPA, manager, service, Express and data responsibilities.": "Tanggungjawab semasa SPA, pengurus, perkhidmatan, Express dan data.",
    "Browser Frontend": "Antara Muka Pelayar", "Manager Layer": "Lapisan Pengurus",
    "Service Layer": "Lapisan Perkhidmatan", "Express Backend": "Bahagian Belakang Express",
    "Data and External Services": "Data dan Perkhidmatan Luaran",
    "UI and map interaction": "Interaksi UI dan peta", "Data calls": "Panggilan data",
    "Job search": "Carian pekerjaan", "Protected functions": "Fungsi terlindung",
    "Profiles, status and indexes": "Profil, status dan indeks", "Open data": "Data terbuka",
    "POI and RPC": "POI dan RPC", "Supabase RPC client": "Klien RPC Supabase",
    "Better Auth middleware": "Middleware Better Auth", "category RPCs": "RPC kategori",
}

LAYERED_ARCHITECTURE_COMPONENTS = {
    "frontend-shell": (["main-ts", "mypeta-app"], ["start-workspaces", "ribbon"]),
    "frontend-ui": (["ui-templates"], ["ribbon"]),
    "frontend-map": (["maplibre-gl"], ["map-canvas"]),
    "manager-poi": (["poi-manager", "search-manager", "category-manager"], ["map-search", "contents-poi", "map-canvas"]),
    "manager-jobs": (["job-manager"], ["jobs-search", "jobs-cards", "jobs-map"]),
    "manager-insights": (["insights-manager"], ["ribbon-data", "catalog-national"]),
    "manager-chatbot": (["chatbot-manager"], ["assistant-panel"]),
    "service-supabase": (["supabase-module"], []),
    "service-job-client": (["jobs-api"], ["jobs-search"]),
    "service-opendata": (["open-data-api"], ["catalog-national"]),
    "service-auth": (["auth-client", "admin-api-client"], ["auth-modal", "user-menu"]),
    "backend-app": (["express-app"], []),
    "backend-supa-jobs": (["supa-jobs-route"], ["jobs-search"]),
    "backend-live-jobs": (["express-app", "jobs-api"], ["jobs-search"]),
    "backend-assistant": (["assistant-stream", "express-app"], ["assistant-panel"]),
    "backend-auth": (["better-auth"], ["auth-modal", "user-menu"]),
    "data-postgres": (["supabase-db"], []),
    "data-jobs": (["job-entity"], ["jobs-cards", "jobs-map"]),
    "data-gov": (["data-gov"], ["catalog-national"]),
    "data-pois": (["poi-entity"], ["map-canvas", "contents-poi"]),
}

MODULE_HIERARCHY_MS = {
    "PetaKerja Module Hierarchy": "Hierarki Modul PetaKerja",
    "Current core, job-search, analytics and account module responsibilities.": "Tanggungjawab semasa modul teras, carian pekerjaan, analitik dan akaun.",
    "Top-to-bottom ownership hierarchy with cross-module dependencies listed separately.": "Hierarki pemilikan dari atas ke bawah dengan kebergantungan silang modul disenaraikan secara berasingan.",
    "Core Application": "Aplikasi Teras", "Job Search Module": "Modul Carian Pekerjaan",
    "Accounts and Administration": "Akaun dan Pentadbiran", "Analytics and Assistance": "Analitik dan Bantuan",
    "Boot and application shell": "But dan cangkerang aplikasi", "MyPetaApp + templates": "MyPetaApp + templat",
    "Interactive map": "Peta interaktif", "POI and categories": "POI dan kategori",
    "Daily Index": "Indeks Harian", "Pipeline Index": "Indeks Pipeline", "Live Search": "Carian Langsung",
    "Job cards and map markers": "Kad pekerjaan dan penanda peta",
    "public.users profile bridge": "Jambatan profil public.users",
    "Administration, configuration": "Pentadbiran dan konfigurasi", "and user status": "serta status pengguna",
    "Area highlighting": "Sorotan kawasan", "AI provider routes": "Laluan penyedia AI",
    "Cross-module dependencies": "Kebergantungan silang modul",
    "Map workspace": "Ruang kerja peta", "Location context": "Konteks lokasi",
    "Save job status": "Simpan status pekerjaan", "Protected AI functions": "Fungsi AI terlindung",
}

MODULE_HIERARCHY_COMPONENTS = {
    "core-shell": (["mypeta-app", "ui-templates"], ["start-workspaces", "ribbon"]),
    "core-map": (["map-manager", "maplibre-gl"], ["map-canvas", "ribbon-map"]),
    "core-poi": (["poi-manager", "search-manager", "category-manager"], ["map-search", "contents-poi"]),
    "jobs-manager": (["job-manager"], ["jobs-search", "jobs-cards", "jobs-map"]),
    "jobs-modes": (["jobs-api", "supa-jobs-route"], ["jobs-search"]),
    "jobs-markers": (["job-manager", "map-manager"], ["jobs-cards", "jobs-map"]),
    "account-auth": (["auth-manager", "better-auth"], ["auth-modal", "user-menu"]),
    "account-bridge": (["profile-bridge", "user-profile"], ["user-menu"]),
    "account-admin": (["admin-manager", "admin-ui"], ["user-menu"]),
    "analysis-insights": (["insights-manager", "open-data-api"], ["ribbon-data", "catalog-national"]),
    "analysis-highlight": (["highlight-manager", "highlight-entity"], ["assistant-highlight", "map-canvas"]),
    "analysis-chatbot": (["chatbot-manager", "ai-provider"], ["assistant-panel"]),
}

MODULE_HIERARCHY_DEPENDENCIES = (
    ("modules-semantic-core-jobs", "core-map", "jobs-manager", "Map workspace"),
    ("modules-semantic-core-analysis", "core-map", "analysis-insights", "Location context"),
    ("modules-semantic-account-jobs", "account-bridge", "jobs-manager", "Save job status"),
    ("modules-semantic-account-analysis", "account-auth", "analysis-chatbot", "Protected AI functions"),
)

DESIGN_SPECS = {
    "architecture": (LAYERED_ARCHITECTURE_SOURCE, LAYERED_ARCHITECTURE_MS, LAYERED_ARCHITECTURE_COMPONENTS, "architecture"),
    "architecture-original": (LAYERED_ARCHITECTURE_ORIGINAL_SOURCE, LAYERED_ARCHITECTURE_MS, LAYERED_ARCHITECTURE_COMPONENTS, "architecture"),
    "modules": (MODULE_HIERARCHY_SOURCE, MODULE_HIERARCHY_MS, MODULE_HIERARCHY_COMPONENTS, "modules"),
    "modules-original": (MODULE_HIERARCHY_ORIGINAL_SOURCE, MODULE_HIERARCHY_MS, MODULE_HIERARCHY_COMPONENTS, "modules"),
    "modules-layered-stack": (MODULE_HIERARCHY_LAYERED_STACK_SOURCE, MODULE_HIERARCHY_MS, MODULE_HIERARCHY_COMPONENTS, "modules"),
}

ADMIN_MANAGE_USERS_FLOWCHART_MS = {
    "PetaKerja Administrator Manage Users Flow Chart": "Carta Alir Pentadbir Mengurus Pengguna PetaKerja",
    "Focused read-only Users branch; dashboard access validation is documented separately.": "Aliran Pengguna baca sahaja yang difokuskan; pengesahan akses papan pemuka didokumenkan secara berasingan.",
    "Precondition: The Administrator is signed in, has the admin or owner role, and the Admin Dashboard is open.": "Prasyarat: Pentadbir telah log masuk, mempunyai peranan admin atau owner, dan Papan Pemuka Pentadbir telah dibuka.",
    "Start": "Mula",
    "End": "Tamat",
    "Administrator selects the Users section": "Pentadbir memilih bahagian Pengguna",
    "Display the loading state": "Paparkan keadaan pemuatan",
    "Request recent user information": "Minta maklumat pengguna terkini",
    "Retrieve up to 100 recent profiles and role assignments": "Dapatkan sehingga 100 profil dan peranan pengguna terkini",
    "Request successful?": "Permintaan berjaya?",
    "Clear the loading state and display the dashboard loading error": "Tamatkan keadaan pemuatan dan paparkan ralat pemuatan papan pemuka",
    "Store the returned records and clear the loading state": "Simpan rekod yang diterima dan tamatkan keadaan pemuatan",
    "Users returned?": "Pengguna dipulangkan?",
    "Display No users returned": "Paparkan Tiada pengguna dipulangkan",
    "Display names, emails, roles, creation dates and last-login dates": "Paparkan nama, e-mel, peranan, tarikh dicipta dan tarikh log masuk terakhir",
    "The current implementation is read-only. Role changes, account suspension and account deletion are not available.": "Pelaksanaan semasa hanya untuk paparan. Perubahan peranan, penggantungan akaun dan pemadaman akaun tidak tersedia.",
    "Yes": "Ya",
    "No": "Tidak",
}

ADMIN_MANAGE_USERS_FLOWCHART_COMPONENTS = {
    "start": (["pentadbir"], [], "Mula", "Start"),
    "select-users": (["pentadbir", "admin-ui"], [], "Pentadbir memilih bahagian Pengguna", "Administrator selects the Users section"),
    "loading-state": (["admin-ui", "admin-manager"], [], "Paparkan keadaan pemuatan", "Display the loading state"),
    "request-users": (["admin-manager", "admin-api-client", "admin-users-api"], [], "Minta maklumat pengguna terkini", "Request recent user information"),
    "retrieve-users": (["admin-users-api", "supabase-db", "user-profile"], [], "Dapatkan sehingga 100 profil dan peranan pengguna terkini", "Retrieve up to 100 recent profiles and role assignments"),
    "request-successful": (["admin-api-client", "admin-users-api", "admin-manager"], [], "Permintaan berjaya?", "Request successful?"),
    "request-error": (["admin-manager", "admin-ui"], [], "Paparkan ralat pemuatan papan pemuka", "Display the dashboard loading error"),
    "store-users": (["admin-manager"], [], "Simpan rekod pengguna", "Store the user records"),
    "users-returned": (["admin-manager", "user-profile"], [], "Pengguna dipulangkan?", "Users returned?"),
    "empty-state": (["admin-manager", "admin-ui"], [], "Paparkan keadaan kosong", "Display the empty state"),
    "display-users": (["admin-ui", "admin-manager", "user-profile"], [], "Paparkan jadual pengguna dan peranan", "Display the user table and roles"),
    "end": (["pentadbir", "admin-ui"], [], "Tamat", "End"),
}

ADMIN_ACCESS_DASHBOARD_FLOWCHART_MS = {
    "PetaKerja Access Administrator Dashboard Flow Chart": "Carta Alir Pentadbir PetaKerja Mengakses Papan Pemuka",
    "Administrator entry, local access guard and protected dashboard-data loading.": "Kemasukan pentadbir, kawalan akses setempat dan pemuatan data papan pemuka terlindung.",
    "Precondition: The Administrator entry is selected from the signed-in user menu or the /admin route is opened directly.": "Prasyarat: Pilihan Pentadbir dipilih daripada menu pengguna yang log masuk atau route /admin dibuka secara terus.",
    "Administrator selects the Admin Dashboard": "Pentadbir memilih Papan Pemuka Pentadbir",
    "Check the current signed-in user": "Semak pengguna yang sedang log masuk",
    "Active session found?": "Sesi aktif ditemui?",
    "Return to PetaKerja and request administrator sign-in": "Kembali ke PetaKerja dan minta log masuk pentadbir",
    "Administrator role allowed?": "Peranan pentadbir dibenarkan?",
    "Return to PetaKerja and deny administrator access": "Kembali ke PetaKerja dan nafikan akses pentadbir",
    "Open the administrator dashboard": "Buka papan pemuka pentadbir",
    "Display the dashboard loading state": "Paparkan keadaan pemuatan papan pemuka",
    "Request provider, AI usage and user information": "Minta maklumat penyedia, penggunaan AI dan pengguna",
    "Retrieve the three protected dashboard data sets": "Dapatkan tiga set data papan pemuka terlindung",
    "Dashboard requests successful?": "Permintaan papan pemuka berjaya?",
    "Clear loading and display the dashboard loading error": "Tamatkan pemuatan dan paparkan ralat pemuatan papan pemuka",
    "Store the returned provider, usage and user information": "Simpan maklumat penyedia, penggunaan dan pengguna yang diterima",
    "Clear the dashboard loading state": "Tamatkan keadaan pemuatan papan pemuka",
    "Display the administrator Overview": "Paparkan Overview pentadbir",
    "Protected provider, usage and user requests repeat the Better Auth session and admin/owner role checks on the server.": "Permintaan penyedia, penggunaan dan pengguna yang dilindungi mengulangi semakan sesi Better Auth serta peranan admin/owner pada pelayan.",
    "Blog statistics are loaded separately only when the Blog section is selected.": "Statistik blog dimuatkan secara berasingan hanya apabila bahagian Blog dipilih.",
    "Start": "Mula", "End": "Tamat", "Yes": "Ya", "No": "Tidak",
}

ADMIN_ACCESS_DASHBOARD_FLOWCHART_COMPONENTS = {
    "start": (["pentadbir"], [], "Mula", "Start"),
    "select-dashboard": (["pentadbir", "admin-ui"], [], "Pilih papan pemuka pentadbir", "Select the Admin Dashboard"),
    "check-user": (["admin-ui", "auth-manager"], [], "Semak pengguna semasa", "Check the current user"),
    "session-active": (["auth-manager", "better-auth"], [], "Sesi aktif ditemui?", "Active session found?"),
    "sign-in-required": (["auth-manager", "admin-ui"], ["auth-modal"], "Minta log masuk pentadbir", "Request administrator sign-in"),
    "role-allowed": (["auth-manager", "user-profile"], [], "Peranan pentadbir dibenarkan?", "Administrator role allowed?"),
    "access-denied": (["auth-manager", "admin-ui"], [], "Nafikan akses pentadbir", "Deny administrator access"),
    "open-dashboard": (["admin-ui", "admin-manager"], ["user-menu"], "Buka papan pemuka pentadbir", "Open the administrator dashboard"),
    "loading-state": (["admin-ui", "admin-manager"], [], "Paparkan keadaan pemuatan", "Display the loading state"),
    "request-admin-data": (["admin-manager", "admin-api-client"], [], "Minta data Overview", "Request Overview data"),
    "retrieve-admin-data": (["admin-dashboard-api", "better-auth", "user-profile", "supabase-db"], [], "Dapatkan data terlindung", "Retrieve protected data"),
    "request-successful": (["admin-api-client", "admin-dashboard-api"], [], "Permintaan berjaya?", "Requests successful?"),
    "request-error": (["admin-manager", "admin-ui"], [], "Paparkan ralat pemuatan", "Display the loading error"),
    "store-admin-data": (["admin-manager"], [], "Simpan data Overview", "Store Overview data"),
    "clear-loading": (["admin-manager", "admin-ui"], [], "Tamatkan pemuatan", "Clear loading"),
    "display-overview": (["admin-manager", "admin-ui"], [], "Paparkan Overview", "Display Overview"),
    "end": (["pentadbir", "admin-ui"], [], "Tamat", "End"),
}

ADMIN_MONITOR_ACTIVITY_FLOWCHART_MS = {
    "PetaKerja Administrator Monitor System Activity Logs Flow Chart": "Carta Alir Pentadbir PetaKerja Memantau Aktiviti Sistem",
    "Current implementation: the latest 100 AI assistant usage events, not general server logs.": "Pelaksanaan semasa: 100 peristiwa penggunaan pembantu AI terkini, bukan log pelayan umum.",
    "Precondition: The Administrator is signed in, has the admin or owner role, and the Admin Dashboard is open.": "Prasyarat: Pentadbir telah log masuk, mempunyai peranan admin atau owner, dan Papan Pemuka Pentadbir telah dibuka.",
    "Administrator selects the Usage section": "Pentadbir memilih bahagian Usage",
    "Display the loading state": "Paparkan keadaan pemuatan",
    "Request recent AI activity information": "Minta maklumat aktiviti AI terkini",
    "Retrieve up to 100 recent AI usage events and calculate totals": "Dapatkan sehingga 100 peristiwa penggunaan AI terkini dan kira jumlah",
    "Request successful?": "Permintaan berjaya?",
    "Clear loading and display the dashboard loading error": "Tamatkan pemuatan dan paparkan ralat pemuatan papan pemuka",
    "Store the activity rows and totals, then clear loading": "Simpan baris aktiviti dan jumlah, kemudian tamatkan pemuatan",
    "Activity events returned?": "Peristiwa aktiviti dipulangkan?",
    "Display No usage events yet": "Paparkan Belum ada peristiwa penggunaan",
    "Display usage totals and the activity table": "Paparkan jumlah penggunaan dan jadual aktiviti",
    "The Usage section reads public.ai_usage_events and calculates request, error, token and estimated-cost totals.": "Bahagian Usage membaca public.ai_usage_events dan mengira jumlah permintaan, ralat, token serta anggaran kos.",
    "General server logs and public.ai_admin_audit_logs are not displayed by this use case.": "Log pelayan umum dan public.ai_admin_audit_logs tidak dipaparkan oleh kes guna ini.",
    "Start": "Mula", "End": "Tamat", "Yes": "Ya", "No": "Tidak",
}

ADMIN_MONITOR_ACTIVITY_FLOWCHART_COMPONENTS = {
    "start": (["pentadbir"], [], "Mula", "Start"),
    "select-usage": (["pentadbir", "admin-ui"], [], "Pilih bahagian Usage", "Select the Usage section"),
    "loading-state": (["admin-ui", "admin-manager"], [], "Paparkan keadaan pemuatan", "Display the loading state"),
    "request-activity": (["admin-manager", "admin-api-client", "admin-usage-api"], [], "Minta aktiviti AI terkini", "Request recent AI activity"),
    "retrieve-activity": (["admin-usage-api", "ai-usage-entity", "supabase-db"], [], "Dapatkan peristiwa dan jumlah", "Retrieve events and totals"),
    "request-successful": (["admin-api-client", "admin-usage-api", "admin-manager"], [], "Permintaan berjaya?", "Request successful?"),
    "request-error": (["admin-manager", "admin-ui"], [], "Paparkan ralat pemuatan", "Display the loading error"),
    "store-activity": (["admin-manager"], [], "Simpan aktiviti dan jumlah", "Store activity and totals"),
    "events-returned": (["admin-manager", "ai-usage-entity"], [], "Peristiwa dipulangkan?", "Events returned?"),
    "empty-state": (["admin-manager", "admin-ui"], [], "Paparkan keadaan kosong", "Display the empty state"),
    "display-activity": (["admin-manager", "admin-ui", "ai-usage-entity"], [], "Paparkan jumlah dan jadual", "Display totals and table"),
    "end": (["pentadbir", "admin-ui"], [], "Tamat", "End"),
}

ADMIN_MANAGE_AI_CONFIGURATION_FLOWCHART_MS = {
    "PetaKerja Administrator Manage AI Chatbot Configuration Flow Chart": "Carta Alir Pentadbir PetaKerja Mengurus Konfigurasi Chatbot AI",
    "Provider visibility for administrators and owners; shared-key and model-refresh actions are owner-only.": "Status penyedia boleh dilihat oleh admin dan owner; tindakan kunci bersama serta segar semula model hanya untuk owner.",
    "Precondition: The Administrator is signed in, has the admin or owner role, and the Admin Dashboard is open.": "Prasyarat: Pentadbir telah log masuk, mempunyai peranan admin atau owner, dan Papan Pemuka Pentadbir telah dibuka.",
    "Administrator selects the AI Providers section": "Pentadbir memilih bahagian AI Providers",
    "Display the loading state": "Paparkan keadaan pemuatan",
    "Request provider configuration": "Minta konfigurasi penyedia",
    "Read platform credentials and combine them with the provider registry": "Baca kelayakan platform dan gabungkan dengan daftar penyedia",
    "Request successful?": "Permintaan berjaya?",
    "Clear loading and display the provider loading error": "Tamatkan pemuatan dan paparkan ralat pemuatan penyedia",
    "Display provider names, key status, model counts and fetch status": "Paparkan nama penyedia, status kunci, bilangan model dan status pengambilan",
    "Owner role?": "Peranan owner?",
    "Display provider information in read-only mode and explain the owner requirement": "Paparkan maklumat penyedia dalam mod baca sahaja dan jelaskan keperluan owner",
    "Owner action?": "Tindakan owner?",
    "Open the platform-key dialog": "Buka dialog kunci platform",
    "Enter and submit a platform API key": "Masukkan dan hantar kunci API platform",
    "Provider and key valid?": "Penyedia dan kunci sah?",
    "Display the platform-key validation error": "Paparkan ralat pengesahan kunci platform",
    "Encrypt and save the shared platform credential": "Enkripsi dan simpan kelayakan platform bersama",
    "Credential saved successfully?": "Kelayakan berjaya disimpan?",
    "Display the platform-key request error": "Paparkan ralat permintaan kunci platform",
    "Record the platform key saved audit event": "Rekod peristiwa audit kunci platform disimpan",
    "Display success for the saved platform key": "Paparkan kejayaan kunci platform yang disimpan",
    "Request model-list refresh": "Minta segar semula senarai model",
    "Read available platform credentials": "Baca kelayakan platform yang tersedia",
    "Refresh every supported provider and continue after individual failures": "Segarkan setiap penyedia yang disokong dan teruskan selepas kegagalan individu",
    "Any provider failures?": "Ada kegagalan penyedia?",
    "Save model metadata, invalidate caches and display complete success": "Simpan metadata model, batalkan cache dan paparkan kejayaan penuh",
    "Save successful metadata, record errors and display partial results": "Simpan metadata berjaya, rekod ralat dan paparkan hasil separa",
    "Reload the provider table": "Muatkan semula jadual penyedia",
    "Reload provider information and display the result": "Muatkan semula maklumat penyedia dan paparkan hasil",
    "Individual users' model preferences are outside this administrator use case.": "Pilihan model pengguna individu berada di luar kes guna pentadbir ini.",
    "Deployment warning: the refresh handler expects custom_headers, fetched_models, models_fetched_at and fetch_error, but those fields are absent from the live ai_provider_credentials table snapshot.": "Amaran penggunaan: pengendali segar semula menjangkakan custom_headers, fetched_models, models_fetched_at dan fetch_error, tetapi medan tersebut tiada dalam snapshot langsung jadual ai_provider_credentials.",
    "Start": "Mula", "End": "Tamat", "Yes": "Ya", "No": "Tidak", "Save key": "Simpan kunci", "Refresh models": "Segar semula model", "Finish": "Selesai",
}

ADMIN_MANAGE_AI_CONFIGURATION_FLOWCHART_COMPONENTS = {
    "start": (["pentadbir"], [], "Mula", "Start"),
    "select-providers": (["pentadbir", "admin-ui"], [], "Pilih AI Providers", "Select AI Providers"),
    "loading-state": (["admin-ui", "admin-manager"], [], "Paparkan pemuatan", "Display loading"),
    "request-providers": (["admin-manager", "admin-api-client", "admin-ai-providers-api"], [], "Minta konfigurasi penyedia", "Request provider configuration"),
    "retrieve-providers": (["admin-ai-providers-api", "ai-credential-entity", "ai-provider-registry", "supabase-db"], [], "Gabung kelayakan dan daftar", "Combine credentials and registry"),
    "request-successful": (["admin-api-client", "admin-ai-providers-api", "admin-manager"], [], "Permintaan berjaya?", "Request successful?"),
    "request-error": (["admin-manager", "admin-ui"], [], "Paparkan ralat pemuatan", "Display loading error"),
    "display-providers": (["admin-manager", "admin-ui", "ai-provider-registry"], [], "Paparkan status penyedia", "Display provider status"),
    "owner-role": (["user-profile", "admin-ai-providers-api"], [], "Peranan owner?", "Owner role?"),
    "read-only": (["admin-ui", "admin-manager"], [], "Paparkan mod baca sahaja", "Display read-only mode"),
    "owner-action": (["pentadbir", "admin-ui"], [], "Tindakan owner?", "Owner action?"),
    "open-key-modal": (["admin-ui", "admin-manager"], [], "Buka dialog kunci", "Open the key dialog"),
    "enter-key": (["pentadbir", "admin-ui", "admin-api-client"], [], "Hantar kunci platform", "Submit platform key"),
    "key-valid": (["admin-ai-providers-api", "ai-provider-registry"], [], "Penyedia dan kunci sah?", "Provider and key valid?"),
    "validation-error": (["admin-ai-providers-api", "admin-ui"], [], "Paparkan ralat pengesahan", "Display validation error"),
    "save-credential": (["admin-ai-providers-api", "ai-credential-entity", "supabase-db"], [], "Simpan kelayakan terenkripsi", "Save encrypted credential"),
    "save-successful": (["admin-ai-providers-api", "admin-api-client"], [], "Kelayakan disimpan?", "Credential saved?"),
    "save-error": (["admin-ai-providers-api", "admin-ui"], [], "Paparkan ralat simpanan", "Display save error"),
    "record-audit": (["admin-ai-providers-api", "audit-log-entity", "supabase-db"], [], "Rekod audit", "Record audit event"),
    "save-success": (["admin-manager", "admin-ui"], [], "Paparkan kejayaan", "Display success"),
    "request-refresh": (["admin-manager", "admin-api-client", "admin-ai-providers-api"], [], "Minta segar semula model", "Request model refresh"),
    "read-credentials": (["admin-ai-providers-api", "ai-credential-entity", "supabase-db"], [], "Baca kelayakan platform", "Read platform credentials"),
    "refresh-providers": (["admin-ai-providers-api", "ai-provider"], [], "Segar semula penyedia", "Refresh providers"),
    "any-failures": (["admin-ai-providers-api", "ai-provider"], [], "Ada kegagalan penyedia?", "Any provider failures?"),
    "refresh-complete": (["admin-ai-providers-api", "ai-provider", "supabase-db"], [], "Paparkan kejayaan penuh", "Display complete success"),
    "refresh-partial": (["admin-ai-providers-api", "ai-provider", "supabase-db"], [], "Paparkan hasil separa", "Display partial results"),
    "reload-refresh": (["admin-manager", "admin-ui"], [], "Muatkan semula jadual", "Reload provider table"),
    "reload-providers": (["admin-manager", "admin-ui"], [], "Paparkan hasil terkini", "Display updated result"),
    "end": (["pentadbir", "admin-ui"], [], "Tamat", "End"),
}

ADMIN_SIGN_OUT_FLOWCHART_MS = {
    "PetaKerja Administrator Sign Out Flow Chart": "Carta Alir Pentadbir PetaKerja Log Keluar",
    "Better Auth sign-out followed by application-state and administrator-dashboard synchronization.": "Log keluar Better Auth diikuti penyelarasan keadaan aplikasi dan papan pemuka pentadbir.",
    "Precondition: The Administrator is signed in and an authenticated Sign Out control is available.": "Prasyarat: Pentadbir telah log masuk dan kawalan Sign Out yang disahkan tersedia.",
    "Administrator selects Sign Out": "Pentadbir memilih Sign Out",
    "Disable the available Sign Out control": "Nyahaktifkan kawalan Sign Out yang tersedia",
    "Submit the sign-out request to Better Auth": "Hantar permintaan log keluar kepada Better Auth",
    "Sign-out successful?": "Log keluar berjaya?",
    "Keep the current session and re-enable Sign Out": "Kekalkan sesi semasa dan aktifkan semula Sign Out",
    "Invalidate the session and clear its cookie": "Batalkan sesi dan kosongkan kukinya",
    "Clear the PetaKerja user state": "Kosongkan keadaan pengguna PetaKerja",
    "Notify authentication subscribers": "Maklumkan pelanggan pengesahan",
    "Display the signed-out dashboard access state and guest menu": "Paparkan keadaan akses papan pemuka signed-out dan menu tetamu",
    "If sign-out fails, the current implementation logs the failure, preserves the session and re-enables the available Sign Out control.": "Jika log keluar gagal, pelaksanaan semasa merekodkan kegagalan, mengekalkan sesi dan mengaktifkan semula kawalan Sign Out yang tersedia.",
    "After successful sign-out, an open administrator dashboard renders its signed-out access state.": "Selepas log keluar berjaya, papan pemuka pentadbir yang terbuka memaparkan keadaan akses signed-out.",
    "Start": "Mula", "End": "Tamat", "Yes": "Ya", "No": "Tidak",
}

ADMIN_SIGN_OUT_FLOWCHART_COMPONENTS = {
    "start": (["pentadbir"], ["user-menu"], "Mula", "Start"),
    "select-sign-out": (["pentadbir", "user-menu-manager"], ["user-menu"], "Pilih Sign Out", "Select Sign Out"),
    "pending-state": (["user-menu-manager"], ["user-menu"], "Nyahaktifkan kawalan", "Disable the control"),
    "request-sign-out": (["user-menu-manager", "auth-manager", "auth-client", "better-auth"], ["user-menu"], "Hantar permintaan log keluar", "Submit sign-out request"),
    "sign-out-successful": (["auth-manager", "auth-client", "better-auth"], ["user-menu"], "Log keluar berjaya?", "Sign-out successful?"),
    "sign-out-failure": (["user-menu-manager", "auth-manager"], ["user-menu"], "Kekalkan sesi semasa", "Keep current session"),
    "invalidate-session": (["better-auth", "auth-client"], ["user-menu"], "Batalkan sesi", "Invalidate session"),
    "clear-user": (["auth-manager"], ["user-menu"], "Kosongkan keadaan pengguna", "Clear user state"),
    "notify-subscribers": (["auth-manager", "admin-manager"], ["user-menu"], "Maklumkan pelanggan", "Notify subscribers"),
    "display-signed-out": (["admin-manager", "admin-ui", "user-menu-manager"], ["user-menu"], "Paparkan keadaan signed-out", "Display signed-out state"),
    "end": (["pentadbir", "admin-ui"], ["user-menu"], "Tamat", "End"),
}

ADMIN_FLOWCHART_SPECS = {
    "admin-manage-users-flowchart": (ADMIN_MANAGE_USERS_FLOWCHART_SOURCE, ADMIN_MANAGE_USERS_FLOWCHART_MS, ADMIN_MANAGE_USERS_FLOWCHART_COMPONENTS, "admin-manage-users-flowchart"),
    "admin-access-dashboard-flowchart": (ADMIN_ACCESS_DASHBOARD_FLOWCHART_SOURCE, ADMIN_ACCESS_DASHBOARD_FLOWCHART_MS, ADMIN_ACCESS_DASHBOARD_FLOWCHART_COMPONENTS, "admin-access-dashboard-flowchart"),
    "admin-monitor-activity-flowchart": (ADMIN_MONITOR_ACTIVITY_FLOWCHART_SOURCE, ADMIN_MONITOR_ACTIVITY_FLOWCHART_MS, ADMIN_MONITOR_ACTIVITY_FLOWCHART_COMPONENTS, "admin-monitor-activity-flowchart"),
    "admin-manage-ai-configuration-flowchart": (ADMIN_MANAGE_AI_CONFIGURATION_FLOWCHART_SOURCE, ADMIN_MANAGE_AI_CONFIGURATION_FLOWCHART_MS, ADMIN_MANAGE_AI_CONFIGURATION_FLOWCHART_COMPONENTS, "admin-manage-ai-configuration-flowchart"),
    "admin-sign-out-flowchart": (ADMIN_SIGN_OUT_FLOWCHART_SOURCE, ADMIN_SIGN_OUT_FLOWCHART_MS, ADMIN_SIGN_OUT_FLOWCHART_COMPONENTS, "admin-sign-out-flowchart"),
    "admin-manage-users-flowchart-original": (ADMIN_MANAGE_USERS_FLOWCHART_ORIGINAL_SOURCE, ADMIN_MANAGE_USERS_FLOWCHART_MS, ADMIN_MANAGE_USERS_FLOWCHART_COMPONENTS, "admin-manage-users-flowchart"),
    "admin-access-dashboard-flowchart-original": (ADMIN_ACCESS_DASHBOARD_FLOWCHART_ORIGINAL_SOURCE, ADMIN_ACCESS_DASHBOARD_FLOWCHART_MS, ADMIN_ACCESS_DASHBOARD_FLOWCHART_COMPONENTS, "admin-access-dashboard-flowchart"),
    "admin-monitor-activity-flowchart-original": (ADMIN_MONITOR_ACTIVITY_FLOWCHART_ORIGINAL_SOURCE, ADMIN_MONITOR_ACTIVITY_FLOWCHART_MS, ADMIN_MONITOR_ACTIVITY_FLOWCHART_COMPONENTS, "admin-monitor-activity-flowchart"),
    "admin-manage-ai-configuration-flowchart-original": (ADMIN_MANAGE_AI_CONFIGURATION_FLOWCHART_ORIGINAL_SOURCE, ADMIN_MANAGE_AI_CONFIGURATION_FLOWCHART_MS, ADMIN_MANAGE_AI_CONFIGURATION_FLOWCHART_COMPONENTS, "admin-manage-ai-configuration-flowchart"),
    "admin-sign-out-flowchart-original": (ADMIN_SIGN_OUT_FLOWCHART_ORIGINAL_SOURCE, ADMIN_SIGN_OUT_FLOWCHART_MS, ADMIN_SIGN_OUT_FLOWCHART_COMPONENTS, "admin-sign-out-flowchart"),
}

JOB_SEARCH_SEQUENCE_MS = {
    "PetaKerja Search Jobs Sequence": "Jujukan Carian Pekerjaan PetaKerja",
    "User": "Pengguna",
    "PetaKerja Job Finder UI": "UI Pencari Kerja PetaKerja",
    "Supa Jobs Route": "Route Kerja Supa",
    "Job Results / MapLibre": "Hasil Kerja / MapLibre",
    "Enter query, location and filters": "Masukkan query, lokasi dan penapis",
    "Select Search": "Pilih Cari",
    "Show loading; clear results": "Paparkan pemuatan; kosongkan hasil",
    "Show loading state and clear previous results": "Paparkan keadaan pemuatan dan kosongkan hasil terdahulu",
    "Cached JobGrepResponse": "JobGrepResponse daripada cache",
    "Rows and exact count": "Baris dan jumlah tepat",
    "Normalize rows; apply Malaysia, tech and salary filters": "Normalkan baris; tapis Malaysia, teknologi dan gaji",
    "Ranked jobs": "Pekerjaan tersusun",
    "Paginate and build source breakdown": "Bina halaman dan pecahan sumber",
    "Catch fetch failure": "Tangkap kegagalan fetch",
    "Stale JobGrepResponse": "JobGrepResponse cache lama",
    "Display job cards, result count and markers": "Paparkan kad kerja, jumlah hasil dan marker",
    "Empty JobGrepResponse": "JobGrepResponse kosong",
    "Display no matching jobs": "Paparkan tiada pekerjaan sepadan",
    "HTTP 502 / network error": "Ralat HTTP 502 / rangkaian",
    "Throw Daily Index failed": "Lontar kegagalan Daily Index",
    "Display error; remain in guest state": "Paparkan ralat; kekal sebagai tetamu",
    "Clear loading state and hide overlay": "Kosongkan keadaan pemuatan dan sembunyikan overlay",
    "[fresh 60-second cache]": "[cache segar 60 saat]",
    "[cache miss or refresh]": "[cache tiada atau perlu disegar]",
    "[fetch failure and stale cache exists]": "[fetch gagal dan cache lama wujud]",
    "[query supplied]": "[query diberikan]",
    "[jobs returned]": "[pekerjaan dipulangkan]",
    "[no matching jobs]": "[tiada pekerjaan sepadan]",
    "[request fails without usable cache]": "[permintaan gagal tanpa cache boleh guna]",
    "Daily Index is public. Google sign-in is not required for this search path.": "Daily Index ialah fungsi awam. Log masuk Google tidak diperlukan untuk aliran carian ini.",
}

JOB_SEARCH_SEQUENCE_COMPONENTS = [
    ("fragment-cache", ["sequence/fragment-cache", "sequence/cache-"], ["jobs-api", "supa-jobs-route", "supabase-db", "job-search-relevance"], ["jobs-search"], "Alternatif cache pelayan", "Server-cache alternative"),
    ("fragment-query", ["sequence/fragment-query", "sequence/query-"], ["supa-jobs-route", "job-search-relevance"], ["jobs-search"], "Tapisan query pilihan", "Optional query filtering"),
    ("fragment-results", ["sequence/fragment-results", "sequence/result-", "sequence/results-"], ["job-manager", "job-entity", "map-manager"], ["jobs-cards", "jobs-map"], "Alternatif hasil", "Result alternative"),
    ("participant-user", ["sequence/participant-user"], ["pengguna"], ["jobs-search", "jobs-cards", "jobs-map"], "Pengguna", "User"),
    ("participant-ui", ["sequence/participant-ui"], ["job-manager"], ["jobs-search", "jobs-cards"], "UI Pencari Kerja PetaKerja", "PetaKerja Job Finder UI"),
    ("participant-manager", ["sequence/participant-manager"], ["job-manager"], ["jobs-search", "jobs-cards", "jobs-map"], "JobFinderManager", "JobFinderManager"),
    ("participant-client", ["sequence/participant-client"], ["jobs-api"], ["jobs-search"], "supa-api.ts", "supa-api.ts"),
    ("participant-route", ["sequence/participant-route"], ["supa-jobs-route"], ["jobs-search"], "Route Kerja Supa", "Supa Jobs Route"),
    ("participant-database", ["sequence/participant-database"], ["supabase-db", "job-entity"], ["jobs-search", "jobs-cards"], "Supabase / PostgreSQL", "Supabase / PostgreSQL"),
    ("participant-relevance", ["sequence/participant-relevance"], ["job-search-relevance", "job-entity"], ["jobs-search", "jobs-cards"], "jobSearchRelevance", "jobSearchRelevance"),
    ("participant-results", ["sequence/participant-results"], ["job-manager", "map-manager", "job-entity"], ["jobs-cards", "jobs-map"], "Hasil Kerja / MapLibre", "Job Results / MapLibre"),
]

ADMIN_MANAGE_USERS_SEQUENCE_MS = {
    "PetaKerja Administrator Manage Users Sequence": "Jujukan Pentadbir Mengurus Pengguna PetaKerja",
    "Administrator": "Pentadbir",
    "PetaKerja Admin UI": "UI Pentadbir PetaKerja",
    "Admin API Client": "Klien API Pentadbir",
    "Admin Users API": "API Pengguna Pentadbir",
    "Better Auth Session": "Sesi Better Auth",
    "[administrator or owner]": "[pentadbir atau owner]",
    "[no active session]": "[tiada sesi aktif]",
    "[role not allowed]": "[peranan tidak dibenarkan]",
    "[users available]": "[pengguna tersedia]",
    "[no users]": "[tiada pengguna]",
    "[request failed]": "[permintaan gagal]",
    "Current implementation displays the latest 100 users and their roles only. Account or role modification is not implemented.": "Pelaksanaan semasa hanya memaparkan 100 pengguna terkini dan peranan mereka. Pengubahsuaian akaun atau peranan belum dilaksanakan.",
}

ADMIN_MANAGE_USERS_SEQUENCE_COMPONENTS = [
    ("fragment-access", ["admin-manage-users-sequence/fragment-access", "admin-manage-users-sequence/authorized", "admin-manage-users-sequence/no-session", "admin-manage-users-sequence/role-denied"], ["admin-users-api", "better-auth", "user-profile"], ["admin-entry", "admin-users-tab"], "Alternatif akses", "Access alternative"),
    ("fragment-results", ["admin-manage-users-sequence/fragment-results", "admin-manage-users-sequence/users-available", "admin-manage-users-sequence/no-users", "admin-manage-users-sequence/request-failed"], ["admin-manager", "admin-ui", "admin-api-client"], ["admin-users-tab", "admin-users-table"], "Alternatif hasil", "Result alternative"),
    ("participant-administrator", ["admin-manage-users-sequence/participant-administrator"], ["pentadbir"], ["admin-entry", "admin-users-tab", "admin-users-table"], "Pentadbir", "Administrator"),
    ("participant-ui", ["admin-manage-users-sequence/participant-ui"], ["admin-ui"], ["admin-entry", "admin-users-tab", "admin-users-table"], "UI Pentadbir PetaKerja", "PetaKerja Admin UI"),
    ("participant-manager", ["admin-manage-users-sequence/participant-manager"], ["admin-manager"], ["admin-entry", "admin-users-tab", "admin-users-table"], "AdminDashboardManager", "AdminDashboardManager"),
    ("participant-client", ["admin-manage-users-sequence/participant-client"], ["admin-api-client"], ["admin-users-tab", "admin-users-table"], "Klien API Pentadbir", "Admin API Client"),
    ("participant-api", ["admin-manage-users-sequence/participant-api"], ["admin-users-api"], ["admin-users-tab", "admin-users-table"], "API Pengguna Pentadbir", "Admin Users API"),
    ("participant-session", ["admin-manage-users-sequence/participant-session"], ["better-auth"], ["admin-entry"], "Sesi Better Auth", "Better Auth Session"),
    ("participant-database", ["admin-manage-users-sequence/participant-database"], ["supabase-db", "user-profile"], ["admin-users-table"], "Supabase / PostgreSQL", "Supabase / PostgreSQL"),
]

ADMIN_MANAGE_AI_CONFIGURATION_SEQUENCE_MS = {
    "PetaKerja Administrator Manage AI Chatbot Configuration Sequence": "Jujukan Pentadbir Mengurus Konfigurasi Chatbot AI PetaKerja",
    "Administrator": "Pentadbir",
    "PetaKerja Admin UI": "UI Pentadbir PetaKerja",
    "Admin API Client": "Klien API Pentadbir",
    "Admin AI Providers API": "API Penyedia AI Pentadbir",
    "Better Auth Session": "Sesi Better Auth",
    "External AI Provider APIs": "API Penyedia AI Luaran",
    "[administrator or owner]": "[pentadbir atau owner]",
    "[no active session]": "[tiada sesi aktif]",
    "[role not allowed]": "[peranan tidak dibenarkan]",
    "[administrator]": "[pentadbir]",
    "[owner]": "[owner]",
    "[save platform key]": "[simpan kekunci platform]",
    "[key saved]": "[kekunci disimpan]",
    "[invalid provider, empty key or request failed]": "[penyedia tidak sah, kekunci kosong atau permintaan gagal]",
    "[refresh model lists]": "[segar semula senarai model]",
    "[each provider supporting model fetching]": "[setiap penyedia yang menyokong pengambilan model]",
    "[refresh succeeded]": "[segar semula berjaya]",
    "[refresh failed]": "[segar semula gagal]",
    "[complete success]": "[kejayaan penuh]",
    "[partial provider failure]": "[kegagalan separa penyedia]",
    "[request failed]": "[permintaan gagal]",
    "Implementation note:": "Nota pelaksanaan:",
    "admin and owner may view providers; only owner may save shared keys or refresh models.": "pentadbir dan owner boleh melihat penyedia; hanya owner boleh menyimpan kekunci dikongsi atau menyegar semula model.",
    "The refresh path expects": "Laluan segar semula menjangkakan",
    "which are absent from the current live": "yang tiada dalam snapshot langsung semasa",
    "snapshot. Individual user model preferences are outside this use case.": "Pilihan model pengguna individu berada di luar kes guna ini.",
    "Implementation note: admin and owner may view providers; only owner may save shared keys or refresh models. The refresh path expects custom_headers, fetched_models, models_fetched_at and fetch_error, which are absent from the current live ai_provider_credentials snapshot. Individual user model preferences are outside this use case.": "Nota pelaksanaan: pentadbir dan owner boleh melihat penyedia; hanya owner boleh menyimpan kekunci dikongsi atau menyegar semula model. Laluan segar semula menjangkakan custom_headers, fetched_models, models_fetched_at dan fetch_error, yang tiada dalam snapshot langsung ai_provider_credentials semasa. Pilihan model pengguna individu berada di luar kes guna ini.",
}

ADMIN_MANAGE_AI_CONFIGURATION_SEQUENCE_COMPONENTS = [
    ("fragment-access", ["admin-manage-ai-configuration-sequence/fragment-access", "admin-manage-ai-configuration-sequence/access-"], ["admin-ai-providers-api", "better-auth", "user-profile"], ["admin-entry", "admin-providers-tab"], "Alternatif akses", "Access alternative"),
    ("fragment-capability", ["admin-manage-ai-configuration-sequence/fragment-capability", "admin-manage-ai-configuration-sequence/capability-", "admin-manage-ai-configuration-sequence/administrator-read-only"], ["admin-ui", "admin-manager", "admin-ai-providers-api"], ["admin-providers-tab", "admin-platform-key", "admin-refresh-models"], "Alternatif keupayaan peranan", "Role-capability alternative"),
    ("fragment-save-key", ["admin-manage-ai-configuration-sequence/fragment-save-key", "admin-manage-ai-configuration-sequence/save-key"], ["admin-ui", "admin-manager", "admin-api-client", "admin-ai-providers-api", "ai-credential-entity", "audit-log-entity"], ["admin-platform-key"], "Pilihan simpan kekunci platform", "Optional platform-key save"),
    ("fragment-save-result", ["admin-manage-ai-configuration-sequence/fragment-save-result", "admin-manage-ai-configuration-sequence/save-success", "admin-manage-ai-configuration-sequence/save-error", "admin-manage-ai-configuration-sequence/divider-save-error"], ["admin-manager", "admin-api-client", "admin-ai-providers-api"], ["admin-platform-key"], "Alternatif hasil simpanan", "Save-result alternative"),
    ("fragment-refresh-models", ["admin-manage-ai-configuration-sequence/fragment-refresh-models", "admin-manage-ai-configuration-sequence/refresh-models"], ["admin-manager", "admin-api-client", "admin-ai-providers-api", "ai-provider", "ai-credential-entity"], ["admin-refresh-models", "admin-providers-table"], "Pilihan segar semula model", "Optional model refresh"),
    ("fragment-provider-loop", ["admin-manage-ai-configuration-sequence/fragment-provider-loop", "admin-manage-ai-configuration-sequence/provider-loop"], ["admin-ai-providers-api", "ai-provider", "supabase-db"], ["admin-refresh-models"], "Ulangan penyedia", "Provider loop"),
    ("fragment-provider-result", ["admin-manage-ai-configuration-sequence/fragment-provider-result", "admin-manage-ai-configuration-sequence/provider-", "admin-manage-ai-configuration-sequence/divider-provider-failure"], ["admin-ai-providers-api", "ai-provider", "supabase-db"], ["admin-providers-table"], "Alternatif hasil penyedia", "Provider-result alternative"),
    ("fragment-refresh-summary", ["admin-manage-ai-configuration-sequence/fragment-refresh-summary", "admin-manage-ai-configuration-sequence/refresh-complete", "admin-manage-ai-configuration-sequence/refresh-partial", "admin-manage-ai-configuration-sequence/refresh-request-error", "admin-manage-ai-configuration-sequence/divider-refresh-"], ["admin-ui", "admin-manager", "admin-api-client"], ["admin-providers-table", "admin-refresh-models"], "Alternatif ringkasan segar semula", "Refresh-summary alternative"),
    ("participant-administrator", ["admin-manage-ai-configuration-sequence/participant-administrator"], ["pentadbir"], ["admin-entry", "admin-providers-tab", "admin-platform-key", "admin-refresh-models"], "Pentadbir", "Administrator"),
    ("participant-ui", ["admin-manage-ai-configuration-sequence/participant-ui"], ["admin-ui"], ["admin-entry", "admin-providers-tab", "admin-providers-table", "admin-platform-key", "admin-refresh-models"], "UI Pentadbir PetaKerja", "PetaKerja Admin UI"),
    ("participant-manager", ["admin-manage-ai-configuration-sequence/participant-manager"], ["admin-manager"], ["admin-providers-tab", "admin-providers-table", "admin-platform-key", "admin-refresh-models"], "AdminDashboardManager", "AdminDashboardManager"),
    ("participant-client", ["admin-manage-ai-configuration-sequence/participant-client"], ["admin-api-client"], ["admin-providers-tab", "admin-platform-key", "admin-refresh-models"], "Klien API Pentadbir", "Admin API Client"),
    ("participant-api", ["admin-manage-ai-configuration-sequence/participant-api"], ["admin-ai-providers-api"], ["admin-providers-tab", "admin-platform-key", "admin-refresh-models"], "API Penyedia AI Pentadbir", "Admin AI Providers API"),
    ("participant-session", ["admin-manage-ai-configuration-sequence/participant-session"], ["better-auth"], ["admin-entry"], "Sesi Better Auth", "Better Auth Session"),
    ("participant-database", ["admin-manage-ai-configuration-sequence/participant-database"], ["supabase-db", "user-profile", "ai-credential-entity", "audit-log-entity"], ["admin-providers-table", "admin-platform-key", "admin-refresh-models"], "Supabase / PostgreSQL", "Supabase / PostgreSQL"),
    ("participant-external", ["admin-manage-ai-configuration-sequence/participant-external"], ["ai-provider"], ["admin-refresh-models"], "API Penyedia AI Luaran", "External AI Provider APIs"),
]

ADMIN_ACCESS_DASHBOARD_SEQUENCE_MS = {
    "PetaKerja Administrator Access Dashboard Sequence": "Jujukan Pentadbir Mengakses Papan Pemuka PetaKerja",
    "Administrator": "Pentadbir",
    "PetaKerja User Menu": "Menu Pengguna PetaKerja",
    "Admin API Client": "Klien API Pentadbir",
    "Protected Admin APIs": "API Pentadbir Terlindung",
    "Better Auth Session": "Sesi Better Auth",
    "[administrator or owner]": "[pentadbir atau owner]",
    "[dashboard data returned]": "[data papan pemuka dipulangkan]",
    "[request failed]": "[permintaan gagal]",
    "[no active session]": "[tiada sesi aktif]",
    "[role not allowed]": "[peranan tidak dibenarkan]",
    "Implementation note: opening the dashboard loads provider status, AI usage and recent users together. Blog analytics is loaded separately only when the Blog tab is opened.": "Nota pelaksanaan: pembukaan papan pemuka memuatkan status penyedia, penggunaan AI dan pengguna terkini serentak. Analitik blog dimuatkan berasingan hanya apabila tab Blog dibuka.",
}

ADMIN_ACCESS_DASHBOARD_SEQUENCE_COMPONENTS = [
    ("fragment-access", ["admin-access-dashboard-sequence/fragment-access", "admin-access-dashboard-sequence/access-", "admin-access-dashboard-sequence/divider-no-session", "admin-access-dashboard-sequence/divider-role-denied"], ["admin-dashboard-api", "better-auth", "user-profile"], ["admin-entry", "admin-overview"], "Alternatif akses", "Access alternative"),
    ("fragment-load-result", ["admin-access-dashboard-sequence/fragment-load-result", "admin-access-dashboard-sequence/load-", "admin-access-dashboard-sequence/divider-load-error"], ["admin-manager", "admin-api-client", "admin-dashboard-api"], ["admin-overview"], "Alternatif pemuatan", "Load-result alternative"),
    ("participant-administrator", ["admin-access-dashboard-sequence/participant-administrator"], ["pentadbir"], ["admin-entry"], "Pentadbir", "Administrator"),
    ("participant-ui", ["admin-access-dashboard-sequence/participant-ui"], ["admin-ui"], ["admin-entry", "admin-overview"], "Menu Pengguna PetaKerja", "PetaKerja User Menu"),
    ("participant-auth", ["admin-access-dashboard-sequence/participant-auth"], ["auth-manager"], ["admin-entry", "user-menu"], "AuthManager", "AuthManager"),
    ("participant-manager", ["admin-access-dashboard-sequence/participant-manager"], ["admin-manager"], ["admin-entry", "admin-overview"], "AdminDashboardManager", "AdminDashboardManager"),
    ("participant-client", ["admin-access-dashboard-sequence/participant-client"], ["admin-api-client"], ["admin-overview"], "Klien API Pentadbir", "Admin API Client"),
    ("participant-api", ["admin-access-dashboard-sequence/participant-api"], ["admin-dashboard-api", "admin-users-api", "admin-ai-providers-api", "admin-usage-api"], ["admin-overview"], "API Pentadbir Terlindung", "Protected Admin APIs"),
    ("participant-session", ["admin-access-dashboard-sequence/participant-session"], ["better-auth"], ["admin-entry"], "Sesi Better Auth", "Better Auth Session"),
    ("participant-database", ["admin-access-dashboard-sequence/participant-database"], ["supabase-db", "user-profile", "ai-credential-entity", "ai-usage-entity"], ["admin-overview"], "Supabase / PostgreSQL", "Supabase / PostgreSQL"),
]

ADMIN_MONITOR_ACTIVITY_SEQUENCE_MS = {
    "PetaKerja Administrator Monitor System Activity Logs Sequence": "Jujukan Pentadbir Memantau Log Aktiviti Sistem PetaKerja",
    "Administrator": "Pentadbir",
    "PetaKerja Admin UI": "UI Pentadbir PetaKerja",
    "Admin API Client": "Klien API Pentadbir",
    "Admin Usage API": "API Penggunaan Pentadbir",
    "Better Auth Session": "Sesi Better Auth",
    "[administrator or owner]": "[pentadbir atau owner]",
    "[no active session]": "[tiada sesi aktif]",
    "[role not allowed]": "[peranan tidak dibenarkan]",
    "[activity events available]": "[peristiwa aktiviti tersedia]",
    "[no activity events]": "[tiada peristiwa aktiviti]",
    "[request failed]": "[permintaan gagal]",
    "Implementation note: this use case currently monitors the latest 100 AI assistant usage events only. It does not read general server logs or public.ai_admin_audit_logs.": "Nota pelaksanaan: kes guna ini kini hanya memantau 100 peristiwa penggunaan pembantu AI terkini. Ia tidak membaca log pelayan umum atau public.ai_admin_audit_logs.",
}

ADMIN_MONITOR_ACTIVITY_SEQUENCE_COMPONENTS = [
    ("fragment-access", ["admin-monitor-activity-sequence/fragment-access", "admin-monitor-activity-sequence/access-", "admin-monitor-activity-sequence/divider-no-session", "admin-monitor-activity-sequence/divider-role-denied"], ["admin-usage-api", "better-auth", "user-profile"], ["admin-entry", "admin-usage-tab"], "Alternatif akses", "Access alternative"),
    ("fragment-results", ["admin-monitor-activity-sequence/fragment-results", "admin-monitor-activity-sequence/events-available", "admin-monitor-activity-sequence/no-events", "admin-monitor-activity-sequence/request-failed", "admin-monitor-activity-sequence/divider-no-events", "admin-monitor-activity-sequence/divider-request-failed"], ["admin-manager", "admin-ui", "ai-usage-entity"], ["admin-usage-tab", "admin-usage-table"], "Alternatif hasil aktiviti", "Activity-result alternative"),
    ("participant-administrator", ["admin-monitor-activity-sequence/participant-administrator"], ["pentadbir"], ["admin-entry", "admin-usage-tab"], "Pentadbir", "Administrator"),
    ("participant-ui", ["admin-monitor-activity-sequence/participant-ui"], ["admin-ui"], ["admin-entry", "admin-usage-tab", "admin-usage-table"], "UI Pentadbir PetaKerja", "PetaKerja Admin UI"),
    ("participant-manager", ["admin-monitor-activity-sequence/participant-manager"], ["admin-manager"], ["admin-usage-tab", "admin-usage-table"], "AdminDashboardManager", "AdminDashboardManager"),
    ("participant-client", ["admin-monitor-activity-sequence/participant-client"], ["admin-api-client"], ["admin-usage-tab"], "Klien API Pentadbir", "Admin API Client"),
    ("participant-api", ["admin-monitor-activity-sequence/participant-api"], ["admin-usage-api"], ["admin-usage-tab", "admin-usage-table"], "API Penggunaan Pentadbir", "Admin Usage API"),
    ("participant-session", ["admin-monitor-activity-sequence/participant-session"], ["better-auth"], ["admin-entry"], "Sesi Better Auth", "Better Auth Session"),
    ("participant-database", ["admin-monitor-activity-sequence/participant-database"], ["supabase-db", "user-profile", "ai-usage-entity"], ["admin-usage-table"], "Supabase / PostgreSQL", "Supabase / PostgreSQL"),
]

SIGN_OUT_SEQUENCE_MS = {
    "PetaKerja Administrator Sign Out Sequence": "Jujukan Pentadbir Log Keluar PetaKerja",
    "PetaKerja User Sign Out Sequence": "Jujukan Pengguna Log Keluar PetaKerja",
    "Administrator": "Pentadbir",
    "User": "Pengguna",
    "PetaKerja User Menu": "Menu Pengguna PetaKerja",
    "Better Auth API": "API Better Auth",
    "Better Auth Session": "Sesi Better Auth",
    "[sign-out succeeds]": "[log keluar berjaya]",
    "[sign-out fails]": "[log keluar gagal]",
    "Implementation note: on successful sign-out, UserDashboardManager closes and clears per-user caches. AdminDashboardManager currently remains on screen but re-renders its signed-out access state.": "Nota pelaksanaan: apabila log keluar berjaya, UserDashboardManager ditutup dan cache setiap pengguna dikosongkan. AdminDashboardManager kini kekal pada skrin tetapi memaparkan semula keadaan akses selepas log keluar.",
}

def sign_out_sequence_components(prefix: str, source: Path, administrator: bool) -> tuple[list[dict], list[dict]]:
    dashboard_node = "admin-manager" if administrator else "user-dashboard"
    dashboard_hotspots = ["admin-entry", "admin-overview"] if administrator else ["user-menu"]
    actor_node = "pentadbir" if administrator else "pengguna"
    actor_ms = "Pentadbir" if administrator else "Pengguna"
    specs = [
        ("fragment-result", [f"{prefix}/fragment-result", f"{prefix}/sign-out-", f"{prefix}/divider-sign-out-failed"], ["auth-manager", "better-auth", dashboard_node], ["user-menu"], "Alternatif hasil log keluar", "Sign-out result alternative"),
        (f"participant-{actor_node}", [f"{prefix}/participant-{'administrator' if administrator else 'user'}"], [actor_node], ["user-menu"], actor_ms, "Administrator" if administrator else "User"),
        ("participant-ui", [f"{prefix}/participant-ui"], ["admin-ui" if administrator else "workspace-ui"], ["user-menu"], "Menu Pengguna PetaKerja", "PetaKerja User Menu"),
        ("participant-menu-manager", [f"{prefix}/participant-menu-manager"], ["user-menu-manager"], ["user-menu"], "UserMenuManager", "UserMenuManager"),
        ("participant-auth", [f"{prefix}/participant-auth"], ["auth-manager"], ["user-menu"], "AuthManager", "AuthManager"),
        ("participant-client", [f"{prefix}/participant-client"], ["auth-client"], ["user-menu"], "authClient", "authClient"),
        ("participant-api", [f"{prefix}/participant-api"], ["better-auth"], ["user-menu"], "API Better Auth", "Better Auth API"),
        ("participant-session", [f"{prefix}/participant-session"], ["better-auth", "supabase-db"], ["user-menu"], "Sesi Better Auth", "Better Auth Session"),
        ("participant-dashboard", [f"{prefix}/participant-{'admin-dashboard' if administrator else 'user-dashboard'}"], [dashboard_node], dashboard_hotspots, "Papan Pemuka Pentadbir" if administrator else "Papan Pemuka Pengguna", "AdminDashboardManager" if administrator else "UserDashboardManager"),
    ]
    return sequence_components(source, prefix, specs, SIGN_OUT_SEQUENCE_MS)

USER_EXPLORE_3D_MAP_SEQUENCE_MS = {
    "PetaKerja User Explore the 3D Map Sequence": "Jujukan Pengguna Meneroka Peta 3D PetaKerja",
    "User": "Pengguna",
    "PetaKerja Workspace UI": "UI Ruang Kerja PetaKerja",
    "PetaKerja Data API": "API Data PetaKerja",
    "[map data available]": "[data peta tersedia]",
    "[data request fails]": "[permintaan data gagal]",
    "[user enables 3D terrain]": "[pengguna mengaktifkan terrain 3D]",
    "[user toggles 3D buildings]": "[pengguna menogol bangunan 3D]",
    "Implementation note: map exploration is public. 3D terrain uses satellite imagery plus a DEM on screens wider than 768px; building extrusions appear within their configured zoom range.": "Nota pelaksanaan: penerokaan peta ialah fungsi awam. Terrain 3D menggunakan imej satelit bersama DEM pada skrin melebihi 768px; ekstrusi bangunan muncul dalam julat zum yang ditetapkan.",
}

USER_EXPLORE_3D_MAP_SEQUENCE_COMPONENTS = [
    ("fragment-data-result", ["user-explore-3d-map-sequence/fragment-data-result", "user-explore-3d-map-sequence/data-", "user-explore-3d-map-sequence/divider-data-failed"], ["poi-manager", "category-manager", "supabase-module"], ["map-canvas", "contents-poi"], "Alternatif hasil data", "Data-result alternative"),
    ("fragment-terrain", ["user-explore-3d-map-sequence/fragment-terrain", "user-explore-3d-map-sequence/terrain-selected"], ["map-manager", "maplibre-gl"], ["ribbon-map", "map-canvas"], "Pilihan terrain 3D", "Optional 3D terrain"),
    ("fragment-buildings", ["user-explore-3d-map-sequence/fragment-buildings", "user-explore-3d-map-sequence/buildings-selected"], ["map-manager", "maplibre-gl"], ["ribbon-map", "map-canvas"], "Pilihan bangunan 3D", "Optional 3D buildings"),
    ("participant-user", ["user-explore-3d-map-sequence/participant-user"], ["pengguna"], ["start-workspaces", "map-canvas"], "Pengguna", "User"),
    ("participant-ui", ["user-explore-3d-map-sequence/participant-ui"], ["workspace-ui", "panel-manager"], ["start-map-preset", "ribbon-map", "map-canvas"], "UI Ruang Kerja PetaKerja", "PetaKerja Workspace UI"),
    ("participant-app", ["user-explore-3d-map-sequence/participant-app"], ["mypeta-app"], ["start-workspaces"], "MyPetaApp", "MyPetaApp"),
    ("participant-map-manager", ["user-explore-3d-map-sequence/participant-map-manager"], ["map-manager"], ["map-canvas", "ribbon-map"], "MapManager", "MapManager"),
    ("participant-poi-managers", ["user-explore-3d-map-sequence/participant-poi-managers"], ["poi-manager", "category-manager"], ["map-canvas", "contents-poi"], "POIManager / CategoryManager", "POIManager / CategoryManager"),
    ("participant-data-api", ["user-explore-3d-map-sequence/participant-data-api"], ["supabase-module"], ["map-canvas"], "API Data PetaKerja", "PetaKerja Data API"),
    ("participant-database", ["user-explore-3d-map-sequence/participant-database"], ["supabase-db", "poi-entity", "poi-category-entity"], ["map-canvas", "contents-poi"], "Supabase / PostgreSQL", "Supabase / PostgreSQL"),
    ("participant-maplibre", ["user-explore-3d-map-sequence/participant-maplibre"], ["maplibre-gl"], ["map-canvas"], "MapLibre GL", "MapLibre GL"),
]

CLASS_EN = {
    "PEKERJAAN &amp; STATUS PENGGUNA": "JOBS &amp; USER STATUS",
    "PEKERJAAN & STATUS PENGGUNA": "JOBS & USER STATUS",
    "Rajah Kelas Domain Teras Sistem PetaKerja": "PetaKerja Core Domain Class Diagram",
    "Model domain berdasarkan kod TypeScript dan jadual Supabase langsung. Operasi pada entiti mewakili operasi aplikasi yang mengurus rekod, bukan kaedah ORM.": "Domain model based on TypeScript code and live Supabase tables. Entity operations represent application behaviour that manages records, not ORM methods.",
    "IDENTITI DAN PROFIL": "IDENTITY AND PROFILE",
    "IDENTITI & PROFIL": "IDENTITY & PROFILE",
    "PEMETAAN, POI DAN DATA TERBUKA": "MAPPING, POI AND OPEN DATA",
    "PEMETAAN, POI & DATA TERBUKA": "MAPPING, POI & OPEN DATA",
    "PEKERJAAN DAN STATUS PENGGUNA": "JOBS AND USER STATUS",
    "AI DAN PENTADBIRAN": "AI AND ADMINISTRATION",
    "AI & PENTADBIRAN": "AI & ADMINISTRATION",
    "Model domain berdasarkan kod TypeScript dan jadual Supabase langsung. Operasi pada entiti mewakili tanggungjawab aplikasi yang mengurus rekod, bukan kaedah ORM atau kaedah literal pada entiti.": "Domain model based on TypeScript code and live Supabase tables. Entity operations represent application responsibilities that manage records, not ORM methods or literal methods on the entities.",
    "Legenda: <<entity>> = rekod Supabase; <<service>> = servis TypeScript; <<interface>> = kontrak TypeScript; JobListing menormalkan rekod public.scraped_jobs; garisan putus-putus = hubungan logik atau dependency; berlian kosong = aggregation.": "Legend: <<entity>> = Supabase record; <<service>> = TypeScript service; <<interface>> = TypeScript contract; JobListing normalizes public.scraped_jobs records; dashed line = logical relationship or dependency; hollow diamond = aggregation.",
    "dipadankan melalui provider_id": "resolved through provider_id",
    "membekalkan": "supplies",
    "berada di": "located in",
    "mengandungi": "contains",
    "mengelaskan": "classifies",
    "mengagregat": "aggregates",
    "kumpulan mengikut negeri": "groups by state",
    "Legenda:": "Legend:",
    "rekod Supabase": "Supabase record",
    "servis TypeScript": "TypeScript service",
    "kontrak TypeScript": "TypeScript contract",
    "hubungan logik": "logical relationship",
    "Kebergantungan Kelas Pelaksanaan PetaKerja": "PetaKerja Implementation Class Dependencies",
    "Paparan kelas dan modul TypeScript sebenar. MyPetaApp ialah orchestrator frontend; semua manager berkongsi AppState.": "Actual TypeScript classes and modules. MyPetaApp is the frontend orchestrator; all managers share AppState.",
    "Nota seni bina: Garisan pejal = association constructor; berlian penuh = pemilikan oleh MyPetaApp; putus-putus beranak panah = dependency modul. Aplikasi menggunakan supabase-js dan pg.Pool secara langsung, bukan ORM. public.job_listings dijangka oleh mod API Grep luaran tetapi tidak wujud dalam skema langsung; public.scraped_jobs ialah sumber Supa Grep yang tersedia.": "Architecture note: solid line = constructor association; filled diamond = ownership by MyPetaApp; dashed open arrow = module dependency. The application uses supabase-js and pg.Pool directly, not an ORM. public.job_listings is expected by an external Grep API mode but is absent from the live schema; public.scraped_jobs is the available Supa Grep source.",
    "TERAS APLIKASI": "APPLICATION CORE",
    "PENGURUS FRONTEND": "FRONTEND MANAGERS",
    "SERVIS DAN MODUL": "SERVICES AND MODULES",
    "JENIS KONGSI": "SHARED TYPES",
    "memiliki": "owns",
    "menggunakan": "uses",
    "bergantung pada": "depends on",
    "Lampiran - Peta Entiti Supabase Penuh": "Appendix - Full Supabase Entity Map",
    "Snapshot projek pbjbxfkztpgpwbqkqegy: 73 jadual public, 86 foreign key dan 1 hubungan logik Better Auth.": "Project pbjbxfkztpgpwbqkqegy snapshot: 73 public tables, 86 foreign keys and 1 logical Better Auth relationship.",
    "AI dan Pentadbiran": "AI and Administration",
    "Profil, Geo dan POI Teras": "Core Profile, Geo and POI",
    "Pekerjaan, Pipeline, Gmail, Watchlist dan Extractor": "Jobs, Pipeline, Gmail, Watchlist and Extractor",
    "Blog dan Newsletter": "Blog and Newsletter",
    "Komuniti dan Intel": "Community and Intel",
    "Infrastruktur dan Data Sokongan": "Infrastructure and Supporting Data",
    "Nota sistem: public.spatial_ref_sys ialah jadual PostGIS dan RLS tidak diaktifkan menurut advisor Supabase. Rajah ini hanya mendokumenkan keadaan tersebut; tiada perubahan pangkalan data dibuat.": "System note: public.spatial_ref_sys is a PostGIS table and Supabase Advisor reports RLS as disabled. This diagram only documents that state; no database changes are made.",
    "Multiplicity: FK nullable -&gt; 0..1 parent; FK wajib -&gt; 1 parent; FK unik/PK -&gt; 0..1 child; selainnya -&gt; 0..* child.": "Multiplicity: nullable FK -&gt; 0..1 parent; required FK -&gt; 1 parent; unique/PK FK -&gt; 0..1 child; otherwise -&gt; 0..* child.",
    "Multiplicity: FK nullable -> 0..1 parent; FK wajib -> 1 parent; FK unik/PK -> 0..1 child; selainnya -> 0..* child.": "Multiplicity: nullable FK -> 0..1 parent; required FK -> 1 parent; unique/PK FK -> 0..1 child; otherwise -> 0..* child.",
    "Legenda: PK = primary key, FK = foreign key, UK = unique key; garisan putus-putus = hubungan logik tanpa FK fizikal.": "Legend: PK = primary key, FK = foreign key, UK = unique key; dashed line = logical relationship without a physical FK.",
    "hubungan foreign key": "foreign-key relationships",
    "hubungan Better Auth logik": "logical Better Auth relationship",
    "Jadual sistem PostGIS": "PostGIS system table",
    "RLS tidak aktif": "RLS disabled",
    "Operasi pada entiti mewakili operasi aplikasi yang mengurus rekod, bukan kaedah ORM.": "Entity operations represent application behaviour that manages records, not ORM methods.",
    "Nota seni bina:": "Architecture note:",
    "Garisan pejal": "Solid line",
    "putus-putus": "dashed line",
    "pemilikan oleh": "ownership by",
    "Aplikasi menggunakan": "The application uses",
    "secara langsung, bukan ORM": "directly, not an ORM",
    "tidak wujud dalam skema langsung": "is absent from the live schema",
    "ialah sumber": "is the available source",
    "jadual public": "public tables",
    "foreign key dan": "foreign keys and",
    "hubungan logik Better Auth": "logical Better Auth relationship",
    "berlian penuh": "filled diamond",
    "beranak panah": "with open arrow",
    "dependency modul": "module dependency",
    "supabase-js dan pg.Pool": "supabase-js and pg.Pool",
    "dijangka oleh mod API Grep luaran tetapi": "is expected by an external Grep API mode but",
    "Supa Grep yang tersedia": "available Supa Grep",
    "yang tersedia": "available",
    "Nota sistem:": "System note:",
    "ialah jadual PostGIS dan RLS tidak diaktifkan menurut advisor Supabase.": "is a PostGIS table and Supabase Advisor reports RLS as disabled.",
    "Rajah ini hanya mendokumenkan keadaan tersebut; tiada perubahan pangkalan data dibuat.": "This diagram only documents that state; no database changes are made.",
    "FK nullable": "nullable FK",
    "FK wajib": "required FK",
    "FK unik/PK": "unique/PK FK",
    "selainnya": "otherwise",
    "garisan dashed line": "dashed line",
    "tanpa FK fizikal": "without a physical FK",
    "garisan": "line",
}

REPORT_EN = {
    "Rajah Aktiviti Carian Pekerjaan": "Job Search Activity Diagram",
    "Rajah Jujukan Carian Pekerjaan": "Job Search Sequence Diagram",
    "Seni Bina Sistem PetaKerja": "PetaKerja System Architecture",
    "Hierarki Modul PetaKerja": "PetaKerja Module Hierarchy",
    "Rajah Hubungan Entiti Teras": "Core Entity Relationship Diagram",
    "Aliran Data PetaKerja": "PetaKerja Data Flow",
    "Mula": "Start",
    "Tamat": "End",
    "Pengguna": "User",
    "Pilih carian pekerjaan": "Open job search",
    "Masukkan kata kunci dan lokasi": "Enter keywords and location",
    "Cari pekerjaan": "Search jobs",
    "Papar kad dan penanda peta": "Show cards and map markers",
    "Carian berjaya?": "Search successful?",
    "Ya": "Yes",
    "Tidak": "No",
    "Papar ralat": "Show error",
    "Antara muka": "Interface",
    "Pengurus": "Managers",
    "Servis": "Services",
    "Pangkalan data": "Database",
    "Perkhidmatan luar": "External services",
    "Sumber data": "Data sources",
    "Pemerolehan dan pertanyaan": "Ingestion and queries",
    "Penyimpanan": "Storage",
    "Paparan": "Presentation",
    "Kod semasa": "Current code",
    "Model konseptual": "Conceptual model",
    "Pengguna membuka ruang kerja PetaKerja": "User opens the PetaKerja workspace",
    "Pilih mod data": "Choose a data mode",
    "Normalisasi, deduplikasi dan tapisan relevan": "Normalise, deduplicate and filter for relevance",
    "Paparkan senarai dan penanda peta": "Render the list and map markers",
    "Pengguna melihat butiran kerja": "User views job details",
    "Simpan, abaikan atau buka pautan permohonan": "Save, dismiss or open the application link",
    "lalai": "default",
    "indeks pipeline": "pipeline index",
    "carian semasa": "live search",
    "Hantar query, lokasi dan penapis": "Send query, location and filters",
    "HTTP GET dengan parameter carian": "HTTP GET with search parameters",
    "Baris kerja berpadanan": "Matching job rows",
    "Tapis konteks Malaysia dan skor tajuk": "Filter Malaysian context and score job titles",
    "Susun keputusan + metadata sumber": "Sort results + source metadata",
    "Pulangkan respons JSON": "Return JSON response",
    "Kemas kini senarai kerja": "Update the job list",
    "setData pada source peta": "setData on the map source",
    "Kad kerja dan penanda dipaparkan": "Render job cards and markers",
    "Frontend Pelayar": "Browser Frontend",
    "Lapisan Pengurus": "Manager Layer",
    "Lapisan Servis": "Service Layer",
    "Data dan Perkhidmatan": "Data and Services",
    "interaksi UI dan peta": "UI and map interactions",
    "panggilan data": "data calls",
    "POI dan RPC": "POIs and RPCs",
    "carian kerja": "job search",
    "fungsi terlindung": "protected functions",
    "profil, status, indeks": "profile, status and indexes",
    "data terbuka": "open data",
    "Teras Aplikasi": "Application Core",
    "Modul Carian Kerja": "Job Search Module",
    "Analitik dan Bantuan": "Analytics and Assistance",
    "Akaun dan Pentadbiran": "Accounts and Administration",
    "Boot dan shell": "Boot and shell",
    "Peta interaktif": "Interactive map",
    "POI dan kategori": "POIs and categories",
    "Kad kerja": "Job cards",
    "Highlight kawasan": "Area highlight",
    "Admin, konfigurasi": "Admin and configuration",
    "status pengguna": "user status",
    "ruang kerja peta": "map workspace",
    "konteks lokasi": "location context",
    "simpan status kerja": "save job status",
    "fungsi AI terlindung": "protected AI functions",
    "Ingestion": "Ingestion",
    "Storan": "Storage",
    "Query": "Query",
    "Paparan": "Presentation",
    "Kad kerja": "Job cards",
    "Carta dan choropleth": "Charts and choropleths",
    "Konteks pembantu AI": "AI assistant context",
    "Tapisan relevan": "Relevance filter",
    "Sumber": "Sources",
}


REPORT_COMPONENTS = {
    "activity": [
        ("job-manager", ["JobFinderManager", "Cari pekerjaan", "Search jobs"]),
        ("jobs-api", ["supa-api.ts", "/api/jobs/supa"]),
        ("job-entity", ["scraped_jobs", "Kad pekerjaan"]),
        ("pengguna", ["Pengguna", "User"]),
    ],
    "sequence": [
        ("job-manager", ["JobFinderManager"]),
        ("jobs-api", ["supa-api.ts", "/api/jobs/supa"]),
        ("express-app", ["Express"]),
        ("job-entity", ["scraped_jobs"]),
        ("pengguna", ["Pengguna", "User"]),
    ],
    "architecture": [
        ("main-ts", ["src/main.ts"]),
        ("mypeta-app", ["MyPetaApp.ts", "MyPetaApp"]),
        ("job-manager", ["JobFinderManager"]),
        ("express-app", ["Express", "server/app.ts"]),
        ("supabase-db", ["Supabase", "PostgreSQL"]),
        ("better-auth", ["Better Auth"]),
    ],
    "modules": [
        ("mypeta-app", ["MyPetaApp"]),
        ("map-manager", ["MapManager"]),
        ("poi-manager", ["POIManager"]),
        ("job-manager", ["JobFinderManager"]),
        ("chatbot-manager", ["ChatbotManager"]),
        ("admin-manager", ["AdminDashboardManager"]),
    ],
    "erd": [
        ("auth-identity", ["public.user"]),
        ("user-profile", ["public.users"]),
        ("poi-entity", ["public.pois"]),
        ("job-entity", ["public.scraped_jobs"]),
        ("job-state-entity", ["public.user_job_states"]),
    ],
    "data-flow": [
        ("open-data-api", ["OpenDataAPI"]),
        ("supabase-db", ["Supabase"]),
        ("job-manager", ["JobFinderManager"]),
        ("chatbot-manager", ["ChatbotManager"]),
        ("data-gov", ["data.gov.my"]),
    ],
}


def export_drawio(source: Path, page: int, destination: Path) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    if destination.exists():
        destination.unlink()
    subprocess.run(
        [str(DRAWIO), "--export", "--format", "svg", "--page-index", str(page),
         "--output", str(destination), str(source)],
        check=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    deadline = time.time() + 20
    while time.time() < deadline:
        if destination.exists() and destination.stat().st_size > 1000:
            return
        time.sleep(0.2)
    raise RuntimeError(f"Draw.io did not produce {destination}")


def slim_svg(svg: str, preserve_embedded_images: bool = False) -> str:
    image_pattern = re.compile(r"<image\b[^>]*(?:/>|>.*?</image>)", flags=re.I | re.S)
    if preserve_embedded_images:
        def retain_workflow_logo(match: re.Match[str]) -> str:
            tag = match.group(0)
            if "data:image/svg+xml" in tag:
                return tag
            if "data:image/png" in tag:
                return tag
            return ""

        svg = image_pattern.sub(retain_workflow_logo, svg)
    else:
        svg = image_pattern.sub("", svg)
    svg = re.sub(r"<a\b[^>]*>\s*<text[^>]*>Text is not SVG[^<]*</text>\s*</a>", "", svg, flags=re.I | re.S)
    svg = re.sub(r">\s+<", "><", svg)
    return svg.strip()


def translate_svg(svg: str, replacements: dict[str, str]) -> str:
    # Replace longest phrases first in both plain and HTML-escaped forms.
    for source, target in sorted(replacements.items(), key=lambda item: len(item[0]), reverse=True):
        svg = svg.replace(source, target)
        escaped_source = html.escape(source, quote=False)
        escaped_target = html.escape(target, quote=False)
        if escaped_source != source:
            svg = svg.replace(escaped_source, escaped_target)
    return svg


def clean_label(value: str) -> str:
    text = html.unescape(re.sub(r"<[^>]+>", " ", value or ""))
    return re.sub(r"\s+", " ", text).strip()


def drawio_page(source: Path, page: int) -> tuple[ET.Element, dict[str, ET.Element]]:
    diagram = ET.parse(source).getroot().findall("diagram")[page - 1]
    cells = {cell.get("id", ""): cell for cell in diagram.findall(".//mxCell")}
    return diagram, cells


def connected_edges(cells: dict[str, ET.Element], cell_id: str) -> list[str]:
    return [cid for cid, cell in cells.items()
            if cell.get("edge") == "1" and cell_id in (cell.get("source"), cell.get("target"))]


def component_name(label: str, schema: bool) -> str | None:
    if schema:
        match = re.search(r"(?:public\.)?([A-Za-z0-9_]+)", label)
        return match.group(1) if match else None
    for name in sorted(CLASS_NODE_MAP, key=len, reverse=True):
        if label.startswith(name):
            return name
    match = re.search(r"([A-Za-z0-9_.-]+)", label)
    return match.group(1) if match else None


def translate_label(value: str, replacements: dict[str, str]) -> str:
    translated = value
    for source, target in sorted(replacements.items(), key=lambda item: len(item[0]), reverse=True):
        source_text = clean_label(source)
        target_text = clean_label(target)
        translated = translated.replace(source, target)
        translated = translated.replace(source_text, target_text)
        translated = translated.replace(
            html.escape(source_text, quote=False),
            html.escape(target_text, quote=False),
        )
    return translated


def edge_label(cells: dict[str, ET.Element], edge_id: str) -> str:
    edge = cells[edge_id]
    labels = [clean_label(edge.get("value", ""))]
    labels.extend(clean_label(cell.get("value", "")) for cell in cells.values() if cell.get("parent") == edge_id)
    return " · ".join(dict.fromkeys(label for label in labels if label))


def connection_kind(cell: ET.Element, label: str) -> str:
    style = cell.get("style", "")
    lowered = label.lower()
    if "include" in lowered:
        return "include"
    if "extend" in lowered:
        return "extend"
    if "startArrow=diamond" in style and "startFill=1" in style:
        return "composition"
    if "startArrow=diamond" in style:
        return "aggregation"
    if "dashed=1" in style and "endArrow=open" in style:
        return "dependency"
    if "dashed=1" in style:
        return "logical"
    return "association"


def build_connections(cells: dict[str, ET.Element], components: list[dict],
                      replacements: dict[str, str]) -> list[dict]:
    owner = {}
    for component in components:
        for cell_id in component.get("cellIds", []):
            owner[cell_id] = component["componentKey"]

    connections = []
    for edge_id, cell in cells.items():
        if cell.get("edge") != "1":
            continue
        source_key = owner.get(cell.get("source", ""))
        target_key = owner.get(cell.get("target", ""))
        if not source_key or not target_key:
            continue
        label_ms = edge_label(cells, edge_id)
        connections.append({
            "id": edge_id,
            "sourceComponentKey": source_key,
            "targetComponentKey": target_key,
            "kind": connection_kind(cell, label_ms),
            "label": {"ms": label_ms, "en": translate_label(label_ms, replacements)},
        })
    return connections


def class_components(source: Path, page: int, schema: bool = False,
                     stable_keys: bool = False) -> tuple[list[dict], list[dict]]:
    _diagram, cells = drawio_page(source, page)
    components = []
    if schema:
        class_ids = [cid for cid in cells if cid.startswith("class_")]
    else:
        class_ids = []
        for cid, cell in cells.items():
            if cell.get("vertex") != "1":
                continue
            label = clean_label(cell.get("value", ""))
            name = component_name(label, False)
            style = cell.get("style", "")
            if name in CLASS_NODE_MAP and ("swimlane" in style or cid.startswith("class_")):
                class_ids.append(cid)
    for cid in class_ids:
        label = clean_label(cells[cid].get("value", ""))
        name = component_name(label, schema)
        if not name:
            continue
        owned = [cid, *[child_id for child_id, child in cells.items() if child.get("parent") == cid]]
        table_name = name if schema else None
        node_id = TABLE_NODE_MAP.get(name) if schema else CLASS_NODE_MAP.get(name)
        relation_ids = connected_edges(cells, cid)
        component_key = node_id if stable_keys and node_id else f"drawio:{cid}"
        components.append({
            "componentKey": component_key,
            "id": f"table:{name}" if schema else (node_id or f"cell:{cid}"),
            "cellIds": list(dict.fromkeys(owned)),
            "relationCellIds": relation_ids,
            "nodeIds": [node_id] if node_id else [],
            "tableName": table_name,
            "uiHotspots": HOTSPOTS.get(node_id, []),
            "label": name,
        })
    return components, build_connections(cells, components, CLASS_EN)


def usecase_components() -> tuple[list[dict], list[dict]]:
    _diagram, cells = drawio_page(USECASE_SOURCE, 1)
    result = []
    for cid, node_id in USECASE_NODE_MAP.items():
        cell = cells.get(cid)
        if cell is None:
            continue
        label_ms = clean_label(cell.get("value", ""))
        label_en = label_ms
        for source, target in sorted(USECASE_EN.items(), key=lambda item: len(item[0]), reverse=True):
            label_en = label_en.replace(clean_label(source), clean_label(target))
        result.append({
            "componentKey": f"drawio:{cid}",
            "id": node_id,
            "cellIds": [cid],
            "relationCellIds": connected_edges(cells, cid),
            "nodeIds": [node_id],
            "tableName": None,
            "uiHotspots": HOTSPOTS.get(node_id, []),
            "label": label_ms,
            "labelEn": label_en,
        })
    return result, build_connections(cells, result, USECASE_EN)


def sequence_components(source: Path, key_prefix: str, specs: list[tuple],
                        translations: dict[str, str]) -> tuple[list[dict], list[dict]]:
    diagram = ET.parse(source).getroot().findall("diagram")[0]
    objects = []
    for wrapper in diagram.findall(".//object"):
        cell = wrapper.find("mxCell")
        if cell is None:
            continue
        objects.append({
            "id": wrapper.get("id", ""),
            "key": wrapper.get("petakerjaKey", ""),
            "label": clean_label(wrapper.get("label", "")),
            "simpleLabelEn": clean_label(wrapper.get("simpleLabelEn", "")),
            "simpleLabelMs": clean_label(wrapper.get("simpleLabelMs", "")),
            "codeLabelEn": clean_label(wrapper.get("codeLabelEn", "")),
            "codeLabelMs": clean_label(wrapper.get("codeLabelMs", "")),
            "cell": cell,
        })

    components = []
    object_owner = {}

    def matches_prefix(item_key: str, prefix: str) -> bool:
        """Match one canonical component family without swallowing neighbours.

        A trailing hyphen explicitly opts into a key family (for example an
        ``access-`` fragment and its operands).  Otherwise a participant owns
        only its exact cell plus the matching activation.  A plain
        ``participant-user`` prefix must therefore not also claim
        ``participant-user-dashboard``.
        """
        if prefix.endswith("-"):
            return item_key.startswith(prefix)
        if item_key == prefix:
            return True
        if item_key == f"{prefix}-activation":
            return True
        if "/participant-" in prefix:
            return item_key == prefix.replace("/participant-", "/activation-", 1)
        return False

    for component_key, prefixes, node_ids, hotspots, label_ms, label_en in specs:
        owned_items = [item for item in objects
                       if any(matches_prefix(item["key"], prefix) for prefix in prefixes)]
        # Keep the component's root cell first.  The editor manifest treats the
        # first cell as the canonical match and the remaining cells as nested
        # operands/activations.  Prefix families such as ``provider-`` can also
        # match an operand before the actual UML frame in document order.
        owned_items.sort(key=lambda item: (
            0 if item["key"] == prefixes[0] else 1,
            prefixes.index(next(prefix for prefix in prefixes
                                if matches_prefix(item["key"], prefix))),
            item["id"],
        ))
        owned = [item["id"] for item in owned_items]
        component = {
            "componentKey": component_key,
            "id": node_ids[0],
            "cellIds": owned,
            "relationCellIds": [],
            "nodeIds": node_ids,
            "tableName": None,
            "uiHotspots": hotspots,
            "label": label_ms,
            "labelEn": label_en,
        }
        components.append(component)
        for cell_id in owned:
            object_owner[cell_id] = component_key

    connections = []
    for item in objects:
        if not item["key"].startswith(f"{key_prefix}/message-"):
            continue
        cell = item["cell"]
        source_key = object_owner.get(cell.get("source", ""))
        target_key = object_owner.get(cell.get("target", ""))
        if not source_key or not target_key:
            continue
        style = cell.get("style", "")
        if source_key == target_key:
            kind = "sequence-self"
        elif "dashed=1" in style:
            kind = "sequence-return"
        else:
            kind = "sequence-sync"
        simple_en = item["simpleLabelEn"] or item["label"]
        simple_ms = item["simpleLabelMs"] or translate_label(simple_en, translations)
        code_en = item["codeLabelEn"] or item["label"]
        code_ms = item["codeLabelMs"] or code_en
        connections.append({
            "id": item["id"],
            "sourceComponentKey": source_key,
            "targetComponentKey": target_key,
            "kind": kind,
            "label": {"ms": simple_ms, "en": simple_en},
            "labels": {
                "simple": {"ms": simple_ms, "en": simple_en},
                "code": {"ms": code_ms, "en": code_en},
            },
            "petakerjaKey": item["key"],
        })
        for component in components:
            if component["componentKey"] in (source_key, target_key):
                component["relationCellIds"].append(item["id"])

    for component in components:
        component["relationCellIds"] = list(dict.fromkeys(component["relationCellIds"]))
    return components, connections


def google_oauth_sequence_components() -> tuple[list[dict], list[dict]]:
    return sequence_components(
        GOOGLE_OAUTH_SEQUENCE_SOURCE,
        "google-oauth-sequence",
        GOOGLE_OAUTH_SEQUENCE_COMPONENTS,
        GOOGLE_OAUTH_SEQUENCE_MS,
    )


def job_search_sequence_components() -> tuple[list[dict], list[dict]]:
    return sequence_components(
        JOB_SEARCH_SEQUENCE_SOURCE,
        "sequence",
        JOB_SEARCH_SEQUENCE_COMPONENTS,
        JOB_SEARCH_SEQUENCE_MS,
    )


def admin_manage_users_sequence_components() -> tuple[list[dict], list[dict]]:
    return sequence_components(
        ADMIN_MANAGE_USERS_SEQUENCE_SOURCE,
        "admin-manage-users-sequence",
        ADMIN_MANAGE_USERS_SEQUENCE_COMPONENTS,
        ADMIN_MANAGE_USERS_SEQUENCE_MS,
    )


def admin_manage_ai_configuration_sequence_components() -> tuple[list[dict], list[dict]]:
    return sequence_components(
        ADMIN_MANAGE_AI_CONFIGURATION_SEQUENCE_SOURCE,
        "admin-manage-ai-configuration-sequence",
        ADMIN_MANAGE_AI_CONFIGURATION_SEQUENCE_COMPONENTS,
        ADMIN_MANAGE_AI_CONFIGURATION_SEQUENCE_MS,
    )


def admin_access_dashboard_sequence_components() -> tuple[list[dict], list[dict]]:
    return sequence_components(
        ADMIN_ACCESS_DASHBOARD_SEQUENCE_SOURCE,
        "admin-access-dashboard-sequence",
        ADMIN_ACCESS_DASHBOARD_SEQUENCE_COMPONENTS,
        ADMIN_ACCESS_DASHBOARD_SEQUENCE_MS,
    )


def admin_monitor_activity_sequence_components() -> tuple[list[dict], list[dict]]:
    return sequence_components(
        ADMIN_MONITOR_ACTIVITY_SEQUENCE_SOURCE,
        "admin-monitor-activity-sequence",
        ADMIN_MONITOR_ACTIVITY_SEQUENCE_COMPONENTS,
        ADMIN_MONITOR_ACTIVITY_SEQUENCE_MS,
    )


def user_explore_3d_map_sequence_components() -> tuple[list[dict], list[dict]]:
    return sequence_components(
        USER_EXPLORE_3D_MAP_SEQUENCE_SOURCE,
        "user-explore-3d-map-sequence",
        USER_EXPLORE_3D_MAP_SEQUENCE_COMPONENTS,
        USER_EXPLORE_3D_MAP_SEQUENCE_MS,
    )


def sequence_source_translations(source: Path, base: dict[str, str]) -> dict[str, str]:
    replacements = dict(base)
    for wrapper in ET.parse(source).getroot().findall(".//object"):
        label_en = clean_label(wrapper.get("labelEn", ""))
        label_ms = clean_label(wrapper.get("labelMs", ""))
        if label_en and label_ms:
            replacements[label_en] = label_ms
        simple_en = clean_label(wrapper.get("simpleLabelEn", ""))
        simple_ms = clean_label(wrapper.get("simpleLabelMs", ""))
        if simple_en and simple_ms:
            replacements[simple_en] = simple_ms
    return replacements


AUTH_SEQUENCE_MS = {
    **GOOGLE_OAUTH_SEQUENCE_MS,
    **SIGN_OUT_SEQUENCE_MS,
    "PetaKerja User Login and Logout Sequence": "Jujukan Log Masuk dan Log Keluar Pengguna PetaKerja",
    "alt [sign-out]": "alt [log keluar]",
    "alt [profile]": "alt [profil]",
    "PetaKerja UI": "Antara Muka PetaKerja",
    "Better Auth API": "API Better Auth",
    "PetaKerja Profile API": "API Profil PetaKerja",
    "Account selection / consent": "Pemilihan akaun / persetujuan",
    "Account + session persisted": "Akaun dan sesi disimpan",
    "Application profile": "Profil aplikasi",
    "AuthUser profile": "Profil AuthUser",
    "Session invalidated": "Sesi dibatalkan",
    "Clear session cookie": "Kosongkan kuki sesi",
    "Sign-out error response": "Respons ralat log keluar",
    "keep current session state": "kekalkan keadaan sesi semasa",
    "Close authenticated views; render guest sign-in": "Tutup paparan pengguna dan paparkan log masuk tetamu",
}

MAP_ROUTING_STACK_MS = {
    "PetaKerja A-to-B Navigation: Who Does What?": "Navigasi A-ke-B PetaKerja: Siapa Melakukan Apa?",
    "MapLibre renders. GeoGateway orchestrates. Valhalla routes. Nominatim searches.": "MapLibre memapar. GeoGateway mengatur. Valhalla menghala. Nominatim mencari.",
    "LAYER 1 · INPUTS": "LAPISAN 1 · INPUT",
    "Place / address": "Tempat / alamat", "Search text": "Teks carian",
    "A and B": "A dan B", "Map click / selected place": "Klik peta / tempat dipilih",
    "Browser GPS": "GPS pelayar", "Current coordinates": "Koordinat semasa",
    "LAYER 2 · RENDERING — MAPLIBRE GL JS": "LAPISAN 2 · PAPARAN — MAPLIBRE GL JS",
    "Current PetaKerja rendering": "Paparan PetaKerja semasa",
    "A/B markers · GPS · primary + alternative lines": "Penanda A/B · GPS · garisan utama + alternatif",
    "Rendering capabilities": "Keupayaan paparan",
    "Direction graphics · marker animation · camera fit": "Grafik arah · animasi penanda · muat kamera",
    "LAYER 3 · PETAKERJA BROWSER ORCHESTRATION": "LAPISAN 3 · ORKESTRASI PELAYAR PETAKERJA",
    "Hybrid POI + place search": "Carian hibrid POI + tempat",
    "profiles · alternatives · maneuvers": "profil · alternatif · manuver",
    "Same-origin /api/geo requests": "Permintaan /api/geo asal sama",
    "LAYER 4 · PETAKERJA GEOGATEWAY": "LAPISAN 4 · GEOGATEWAY PETAKERJA",
    "Same-origin API surface": "Permukaan API asal sama",
    "Provider-neutral orchestration": "Orkestrasi neutral penyedia",
    "Safety + normalization": "Keselamatan + penormalan",
    "Malaysia validation · timeouts · rate limits · cache": "Pengesahan Malaysia · had masa · had kadar · cache",
    "LAYER 5 · PROVIDERS + REUSABLE DATA": "LAPISAN 5 · PENYEDIA + DATA BOLEH GUNA SEMULA",
    "Search · reverse · lookup": "Cari · songsang · semak",
    "place/address ↔ coordinates": "tempat/alamat ↔ koordinat",
    "Road geometry · distance · traffic-independent ETA": "Geometri jalan · jarak · ETA tanpa trafik",
    "maneuvers · alternatives · matrices · isochrones": "manuver · alternatif · matriks · isokron",
    "THE BOTTOM LINE": "RINGKASANNYA",
    "visualizer": "pemapar", "route calculator": "pengira laluan", "place/address search": "carian tempat/alamat",
    "MAPLIBRE IS NOT A ROUTING ENGINE": "MAPLIBRE BUKAN ENJIN PENGHALAAN",
    "It receives already-calculated GeoJSON and renders it. It does not follow roads, calculate driving distance, produce ETA, or generate turn instructions.": "Ia menerima GeoJSON yang telah dikira lalu memaparkannya. Ia tidak mengekori jalan, mengira jarak pemanduan, menghasilkan ETA atau menjana arahan membelok.",
    "zoom buttons + compass only": "butang zum + kompas sahaja",
    "Official MapLibre documentation ↗": "Dokumentasi rasmi MapLibre ↗",
    "sends requests to a configured external routing API. PetaKerja currently uses GeoNavigationManager instead of this plugin.": "menghantar permintaan kepada API penghalaan luar yang dikonfigurasi. PetaKerja kini menggunakan GeoNavigationManager dan bukan pemalam ini.",
    "Plugin configuration ↗": "Konfigurasi pemalam ↗",
    "SEPARATE INPUT FLOWS": "ALIRAN INPUT BERASINGAN",
    "Place/address → GeoGateway → Nominatim → coordinates": "Tempat/alamat → GeoGateway → Nominatim → koordinat",
    "Browser GPS → current coordinates → MapLibre": "GPS pelayar → koordinat semasa → MapLibre",
    "GPS coordinate → Nominatim reverse lookup → readable label": "Koordinat GPS → carian songsang Nominatim → label boleh dibaca",
    "ROUTING FALLBACK": "SANDARAN PENGHALAAN",
    "Valhalla unavailable or disabled": "Valhalla tidak tersedia atau dilumpuhkan",
    "Haversine straight-line estimate": "Anggaran garis lurus Haversine",
    "No ETA · no maneuvers · not navigable": "Tiada ETA · tiada manuver · tidak boleh dinavigasi",
    "ROLLOUT STATUS": "STATUS PELAKSANAAN",
    "Implementation is present. GEO_PROVIDER_ENABLED and VITE_GEO_* flags remain opt-in until staging import, health, route-generation, and failover checks pass.": "Pelaksanaan telah tersedia. Bendera GEO_PROVIDER_ENABLED dan VITE_GEO_* kekal ikut serta sehingga semakan import staging, kesihatan, penjanaan laluan dan failover lulus.",
    "Source-grounded in GeoNavigationManager, src/services/geo.ts, Express /api/geo, and server GeoGateway. Current ETA is traffic-independent.": "Berasaskan sumber GeoNavigationManager, src/services/geo.ts, Express /api/geo dan GeoGateway pelayan. ETA semasa tidak mengambil kira trafik.",
    "REQUEST ↓": "PERMINTAAN ↓", "A/B + profile": "A/B + profil",
    "RESPONSE ↑": "RESPONS ↑", "distance + ETA": "jarak + ETA",
    "maneuvers + alternatives": "manuver + alternatif",
    "provider unavailable / disabled": "penyedia tidak tersedia / dilumpuhkan",
}

MAP_ROUTING_STACK_COMPONENTS = {
    "input-gps": ("browser", ["browser"]),
    "browser-search-manager": ("search-manager", ["search-manager"]),
    "maplibre-current": ("maplibre-gl", ["maplibre-gl"]),
    "gateway-express": ("express-app", ["express-app"]),
    "provider-supabase": ("supabase-db", ["supabase-db"]),
}


def v2_georouting_translations(source: Path) -> dict[str, str]:
    """Read the bilingual labels embedded by the V2 source generator."""
    replacements: dict[str, str] = {}
    diagram = ET.parse(source).getroot().find("diagram")
    if diagram is None:
        return replacements
    for element in [*diagram.findall(".//object"), *diagram.findall(".//mxCell")]:
        raw_en = element.get("labelEn") or element.get("label") or element.get("value") or ""
        raw_ms = element.get("labelMs") or ""
        label_en = clean_label(raw_en)
        label_ms = clean_label(raw_ms)
        if label_en and label_ms and label_en != label_ms:
            replacements[label_en] = label_ms
        for prefix in ("simple", "code"):
            mode_en = clean_label(element.get(f"{prefix}LabelEn", ""))
            mode_ms = clean_label(element.get(f"{prefix}LabelMs", ""))
            if mode_en and mode_ms and mode_en != mode_ms:
                replacements[mode_en] = mode_ms
        if source in WORKFLOW_SOURCES:
            lines_en = [clean_label(value) for value in re.split(r"<br\s*/?>", raw_en, flags=re.I)]
            lines_ms = [clean_label(value) for value in re.split(r"<br\s*/?>", raw_ms, flags=re.I)]
            if len(lines_en) == len(lines_ms):
                for line_en, line_ms in zip(lines_en, lines_ms):
                    if line_en and line_ms and line_en != line_ms:
                        replacements[line_en] = line_ms
    return replacements


def bilingual_translation_spec(diagram_id: str, source: Path) -> tuple[str, dict[str, str]] | None:
    """Return the source language and BM/EN dictionary for an editor page."""
    if diagram_id in V2_GEOROUTING_IDS or diagram_id in EMBEDDED_BILINGUAL_IDS:
        return "en", v2_georouting_translations(source)
    if diagram_id == "usecase":
        return "ms", USECASE_EN
    if diagram_id in {"domain", "domain-original", "implementation", "supabase"}:
        return "ms", CLASS_EN
    if diagram_id in {"user-google-sign-in-flowchart", "user-google-sign-in-flowchart-original"}:
        return "en", GOOGLE_SIGN_IN_FLOWCHART_MS
    if diagram_id in USER_FLOWCHART_SPECS:
        return "en", USER_FLOWCHART_SPECS[diagram_id][1]
    if diagram_id in ADMIN_FLOWCHART_SPECS:
        return "en", ADMIN_FLOWCHART_SPECS[diagram_id][1]
    if diagram_id in DESIGN_SPECS:
        return "en", DESIGN_SPECS[diagram_id][1]
    if diagram_id == "map-routing-responsibility-stack":
        return "en", MAP_ROUTING_STACK_MS
    sequence_maps = {
        "sequence": JOB_SEARCH_SEQUENCE_MS,
        "auth-sequence": AUTH_SEQUENCE_MS,
        "google-oauth-sequence": GOOGLE_OAUTH_SEQUENCE_MS,
        "admin-manage-users-sequence": ADMIN_MANAGE_USERS_SEQUENCE_MS,
        "admin-manage-ai-configuration-sequence": ADMIN_MANAGE_AI_CONFIGURATION_SEQUENCE_MS,
        "admin-access-dashboard-sequence": ADMIN_ACCESS_DASHBOARD_SEQUENCE_MS,
        "admin-monitor-activity-sequence": ADMIN_MONITOR_ACTIVITY_SEQUENCE_MS,
        "admin-sign-out-sequence": SIGN_OUT_SEQUENCE_MS,
        "user-explore-3d-map-sequence": USER_EXPLORE_3D_MAP_SEQUENCE_MS,
        "user-sign-out-sequence": SIGN_OUT_SEQUENCE_MS,
    }
    if diagram_id in sequence_maps:
        return "en", sequence_source_translations(source, sequence_maps[diagram_id])
    return None


def annotate_bilingual_page(diagram: ET.Element, source_language: str,
                            replacements: dict[str, str]) -> int:
    """Attach BM/EN labels without wrapping or restructuring existing cells."""
    changed = 0
    wrappers = diagram.findall(".//object")
    wrapped_cell_ids = {
        cell.get("id", "")
        for wrapper in wrappers
        for cell in [wrapper.find("mxCell")]
        if cell is not None
    }
    elements: list[tuple[ET.Element, str]] = [(wrapper, "label") for wrapper in wrappers]
    elements.extend(
        (cell, "value")
        for cell in diagram.findall(".//mxCell")
        if cell.get("id", "") not in wrapped_cell_ids
    )
    for element, visible_attribute in elements:
        visible = element.get(visible_attribute, "")
        if not visible:
            continue
        if source_language == "ms":
            label_ms = element.get("labelMs") or visible
            label_en = element.get("labelEn") or translate_label(label_ms, replacements)
        else:
            label_en = element.get("labelEn") or visible
            label_ms = element.get("labelMs") or translate_label(label_en, replacements)
        for attribute, value in (("labelEn", label_en), ("labelMs", label_ms)):
            if element.get(attribute) != value:
                element.set(attribute, value)
                changed += 1
        key = element.get("petakerjaKey", "")
        if element.tag == "object" and "/message-" in key and not element.get("simpleLabelEn"):
            simple_en = re.sub(r"^\s*\d+\.\s*", "", label_en).strip()
            simple_ms = re.sub(r"^\s*\d+\.\s*", "", label_ms).strip()
            for attribute, value in (
                ("simpleLabelEn", simple_en),
                ("simpleLabelMs", simple_ms),
                ("codeLabelEn", simple_en),
                ("codeLabelMs", simple_en),
            ):
                element.set(attribute, value)
                changed += 1
        canonical = element.get("simpleLabelEn") or label_en
        if element.get(visible_attribute) != canonical:
            element.set(visible_attribute, canonical)
            changed += 1
    return changed


def apply_all_bilingual_metadata(root: Path) -> int:
    """Annotate every registered editable page using its existing View dictionary."""
    manifest_path = root / "workspace-manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    grouped: dict[Path, list[tuple[str, str, str, dict[str, str]]]] = {}
    for diagram_id, entry in manifest.get("diagrams", {}).items():
        source = root / entry["xml"]
        spec = bilingual_translation_spec(diagram_id, source)
        if not spec:
            continue
        source_language, replacements = spec
        grouped.setdefault(source, []).append(
            (diagram_id, entry["pageId"], source_language, replacements)
        )

    total_changed = 0
    for source, page_specs in grouped.items():
        tree = ET.parse(source)
        pages = {page.get("id", ""): page for page in tree.getroot().findall("diagram")}
        file_changed = 0
        annotated_pages: set[str] = set()
        for diagram_id, page_id, source_language, replacements in page_specs:
            if page_id in annotated_pages:
                continue
            diagram = pages.get(page_id)
            if diagram is None:
                raise ValueError(f"Missing page {page_id!r} for {diagram_id!r} in {source}")
            file_changed += annotate_bilingual_page(diagram, source_language, replacements)
            annotated_pages.add(page_id)
        if file_changed:
            ET.indent(tree, space="  ")
            tree.write(source, encoding="utf-8", xml_declaration=False)
            total_changed += file_changed
    return total_changed


def google_sign_in_flowchart_components(source: Path = GOOGLE_SIGN_IN_FLOWCHART_SOURCE) -> tuple[list[dict], list[dict]]:
    """Build the interactive manifest from stable flow-chart metadata."""
    diagram = ET.parse(source).getroot().findall("diagram")[0]
    wrappers = {wrapper.get("id", ""): wrapper for wrapper in diagram.findall(".//object")}
    components = []
    owner = {}
    prefix = "user-google-sign-in-flowchart/"
    for wrapper_id, wrapper in wrappers.items():
        cell = wrapper.find("mxCell")
        stable_key = wrapper.get("petakerjaKey", "")
        if cell is None or cell.get("vertex") != "1" or not stable_key.startswith(prefix):
            continue
        suffix = stable_key[len(prefix):]
        spec = GOOGLE_SIGN_IN_FLOWCHART_COMPONENTS.get(suffix)
        if not spec:
            continue
        node_ids, hotspots, label_ms, label_en = spec
        component = {
            "componentKey": suffix,
            "id": node_ids[0],
            "cellIds": [wrapper_id],
            "relationCellIds": [],
            "nodeIds": node_ids,
            "tableName": None,
            "uiHotspots": hotspots,
            "label": label_ms,
            "labelEn": label_en,
        }
        components.append(component)
        owner[wrapper_id] = component

    connections = []
    for wrapper_id, wrapper in wrappers.items():
        cell = wrapper.find("mxCell")
        if cell is None or cell.get("edge") != "1":
            continue
        source = owner.get(cell.get("source", ""))
        target = owner.get(cell.get("target", ""))
        if not source or not target:
            continue
        source["relationCellIds"].append(wrapper_id)
        target["relationCellIds"].append(wrapper_id)
        label_en = clean_label(wrapper.get("label", ""))
        label_ms = GOOGLE_SIGN_IN_FLOWCHART_MS.get(label_en, label_en)
        connections.append({
            "id": wrapper_id,
            "sourceComponentKey": source["componentKey"],
            "targetComponentKey": target["componentKey"],
            "kind": "flow-decision" if label_en in ("Yes", "No") else "flow",
            "label": {"ms": label_ms, "en": label_en},
        })
    return components, connections


def admin_flowchart_components(diagram_id: str) -> tuple[list[dict], list[dict]]:
    """Build an administrator flow chart from stable metadata."""
    source_path, translations, component_specs, key_prefix = ADMIN_FLOWCHART_SPECS[diagram_id]
    table_by_node = {
        "user-profile": "users",
        "ai-usage-entity": "ai_usage_events",
        "ai-credential-entity": "ai_provider_credentials",
        "audit-log-entity": "ai_admin_audit_logs",
    }
    diagram = ET.parse(source_path).getroot().findall("diagram")[0]
    wrappers = {wrapper.get("id", ""): wrapper for wrapper in diagram.findall(".//object")}
    components = []
    owner = {}
    prefix = f"{key_prefix}/"
    for wrapper_id, wrapper in wrappers.items():
        cell = wrapper.find("mxCell")
        stable_key = wrapper.get("petakerjaKey", "")
        if cell is None or cell.get("vertex") != "1" or not stable_key.startswith(prefix):
            continue
        component_key = stable_key[len(prefix):]
        spec = component_specs.get(component_key)
        if not spec:
            continue
        node_ids, hotspots, label_ms, label_en = spec
        component = {
            "componentKey": component_key,
            "id": node_ids[0],
            "cellIds": [wrapper_id],
            "relationCellIds": [],
            "nodeIds": node_ids,
            "tableName": next((table_by_node[node_id] for node_id in node_ids if node_id in table_by_node), None),
            "uiHotspots": hotspots,
            "label": label_ms,
            "labelEn": label_en,
        }
        components.append(component)
        owner[wrapper_id] = component

    connections = []
    for wrapper_id, wrapper in wrappers.items():
        cell = wrapper.find("mxCell")
        if cell is None or cell.get("edge") != "1":
            continue
        source = owner.get(cell.get("source", ""))
        target = owner.get(cell.get("target", ""))
        if not source or not target:
            continue
        source["relationCellIds"].append(wrapper_id)
        target["relationCellIds"].append(wrapper_id)
        label_en = clean_label(wrapper.get("label", ""))
        label_ms = translations.get(label_en, label_en)
        connections.append({
            "id": wrapper_id,
            "sourceComponentKey": source["componentKey"],
            "targetComponentKey": target["componentKey"],
            "kind": "flow-decision" if label_en in ("Yes", "No") else "flow",
            "label": {"ms": label_ms, "en": label_en},
        })
    return components, connections


def element_label_modes(element: ET.Element, translations: dict[str, str] | None = None) -> dict | None:
    translations = translations or {}
    simple_en = clean_label(element.get("simpleLabelEn", ""))
    code_en = clean_label(element.get("codeLabelEn", ""))
    if not simple_en or not code_en:
        return None
    simple_ms = clean_label(element.get("simpleLabelMs", "")) or translations.get(simple_en, simple_en)
    code_ms = clean_label(element.get("codeLabelMs", "")) or translations.get(code_en, code_en)
    return {
        "simple": {"en": simple_en, "ms": simple_ms},
        "code": {"en": code_en, "ms": code_ms},
    }


def drawio_label_elements(source: Path, translations: dict[str, str] | None = None) -> list[dict]:
    diagram = ET.parse(source).getroot().find("diagram")
    if diagram is None:
        return []
    result = []
    for element in [*diagram.findall(".//object"), *diagram.findall(".//mxCell")]:
        labels = element_label_modes(element, translations)
        if labels and element.get("id"):
            result.append({"cellId": element.get("id"), "labels": labels})
    return result


def keyed_drawio_components(
    diagram_id: str,
    specs: dict[str, tuple[Path, dict[str, str], dict, str]],
    connection_kind: str,
) -> tuple[list[dict], list[dict]]:
    """Build interactive components from stable petakerjaKey values."""
    source_path, translations, component_specs, key_prefix = specs[diagram_id]
    table_by_node = {
        "job-entity": "scraped_jobs", "poi-entity": "pois", "user-profile": "users",
        "supabase-db": None,
    }
    diagram = ET.parse(source_path).getroot().findall("diagram")[0]
    wrappers = {wrapper.get("id", ""): wrapper for wrapper in diagram.findall(".//object")}
    components: list[dict] = []
    owner: dict[str, dict] = {}
    prefix = f"{key_prefix}/"
    for wrapper_id, wrapper in wrappers.items():
        cell = wrapper.find("mxCell")
        stable_key = wrapper.get("petakerjaKey", "")
        if cell is None or cell.get("vertex") != "1" or not stable_key.startswith(prefix):
            continue
        component_key = stable_key[len(prefix):]
        spec = component_specs.get(component_key)
        if not spec:
            continue
        node_ids, hotspots = spec[:2]
        label_en = clean_label(wrapper.get("label", ""))
        label_ms = translations.get(label_en, label_en)
        component = {
            "componentKey": component_key,
            "id": node_ids[0],
            "cellIds": [wrapper_id],
            "relationCellIds": [],
            "nodeIds": list(node_ids),
            "tableName": next((table_by_node[node_id] for node_id in node_ids if node_id in table_by_node), None),
            "uiHotspots": list(hotspots),
            "label": label_ms,
            "labelEn": label_en,
        }
        labels = element_label_modes(wrapper, translations)
        if labels:
            component["labels"] = labels
        components.append(component)
        owner[wrapper_id] = component

    connections: list[dict] = []
    for wrapper_id, wrapper in wrappers.items():
        cell = wrapper.find("mxCell")
        if cell is None or cell.get("edge") != "1" or wrapper.get("petakerjaRelation") == "structural":
            continue
        source = owner.get(cell.get("source", ""))
        target = owner.get(cell.get("target", ""))
        if not source or not target:
            continue
        source["relationCellIds"].append(wrapper_id)
        target["relationCellIds"].append(wrapper_id)
        label_en = clean_label(wrapper.get("label", ""))
        label_ms = translations.get(label_en, label_en)
        kind = "flow-decision" if connection_kind == "flow" and label_en in ("Yes", "No") else connection_kind
        connection = {
            "id": wrapper_id,
            "sourceComponentKey": source["componentKey"],
            "targetComponentKey": target["componentKey"],
            "kind": kind,
            "label": {"ms": label_ms, "en": label_en},
        }
        labels = element_label_modes(wrapper, translations)
        if labels:
            connection["labels"] = labels
        connections.append(connection)
    return components, connections


def v2_georouting_components(source: Path) -> tuple[list[dict], list[dict]]:
    """Build Explorer interaction metadata directly from generated stable keys."""
    diagram = ET.parse(source).getroot().find("diagram")
    if diagram is None:
        return [], []
    wrappers = {wrapper.get("id", ""): wrapper for wrapper in diagram.findall(".//object")}
    components: list[dict] = []
    owner: dict[str, dict] = {}
    for wrapper_id, wrapper in wrappers.items():
        cell = wrapper.find("mxCell")
        node_ids = [value for value in wrapper.get("nodeIds", "").split(",") if value]
        if cell is None or cell.get("vertex") != "1" or not node_ids:
            continue
        component = {
            "componentKey": wrapper.get("petakerjaKey") or wrapper_id,
            "id": node_ids[0],
            "cellIds": [wrapper_id],
            "relationCellIds": [],
            "nodeIds": node_ids,
            "tableName": wrapper.get("tableName") or None,
            "uiHotspots": [value for value in wrapper.get("uiHotspots", "").split(",") if value],
            "label": clean_label(wrapper.get("labelMs") or wrapper.get("label") or ""),
            "labelEn": clean_label(wrapper.get("labelEn") or wrapper.get("label") or ""),
        }
        components.append(component)
        owner[wrapper_id] = component

    connections: list[dict] = []
    for wrapper_id, wrapper in wrappers.items():
        cell = wrapper.find("mxCell")
        if cell is None or cell.get("edge") != "1" or wrapper.get("petakerjaRelation") == "structural":
            continue
        source = owner.get(cell.get("source", ""))
        target = owner.get(cell.get("target", ""))
        if not source or not target:
            continue
        source["relationCellIds"].append(wrapper_id)
        target["relationCellIds"].append(wrapper_id)
        label_en = clean_label(wrapper.get("labelEn") or wrapper.get("label") or "")
        label_ms = clean_label(wrapper.get("labelMs") or label_en)
        is_message = wrapper.get("message") == "1"
        if is_message and source is target:
            connection_kind = "sequence-self"
        elif is_message and "dashed=1" in cell.get("style", ""):
            connection_kind = "sequence-return"
        elif is_message:
            connection_kind = "sequence-sync"
        else:
            connection_kind = "flow"
        connection = {
            "id": wrapper_id,
            "sourceComponentKey": source["componentKey"],
            "targetComponentKey": target["componentKey"],
            "kind": connection_kind,
            "label": {"ms": label_ms, "en": label_en},
        }
        if is_message:
            connection["labels"] = {
                "simple": {
                    "en": clean_label(wrapper.get("simpleLabelEn") or label_en),
                    "ms": clean_label(wrapper.get("simpleLabelMs") or label_ms),
                },
                "code": {
                    "en": clean_label(wrapper.get("codeLabelEn") or label_en),
                    "ms": clean_label(wrapper.get("codeLabelMs") or label_ms),
                },
            }
        connections.append(connection)
    return components, connections


def user_flowchart_components(diagram_id: str) -> tuple[list[dict], list[dict]]:
    return keyed_drawio_components(diagram_id, USER_FLOWCHART_SPECS, "flow")


def design_components(diagram_id: str) -> tuple[list[dict], list[dict]]:
    components, connections = keyed_drawio_components(diagram_id, DESIGN_SPECS, "dependency")
    if diagram_id in {"modules", "modules-layered-stack"}:
        known_components = {component["componentKey"] for component in components}
        for connection_id, source_key, target_key, label_en in MODULE_HIERARCHY_DEPENDENCIES:
            if source_key not in known_components or target_key not in known_components:
                raise ValueError(f"Module dependency references an unknown component: {connection_id}")
            connections.append({
                "id": connection_id,
                "sourceComponentKey": source_key,
                "targetComponentKey": target_key,
                "kind": "dependency",
                "label": {"ms": MODULE_HIERARCHY_MS[label_en], "en": label_en},
                "visual": False,
            })
    return components, connections


def map_routing_stack_components() -> tuple[list[dict], list[dict]]:
    """Map only canonical Explorer entities represented by the routing stack."""
    diagram = ET.parse(MAP_ROUTING_STACK_SOURCE).getroot().findall("diagram")[0]
    wrappers = {wrapper.get("id", ""): wrapper for wrapper in diagram.findall(".//object")}
    components: list[dict] = []
    for wrapper_id, (component_key, node_ids) in MAP_ROUTING_STACK_COMPONENTS.items():
        wrapper = wrappers.get(wrapper_id)
        if wrapper is None:
            raise ValueError(f"Missing routing-stack component {wrapper_id!r}")
        label_en = clean_label(wrapper.get("label", ""))
        label_ms = clean_label(translate_label(wrapper.get("label", ""), MAP_ROUTING_STACK_MS))
        component = {
            "componentKey": component_key,
            "id": node_ids[0],
            "cellIds": [wrapper_id],
            "relationCellIds": [],
            "nodeIds": list(node_ids),
            "tableName": None,
            "uiHotspots": list(HOTSPOTS.get(node_ids[0], [])),
            "matchTexts": [label_en],
            "label": label_ms,
            "labelEn": label_en,
        }
        labels = element_label_modes(wrapper, MAP_ROUTING_STACK_MS)
        if labels:
            component["labels"] = labels
        components.append(component)
    return components, []


def report_components(diagram_id: str) -> list[dict]:
    result = []
    for index, (node_id, labels) in enumerate(REPORT_COMPONENTS.get(diagram_id, [])):
        result.append({
            "componentKey": f"report:{diagram_id}:{index}",
            "id": node_id,
            "cellIds": [],
            "relationCellIds": [],
            "nodeIds": [node_id],
            "tableName": None,
            "uiHotspots": HOTSPOTS.get(node_id, []),
            "matchTexts": labels,
            "label": labels[0],
        })
    return result


def main() -> None:
    if not DRAWIO.exists():
        raise FileNotFoundError(f"Draw.io Desktop not found: {DRAWIO}")
    apply_all(ROOT)
    annotated = apply_all_bilingual_metadata(ROOT)
    if annotated:
        print(f"Updated {annotated} bilingual editor labels")
    assets = {}
    output_dir = ROOT / "assets" / "diagrams"
    output_dir.mkdir(parents=True, exist_ok=True)
    reuse_exports = os.environ.get("PETAKERJA_REUSE_DIAGRAM_EXPORTS") == "1"
    DOMAIN_EDITOR_ASSET.parent.mkdir(parents=True, exist_ok=True)
    if not DOMAIN_EDITOR_ASSET.exists():
        shutil.copy2(DOMAIN_SOURCE, DOMAIN_EDITOR_ASSET)
    with tempfile.TemporaryDirectory(prefix="petakerja-diagrams-") as temp:
        temp_dir = Path(temp)
        for diagram_id, (source, page, filename) in DRAWIO_EXPORTS.items():
            existing_export = output_dir / filename
            exported = existing_export if reuse_exports and existing_export.exists() else temp_dir / filename
            if exported != existing_export:
                export_drawio(source, page, exported)
            exported_svg = slim_svg(
                exported.read_text(encoding="utf-8"),
                preserve_embedded_images=diagram_id in {"daily-index-workflow", "live-search-workflow", "architecture-visual-stack", *MAP_ROUTING_WORKFLOW_IDS},
            )
            if diagram_id in V2_GEOROUTING_IDS or diagram_id in EMBEDDED_BILINGUAL_IDS:
                en = exported_svg
                ms = translate_svg(en, v2_georouting_translations(source))
            elif diagram_id in ("user-google-sign-in-flowchart", "user-google-sign-in-flowchart-original"):
                en = exported_svg
                ms = translate_svg(en, GOOGLE_SIGN_IN_FLOWCHART_MS)
            elif diagram_id in USER_FLOWCHART_SPECS:
                en = exported_svg
                ms = translate_svg(en, USER_FLOWCHART_SPECS[diagram_id][1])
            elif diagram_id in ADMIN_FLOWCHART_SPECS:
                en = exported_svg
                ms = translate_svg(en, ADMIN_FLOWCHART_SPECS[diagram_id][1])
            elif diagram_id in DESIGN_SPECS:
                en = exported_svg
                ms = translate_svg(en, DESIGN_SPECS[diagram_id][1])
            elif diagram_id == "map-routing-responsibility-stack":
                en = exported_svg
                ms = translate_svg(en, MAP_ROUTING_STACK_MS)
            elif diagram_id in (
                "google-oauth-sequence", "sequence", "admin-manage-users-sequence",
                "admin-manage-ai-configuration-sequence", "admin-access-dashboard-sequence",
                "admin-monitor-activity-sequence", "admin-sign-out-sequence",
                "user-explore-3d-map-sequence", "user-sign-out-sequence",
            ):
                en = exported_svg
                if diagram_id == "google-oauth-sequence":
                    replacements = sequence_source_translations(GOOGLE_OAUTH_SEQUENCE_SOURCE, GOOGLE_OAUTH_SEQUENCE_MS)
                elif diagram_id == "sequence":
                    replacements = sequence_source_translations(JOB_SEARCH_SEQUENCE_SOURCE, JOB_SEARCH_SEQUENCE_MS)
                elif diagram_id == "admin-manage-users-sequence":
                    replacements = sequence_source_translations(ADMIN_MANAGE_USERS_SEQUENCE_SOURCE, ADMIN_MANAGE_USERS_SEQUENCE_MS)
                elif diagram_id == "admin-manage-ai-configuration-sequence":
                    replacements = sequence_source_translations(ADMIN_MANAGE_AI_CONFIGURATION_SEQUENCE_SOURCE, ADMIN_MANAGE_AI_CONFIGURATION_SEQUENCE_MS)
                elif diagram_id == "admin-access-dashboard-sequence":
                    replacements = sequence_source_translations(ADMIN_ACCESS_DASHBOARD_SEQUENCE_SOURCE, ADMIN_ACCESS_DASHBOARD_SEQUENCE_MS)
                elif diagram_id == "admin-monitor-activity-sequence":
                    replacements = sequence_source_translations(ADMIN_MONITOR_ACTIVITY_SEQUENCE_SOURCE, ADMIN_MONITOR_ACTIVITY_SEQUENCE_MS)
                elif diagram_id == "admin-sign-out-sequence":
                    replacements = sequence_source_translations(ADMIN_SIGN_OUT_SEQUENCE_SOURCE, SIGN_OUT_SEQUENCE_MS)
                elif diagram_id == "user-explore-3d-map-sequence":
                    replacements = sequence_source_translations(USER_EXPLORE_3D_MAP_SEQUENCE_SOURCE, USER_EXPLORE_3D_MAP_SEQUENCE_MS)
                else:
                    replacements = sequence_source_translations(USER_SIGN_OUT_SEQUENCE_SOURCE, SIGN_OUT_SEQUENCE_MS)
                ms = translate_svg(en, replacements)
            else:
                ms = exported_svg
                replacements = USECASE_EN if diagram_id == "usecase" else CLASS_EN
                en = translate_svg(ms, replacements)
            output_path = output_dir / filename
            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.write_text(exported_svg, encoding="utf-8")
            if diagram_id in V2_GEOROUTING_IDS:
                components, connections = v2_georouting_components(source)
            elif diagram_id in DESIGN_SPECS:
                components, connections = design_components(diagram_id)
            elif diagram_id in EMBEDDED_BILINGUAL_IDS:
                components, connections = v2_georouting_components(source)
            elif diagram_id == "usecase":
                components, connections = usecase_components()
            elif diagram_id == "sequence":
                components, connections = job_search_sequence_components()
            elif diagram_id == "google-oauth-sequence":
                components, connections = google_oauth_sequence_components()
            elif diagram_id == "user-google-sign-in-flowchart":
                components, connections = google_sign_in_flowchart_components(GOOGLE_SIGN_IN_FLOWCHART_SOURCE)
            elif diagram_id == "user-google-sign-in-flowchart-original":
                components, connections = google_sign_in_flowchart_components(GOOGLE_SIGN_IN_FLOWCHART_ORIGINAL_SOURCE)
            elif diagram_id in USER_FLOWCHART_SPECS:
                components, connections = user_flowchart_components(diagram_id)
            elif diagram_id in ADMIN_FLOWCHART_SPECS:
                components, connections = admin_flowchart_components(diagram_id)
            elif diagram_id == "map-routing-responsibility-stack":
                components, connections = map_routing_stack_components()
            elif diagram_id == "admin-manage-users-sequence":
                components, connections = admin_manage_users_sequence_components()
            elif diagram_id == "admin-manage-ai-configuration-sequence":
                components, connections = admin_manage_ai_configuration_sequence_components()
            elif diagram_id == "admin-access-dashboard-sequence":
                components, connections = admin_access_dashboard_sequence_components()
            elif diagram_id == "admin-monitor-activity-sequence":
                components, connections = admin_monitor_activity_sequence_components()
            elif diagram_id == "admin-sign-out-sequence":
                components, connections = sign_out_sequence_components(
                    "admin-sign-out-sequence", ADMIN_SIGN_OUT_SEQUENCE_SOURCE, True
                )
            elif diagram_id == "user-explore-3d-map-sequence":
                components, connections = user_explore_3d_map_sequence_components()
            elif diagram_id == "user-sign-out-sequence":
                components, connections = sign_out_sequence_components(
                    "user-sign-out-sequence", USER_SIGN_OUT_SEQUENCE_SOURCE, False
                )
            elif diagram_id == "supabase":
                components, connections = class_components(source, page, schema=True)
            else:
                components, connections = class_components(
                    source, page, stable_keys=(diagram_id in ("domain", "domain-original"))
                )
            translation_spec = bilingual_translation_spec(diagram_id, source)
            label_elements = drawio_label_elements(source, translation_spec[1] if translation_spec else None)
            supports_sequence_labels = diagram_id in V2_GEOROUTING_SEQUENCE_IDS or diagram_id in (
                "google-oauth-sequence", "sequence", "admin-manage-users-sequence",
                "admin-manage-ai-configuration-sequence", "admin-access-dashboard-sequence",
                "admin-monitor-activity-sequence", "admin-sign-out-sequence",
                "user-explore-3d-map-sequence", "user-sign-out-sequence",
            )
            assets[diagram_id] = {
                "svg": {"ms": ms, "en": en},
                "components": components,
                "connections": connections,
                "labelElements": label_elements,
                "labelModes": ["simple", "code"] if label_elements or supports_sequence_labels else [],
                "supportsLabelModes": bool(label_elements) or supports_sequence_labels,
                "supportsSequenceLabels": supports_sequence_labels,
            }

    for diagram_id, filename in REPORT_EXPORTS.items():
        source = REPORT_DIAGRAMS / filename
        if not source.exists():
            source = ROOT / "assets" / "diagrams" / filename
        ms = slim_svg(source.read_text(encoding="utf-8"))
        en = translate_svg(ms, REPORT_EN)
        (output_dir / filename).write_text(ms, encoding="utf-8")
        assets[diagram_id] = {
            "svg": {"ms": ms, "en": en},
            "components": report_components(diagram_id),
            "connections": [],
        }

    payload = json.dumps(assets, ensure_ascii=False, separators=(",", ":")).replace("</script", "<\\/script")
    OUTPUT.write_text(
        "/* Generated by scripts/build-diagram-assets.py. Do not edit manually. */\n"
        f"window.PETAKERJA_DIAGRAM_ASSETS={payload};\n",
        encoding="utf-8",
    )
    print(f"Wrote {OUTPUT} ({OUTPUT.stat().st_size:,} bytes)")
    print(f"Supabase components: {len(assets['supabase']['components'])}")
    print(f"Google OAuth sequence components: {len(assets['google-oauth-sequence']['components'])}")
    print(f"Google OAuth sequence connections: {len(assets['google-oauth-sequence']['connections'])}")
    print(f"Job Search sequence components: {len(assets['sequence']['components'])}")
    print(f"Job Search sequence connections: {len(assets['sequence']['connections'])}")
    print(f"Google Sign-In flow-chart components: {len(assets['user-google-sign-in-flowchart']['components'])}")
    print(f"Google Sign-In flow-chart connections: {len(assets['user-google-sign-in-flowchart']['connections'])}")
    print(f"Manage Users flow-chart components: {len(assets['admin-manage-users-flowchart']['components'])}")
    print(f"Manage Users flow-chart connections: {len(assets['admin-manage-users-flowchart']['connections'])}")
    print(f"Manage Users sequence components: {len(assets['admin-manage-users-sequence']['components'])}")
    print(f"Manage Users sequence connections: {len(assets['admin-manage-users-sequence']['connections'])}")
    print(f"Manage AI configuration sequence components: {len(assets['admin-manage-ai-configuration-sequence']['components'])}")
    print(f"Manage AI configuration sequence connections: {len(assets['admin-manage-ai-configuration-sequence']['connections'])}")
    for diagram_id, label in (
        ("admin-access-dashboard-sequence", "Access Dashboard"),
        ("admin-monitor-activity-sequence", "Monitor Activity"),
        ("admin-sign-out-sequence", "Administrator Sign Out"),
        ("user-explore-3d-map-sequence", "Explore 3D Map"),
        ("user-sign-out-sequence", "User Sign Out"),
    ):
        print(f"{label} sequence components: {len(assets[diagram_id]['components'])}")
        print(f"{label} sequence connections: {len(assets[diagram_id]['connections'])}")


if __name__ == "__main__":
    main()
