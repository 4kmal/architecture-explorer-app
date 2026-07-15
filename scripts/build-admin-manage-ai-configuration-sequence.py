#!/usr/bin/env python3
"""Build the PetaKerja Administrator Manage AI Configuration sequence.

The supplied TTTE1113 sequence template remains unchanged and is read only for
its actor, lifeline, activation, frame, call and return styles. The generated
source uses plain-language English labels while retaining bilingual Simple and
Code labels as non-visual metadata for Architecture Explorer.
"""

from __future__ import annotations

import re
import xml.etree.ElementTree as ET
from pathlib import Path

from sequence_label_catalog import apply_label_modes_to_file
from paths import DIAGRAMS, TEMPLATES

TEMPLATE = TEMPLATES / "Sequence Diagram Template.drawio"
OUTPUT = DIAGRAMS / "Sequence Diagram PetaKerja - Manage AI Chatbot Configuration.drawio"
EXPLORER = Path(__file__).resolve().parents[1]
EDITOR_OUTPUT = EXPLORER / "assets" / "editor" / "sequence-admin-manage-ai-configuration.drawio"

PAGE_ID = "petakerja_admin_manage_ai_configuration_sequence"
KEY_PREFIX = "admin-manage-ai-configuration-sequence"
ROOT_ID = "admin-manage-ai-configuration-sequence-root"
LAYER_ID = "admin-manage-ai-configuration-sequence-layer"
ACTIVATION_Y = 130.0
ACTIVATION_HEIGHT = 965.0


def template_style(predicate) -> str:
    root = ET.parse(TEMPLATE).getroot()
    for cell in root.findall(".//mxCell"):
        style = cell.get("style", "")
        if predicate(cell, style):
            return style
    raise RuntimeError("Required style was not found in Sequence Diagram Template.drawio")


ACTOR_STYLE = template_style(lambda _cell, style: "shape=umlActor" in style)
LIFELINE_STYLE = template_style(lambda _cell, style: "shape=umlLifeline" in style)
ACTIVATION_STYLE = template_style(
    lambda cell, style: cell.get("vertex") == "1" and "targetShapes=umlLifeline" in style
)
FRAME_STYLE = template_style(lambda _cell, style: "shape=umlFrame" in style)
TEMPLATE_CALL_STYLE = template_style(
    lambda cell, style: cell.get("edge") == "1" and "startArrow=classic" in style
)
TEMPLATE_RETURN_STYLE = template_style(
    lambda cell, style: cell.get("edge") == "1" and "endArrow=open" in style and "dashed=1" in style
)


def strip_style_properties(style: str, names: tuple[str, ...]) -> str:
    for name in names:
        style = re.sub(rf"(?:^|;){name}=[^;]*;?", ";", style)
    return style.strip(";")


CALL_STYLE = strip_style_properties(
    TEMPLATE_CALL_STYLE,
    ("startArrow", "startFill", "endArrow", "endFill", "entryX", "entryY", "entryDx", "entryDy", "exitX", "exitY", "exitDx", "exitDy"),
) + ";endArrow=classic;endFill=1;strokeWidth=1;fontSize=8;"
RETURN_STYLE = strip_style_properties(
    TEMPLATE_RETURN_STYLE,
    ("entryX", "entryY", "entryDx", "entryDy", "exitX", "exitY", "exitDx", "exitDy"),
) + ";strokeWidth=1;fontSize=8;"
TEXT_STYLE = "text;html=1;whiteSpace=wrap;strokeColor=none;fillColor=none;align=center;verticalAlign=middle;rounded=0;"


def add_geometry(cell: ET.Element, *, x: float | None = None, y: float | None = None,
                 width: float | None = None, height: float | None = None,
                 relative: bool = False) -> ET.Element:
    attrs = {"as": "geometry"}
    if relative:
        attrs["relative"] = "1"
    geometry = ET.SubElement(cell, "mxGeometry", attrs)
    for name, value in (("x", x), ("y", y), ("width", width), ("height", height)):
        if value is not None:
            geometry.set(name, f"{value:g}")
    return geometry


def add_object(root: ET.Element, *, key: str | None, cell_id: str, label: str, style: str,
               vertex: bool = False, edge: bool = False, source: str | None = None,
               target: str | None = None, geometry: dict | None = None,
               metadata: dict[str, str] | None = None) -> ET.Element:
    wrapper_attrs = {"label": label, "id": cell_id}
    if key:
        wrapper_attrs["petakerjaKey"] = key
    if metadata:
        wrapper_attrs.update(metadata)
    wrapper = ET.SubElement(root, "object", wrapper_attrs)
    attrs = {"parent": LAYER_ID, "style": style}
    if vertex:
        attrs["vertex"] = "1"
    if edge:
        attrs["edge"] = "1"
    if source:
        attrs["source"] = source
    if target:
        attrs["target"] = target
    cell = ET.SubElement(wrapper, "mxCell", attrs)
    add_geometry(cell, **(geometry or {}))
    return cell


def ratio(y: float) -> float:
    return max(0.0, min(1.0, (y - ACTIVATION_Y) / ACTIVATION_HEIGHT))


def message_style(base: str, y: float, source: str, target: str) -> str:
    left_to_right = PARTICIPANT_CENTRES[target] > PARTICIPANT_CENTRES[source]
    exit_x, entry_x = (1, 0) if left_to_right else (0, 1)
    return base + (
        f"exitX={exit_x};exitY={ratio(y):.6f};exitPerimeter=0;"
        f"entryX={entry_x};entryY={ratio(y):.6f};entryPerimeter=0;"
        "labelBackgroundColor=none;"
    )


def add_message(root: ET.Element, message: dict, activation_ids: dict[str, str]) -> None:
    index = message["index"]
    source = activation_ids[message["source"]]
    target = activation_ids[message["target"]]
    add_object(
        root,
        key=f"{KEY_PREFIX}/message-{index:02d}",
        cell_id=f"admin-manage-ai-configuration-message-{index:02d}",
        label=message["simple_en"],
        style=message_style(RETURN_STYLE if message["returned"] else CALL_STYLE, message["y"], source, target),
        edge=True,
        source=source,
        target=target,
        geometry={"relative": True},
        metadata={
            "simpleLabelEn": message["simple_en"],
            "simpleLabelMs": message["simple_ms"],
            "codeLabelEn": message["code_en"],
            "codeLabelMs": message["code_ms"],
        },
    )


def add_divider(root: ET.Element, key: str, y: float, x1: float, x2: float) -> None:
    wrapper = ET.SubElement(root, "object", {"label": "", "petakerjaKey": key, "id": key.replace("/", "-")})
    cell = ET.SubElement(wrapper, "mxCell", {
        "edge": "1", "parent": LAYER_ID,
        "style": "endArrow=none;dashed=1;html=1;rounded=0;strokeWidth=1;",
    })
    geometry = add_geometry(cell, relative=True)
    ET.SubElement(geometry, "mxPoint", {"x": f"{x1:g}", "y": f"{y:g}", "as": "sourcePoint"})
    ET.SubElement(geometry, "mxPoint", {"x": f"{x2:g}", "y": f"{y:g}", "as": "targetPoint"})


def add_operand(root: ET.Element, key: str, label: str, x: float, y: float,
                width: float = 300, font_size: int = 8) -> None:
    add_object(
        root, key=key, cell_id=key.replace("/", "-"), label=label,
        style=TEXT_STYLE + f"align=left;fontStyle=2;fontSize={font_size};", vertex=True,
        geometry={"x": x, "y": y, "width": width, "height": 16},
    )


PARTICIPANTS = [
    ("administrator", "Administrator", 75, "pentadbir"),
    ("ui", "PetaKerja Admin UI", 275, "admin-ui"),
    ("manager", "<font style=\"font-size: 9px;\">AdminDashboard<br>Manager</font>", 475, "admin-manager"),
    ("client", "Admin API Client<div><font style=\"font-size: 8px;\">aiProviderApi.ts</font></div>", 675, "admin-api-client"),
    ("api", "Admin AI Providers API<div><font style=\"font-size: 8px;\">/api/admin/ai/providers*</font></div>", 875, "admin-ai-providers-api"),
    ("session", "Better Auth Session", 1060, "better-auth"),
    ("database", "Supabase / PostgreSQL<div><font style=\"font-size: 7px;\">users · credentials · audit logs</font></div>", 1260, "supabase-db"),
    ("external", "External AI Provider APIs", 1480, "ai-provider"),
]
PARTICIPANT_CENTRES = {
    f"admin-manage-ai-configuration-activation-{slug}": centre
    for slug, _label, centre, _node in PARTICIPANTS
}


def msg(index: int, simple_en: str, simple_ms: str, code_en: str, code_ms: str,
        source: str, target: str, y: float, returned: bool = False) -> dict:
    return {
        "index": index, "simple_en": simple_en, "simple_ms": simple_ms,
        "code_en": code_en, "code_ms": code_ms,
        "source": source, "target": target, "y": y, "returned": returned,
    }


MESSAGES = [
    msg(1, "Select the Admin Dashboard", "Pilih Papan Pemuka Pentadbir", '[data-dropdown-action="admin"]', '[data-dropdown-action="admin"]', "administrator", "ui", 145),
    msg(2, "Open the administrator dashboard", "Buka papan pemuka pentadbir", "AdminDashboardManager.open(true)", "AdminDashboardManager.open(true)", "ui", "manager", 165),
    msg(3, "Request provider configuration", "Minta konfigurasi penyedia", "loadAdminData(); listAdminAIProviders()", "loadAdminData(); listAdminAIProviders()", "manager", "client", 185),
    msg(4, "Send the provider-list request", "Hantar permintaan senarai penyedia", 'authenticatedFetch("/api/admin/ai/providers")', 'authenticatedFetch("/api/admin/ai/providers")', "client", "api", 205),
    msg(5, "Verify the active sign-in session", "Sahkan sesi log masuk aktif", "requireAuth(); getAppSessionFromHeaders()", "requireAuth(); getAppSessionFromHeaders()", "api", "session", 225),
    msg(6, "Return the verified user", "Pulangkan pengguna yang disahkan", "req.user = session.user", "req.user = session.user", "session", "api", 245, True),
    msg(7, "Check the administrator role", "Semak peranan pentadbir", "requireAdmin(); SELECT role FROM public.users", "requireAdmin(); SELECT role FROM public.users", "api", "database", 275),
    msg(8, "Return the assigned role", "Pulangkan peranan yang ditetapkan", "{ role: admin | owner }", "{ role: admin | owner }", "database", "api", 295, True),
    msg(9, "Retrieve platform provider configuration", "Dapatkan konfigurasi penyedia platform", "SELECT platform credentials FROM ai_provider_credentials", "SELECT platform credentials FROM ai_provider_credentials", "api", "database", 315),
    msg(10, "Return the saved provider configuration", "Pulangkan konfigurasi penyedia yang disimpan", "platform credentials", "platform credentials", "database", "api", 335, True),
    msg(11, "Prepare the provider status list", "Sediakan senarai status penyedia", "AI_PROVIDER_REGISTRY.map(provider => mergeCredential(provider))", "AI_PROVIDER_REGISTRY.map(provider => mergeCredential(provider))", "api", "client", 355, True),
    msg(12, "Return provider information", "Pulangkan maklumat penyedia", "AdminProvidersResponse { providers }", "AdminProvidersResponse { providers }", "client", "manager", 375, True),
    msg(13, "Provide configuration to the dashboard", "Berikan konfigurasi kepada papan pemuka", "state.adminDashboard.providers = providers.providers", "state.adminDashboard.providers = providers.providers", "manager", "ui", 395, True),
    msg(14, "Select the AI Providers section", "Pilih bahagian Penyedia AI", '[data-admin-action="tab"][data-tab="providers"]', '[data-admin-action="tab"][data-tab="providers"]', "administrator", "ui", 415),
    msg(15, "Open the AI Providers section", "Buka bahagian Penyedia AI", 'activeTab = "providers"; renderProviders(user)', 'activeTab = "providers"; renderProviders(user)', "ui", "manager", 435),
    msg(16, "Display providers, keys and model status", "Paparkan penyedia, kunci dan status model", ".admin-provider-table", ".admin-provider-table", "ui", "administrator", 455, True),
    msg(17, "Request sign-in", "Minta pengguna log masuk", "HTTP 401; requireAuth()", "HTTP 401; requireAuth()", "api", "ui", 486, True),
    msg(18, "Display the sign-in prompt", "Paparkan prompt log masuk", "AuthModalManager.openAuthPrompt()", "AuthModalManager.openAuthPrompt()", "ui", "administrator", 502, True),
    msg(19, "Return administrator access required", "Pulangkan keperluan akses pentadbir", "HTTP 403; requireAdmin()", "HTTP 403; requireAdmin()", "api", "ui", 531, True),
    msg(20, "Display administrator access required", "Paparkan keperluan akses pentadbir", "renderError(ADMIN_REQUIRED)", "renderError(ADMIN_REQUIRED)", "ui", "administrator", 547, True),
    msg(21, "Select Save platform key", "Pilih Simpan kunci platform", '[data-admin-action="platform-key"]', '[data-admin-action="platform-key"]', "administrator", "ui", 641),
    msg(22, "Open the platform-key form", "Buka borang kunci platform", 'openPlatformKeyModal(provider)', 'openPlatformKeyModal(provider)', "ui", "manager", 658),
    msg(23, "Enter and submit the platform key", "Masukkan dan hantar kunci platform", "#admin-platform-key-form submit", "#admin-platform-key-form submit", "administrator", "ui", 675),
    msg(24, "Process the platform key", "Proses kunci platform", "form submit handler", "form submit handler", "ui", "manager", 692),
    msg(25, "Save the shared platform key", "Simpan kunci platform dikongsi", "saveAdminPlatformKey(provider.id, apiKey)", "saveAdminPlatformKey(provider.id, apiKey)", "manager", "client", 709),
    msg(26, "Send the key-save request", "Hantar permintaan simpan kunci", "POST /api/admin/ai/providers/:providerId/platform-key", "POST /api/admin/ai/providers/:providerId/platform-key", "client", "api", 726),
    msg(27, "Verify ownership, encrypt and store the key", "Sahkan pemilik, enkripsi dan simpan kunci", 'req.adminRole === "owner"; encryptSecret(apiKey); upsert ai_provider_credentials; insert ai_admin_audit_logs', 'req.adminRole === "owner"; encryptSecret(apiKey); upsert ai_provider_credentials; insert ai_admin_audit_logs', "api", "database", 743),
    msg(28, "Confirm the credential and audit record", "Sahkan kelayakan dan rekod audit", "credential + platform_key_saved audit stored", "credential + platform_key_saved audit stored", "database", "api", 760, True),
    msg(29, "Return key saved", "Pulangkan kunci yang disimpan", "{ ok: true }", "{ ok: true }", "api", "client", 775, True),
    msg(30, "Provide the save success", "Berikan kejayaan simpanan", "saveAdminPlatformKey() resolved", "saveAdminPlatformKey() resolved", "client", "manager", 790, True),
    msg(31, "Return the validation or request error", "Pulangkan ralat pengesahan atau permintaan", "HTTP 400 | 403 | 500", "HTTP 400 | 403 | 500", "api", "client", 815, True),
    msg(32, "Provide the save error", "Berikan ralat simpanan", "saveAdminPlatformKey() rejected", "saveAdminPlatformKey() rejected", "client", "manager", 830, True),
    msg(33, "Refresh the displayed provider information", "Segarkan maklumat penyedia yang dipaparkan", "loadAdminData(); render(statusMessage)", "loadAdminData(); render(statusMessage)", "manager", "ui", 844, True),
    msg(34, "Display the save outcome", "Paparkan hasil simpanan", "Platform key saved. | setFormStatus(error)", "Platform key saved. | setFormStatus(error)", "ui", "administrator", 858, True),
    msg(35, "Select Refresh all models", "Pilih Segarkan semua model", '[data-admin-action="refresh-models"]', '[data-admin-action="refresh-models"]', "administrator", "ui", 870),
    msg(36, "Start the model refresh", "Mulakan penyegaran model", "handleRefreshAllModels()", "handleRefreshAllModels()", "ui", "manager", 884),
    msg(37, "Request all provider model lists", "Minta semua senarai model penyedia", "adminRefreshAllModels()", "adminRefreshAllModels()", "manager", "client", 898),
    msg(38, "Send the refresh request", "Hantar permintaan penyegaran", "POST /api/admin/ai/providers/refresh-models", "POST /api/admin/ai/providers/refresh-models", "client", "api", 912),
    msg(39, "Verify ownership and read provider credentials", "Sahkan pemilik dan baca kelayakan penyedia", 'req.adminRole === "owner"; SELECT platform credentials', 'req.adminRole === "owner"; SELECT platform credentials', "api", "database", 926),
    msg(40, "Return the provider credentials", "Pulangkan kelayakan penyedia", "encrypted_api_key + custom_headers", "encrypted_api_key + custom_headers", "database", "api", 940, True),
    msg(41, "Request a provider model list", "Minta senarai model penyedia", "fetchOpenAIModels(getProviderFetchConfig(provider.id))", "fetchOpenAIModels(getProviderFetchConfig(provider.id))", "api", "external", 954),
    msg(42, "Return the model list", "Pulangkan senarai model", "models[]", "models[]", "external", "api", 968, True),
    msg(43, "Store refreshed model information", "Simpan maklumat model yang disegarkan", "upsert fetched_models/models_fetched_at; ModelCache.invalidate(...)", "upsert fetched_models/models_fetched_at; ModelCache.invalidate(...)", "api", "database", 982),
    msg(44, "Return a provider error", "Pulangkan ralat penyedia", "provider API error", "ralat API penyedia", "external", "api", 996, True),
    msg(45, "Record the provider fetch error", "Rekod ralat pengambilan penyedia", "UPDATE ai_provider_credentials SET fetch_error = errMsg", "UPDATE ai_provider_credentials SET fetch_error = errMsg", "api", "database", 1010),
    msg(46, "Return the refresh results", "Pulangkan hasil penyegaran", "AdminRefreshModelsResult { results }", "AdminRefreshModelsResult { results }", "api", "client", 1023, True),
    msg(47, "Provide the refresh summary", "Berikan ringkasan penyegaran", "succeeded + failed counts", "bilangan berjaya + gagal", "client", "manager", 1035, True),
    msg(48, "Update the provider table", "Kemas kini jadual penyedia", "loadAdminData(); render(msg)", "loadAdminData(); render(msg)", "manager", "ui", 1047, True),
    msg(49, "Display successful refresh", "Paparkan penyegaran berjaya", "all results.ok === true", "all results.ok === true", "ui", "administrator", 1059, True),
    msg(50, "Display provider failures", "Paparkan kegagalan penyedia", "some results.ok === false", "some results.ok === false", "ui", "administrator", 1073, True),
    msg(51, "Display the refresh request error", "Paparkan ralat permintaan penyegaran", "adminRefreshAllModels() catch", "adminRefreshAllModels() catch", "ui", "administrator", 1087, True),
]


def build() -> ET.ElementTree:
    mxfile = ET.Element("mxfile", {"host": "Electron", "agent": "PetaKerja Architecture Explorer", "version": "27.0.2"})
    diagram = ET.SubElement(mxfile, "diagram", {"name": "Manage AI Chatbot Configuration", "id": PAGE_ID})
    model = ET.SubElement(diagram, "mxGraphModel", {
        "dx": "1600", "dy": "1100", "grid": "1", "gridSize": "10", "guides": "1",
        "tooltips": "1", "connect": "1", "arrows": "1", "fold": "1", "page": "1",
        "pageScale": "1", "pageWidth": "1600", "pageHeight": "1100", "math": "0", "shadow": "0",
    })
    root = ET.SubElement(model, "root")
    ET.SubElement(root, "mxCell", {"id": ROOT_ID})
    ET.SubElement(root, "mxCell", {"id": LAYER_ID, "parent": ROOT_ID})
    background = ET.SubElement(root, "mxCell", {
        "id": "admin-manage-ai-configuration-background", "parent": LAYER_ID, "vertex": "1",
        "style": "rounded=0;whiteSpace=wrap;html=1;fillColor=#ffffff;strokeColor=none;locked=1;pointerEvents=0;",
    })
    add_geometry(background, x=0, y=0, width=1600, height=1100)

    add_object(root, key=f"{KEY_PREFIX}/title", cell_id="admin-manage-ai-configuration-title",
               label="PetaKerja Administrator Manage AI Chatbot Configuration Sequence",
               style=TEXT_STYLE + "fontSize=18;fontStyle=1;", vertex=True,
               geometry={"x": 390, "y": 20, "width": 820, "height": 30})

    activation_ids: dict[str, str] = {}
    for slug, label, centre, _node in PARTICIPANTS:
        participant_key = f"{KEY_PREFIX}/participant-{slug}"
        if slug == "administrator":
            add_object(root, key=participant_key, cell_id="admin-manage-ai-configuration-participant-administrator",
                       label="Administrator", style=ACTOR_STYLE, vertex=True,
                       geometry={"x": centre - 10, "y": 72, "width": 20, "height": 40})
        else:
            add_object(root, key=participant_key, cell_id=f"admin-manage-ai-configuration-participant-{slug}",
                       label=label, style=LIFELINE_STYLE, vertex=True,
                       geometry={"x": centre - 50, "y": 70, "width": 100, "height": 60})
        activation_id = f"admin-manage-ai-configuration-activation-{slug}"
        activation_ids[slug] = activation_id
        add_object(root, key=participant_key + "-activation", cell_id=activation_id, label="",
                   style=ACTIVATION_STYLE, vertex=True,
                   geometry={"x": centre - 5, "y": ACTIVATION_Y, "width": 10, "height": ACTIVATION_HEIGHT})

    add_object(root, key=f"{KEY_PREFIX}/fragment-access", cell_id="admin-manage-ai-configuration-fragment-access",
               label="alt", style=FRAME_STYLE, vertex=True,
               geometry={"x": 220, "y": 255, "width": 1320, "height": 310})
    add_operand(root, f"{KEY_PREFIX}/access-authorized", "[administrator or owner]", 300, 260)
    add_divider(root, f"{KEY_PREFIX}/divider-no-session", 470, 220, 1540)
    add_operand(root, f"{KEY_PREFIX}/access-no-session", "[no active session]", 300, 472)
    add_divider(root, f"{KEY_PREFIX}/divider-role-denied", 515, 220, 1540)
    add_operand(root, f"{KEY_PREFIX}/access-role-denied", "[role not allowed]", 300, 517)

    add_object(root, key=f"{KEY_PREFIX}/fragment-capability", cell_id="admin-manage-ai-configuration-fragment-capability",
               label="alt", style=FRAME_STYLE, vertex=True,
               geometry={"x": 40, "y": 570, "width": 1500, "height": 525})
    add_operand(root, f"{KEY_PREFIX}/capability-administrator", "[administrator]", 120, 574)
    add_object(root, key=f"{KEY_PREFIX}/administrator-read-only",
               cell_id="admin-manage-ai-configuration-administrator-read-only",
               label="View only — owner role required for shared keys and model refresh.",
               style=TEXT_STYLE + "align=left;fontSize=8;fontStyle=2;", vertex=True,
               geometry={"x": 255, "y": 578, "width": 520, "height": 18})
    add_divider(root, f"{KEY_PREFIX}/divider-owner", 610, 40, 1540)
    add_operand(root, f"{KEY_PREFIX}/capability-owner", "[owner]", 120, 612)

    add_object(root, key=f"{KEY_PREFIX}/fragment-save-key", cell_id="admin-manage-ai-configuration-fragment-save-key",
               label="opt", style=FRAME_STYLE, vertex=True,
               geometry={"x": 220, "y": 625, "width": 1320, "height": 240})
    add_operand(root, f"{KEY_PREFIX}/save-key", "[save platform key]", 300, 628)
    add_object(root, key=f"{KEY_PREFIX}/fragment-save-result", cell_id="admin-manage-ai-configuration-fragment-save-result",
               label="alt", style=FRAME_STYLE, vertex=True,
               geometry={"x": 450, "y": 764, "width": 1090, "height": 73})
    add_operand(root, f"{KEY_PREFIX}/save-success", "[key saved]", 520, 766, 180, 8)
    add_divider(root, f"{KEY_PREFIX}/divider-save-error", 800, 450, 1540)
    add_operand(root, f"{KEY_PREFIX}/save-error", "[invalid provider, empty key or request failed]", 520, 802, 330, 8)

    add_object(root, key=f"{KEY_PREFIX}/fragment-refresh-models", cell_id="admin-manage-ai-configuration-fragment-refresh-models",
               label="opt", style=FRAME_STYLE, vertex=True,
               geometry={"x": 220, "y": 864, "width": 1320, "height": 231})
    add_operand(root, f"{KEY_PREFIX}/refresh-models", "[refresh model lists]", 300, 866)
    add_object(root, key=f"{KEY_PREFIX}/fragment-provider-loop", cell_id="admin-manage-ai-configuration-fragment-provider-loop",
               label="loop", style=FRAME_STYLE, vertex=True,
               geometry={"x": 820, "y": 944, "width": 700, "height": 80})
    add_operand(root, f"{KEY_PREFIX}/provider-loop", "[each provider supporting model fetching]", 900, 946, 360)
    add_object(root, key=f"{KEY_PREFIX}/fragment-provider-result", cell_id="admin-manage-ai-configuration-fragment-provider-result",
               label="alt", style=FRAME_STYLE, vertex=True,
               geometry={"x": 835, "y": 948, "width": 680, "height": 74})
    add_operand(root, f"{KEY_PREFIX}/provider-success", "[refresh succeeded]", 910, 950, 220, 7)
    add_divider(root, f"{KEY_PREFIX}/divider-provider-failure", 989, 835, 1515)
    add_operand(root, f"{KEY_PREFIX}/provider-failure", "[refresh failed]", 910, 991, 220, 7)
    add_object(root, key=f"{KEY_PREFIX}/fragment-refresh-summary", cell_id="admin-manage-ai-configuration-fragment-refresh-summary",
               label="alt", style=FRAME_STYLE, vertex=True,
               geometry={"x": 220, "y": 1050, "width": 1320, "height": 45})
    add_operand(root, f"{KEY_PREFIX}/refresh-complete", "[complete success]", 300, 1051, 190, 6)
    add_divider(root, f"{KEY_PREFIX}/divider-refresh-partial", 1066, 220, 1540)
    add_operand(root, f"{KEY_PREFIX}/refresh-partial", "[partial provider failure]", 300, 1067, 220, 6)
    add_divider(root, f"{KEY_PREFIX}/divider-refresh-request-error", 1080, 220, 1540)
    add_operand(root, f"{KEY_PREFIX}/refresh-request-error", "[request failed]", 300, 1081, 180, 6)

    for message in MESSAGES:
        add_message(root, message, activation_ids)

    note_label = (
        "<b>Implementation note:</b> admin and owner may view providers; only owner may save shared keys or refresh models. "
        "The refresh path expects <i>custom_headers, fetched_models, models_fetched_at</i> and <i>fetch_error</i>, "
        "which are absent from the current live <i>ai_provider_credentials</i> snapshot. Individual user model preferences are outside this use case."
    )
    add_object(root, key=f"{KEY_PREFIX}/implementation-note",
               cell_id="admin-manage-ai-configuration-implementation-note",
               label=note_label, style=TEXT_STYLE + "fontSize=8;fontStyle=2;", vertex=True,
               geometry={"x": 220, "y": 52, "width": 1320, "height": 16})

    return ET.ElementTree(mxfile)


def write_outputs() -> None:
    tree = build()
    ET.indent(tree, space="  ")
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    EDITOR_OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    tree.write(OUTPUT, encoding="utf-8", xml_declaration=False)
    tree.write(EDITOR_OUTPUT, encoding="utf-8", xml_declaration=False)
    apply_label_modes_to_file(OUTPUT)
    apply_label_modes_to_file(EDITOR_OUTPUT)
    print(f"Wrote {OUTPUT}")
    print(f"Wrote {EDITOR_OUTPUT}")


if __name__ == "__main__":
    write_outputs()
