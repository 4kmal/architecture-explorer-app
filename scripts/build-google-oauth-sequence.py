#!/usr/bin/env python3
"""Build the focused PetaKerja Google OAuth sequence from the supplied template.

The template is read for its UML actor, lifeline, activation, frame and message
styles. It is never modified. The generated source is copied into the Explorer
so Draw.io Edit mode and the exported View asset share the same geometry.
"""

from __future__ import annotations

import copy
import re
import xml.etree.ElementTree as ET
from pathlib import Path

from sequence_label_catalog import apply_label_modes_to_file


DIAGRAMS = Path(r"C:\Users\iamal\Desktop\Semester 8\TTTM4172 Usulan Projek\Akmal\Diagrams")
TEMPLATE = DIAGRAMS / "Sequence Diagram Template.drawio"
OUTPUT = DIAGRAMS / "Sequence Diagram PetaKerja - Sign in Google OAuth.drawio"
EXPLORER = Path(__file__).resolve().parents[1]
EDITOR_OUTPUT = EXPLORER / "assets" / "editor" / "sequence-google-oauth.drawio"

PAGE_ID = "petakerja_google_oauth_sequence"
ROOT_ID = "google-oauth-sequence-root"
LAYER_ID = "google-oauth-sequence-layer"
ACTIVATION_Y = 130.0
ACTIVATION_HEIGHT = 920.0


def template_style(predicate) -> str:
    root = ET.parse(TEMPLATE).getroot()
    for cell in root.findall(".//mxCell"):
        style = cell.get("style", "")
        if predicate(cell, style):
            return style
    raise RuntimeError("Required style was not found in the sequence template")


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


def normalise_call_style(style: str) -> str:
    for property_name in (
        "startArrow", "startFill", "endArrow", "endFill",
        "entryX", "entryY", "entryDx", "entryDy",
        "exitX", "exitY", "exitDx", "exitDy",
    ):
        style = re.sub(rf"(?:^|;){property_name}=[^;]*;?", ";", style)
    return style.strip(";") + ";endArrow=classic;endFill=1;strokeWidth=1;fontSize=10;"


def normalise_return_style(style: str) -> str:
    for property_name in (
        "entryX", "entryY", "entryDx", "entryDy",
        "exitX", "exitY", "exitDx", "exitDy",
    ):
        style = re.sub(rf"(?:^|;){property_name}=[^;]*;?", ";", style)
    return style.strip(";") + ";strokeWidth=1;fontSize=10;"


CALL_STYLE = normalise_call_style(TEMPLATE_CALL_STYLE)
RETURN_STYLE = normalise_return_style(TEMPLATE_RETURN_STYLE)
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


def add_object(root: ET.Element, *, key: str, cell_id: str, label: str, style: str,
               vertex: bool = False, edge: bool = False, source: str | None = None,
               target: str | None = None, geometry: dict | None = None) -> ET.Element:
    wrapper = ET.SubElement(root, "object", {"label": label, "petakerjaKey": key, "id": cell_id})
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


def message_style(base: str, y: float, *, source: str, target: str,
                  self_message: bool = False) -> str:
    if self_message:
        return (
            base
            + f"edgeStyle=orthogonalEdgeStyle;loopSize=42;align=left;spacingLeft=4;"
              f"exitX=1;exitY={ratio(y - 6):.6f};exitPerimeter=0;"
              f"entryX=1;entryY={ratio(y + 8):.6f};entryPerimeter=0;"
        )
    left_to_right = PARTICIPANT_CENTRES[target] > PARTICIPANT_CENTRES[source]
    exit_x, entry_x = (1, 0) if left_to_right else (0, 1)
    return base + (
        f"exitX={exit_x};exitY={ratio(y):.6f};exitPerimeter=0;"
        f"entryX={entry_x};entryY={ratio(y):.6f};entryPerimeter=0;"
        "labelBackgroundColor=none;"
    )


def add_message(root: ET.Element, *, index: int, label: str, source: str,
                target: str, y: float, returned: bool = False,
                self_message: bool = False) -> None:
    key = f"google-oauth-sequence/message-{index:02d}"
    cell_id = f"google-oauth-message-{index:02d}"
    base = RETURN_STYLE if returned else CALL_STYLE
    cell = add_object(
        root,
        key=key,
        cell_id=cell_id,
        label=label,
        style=message_style(base, y, source=source, target=target, self_message=self_message),
        edge=True,
        source=source,
        target=target,
        geometry={"relative": True},
    )
    if self_message:
        geometry = cell.find("mxGeometry")
        points = ET.SubElement(geometry, "Array", {"as": "points"})
        centre_x = PARTICIPANT_CENTRES[source]
        ET.SubElement(points, "mxPoint", {"x": f"{centre_x + 72:g}", "y": f"{y - 6:g}"})
        ET.SubElement(points, "mxPoint", {"x": f"{centre_x + 72:g}", "y": f"{y + 8:g}"})


def add_divider(root: ET.Element, *, key: str, y: float, x1: float, x2: float) -> None:
    wrapper = ET.SubElement(root, "object", {"label": "", "petakerjaKey": key, "id": key.replace("/", "-")})
    cell = ET.SubElement(wrapper, "mxCell", {
        "edge": "1", "parent": LAYER_ID,
        "style": "endArrow=none;dashed=1;html=1;rounded=0;strokeWidth=1;",
    })
    geometry = add_geometry(cell, relative=True)
    ET.SubElement(geometry, "mxPoint", {"x": f"{x1:g}", "y": f"{y:g}", "as": "sourcePoint"})
    ET.SubElement(geometry, "mxPoint", {"x": f"{x2:g}", "y": f"{y:g}", "as": "targetPoint"})


def add_operand(root: ET.Element, *, key: str, label: str, x: float, y: float,
                width: float = 230) -> None:
    add_object(
        root,
        key=key,
        cell_id=key.replace("/", "-"),
        label=label,
        style=TEXT_STYLE + "align=left;fontStyle=2;fontSize=10;",
        vertex=True,
        geometry={"x": x, "y": y, "width": width, "height": 20},
    )


PARTICIPANTS = [
    ("user", "User", 90, "pengguna"),
    ("ui", "PetaKerja UI<div><font style=\"font-size: 8px;\">UserMenuManager / AuthModalManager</font></div>", 280, "user-menu-manager"),
    ("auth-manager", "AuthManager", 480, "auth-manager"),
    ("auth-client", "authClient", 680, "auth-client"),
    ("better-auth", "Better Auth API<div><font style=\"font-size: 8px;\">Express /api/auth/*</font></div>", 880, "better-auth"),
    ("google-oauth", "Google OAuth", 1080, "google-oauth"),
    ("profile-api", "PetaKerja Profile API<div><font style=\"font-size: 8px;\">/api/me/auth-profile</font></div>", 1280, "profile-bridge"),
    ("database", "Supabase / PostgreSQL", 1480, "supabase-db"),
]
PARTICIPANT_CENTRES = {f"google-oauth-activation-{slug}": centre for slug, _label, centre, _node in PARTICIPANTS}


MESSAGES = [
    (1, "1. Select Sign in", "user", "ui", 150, False, False),
    (2, "2. requireAuth()", "ui", "auth-manager", 170, False, False),
    (3, "3. openAuthPrompt()", "auth-manager", "ui", 190, False, False),
    (4, "Display Google sign-in prompt", "ui", "user", 210, True, False),
    (5, "4. Select Continue with Google", "user", "ui", 230, False, False),
    (6, "5. signInWithOAuth(&quot;google&quot;)", "ui", "auth-manager", 250, False, False),
    (7, "6. signIn.social({ provider: &quot;google&quot; })", "auth-manager", "auth-client", 270, False, False),
    (8, "7. POST /api/auth/sign-in/social", "auth-client", "better-auth", 290, False, False),
    (9, "8. Redirect to Google OAuth", "better-auth", "google-oauth", 325, False, False),
    (10, "Show account selection and consent", "google-oauth", "user", 345, True, False),
    (11, "9. Select account and grant consent", "user", "google-oauth", 365, False, False),
    (12, "10. GET /api/auth/callback/google", "google-oauth", "better-auth", 385, False, False),
    (13, "11. Create or update user, account and session", "better-auth", "database", 405, False, False),
    (14, "Account and session persisted", "database", "better-auth", 425, True, False),
    (15, "12. Set session cookie and redirect to PetaKerja", "better-auth", "ui", 445, True, False),
    (16, "OAuth rejected, cancelled or failed", "google-oauth", "better-auth", 475, True, False),
    (17, "Remain in guest state / show sign-in error", "better-auth", "ui", 495, True, False),
    (18, "13. init()", "ui", "auth-manager", 535, False, False),
    (19, "14. getSession()", "auth-manager", "auth-client", 555, False, False),
    (20, "15. GET /api/auth/get-session", "auth-client", "better-auth", 575, False, False),
    (21, "Read Better Auth session and user", "better-auth", "database", 595, False, False),
    (22, "Session and user", "database", "better-auth", 615, True, False),
    (23, "Better Auth session", "better-auth", "auth-client", 635, True, False),
    (24, "Session user", "auth-client", "auth-manager", 655, True, False),
    (25, "No authenticated session", "better-auth", "auth-client", 685, True, False),
    (26, "setUser(null); render guest sign-in", "auth-manager", "ui", 705, True, False),
    (27, "16. GET /api/me/auth-profile", "auth-manager", "profile-api", 735, False, False),
    (28, "17. getAppSessionFromHeaders()", "profile-api", "better-auth", 755, False, False),
    (29, "Verified Better Auth user", "better-auth", "profile-api", 775, True, False),
    (30, "18. Find by better_auth_user_id", "profile-api", "database", 835, False, False),
    (31, "Linked public.users profile", "database", "profile-api", 850, True, False),
    (32, "Find existing user by email", "profile-api", "database", 880, False, False),
    (33, "Update better_auth_user_id and profile fields", "profile-api", "database", 900, False, False),
    (34, "INSERT public.users", "profile-api", "database", 930, False, False),
    (35, "Created application profile", "database", "profile-api", 945, True, False),
    (36, "AuthUser profile", "profile-api", "auth-manager", 970, True, False),
    (37, "19. setUser(profile)", "auth-manager", "auth-manager", 990, False, True),
    (38, "20. Notify subscribers", "auth-manager", "ui", 1010, False, False),
    (39, "Render authenticated user menu", "ui", "user", 1030, True, False),
]


def build() -> ET.ElementTree:
    mxfile = ET.Element("mxfile", {
        "host": "Electron",
        "agent": "PetaKerja Architecture Explorer",
        "version": "27.0.2",
    })
    diagram = ET.SubElement(mxfile, "diagram", {
        "name": "Google OAuth Sign In",
        "id": PAGE_ID,
    })
    model = ET.SubElement(diagram, "mxGraphModel", {
        "dx": "1600", "dy": "1100", "grid": "1", "gridSize": "10",
        "guides": "1", "tooltips": "1", "connect": "1", "arrows": "1",
        "fold": "1", "page": "1", "pageScale": "1",
        "pageWidth": "1600", "pageHeight": "1100", "math": "0", "shadow": "0",
    })
    root = ET.SubElement(model, "root")
    ET.SubElement(root, "mxCell", {"id": ROOT_ID})
    ET.SubElement(root, "mxCell", {"id": LAYER_ID, "parent": ROOT_ID})
    background = ET.SubElement(root, "mxCell", {
        "id": "google-oauth-page-background",
        "parent": LAYER_ID,
        "vertex": "1",
        "style": "rounded=0;whiteSpace=wrap;html=1;fillColor=#ffffff;strokeColor=none;locked=1;pointerEvents=0;",
    })
    add_geometry(background, x=0, y=0, width=1600, height=1100)

    add_object(
        root,
        key="google-oauth-sequence/title",
        cell_id="google-oauth-title",
        label="PetaKerja Sign in with Google OAuth Sequence",
        style=TEXT_STYLE + "fontSize=18;fontStyle=1;",
        vertex=True,
        geometry={"x": 500, "y": 20, "width": 600, "height": 30},
    )

    activation_ids: dict[str, str] = {}
    for slug, label, centre, _node in PARTICIPANTS:
        participant_key = f"google-oauth-sequence/participant-{slug}"
        if slug == "user":
            add_object(
                root,
                key=participant_key,
                cell_id="google-oauth-participant-user",
                label="",
                style=ACTOR_STYLE,
                vertex=True,
                geometry={"x": centre - 10, "y": 72, "width": 20, "height": 40},
            )
            add_object(
                root,
                key=participant_key + "-label",
                cell_id="google-oauth-participant-user-label",
                label="User",
                style=TEXT_STYLE,
                vertex=True,
                geometry={"x": centre - 35, "y": 110, "width": 70, "height": 20},
            )
        else:
            add_object(
                root,
                key=participant_key,
                cell_id=f"google-oauth-participant-{slug}",
                label=label,
                style=LIFELINE_STYLE,
                vertex=True,
                geometry={"x": centre - 50, "y": 70, "width": 100, "height": 60},
            )
        activation_id = f"google-oauth-activation-{slug}"
        activation_ids[slug] = activation_id
        add_object(
            root,
            key=participant_key + "-activation",
            cell_id=activation_id,
            label="",
            style=ACTIVATION_STYLE,
            vertex=True,
            geometry={"x": centre - 5, "y": ACTIVATION_Y, "width": 10, "height": ACTIVATION_HEIGHT},
        )

    for key, label, x, y, width, height in (
        ("fragment-oauth", "alt", 55, 305, 1460, 205),
        ("fragment-session", "alt", 55, 515, 1460, 205),
        ("fragment-profile", "alt", 1160, 795, 355, 165),
    ):
        add_object(
            root,
            key=f"google-oauth-sequence/{key}",
            cell_id=f"google-oauth-{key}",
            label=label,
            style=FRAME_STYLE,
            vertex=True,
            geometry={"x": x, "y": y, "width": width, "height": height},
        )

    for index, label, source, target, y, returned, self_message in MESSAGES:
        add_message(
            root,
            index=index,
            label=label,
            source=activation_ids[source],
            target=activation_ids[target],
            y=y,
            returned=returned,
            self_message=self_message,
        )

    add_divider(root, key="google-oauth-sequence/oauth-divider", y=460, x1=55, x2=1515)
    add_operand(root, key="google-oauth-sequence/oauth-success", label="[OAuth authorized]", x=125, y=310)
    add_operand(root, key="google-oauth-sequence/oauth-failure", label="[else: rejected / cancelled / error]", x=70, y=462, width=270)

    add_divider(root, key="google-oauth-sequence/session-divider", y=670, x1=55, x2=1515)
    add_operand(root, key="google-oauth-sequence/session-success", label="[session user exists]", x=125, y=520)
    add_operand(root, key="google-oauth-sequence/session-empty", label="[else: no session]", x=70, y=672)

    add_divider(root, key="google-oauth-sequence/profile-divider-1", y=860, x1=1160, x2=1515)
    add_divider(root, key="google-oauth-sequence/profile-divider-2", y=910, x1=1160, x2=1515)
    add_operand(root, key="google-oauth-sequence/profile-found", label="[better_auth_user_id found]", x=1215, y=800, width=240)
    add_operand(root, key="google-oauth-sequence/profile-email", label="[else: email match]", x=1172, y=862, width=220)
    add_operand(root, key="google-oauth-sequence/profile-create", label="[else: no profile]", x=1172, y=912, width=220)

    add_object(
        root,
        key="google-oauth-sequence/note",
        cell_id="google-oauth-note",
        label="Google OAuth only. Password sign-in is intentionally unavailable in PetaKerja.",
        style=TEXT_STYLE + "fontSize=10;fontStyle=2;fontColor=#555555;",
        vertex=True,
        geometry={"x": 400, "y": 1062, "width": 800, "height": 20},
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
