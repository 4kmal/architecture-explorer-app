#!/usr/bin/env python3
"""Build the PetaKerja administrator dashboard sequence diagrams.

The supplied TTTE1113 sequence template is used as the source of the actor,
lifeline, activation, message and fragment styles.  The generated Draw.io
sources use plain-language English labels while keeping bilingual Simple/Code
metadata on every message for the Architecture Explorer.
"""

from __future__ import annotations

import re
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from pathlib import Path

from sequence_label_catalog import apply_label_modes_to_file
from paths import DIAGRAMS, TEMPLATES

TEMPLATE = TEMPLATES / "Sequence Diagram Template.drawio"
EXPLORER = Path(__file__).resolve().parents[1]
ACTIVATION_Y = 130.0
ACTIVATION_HEIGHT = 915.0


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
    (
        "startArrow", "startFill", "endArrow", "endFill", "entryX", "entryY",
        "entryDx", "entryDy", "exitX", "exitY", "exitDx", "exitDy",
    ),
) + ";endArrow=classic;endFill=1;strokeWidth=1;fontSize=10;"
RETURN_STYLE = strip_style_properties(
    TEMPLATE_RETURN_STYLE,
    ("entryX", "entryY", "entryDx", "entryDy", "exitX", "exitY", "exitDx", "exitDy"),
) + ";strokeWidth=1;fontSize=10;"
TEXT_STYLE = (
    "text;html=1;whiteSpace=wrap;strokeColor=none;fillColor=none;"
    "align=center;verticalAlign=middle;rounded=0;"
)


@dataclass(frozen=True)
class Participant:
    slug: str
    label: str
    centre: float


@dataclass(frozen=True)
class Message:
    index: int
    simple_en: str
    simple_ms: str
    code_en: str
    code_ms: str
    source: str
    target: str
    y: float
    returned: bool = False


@dataclass(frozen=True)
class Divider:
    key: str
    y: float
    x1: float
    x2: float


@dataclass(frozen=True)
class Operand:
    key: str
    label: str
    x: float
    y: float
    width: float = 250.0


@dataclass(frozen=True)
class Fragment:
    key: str
    label: str
    x: float
    y: float
    width: float
    height: float


@dataclass(frozen=True)
class SequenceConfig:
    prefix: str
    page_id: str
    page_name: str
    title: str
    filename: str
    editor_filename: str
    participants: tuple[Participant, ...]
    messages: tuple[Message, ...]
    fragments: tuple[Fragment, ...]
    dividers: tuple[Divider, ...]
    operands: tuple[Operand, ...]
    note: str


def add_geometry(
    cell: ET.Element,
    *,
    x: float | None = None,
    y: float | None = None,
    width: float | None = None,
    height: float | None = None,
    relative: bool = False,
) -> ET.Element:
    attrs = {"as": "geometry"}
    if relative:
        attrs["relative"] = "1"
    geometry = ET.SubElement(cell, "mxGeometry", attrs)
    for name, value in (("x", x), ("y", y), ("width", width), ("height", height)):
        if value is not None:
            geometry.set(name, f"{value:g}")
    return geometry


def add_object(
    root: ET.Element,
    *,
    layer_id: str,
    key: str | None,
    cell_id: str,
    label: str,
    style: str,
    vertex: bool = False,
    edge: bool = False,
    source: str | None = None,
    target: str | None = None,
    geometry: dict | None = None,
    metadata: dict[str, str] | None = None,
) -> ET.Element:
    wrapper_attrs = {"label": label, "id": cell_id}
    if key:
        wrapper_attrs["petakerjaKey"] = key
    if metadata:
        wrapper_attrs.update(metadata)
    wrapper = ET.SubElement(root, "object", wrapper_attrs)
    attrs = {"parent": layer_id, "style": style}
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


def add_divider(root: ET.Element, config: SequenceConfig, layer_id: str, divider: Divider) -> None:
    key = f"{config.prefix}/{divider.key}"
    wrapper = ET.SubElement(root, "object", {
        "label": "", "petakerjaKey": key, "id": key.replace("/", "-"),
    })
    cell = ET.SubElement(wrapper, "mxCell", {
        "edge": "1", "parent": layer_id,
        "style": "endArrow=none;dashed=1;html=1;rounded=0;strokeWidth=1;",
    })
    geometry = add_geometry(cell, relative=True)
    ET.SubElement(geometry, "mxPoint", {"x": f"{divider.x1:g}", "y": f"{divider.y:g}", "as": "sourcePoint"})
    ET.SubElement(geometry, "mxPoint", {"x": f"{divider.x2:g}", "y": f"{divider.y:g}", "as": "targetPoint"})


def ratio(y: float) -> float:
    return max(0.0, min(1.0, (y - ACTIVATION_Y) / ACTIVATION_HEIGHT))


def message_style(base: str, y: float, source_x: float, target_x: float) -> str:
    left_to_right = target_x > source_x
    exit_x, entry_x = (1, 0) if left_to_right else (0, 1)
    return base + (
        f"exitX={exit_x};exitY={ratio(y):.6f};exitPerimeter=0;"
        f"entryX={entry_x};entryY={ratio(y):.6f};entryPerimeter=0;"
        "labelBackgroundColor=none;"
    )


def build(config: SequenceConfig) -> ET.ElementTree:
    root_id = f"{config.prefix}-root"
    layer_id = f"{config.prefix}-layer"
    mxfile = ET.Element("mxfile", {
        "host": "Electron", "agent": "PetaKerja Architecture Explorer", "version": "27.0.2",
    })
    diagram = ET.SubElement(mxfile, "diagram", {"name": config.page_name, "id": config.page_id})
    model = ET.SubElement(diagram, "mxGraphModel", {
        "dx": "1600", "dy": "1100", "grid": "1", "gridSize": "10", "guides": "1",
        "tooltips": "1", "connect": "1", "arrows": "1", "fold": "1", "page": "1",
        "pageScale": "1", "pageWidth": "1600", "pageHeight": "1100", "math": "0", "shadow": "0",
    })
    graph_root = ET.SubElement(model, "root")
    ET.SubElement(graph_root, "mxCell", {"id": root_id})
    ET.SubElement(graph_root, "mxCell", {"id": layer_id, "parent": root_id})

    background = ET.SubElement(graph_root, "mxCell", {
        "id": f"{config.prefix}-background", "parent": layer_id, "vertex": "1",
        "style": "rounded=0;whiteSpace=wrap;html=1;fillColor=#ffffff;strokeColor=none;locked=1;pointerEvents=0;",
    })
    add_geometry(background, x=0, y=0, width=1600, height=1100)
    add_object(
        graph_root, layer_id=layer_id, key=f"{config.prefix}/title",
        cell_id=f"{config.prefix}-title", label=config.title,
        style=TEXT_STYLE + "fontSize=18;fontStyle=1;", vertex=True,
        geometry={"x": 330, "y": 20, "width": 940, "height": 30},
    )

    centres = {participant.slug: participant.centre for participant in config.participants}
    activation_ids: dict[str, str] = {}
    for participant in config.participants:
        participant_key = f"{config.prefix}/participant-{participant.slug}"
        participant_id = f"{config.prefix}-participant-{participant.slug}"
        if participant.slug in {"administrator", "user"}:
            add_object(
                graph_root, layer_id=layer_id, key=participant_key, cell_id=participant_id,
                label=participant.label, style=ACTOR_STYLE, vertex=True,
                geometry={"x": participant.centre - 10, "y": 72, "width": 20, "height": 40},
            )
        else:
            add_object(
                graph_root, layer_id=layer_id, key=participant_key, cell_id=participant_id,
                label=participant.label, style=LIFELINE_STYLE, vertex=True,
                geometry={"x": participant.centre - 50, "y": 70, "width": 100, "height": 60},
            )
        activation_id = f"{config.prefix}-activation-{participant.slug}"
        activation_ids[participant.slug] = activation_id
        add_object(
            graph_root, layer_id=layer_id, key=participant_key + "-activation",
            cell_id=activation_id, label="", style=ACTIVATION_STYLE, vertex=True,
            geometry={"x": participant.centre - 5, "y": ACTIVATION_Y, "width": 10, "height": ACTIVATION_HEIGHT},
        )

    for fragment in config.fragments:
        add_object(
            graph_root, layer_id=layer_id, key=f"{config.prefix}/{fragment.key}",
            cell_id=f"{config.prefix}-{fragment.key}", label=fragment.label,
            style=FRAME_STYLE, vertex=True,
            geometry={"x": fragment.x, "y": fragment.y, "width": fragment.width, "height": fragment.height},
        )
    for divider in config.dividers:
        add_divider(graph_root, config, layer_id, divider)
    for operand in config.operands:
        add_object(
            graph_root, layer_id=layer_id, key=f"{config.prefix}/{operand.key}",
            cell_id=f"{config.prefix}-{operand.key}", label=operand.label,
            style=TEXT_STYLE + "align=left;fontStyle=2;fontSize=10;", vertex=True,
            geometry={"x": operand.x, "y": operand.y, "width": operand.width, "height": 18},
        )

    for message in sorted(config.messages, key=lambda item: item.y):
        source_id = activation_ids[message.source]
        target_id = activation_ids[message.target]
        add_object(
            graph_root, layer_id=layer_id, key=f"{config.prefix}/message-{message.index:02d}",
            cell_id=f"{config.prefix}-message-{message.index:02d}", label=message.simple_en,
            style=message_style(
                RETURN_STYLE if message.returned else CALL_STYLE,
                message.y, centres[message.source], centres[message.target],
            ),
            edge=True, source=source_id, target=target_id, geometry={"relative": True},
            metadata={
                "simpleLabelEn": message.simple_en,
                "simpleLabelMs": message.simple_ms,
                "codeLabelEn": message.code_en,
                "codeLabelMs": message.code_ms,
            },
        )

    add_object(
        graph_root, layer_id=layer_id, key=f"{config.prefix}/implementation-note",
        cell_id=f"{config.prefix}-implementation-note", label=config.note,
        style=TEXT_STYLE + "fontSize=9;fontStyle=2;fontColor=#555555;", vertex=True,
        geometry={"x": 220, "y": 1065, "width": 1160, "height": 20},
    )
    return ET.ElementTree(mxfile)


def m(
    index: int, simple_en: str, simple_ms: str, code_en: str, code_ms: str,
    source: str, target: str, y: float, returned: bool = False,
) -> Message:
    return Message(index, simple_en, simple_ms, code_en, code_ms, source, target, y, returned)


ACCESS_PARTICIPANTS = (
    Participant("administrator", "Administrator", 90),
    Participant("ui", "PetaKerja User Menu", 290),
    Participant("auth", "AuthManager", 490),
    Participant("manager", "<font style=\"font-size: 9px;\">AdminDashboard<br>Manager</font>", 690),
    Participant("client", "Admin API Client<div><font style=\"font-size: 8px;\">aiProviderApi.ts</font></div>", 890),
    Participant("api", "Protected Admin APIs<div><font style=\"font-size: 8px;\">providers / usage / users</font></div>", 1090),
    Participant("session", "Better Auth Session", 1290),
    Participant("database", "Supabase / PostgreSQL<div><font style=\"font-size: 8px;\">admin data</font></div>", 1490),
)

ACCESS_MESSAGES = (
    m(1, "Select the Admin Dashboard", "Pilih Papan Pemuka Pentadbir", '[data-dropdown-action="admin"]', '[data-dropdown-action="admin"]', "administrator", "ui", 155),
    m(2, "Check the current signed-in user", "Semak pengguna yang sedang log masuk", "AuthManager.getUser()", "AuthManager.getUser()", "ui", "auth", 185),
    m(3, "Return the administrator profile", "Pulangkan profil pentadbir", "AuthUser { role: admin | owner }", "AuthUser { role: admin | owner }", "auth", "ui", 215, True),
    m(4, "Open the administrator dashboard", "Buka papan pemuka pentadbir", "AdminDashboardManager.open(true)", "AdminDashboardManager.open(true)", "ui", "manager", 245),
    m(5, "Show the dashboard loading state", "Paparkan keadaan pemuatan papan pemuka", 'history.pushState({}, "", "/admin"); render()', 'history.pushState({}, "", "/admin"); render()', "manager", "ui", 275, True),
    m(6, "Request provider, usage and user information", "Minta maklumat penyedia, penggunaan dan pengguna", "Promise.all([listAdminAIProviders(), listAdminUsage(), listAdminUsers()])", "Promise.all([listAdminAIProviders(), listAdminUsage(), listAdminUsers()])", "manager", "client", 305),
    m(7, "Send the protected dashboard requests", "Hantar permintaan papan pemuka terlindung", "GET /api/admin/ai/providers + /api/admin/ai/usage + /api/admin/users", "GET /api/admin/ai/providers + /api/admin/ai/usage + /api/admin/users", "client", "api", 335),
    m(8, "Verify the active sign-in session", "Sahkan sesi log masuk aktif", "requireAuth(); getAppSessionFromHeaders()", "requireAuth(); getAppSessionFromHeaders()", "api", "session", 365),
    m(9, "Return the verified user", "Pulangkan pengguna yang disahkan", "req.auth = session", "req.auth = session", "session", "api", 395, True),
    m(10, "Check the administrator role", "Semak peranan pentadbir", "requireAdmin(); SELECT role FROM public.users", "requireAdmin(); SELECT role FROM public.users", "api", "database", 425),
    m(11, "Return the assigned role", "Pulangkan peranan yang ditetapkan", "{ role }", "{ role }", "database", "api", 455, True),
    m(12, "Retrieve dashboard records", "Dapatkan rekod papan pemuka", "SELECT providers, usage events and latest users", "SELECT providers, usage events and latest users", "api", "database", 495),
    m(13, "Return the dashboard records", "Pulangkan rekod papan pemuka", "providerRows + usageRows + userRows", "providerRows + usageRows + userRows", "database", "api", 525, True),
    m(14, "Return the dashboard information", "Pulangkan maklumat papan pemuka", "AdminProvidersResponse + AdminUsageResponse + AdminUsersResponse", "AdminProvidersResponse + AdminUsageResponse + AdminUsersResponse", "api", "client", 555, True),
    m(15, "Provide the information to the dashboard", "Berikan maklumat kepada papan pemuka", "resolve Promise.all responses", "resolve Promise.all responses", "client", "manager", 585, True),
    m(16, "Prepare the administrator overview", "Sediakan gambaran keseluruhan pentadbir", "renderOverview()", "renderOverview()", "manager", "ui", 615, True),
    m(17, "Display the administrator dashboard", "Paparkan papan pemuka pentadbir", "#admin-dashboard", "#admin-dashboard", "ui", "administrator", 645, True),
    m(18, "Report the dashboard loading error", "Laporkan ralat pemuatan papan pemuka", "loadAdminData() catch", "loadAdminData() catch", "client", "manager", 665, True),
    m(19, "Display the dashboard loading error", "Paparkan ralat pemuatan papan pemuka", "renderError()", "renderError()", "manager", "ui", 680, True),
    m(20, "Request sign-in", "Minta pengguna log masuk", "HTTP 401; auth:require-login", "HTTP 401; auth:require-login", "api", "ui", 735, True),
    m(21, "Display the sign-in prompt", "Paparkan prompt log masuk", "AuthModalManager.openAuthPrompt()", "AuthModalManager.openAuthPrompt()", "ui", "administrator", 765, True),
    m(22, "Return administrator access required", "Pulangkan keperluan akses pentadbir", "HTTP 403; requireAdmin()", "HTTP 403; requireAdmin()", "api", "ui", 825, True),
    m(23, "Display administrator access required", "Paparkan keperluan akses pentadbir", 'history.replaceState({}, "", "/")', 'history.replaceState({}, "", "/")', "ui", "administrator", 855, True),
)

ACCESS_CONFIG = SequenceConfig(
    prefix="admin-access-dashboard-sequence",
    page_id="petakerja_admin_access_dashboard_sequence",
    page_name="Access Administrator Dashboard",
    title="PetaKerja Administrator Access Dashboard Sequence",
    filename="Sequence Diagram PetaKerja - Access Administrator Dashboard.drawio",
    editor_filename="sequence-admin-access-dashboard.drawio",
    participants=ACCESS_PARTICIPANTS,
    messages=ACCESS_MESSAGES,
    fragments=(
        Fragment("fragment-access", "alt", 240, 320, 1300, 555),
        Fragment("fragment-load-result", "alt", 245, 475, 1290, 215),
    ),
    dividers=(
        Divider("divider-load-error", 655, 245, 1535),
        Divider("divider-no-session", 705, 240, 1540),
        Divider("divider-role-denied", 795, 240, 1540),
    ),
    operands=(
        Operand("access-authorized", "[administrator or owner]", 310, 323),
        Operand("load-success", "[dashboard data returned]", 315, 478),
        Operand("load-error", "[request failed]", 315, 657),
        Operand("access-no-session", "[no active session]", 310, 707),
        Operand("access-role-denied", "[role not allowed]", 310, 797),
    ),
    note=(
        "Implementation note: opening the dashboard loads provider status, AI usage and recent users together. "
        "Blog analytics is loaded separately only when the Blog tab is opened."
    ),
)


ACTIVITY_PARTICIPANTS = (
    Participant("administrator", "Administrator", 110),
    Participant("ui", "PetaKerja Admin UI", 330),
    Participant("manager", "<font style=\"font-size: 9px;\">AdminDashboard<br>Manager</font>", 550),
    Participant("client", "Admin API Client<div><font style=\"font-size: 8px;\">aiProviderApi.ts</font></div>", 770),
    Participant("api", "Admin Usage API<div><font style=\"font-size: 8px;\">GET /api/admin/ai/usage</font></div>", 990),
    Participant("session", "Better Auth Session", 1210),
    Participant("database", "Supabase / PostgreSQL<div><font style=\"font-size: 8px;\">users / ai_usage_events</font></div>", 1430),
)

ACTIVITY_MESSAGES = (
    m(1, "Open the administrator dashboard", "Buka papan pemuka pentadbir", "AdminDashboardManager.open(true)", "AdminDashboardManager.open(true)", "administrator", "ui", 155),
    m(2, "Request activity information", "Minta maklumat aktiviti", "loadAdminData(); listAdminUsage()", "loadAdminData(); listAdminUsage()", "ui", "manager", 185),
    m(3, "Send the activity request", "Hantar permintaan aktiviti", 'authenticatedFetch("/api/admin/ai/usage")', 'authenticatedFetch("/api/admin/ai/usage")', "manager", "client", 215),
    m(4, "Request the usage ledger", "Minta lejar penggunaan", "GET /api/admin/ai/usage", "GET /api/admin/ai/usage", "client", "api", 245),
    m(5, "Verify the active sign-in session", "Sahkan sesi log masuk aktif", "requireAuth(); getAppSessionFromHeaders()", "requireAuth(); getAppSessionFromHeaders()", "api", "session", 275),
    m(6, "Return the verified user", "Pulangkan pengguna yang disahkan", "req.auth = session", "req.auth = session", "session", "api", 305, True),
    m(7, "Check the administrator role", "Semak peranan pentadbir", "requireAdmin(); SELECT role FROM public.users", "requireAdmin(); SELECT role FROM public.users", "api", "database", 350),
    m(8, "Return the assigned role", "Pulangkan peranan yang ditetapkan", "{ role }", "{ role }", "database", "api", 380, True),
    m(9, "Retrieve the latest assistant activity", "Dapatkan aktiviti pembantu AI terkini", "SELECT usage fields FROM public.ai_usage_events ORDER BY created_at DESC LIMIT 100", "SELECT medan penggunaan FROM public.ai_usage_events ORDER BY created_at DESC LIMIT 100", "api", "database", 425),
    m(10, "Return the activity records", "Pulangkan rekod aktiviti", "usage rows", "baris penggunaan", "database", "api", 455, True),
    m(11, "Return totals and activity events", "Pulangkan jumlah dan peristiwa aktiviti", "AdminUsageResponse { totals, events }", "AdminUsageResponse { totals, events }", "api", "client", 485, True),
    m(12, "Provide activity data to the dashboard", "Berikan data aktiviti kepada papan pemuka", "state.adminDashboard.usageTotals / usageEvents", "state.adminDashboard.usageTotals / usageEvents", "client", "manager", 515, True),
    m(13, "Request sign-in", "Minta pengguna log masuk", "HTTP 401; requireAuth()", "HTTP 401; requireAuth()", "api", "ui", 595, True),
    m(14, "Display the sign-in prompt", "Paparkan prompt log masuk", "AuthModalManager.openAuthPrompt()", "AuthModalManager.openAuthPrompt()", "ui", "administrator", 625, True),
    m(15, "Return administrator access required", "Pulangkan keperluan akses pentadbir", "HTTP 403; requireAdmin()", "HTTP 403; requireAdmin()", "api", "ui", 680, True),
    m(16, "Display administrator access required", "Paparkan keperluan akses pentadbir", "renderError(ADMIN_REQUIRED)", "renderError(ADMIN_REQUIRED)", "ui", "administrator", 710, True),
    m(17, "Select the Usage section", "Pilih bahagian Penggunaan", '[data-admin-action="tab"][data-tab="usage"]', '[data-admin-action="tab"][data-tab="usage"]', "administrator", "ui", 800),
    m(18, "Open the Usage section", "Buka bahagian Penggunaan", 'activeTab = "usage"', 'activeTab = "usage"', "ui", "manager", 830),
    m(19, "Prepare the activity table", "Sediakan jadual aktiviti", "renderUsageTable()", "renderUsageTable()", "manager", "ui", 860, True),
    m(20, "Display totals and recent activity", "Paparkan jumlah dan aktiviti terkini", ".admin-stat-grid + .admin-table", ".admin-stat-grid + .admin-table", "ui", "administrator", 890, True),
    m(21, "Display that no activity is available", "Paparkan bahawa tiada aktiviti tersedia", 'emptyState("No usage events yet.")', 'emptyState("No usage events yet.")', "ui", "administrator", 940, True),
    m(22, "Return the activity request error", "Pulangkan ralat permintaan aktiviti", "HTTP / database error", "Ralat HTTP / pangkalan data", "api", "client", 995, True),
    m(23, "Report the dashboard loading error", "Laporkan ralat pemuatan papan pemuka", "loadAdminData() catch", "loadAdminData() catch", "client", "manager", 1015, True),
    m(24, "Display the activity loading error", "Paparkan ralat pemuatan aktiviti", "renderError()", "renderError()", "manager", "ui", 1030, True),
    m(25, "Show the error to the administrator", "Paparkan ralat kepada pentadbir", ".admin-dashboard__error", ".admin-dashboard__error", "ui", "administrator", 1045, True),
)

ACTIVITY_CONFIG = SequenceConfig(
    prefix="admin-monitor-activity-sequence",
    page_id="petakerja_admin_monitor_activity_sequence",
    page_name="Monitor System Activity Logs",
    title="PetaKerja Administrator Monitor System Activity Logs Sequence",
    filename="Sequence Diagram PetaKerja - Monitor System Activity Logs.drawio",
    editor_filename="sequence-admin-monitor-activity.drawio",
    participants=ACTIVITY_PARTICIPANTS,
    messages=ACTIVITY_MESSAGES,
    fragments=(
        Fragment("fragment-access", "alt", 270, 250, 1220, 480),
        Fragment("fragment-results", "alt", 55, 750, 1435, 300),
    ),
    dividers=(
        Divider("divider-no-session", 565, 270, 1490),
        Divider("divider-role-denied", 650, 270, 1490),
        Divider("divider-no-events", 905, 55, 1490),
        Divider("divider-request-failed", 965, 55, 1490),
    ),
    operands=(
        Operand("access-authorized", "[administrator or owner]", 340, 253),
        Operand("access-no-session", "[no active session]", 340, 567),
        Operand("access-role-denied", "[role not allowed]", 340, 652),
        Operand("events-available", "[activity events available]", 125, 753),
        Operand("no-events", "[no activity events]", 125, 908),
        Operand("request-failed", "[request failed]", 125, 968),
    ),
    note=(
        "Implementation note: this use case currently monitors the latest 100 AI assistant usage events only. "
        "It does not read general server logs or public.ai_admin_audit_logs."
    ),
)


def sign_out_config(*, administrator: bool) -> SequenceConfig:
    actor_slug = "administrator" if administrator else "user"
    actor_label = "Administrator" if administrator else "User"
    prefix = "admin-sign-out-sequence" if administrator else "user-sign-out-sequence"
    dashboard_label = (
        '<font style="font-size: 9px;">AdminDashboard<br>Manager</font>'
        if administrator else '<font style="font-size: 9px;">UserDashboard<br>Manager</font>'
    )
    dashboard_slug = "admin-dashboard" if administrator else "user-dashboard"
    dashboard_simple = (
        "Render the administrator dashboard as signed out"
        if administrator else "Close the user dashboard and clear its cached data"
    )
    dashboard_simple_ms = (
        "Paparkan papan pemuka pentadbir sebagai telah log keluar"
        if administrator else "Tutup papan pemuka pengguna dan kosongkan data cachenya"
    )
    dashboard_code = (
        "AdminDashboardManager.onAuthChange(); loadAdminData(); render()"
        if administrator else "UserDashboardManager.onAuthChange(); resetCaches(); close(true)"
    )
    return SequenceConfig(
        prefix=prefix,
        page_id=(
            "petakerja_administrator_sign_out_sequence"
            if administrator else "petakerja_user_sign_out_sequence"
        ),
        page_name="Administrator Sign Out" if administrator else "User Sign Out",
        title=(
            "PetaKerja Administrator Sign Out Sequence"
            if administrator else "PetaKerja User Sign Out Sequence"
        ),
        filename=(
            "Sequence Diagram PetaKerja - Administrator Sign Out.drawio"
            if administrator else "Sequence Diagram PetaKerja - User Sign Out.drawio"
        ),
        editor_filename=(
            "sequence-admin-sign-out.drawio" if administrator else "sequence-user-sign-out.drawio"
        ),
        participants=(
            Participant(actor_slug, actor_label, 90),
            Participant("ui", "PetaKerja User Menu", 290),
            Participant("menu-manager", "<font style=\"font-size: 9px;\">UserMenu<br>Manager</font>", 490),
            Participant("auth", "AuthManager", 690),
            Participant("client", "authClient", 890),
            Participant("api", "Better Auth API<div><font style=\"font-size: 8px;\">POST /api/auth/sign-out</font></div>", 1090),
            Participant("session", "Better Auth Session", 1290),
            Participant(dashboard_slug, dashboard_label, 1490),
        ),
        messages=(
            m(1, "Select Sign Out", "Pilih Log Keluar", '[data-dropdown-action="signout"]', '[data-dropdown-action="signout"]', actor_slug, "ui", 155),
            m(2, "Start the sign-out process", "Mulakan proses log keluar", "UserMenuManager.handleSignOut()", "UserMenuManager.handleSignOut()", "ui", "menu-manager", 185),
            m(3, "Request sign-out", "Minta log keluar", "AuthManager.signOut()", "AuthManager.signOut()", "menu-manager", "auth", 215),
            m(4, "Send the sign-out request", "Hantar permintaan log keluar", "authClient.signOut()", "authClient.signOut()", "auth", "client", 245),
            m(5, "End the Better Auth session", "Tamatkan sesi Better Auth", "POST /api/auth/sign-out", "POST /api/auth/sign-out", "client", "api", 275),
            m(6, "Invalidate the active session", "Batalkan sesi aktif", "delete session; clear session cookie", "padam sesi; kosongkan kuki sesi", "api", "session", 305),
            m(7, "Confirm that the session ended", "Sahkan bahawa sesi telah tamat", "session invalidated", "sesi dibatalkan", "session", "api", 335, True),
            m(8, "Return sign-out success", "Pulangkan kejayaan log keluar", "HTTP 200; Set-Cookie expired", "HTTP 200; Set-Cookie tamat", "api", "client", 365, True),
            m(9, "Confirm sign-out", "Sahkan log keluar", "{ error: null }", "{ error: null }", "client", "auth", 395, True),
            m(10, "Clear the current user", "Kosongkan pengguna semasa", "AuthManager.setUser(null)", "AuthManager.setUser(null)", "auth", "menu-manager", 425),
            m(11, "Display the guest sign-in control", "Paparkan kawalan log masuk tetamu", "closeProfile(); renderGuest()", "closeProfile(); renderGuest()", "menu-manager", "ui", 455, True),
            m(12, "Notify the protected dashboard", "Maklumkan papan pemuka terlindung", "onAuthChange(null)", "onAuthChange(null)", "auth", dashboard_slug, 485),
            m(13, dashboard_simple, dashboard_simple_ms, dashboard_code, dashboard_code, dashboard_slug, "ui", 515, True),
            m(14, "Display the signed-out interface", "Paparkan antara muka yang telah log keluar", "render signed-out state", "paparkan keadaan log keluar", "ui", actor_slug, 545, True),
            m(15, "Return the sign-out error", "Pulangkan ralat log keluar", "Better Auth signOut error", "Ralat Better Auth signOut", "client", "auth", 675, True),
            m(16, "Report that sign-out failed", "Laporkan bahawa log keluar gagal", "throw error", "lemparkan ralat", "auth", "menu-manager", 705, True),
            m(17, "Keep the current session and re-enable Sign Out", "Kekalkan sesi semasa dan aktifkan semula Log Keluar", "catch; button.disabled = false", "catch; button.disabled = false", "menu-manager", "ui", 735, True),
            m(18, "Display the still-signed-in interface", "Paparkan antara muka yang masih log masuk", "preserve AuthUser", "kekalkan AuthUser", "ui", actor_slug, 765, True),
        ),
        fragments=(
            Fragment("fragment-result", "alt", 40, 350, 1500, 435),
        ),
        dividers=(
            Divider("divider-sign-out-failed", 640, 40, 1540),
        ),
        operands=(
            Operand("sign-out-success", "[sign-out succeeds]", 110, 353),
            Operand("sign-out-failed", "[sign-out fails]", 110, 642),
        ),
        note=(
            "Implementation note: on successful sign-out, UserDashboardManager closes and clears per-user caches. "
            "AdminDashboardManager currently remains on screen but re-renders its signed-out access state."
        ),
    )


USER_EXPLORE_MAP_CONFIG = SequenceConfig(
    prefix="user-explore-3d-map-sequence",
    page_id="petakerja_user_explore_3d_map_sequence",
    page_name="Explore the 3D Map",
    title="PetaKerja User Explore the 3D Map Sequence",
    filename="Sequence Diagram PetaKerja - Explore the 3D Map.drawio",
    editor_filename="sequence-user-explore-3d-map.drawio",
    participants=(
        Participant("user", "User", 90),
        Participant("ui", "PetaKerja Workspace UI", 290),
        Participant("app", "MyPetaApp", 490),
        Participant("map-manager", "MapManager", 690),
        Participant("poi-managers", "<font style=\"font-size: 9px;\">POIManager /<br>CategoryManager</font>", 890),
        Participant("data-api", "PetaKerja Data API<div><font style=\"font-size: 8px;\">supabase.ts</font></div>", 1090),
        Participant("database", "Supabase / PostgreSQL<div><font style=\"font-size: 8px;\">POI data</font></div>", 1290),
        Participant("maplibre", "MapLibre GL", 1490),
    ),
    messages=(
        m(1, "Select the Malaysia Map workspace", "Pilih ruang kerja Peta Malaysia", '.sp-template-card[data-preset="malaysia-map"]', '.sp-template-card[data-preset="malaysia-map"]', "user", "ui", 155),
        m(2, "Open the selected workspace", "Buka ruang kerja yang dipilih", "MyPetaApp.onPresetSelected(preset)", "MyPetaApp.onPresetSelected(preset)", "ui", "app", 185),
        m(3, "Enter the map workspace", "Masuki ruang kerja peta", "MapManager.enterWorkspace()", "MapManager.enterWorkspace()", "app", "map-manager", 215),
        m(4, "Prepare the workspace transition", "Sediakan peralihan ruang kerja", "beginWorkspaceTransition(); map.resize()", "beginWorkspaceTransition(); map.resize()", "map-manager", "maplibre", 245),
        m(5, "Confirm that the base map is ready", "Sahkan bahawa peta asas telah sedia", "style.load / baseLayersReady", "style.load / baseLayersReady", "maplibre", "map-manager", 275, True),
        m(6, "Move the camera to Malaysia", "Gerakkan kamera ke Malaysia", "map.flyTo({ center, zoom, pitch: 1, bearing: 0 })", "map.flyTo({ center, zoom, pitch: 1, bearing: 0 })", "map-manager", "maplibre", 305),
        m(7, "Confirm that the camera movement is complete", "Sahkan pergerakan kamera selesai", "map.once('idle')", "map.once('idle')", "maplibre", "map-manager", 335, True),
        m(8, "Start map exploration", "Mulakan penerokaan peta", "state.explorationStarted = true; onExplorationStart()", "state.explorationStarted = true; onExplorationStart()", "map-manager", "app", 365, True),
        m(9, "Initialize points of interest and categories", "Mulakan titik minat dan kategori", "setupSource(); loadForView(); loadCounts()", "setupSource(); loadForView(); loadCounts()", "app", "poi-managers", 395),
        m(10, "Request map data for the visible area", "Minta data peta bagi kawasan yang kelihatan", "fetchPOIsInBounds(); fetchCategoriesWithCounts()", "fetchPOIsInBounds(); fetchCategoriesWithCounts()", "poi-managers", "data-api", 425),
        m(11, "Retrieve POIs and category counts", "Dapatkan POI dan bilangan kategori", "get_pois_in_bounds + get_poi_categories_with_counts RPC", "RPC get_pois_in_bounds + get_poi_categories_with_counts", "data-api", "database", 455),
        m(12, "Return the map records", "Pulangkan rekod peta", "BoundsPOI[] + CategoryWithCount[]", "BoundsPOI[] + CategoryWithCount[]", "database", "data-api", 485, True),
        m(13, "Return POIs and category totals", "Pulangkan POI dan jumlah kategori", "resolve data requests", "selesaikan permintaan data", "data-api", "poi-managers", 515, True),
        m(14, "Place the POIs on the map", "Letakkan POI pada peta", "GeoJSONSource.setData()", "GeoJSONSource.setData()", "poi-managers", "maplibre", 545),
        m(15, "Display the interactive map and POIs", "Paparkan peta interaktif dan POI", "render map canvas, clusters and labels", "paparkan kanvas peta, kelompok dan label", "maplibre", "user", 575, True),
        m(16, "Display the map without unavailable POIs", "Paparkan peta tanpa POI yang tidak tersedia", "loadForView() catch; counts fallback []", "loadForView() catch; kiraan fallback []", "poi-managers", "ui", 610, True),
        m(17, "Select 3D Terrain", "Pilih Terrain 3D", '.basemap-mode-btn[data-basemap="terrain"]', '.basemap-mode-btn[data-basemap="terrain"]', "user", "ui", 700),
        m(18, "Enable the 3D terrain mode", "Aktifkan mod terrain 3D", "MapManager.setBasemapMode('terrain')", "MapManager.setBasemapMode('terrain')", "ui", "map-manager", 730),
        m(19, "Apply satellite imagery and terrain elevation", "Gunakan imej satelit dan ketinggian terrain", "setStyle(); setTerrain({ source: 'terrain-dem', exaggeration: 1.2 })", "setStyle(); setTerrain({ source: 'terrain-dem', exaggeration: 1.2 })", "map-manager", "maplibre", 760),
        m(20, "Display the 3D terrain", "Paparkan terrain 3D", "map:basemap-transition-end", "map:basemap-transition-end", "maplibre", "user", 790, True),
        m(21, "Toggle 3D buildings", "Togol bangunan 3D", "#toggle-3d-buildings", "#toggle-3d-buildings", "user", "ui", 870),
        m(22, "Update the 3D building layer", "Kemas kini lapisan bangunan 3D", "MapManager.toggle3DBuildings()", "MapManager.toggle3DBuildings()", "ui", "map-manager", 900),
        m(23, "Change building visibility", "Ubah keterlihatan bangunan", "map.setLayoutProperty('building-3d', 'visibility', ...)", "map.setLayoutProperty('building-3d', 'visibility', ...)", "map-manager", "maplibre", 930),
        m(24, "Display the 3D building extrusions", "Paparkan ekstrusi bangunan 3D", "render fill-extrusion layer", "paparkan lapisan fill-extrusion", "maplibre", "user", 960, True),
    ),
    fragments=(
        Fragment("fragment-data-result", "alt", 240, 410, 1300, 220),
        Fragment("fragment-terrain", "opt", 40, 655, 1500, 165),
        Fragment("fragment-buildings", "opt", 40, 825, 1500, 165),
    ),
    dividers=(
        Divider("divider-data-failed", 590, 240, 1540),
    ),
    operands=(
        Operand("data-available", "[map data available]", 310, 413),
        Operand("data-unavailable", "[data request fails]", 310, 592),
        Operand("terrain-selected", "[user enables 3D terrain]", 110, 658),
        Operand("buildings-selected", "[user toggles 3D buildings]", 110, 828),
    ),
    note=(
        "Implementation note: map exploration is public. 3D terrain uses satellite imagery plus a DEM on screens wider than 768px; "
        "building extrusions appear within their configured zoom range."
    ),
)


def write_config(config: SequenceConfig) -> tuple[Path, Path]:
    tree = build(config)
    ET.indent(tree, space="  ")
    report_output = DIAGRAMS / config.filename
    editor_output = EXPLORER / "assets" / "editor" / config.editor_filename
    report_output.parent.mkdir(parents=True, exist_ok=True)
    editor_output.parent.mkdir(parents=True, exist_ok=True)
    tree.write(report_output, encoding="utf-8", xml_declaration=False)
    tree.write(editor_output, encoding="utf-8", xml_declaration=False)
    apply_label_modes_to_file(report_output)
    apply_label_modes_to_file(editor_output)
    return report_output, editor_output


def main() -> None:
    if not TEMPLATE.exists():
        raise FileNotFoundError(TEMPLATE)
    for config in (
        ACCESS_CONFIG,
        ACTIVITY_CONFIG,
        sign_out_config(administrator=True),
        USER_EXPLORE_MAP_CONFIG,
        sign_out_config(administrator=False),
    ):
        report_output, editor_output = write_config(config)
        print(f"Wrote {report_output}")
        print(f"Wrote {editor_output}")


if __name__ == "__main__":
    main()
