#!/usr/bin/env python3
"""Build the PetaKerja Administrator Manage Users sequence diagram.

The supplied TTTE1113-style sequence template is read only for visual styles.
The generated source uses plain-language English labels by default while each
message also stores bilingual Simple and Code labels as non-visual metadata.
"""

from __future__ import annotations

import re
import xml.etree.ElementTree as ET
from pathlib import Path

from sequence_label_catalog import apply_label_modes_to_file


DIAGRAMS = Path(r"C:\Users\iamal\Desktop\Semester 8\TTTM4172 Usulan Projek\Akmal\Diagrams")
TEMPLATE = DIAGRAMS / "Sequence Diagram Template.drawio"
OUTPUT = DIAGRAMS / "Sequence Diagram PetaKerja - Manage Users.drawio"
EXPLORER = Path(__file__).resolve().parents[1]
EDITOR_OUTPUT = EXPLORER / "assets" / "editor" / "sequence-admin-manage-users.drawio"

PAGE_ID = "petakerja_admin_manage_users_sequence"
KEY_PREFIX = "admin-manage-users-sequence"
ROOT_ID = "admin-manage-users-sequence-root"
LAYER_ID = "admin-manage-users-sequence-layer"
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
    ("startArrow", "startFill", "endArrow", "endFill", "entryX", "entryY", "entryDx", "entryDy", "exitX", "exitY", "exitDx", "exitDy"),
) + ";endArrow=classic;endFill=1;strokeWidth=1;fontSize=10;"
RETURN_STYLE = strip_style_properties(
    TEMPLATE_RETURN_STYLE,
    ("entryX", "entryY", "entryDx", "entryDy", "exitX", "exitY", "exitDx", "exitDy"),
) + ";strokeWidth=1;fontSize=10;"
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
        cell_id=f"admin-manage-users-message-{index:02d}",
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


def add_operand(root: ET.Element, key: str, label: str, x: float, y: float, width: float = 250) -> None:
    add_object(
        root, key=key, cell_id=key.replace("/", "-"), label=label,
        style=TEXT_STYLE + "align=left;fontStyle=2;fontSize=10;", vertex=True,
        geometry={"x": x, "y": y, "width": width, "height": 20},
    )


PARTICIPANTS = [
    ("administrator", "Administrator", 110, "pentadbir"),
    ("ui", "PetaKerja Admin UI", 330, "admin-ui"),
    ("manager", "<font style=\"font-size: 9px;\">AdminDashboard<br>Manager</font>", 550, "admin-manager"),
    ("client", "Admin API Client<div><font style=\"font-size: 8px;\">aiProviderApi.ts</font></div>", 770, "admin-api-client"),
    ("api", "Admin Users API<div><font style=\"font-size: 8px;\">GET /api/admin/users</font></div>", 990, "admin-users-api"),
    ("session", "Better Auth Session", 1210, "better-auth"),
    ("database", "Supabase / PostgreSQL<div><font style=\"font-size: 8px;\">public.users</font></div>", 1430, "supabase-db"),
]
PARTICIPANT_CENTRES = {
    f"admin-manage-users-activation-{slug}": centre for slug, _label, centre, _node in PARTICIPANTS
}


def msg(index: int, simple_en: str, simple_ms: str, code_en: str, code_ms: str,
        source: str, target: str, y: float, returned: bool = False) -> dict:
    return {
        "index": index, "simple_en": simple_en, "simple_ms": simple_ms,
        "code_en": code_en, "code_ms": code_ms,
        "source": source, "target": target, "y": y, "returned": returned,
    }


MESSAGES = [
    msg(1, "Select the Admin Dashboard", "Pilih Papan Pemuka Pentadbir", '[data-dropdown-action="admin"]', '[data-dropdown-action="admin"]', "administrator", "ui", 155),
    msg(2, "Open the administrator dashboard", "Buka papan pemuka pentadbir", "AdminDashboardManager.open(true)", "AdminDashboardManager.open(true)", "ui", "manager", 185),
    msg(3, "Request user information", "Minta maklumat pengguna", "loadAdminData(); listAdminUsers()", "loadAdminData(); listAdminUsers()", "manager", "client", 215),
    msg(4, "Send the user-list request", "Hantar permintaan senarai pengguna", 'authenticatedFetch("/api/admin/users")', 'authenticatedFetch("/api/admin/users")', "client", "api", 245),
    msg(5, "Verify the active sign-in session", "Sahkan sesi log masuk aktif", "requireAuth(); getAppSessionFromHeaders()", "requireAuth(); getAppSessionFromHeaders()", "api", "session", 275),
    msg(6, "Return the verified user", "Pulangkan pengguna yang disahkan", "req.auth = session", "req.auth = session", "session", "api", 305, True),
    msg(7, "Check the administrator role", "Semak peranan pentadbir", "requireAdmin(); SELECT role FROM public.users", "requireAdmin(); SELECT role FROM public.users", "api", "database", 350),
    msg(8, "Return the assigned role", "Pulangkan peranan yang ditetapkan", "{ role }", "{ role }", "database", "api", 380, True),
    msg(9, "Retrieve recent user profiles and roles", "Dapatkan profil dan peranan pengguna terkini", "SELECT id, email, username, display_name, role, created_at, last_login FROM public.users ORDER BY created_at DESC LIMIT 100", "SELECT id, email, username, display_name, role, created_at, last_login FROM public.users ORDER BY created_at DESC LIMIT 100", "api", "database", 425),
    msg(10, "Return the user records", "Pulangkan rekod pengguna", "rows", "rows", "database", "api", 455, True),
    msg(11, "Return the user list", "Pulangkan senarai pengguna", "AdminUsersResponse { users }", "AdminUsersResponse { users }", "api", "client", 485, True),
    msg(12, "Provide users to the dashboard", "Berikan pengguna kepada papan pemuka", "state.adminDashboard.users = users.users", "state.adminDashboard.users = users.users", "client", "manager", 515, True),
    msg(13, "Select the Users section", "Pilih bahagian Pengguna", '[data-admin-action="tab"][data-tab="users"]', '[data-admin-action="tab"][data-tab="users"]', "administrator", "ui", 770),
    msg(14, "Open the Users section", "Buka bahagian Pengguna", 'activeTab = "users"', 'activeTab = "users"', "ui", "manager", 800),
    msg(15, "Prepare the user table", "Sediakan jadual pengguna", "renderUsers()", "renderUsers()", "manager", "ui", 830, True),
    msg(16, "Display the user list and roles", "Paparkan senarai pengguna dan peranan", ".admin-table", ".admin-table", "ui", "administrator", 855, True),
    msg(17, "Return an empty user list", "Pulangkan senarai pengguna kosong", "AdminUsersResponse { users: [] }", "AdminUsersResponse { users: [] }", "client", "manager", 900, True),
    msg(18, "Display the empty state", "Paparkan keadaan kosong", "renderUsers(); .empty-state", "renderUsers(); .empty-state", "ui", "administrator", 925, True),
    msg(19, "Return the request error", "Pulangkan ralat permintaan", "HTTP error", "Ralat HTTP", "api", "client", 970, True),
    msg(20, "Report the dashboard loading error", "Laporkan ralat pemuatan papan pemuka", "loadAdminData() catch", "loadAdminData() catch", "client", "manager", 995, True),
    msg(21, "Display the dashboard loading error", "Paparkan ralat pemuatan papan pemuka", "renderError()", "renderError()", "manager", "ui", 1020, True),
    msg(22, "Request sign-in", "Minta pengguna log masuk", "HTTP 401; requireAuth()", "HTTP 401; requireAuth()", "api", "ui", 595, True),
    msg(23, "Display the sign-in prompt", "Paparkan prompt log masuk", "AuthModalManager.openAuthPrompt()", "AuthModalManager.openAuthPrompt()", "ui", "administrator", 620, True),
    msg(24, "Return administrator access required", "Pulangkan keperluan akses pentadbir", "HTTP 403; requireAdmin()", "HTTP 403; requireAdmin()", "api", "ui", 680, True),
    msg(25, "Display administrator access required", "Paparkan keperluan akses pentadbir", "renderError(ADMIN_REQUIRED)", "renderError(ADMIN_REQUIRED)", "ui", "administrator", 705, True),
]


def build() -> ET.ElementTree:
    mxfile = ET.Element("mxfile", {"host": "Electron", "agent": "PetaKerja Architecture Explorer", "version": "27.0.2"})
    diagram = ET.SubElement(mxfile, "diagram", {"name": "Manage Users", "id": PAGE_ID})
    model = ET.SubElement(diagram, "mxGraphModel", {
        "dx": "1600", "dy": "1100", "grid": "1", "gridSize": "10", "guides": "1",
        "tooltips": "1", "connect": "1", "arrows": "1", "fold": "1", "page": "1",
        "pageScale": "1", "pageWidth": "1600", "pageHeight": "1100", "math": "0", "shadow": "0",
    })
    root = ET.SubElement(model, "root")
    ET.SubElement(root, "mxCell", {"id": ROOT_ID})
    ET.SubElement(root, "mxCell", {"id": LAYER_ID, "parent": ROOT_ID})
    background = ET.SubElement(root, "mxCell", {
        "id": "admin-manage-users-background", "parent": LAYER_ID, "vertex": "1",
        "style": "rounded=0;whiteSpace=wrap;html=1;fillColor=#ffffff;strokeColor=none;locked=1;pointerEvents=0;",
    })
    add_geometry(background, x=0, y=0, width=1600, height=1100)

    add_object(root, key=f"{KEY_PREFIX}/title", cell_id="admin-manage-users-title",
               label="PetaKerja Administrator Manage Users Sequence",
               style=TEXT_STYLE + "fontSize=18;fontStyle=1;", vertex=True,
               geometry={"x": 450, "y": 20, "width": 700, "height": 30})

    activation_ids: dict[str, str] = {}
    for slug, label, centre, _node in PARTICIPANTS:
        participant_key = f"{KEY_PREFIX}/participant-{slug}"
        if slug == "administrator":
            add_object(root, key=participant_key, cell_id="admin-manage-users-participant-administrator",
                       label="", style=ACTOR_STYLE, vertex=True,
                       geometry={"x": centre - 10, "y": 72, "width": 20, "height": 40})
            add_object(root, key=None, cell_id="admin-manage-users-participant-administrator-label",
                       label="Administrator", style=TEXT_STYLE, vertex=True,
                       geometry={"x": centre - 45, "y": 110, "width": 90, "height": 20})
        else:
            add_object(root, key=participant_key, cell_id=f"admin-manage-users-participant-{slug}",
                       label=label, style=LIFELINE_STYLE, vertex=True,
                       geometry={"x": centre - 50, "y": 70, "width": 100, "height": 60})
        activation_id = f"admin-manage-users-activation-{slug}"
        activation_ids[slug] = activation_id
        add_object(root, key=participant_key + "-activation", cell_id=activation_id, label="",
                   style=ACTIVATION_STYLE, vertex=True,
                   geometry={"x": centre - 5, "y": ACTIVATION_Y, "width": 10, "height": ACTIVATION_HEIGHT})

    add_object(root, key=f"{KEY_PREFIX}/fragment-access", cell_id="admin-manage-users-fragment-access",
               label="alt", style=FRAME_STYLE, vertex=True,
               geometry={"x": 270, "y": 320, "width": 1220, "height": 410})
    add_object(root, key=f"{KEY_PREFIX}/fragment-results", cell_id="admin-manage-users-fragment-results",
               label="alt", style=FRAME_STYLE, vertex=True,
               geometry={"x": 55, "y": 740, "width": 1435, "height": 300})

    for message in sorted(MESSAGES, key=lambda item: item["y"]):
        add_message(root, message, activation_ids)

    add_divider(root, f"{KEY_PREFIX}/access-divider-session", 560, 270, 1490)
    add_divider(root, f"{KEY_PREFIX}/access-divider-role", 650, 270, 1490)
    add_operand(root, f"{KEY_PREFIX}/authorized", "[administrator or owner]", 350, 323)
    add_operand(root, f"{KEY_PREFIX}/no-session", "[no active session]", 350, 562)
    add_operand(root, f"{KEY_PREFIX}/role-denied", "[role not allowed]", 350, 652)

    add_divider(root, f"{KEY_PREFIX}/results-divider-empty", 875, 55, 1490)
    add_divider(root, f"{KEY_PREFIX}/results-divider-error", 945, 55, 1490)
    add_operand(root, f"{KEY_PREFIX}/users-available", "[users available]", 135, 743)
    add_operand(root, f"{KEY_PREFIX}/no-users", "[no users]", 135, 877)
    add_operand(root, f"{KEY_PREFIX}/request-failed", "[request failed]", 135, 947)

    add_object(
        root, key=f"{KEY_PREFIX}/note", cell_id="admin-manage-users-note",
        label="Current implementation displays the latest 100 users and their roles only. Account or role modification is not implemented.",
        style=TEXT_STYLE + "fontSize=10;fontStyle=2;fontColor=#555555;", vertex=True,
        geometry={"x": 300, "y": 1070, "width": 1000, "height": 18},
    )
    return ET.ElementTree(mxfile)


def main() -> None:
    if not TEMPLATE.exists():
        raise FileNotFoundError(TEMPLATE)
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
    main()
