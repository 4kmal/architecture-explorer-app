#!/usr/bin/env python3
"""Build the remaining PetaKerja Administrator flow charts.

The TTTE1113 Flow Chart Template is a read-only style source.  The diagrams
use a centred success path and separate outer lanes for exceptional outcomes,
matching the readability standard established by the reorganized Google
sign-in flow chart.
"""

from __future__ import annotations

import re
import shutil
import subprocess
import xml.etree.ElementTree as ET
from collections import Counter, defaultdict, deque
from dataclasses import dataclass, field
from pathlib import Path
from paths import DIAGRAMS, DRAWIO, TEMPLATES

TEMPLATE = TEMPLATES / "Flow Chart Template.drawio"
EXPLORER = Path(__file__).resolve().parents[1]


def template_style(predicate) -> str:
    root = ET.parse(TEMPLATE).getroot()
    for cell in root.findall(".//mxCell"):
        style = cell.get("style", "")
        if predicate(cell, style):
            return style
    raise RuntimeError("Required style was not found in Flow Chart Template.drawio")


def strip_properties(style: str, names: tuple[str, ...]) -> str:
    for name in names:
        style = re.sub(rf"(?:^|;){name}=[^;]*;?", ";", style)
    return style.strip(";")


START_STYLE = template_style(lambda _cell, style: "shape=mxgraph.flowchart.start_1" in style)
DECISION_STYLE = template_style(lambda _cell, style: "shape=mxgraph.flowchart.decision" in style)
PROCESS_STYLE = template_style(
    lambda cell, style: cell.get("vertex") == "1"
    and "shape=mxgraph.flowchart" not in style
    and cell.find("mxGeometry") is not None
    and float(cell.find("mxGeometry").get("width", "0")) >= 100
)

THEME_STYLE = (
    "fillColor=light-dark(#ffffff,#151a22);"
    "strokeColor=light-dark(#111827,#d8dde7);"
    "fontColor=light-dark(#111827,#eef1f6);"
)
START_STYLE = strip_properties(START_STYLE, ("fillColor", "strokeColor", "fontColor")) + ";" + THEME_STYLE
DECISION_STYLE = strip_properties(DECISION_STYLE, ("fillColor", "strokeColor", "fontColor")) + ";" + THEME_STYLE
PROCESS_STYLE = strip_properties(PROCESS_STYLE, ("fillColor", "strokeColor", "fontColor")) + ";" + THEME_STYLE
TEXT_STYLE = (
    "text;html=1;whiteSpace=wrap;strokeColor=none;fillColor=none;"
    "align=center;verticalAlign=middle;fontColor=light-dark(#111827,#eef1f6);"
)
NOTE_STYLE = TEXT_STYLE + "align=left;fontSize=11;fontStyle=2;"
FLOW_STYLE = (
    "edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;"
    "endArrow=classic;endFill=1;strokeWidth=2;"
    "strokeColor=light-dark(#111827,#d8dde7);"
    "fontColor=light-dark(#111827,#eef1f6);labelBackgroundColor=none;"
)

VERTICAL = "exitX=0.5;exitY=1;entryX=0.5;entryY=0;exitPerimeter=0;entryPerimeter=0;"
RIGHT = "exitX=1;exitY=0.5;entryX=0;entryY=0.5;exitPerimeter=0;entryPerimeter=0;"
LEFT = "exitX=0;exitY=0.5;entryX=1;entryY=0.5;exitPerimeter=0;entryPerimeter=0;"
END_RIGHT = "exitX=1;exitY=0.5;entryX=1;entryY=0.5;exitPerimeter=0;entryPerimeter=0;"
END_LEFT = "exitX=0;exitY=0.5;entryX=0;entryY=0.5;exitPerimeter=0;entryPerimeter=0;"
DOWN_LEFT = "exitX=0.3;exitY=1;entryX=0.5;entryY=0;exitPerimeter=0;entryPerimeter=0;"
DOWN_RIGHT = "exitX=0.7;exitY=1;entryX=0.5;entryY=0;exitPerimeter=0;entryPerimeter=0;"


@dataclass(frozen=True)
class Node:
    key: str
    label: str
    kind: str
    x: float
    y: float
    width: float
    height: float


@dataclass(frozen=True)
class Edge:
    key: str
    source: str
    target: str
    label: str = ""
    points: tuple[tuple[float, float], ...] = ()
    style: str = VERTICAL
    label_x: float | None = None
    label_y: float | None = None


@dataclass(frozen=True)
class Chart:
    diagram_id: str
    page_id: str
    page_name: str
    file_stem: str
    editor_filename: str
    width: int
    height: int
    title: str
    subtitle: str
    precondition: str
    notes: tuple[str, ...]
    nodes: tuple[Node, ...]
    edges: tuple[Edge, ...]
    decision_branches: dict[str, tuple[str, ...]] = field(default_factory=dict)


def n(key: str, label: str, kind: str, x: float, y: float, width: float, height: float) -> Node:
    return Node(key, label, kind, x, y, width, height)


def e(key: str, source: str, target: str, label: str = "", *,
      points: tuple[tuple[float, float], ...] = (), style: str = VERTICAL,
      label_x: float | None = None, label_y: float | None = None) -> Edge:
    return Edge(key, source, target, label, points, style, label_x, label_y)


ACCESS_DASHBOARD = Chart(
    diagram_id="admin-access-dashboard-flowchart",
    page_id="petakerja_flow_admin_access_dashboard",
    page_name="PetaKerja Access Administrator Dashboard",
    file_stem="Flow Chart PetaKerja - Access Administrator Dashboard",
    editor_filename="flowchart-admin-access-dashboard.drawio",
    width=980,
    height=1500,
    title="PetaKerja Access Administrator Dashboard Flow Chart",
    subtitle="Administrator entry, local access guard and protected dashboard-data loading.",
    precondition="The Administrator entry is selected from the signed-in user menu or the /admin route is opened directly.",
    notes=(
        "Protected provider, usage and user requests repeat the Better Auth session and admin/owner role checks on the server.",
        "Blog statistics are loaded separately only when the Blog section is selected.",
    ),
    nodes=(
        n("start", "Start", "start", 456.665, 135, 66.67, 40),
        n("select-dashboard", "Administrator selects the Admin Dashboard", "process", 380, 205, 220, 50),
        n("check-user", "Check the current signed-in user", "process", 390, 285, 200, 50),
        n("session-active", "Active session found?", "decision", 430, 375, 120, 70),
        n("sign-in-required", "Return to PetaKerja and request administrator sign-in", "process", 690, 380, 220, 60),
        n("role-allowed", "Administrator role allowed?", "decision", 430, 495, 120, 70),
        n("access-denied", "Return to PetaKerja and deny administrator access", "process", 70, 500, 220, 60),
        n("open-dashboard", "Open the administrator dashboard", "process", 390, 615, 200, 50),
        n("loading-state", "Display the dashboard loading state", "process", 385, 695, 210, 50),
        n("request-admin-data", "Request provider, AI usage and user information", "process", 365, 775, 250, 60),
        n("retrieve-admin-data", "Retrieve the three protected dashboard data sets", "process", 370, 865, 240, 60),
        n("request-successful", "Dashboard requests successful?", "decision", 430, 965, 120, 70),
        n("request-error", "Clear loading and display the dashboard loading error", "process", 690, 970, 220, 60),
        n("store-admin-data", "Store the returned provider, usage and user information", "process", 365, 1085, 250, 60),
        n("clear-loading", "Clear the dashboard loading state", "process", 390, 1175, 200, 50),
        n("display-overview", "Display the administrator Overview", "process", 390, 1245, 200, 55),
        n("end", "End", "start", 456.665, 1340, 66.67, 40),
    ),
    edges=(
        e("start-to-select", "start", "select-dashboard"),
        e("select-to-check", "select-dashboard", "check-user"),
        e("check-to-session", "check-user", "session-active"),
        e("session-no", "session-active", "sign-in-required", "No", style=RIGHT),
        e("sign-in-to-end", "sign-in-required", "end", points=((950, 410), (950, 1360)), style=END_RIGHT),
        e("session-yes", "session-active", "role-allowed", "Yes"),
        e("role-no", "role-allowed", "access-denied", "No", style=LEFT),
        e("denied-to-end", "access-denied", "end", points=((30, 530), (30, 1360)), style=END_LEFT),
        e("role-yes", "role-allowed", "open-dashboard", "Yes"),
        e("open-to-loading", "open-dashboard", "loading-state"),
        e("loading-to-request", "loading-state", "request-admin-data"),
        e("request-to-retrieve", "request-admin-data", "retrieve-admin-data"),
        e("retrieve-to-result", "retrieve-admin-data", "request-successful"),
        e("request-no", "request-successful", "request-error", "No", style=RIGHT),
        e("error-to-end", "request-error", "end", points=((925, 1000), (925, 1360)), style=END_RIGHT),
        e("request-yes", "request-successful", "store-admin-data", "Yes"),
        e("store-to-clear", "store-admin-data", "clear-loading"),
        e("clear-to-overview", "clear-loading", "display-overview"),
        e("overview-to-end", "display-overview", "end"),
    ),
    decision_branches={"session-active": ("No", "Yes"), "role-allowed": ("No", "Yes"), "request-successful": ("No", "Yes")},
)


MONITOR_ACTIVITY = Chart(
    diagram_id="admin-monitor-activity-flowchart",
    page_id="petakerja_flow_admin_monitor_activity",
    page_name="PetaKerja Monitor System Activity Logs",
    file_stem="Flow Chart PetaKerja - Monitor System Activity Logs",
    editor_filename="flowchart-admin-monitor-activity.drawio",
    width=980,
    height=1200,
    title="PetaKerja Administrator Monitor System Activity Logs Flow Chart",
    subtitle="Current implementation: the latest 100 AI assistant usage events, not general server logs.",
    precondition="The Administrator is signed in, has the admin or owner role, and the Admin Dashboard is open.",
    notes=(
        "The Usage section reads public.ai_usage_events and calculates request, error, token and estimated-cost totals.",
        "General server logs and public.ai_admin_audit_logs are not displayed by this use case.",
    ),
    nodes=(
        n("start", "Start", "start", 456.665, 145, 66.67, 40),
        n("select-usage", "Administrator selects the Usage section", "process", 390, 220, 200, 50),
        n("loading-state", "Display the loading state", "process", 400, 305, 180, 50),
        n("request-activity", "Request recent AI activity information", "process", 380, 390, 220, 50),
        n("retrieve-activity", "Retrieve up to 100 recent AI usage events and calculate totals", "process", 360, 475, 260, 65),
        n("request-successful", "Request successful?", "decision", 430, 580, 120, 70),
        n("request-error", "Clear loading and display the dashboard loading error", "process", 680, 585, 220, 60),
        n("store-activity", "Store the activity rows and totals, then clear loading", "process", 365, 700, 250, 60),
        n("events-returned", "Activity events returned?", "decision", 430, 800, 120, 70),
        n("empty-state", "Display No usage events yet", "process", 90, 805, 200, 60),
        n("display-activity", "Display usage totals and the activity table", "process", 375, 900, 230, 60),
        n("end", "End", "start", 456.665, 1035, 66.67, 40),
    ),
    edges=(
        e("start-to-select", "start", "select-usage"),
        e("select-to-loading", "select-usage", "loading-state"),
        e("loading-to-request", "loading-state", "request-activity"),
        e("request-to-retrieve", "request-activity", "retrieve-activity"),
        e("retrieve-to-result", "retrieve-activity", "request-successful"),
        e("request-no", "request-successful", "request-error", "No", style=RIGHT),
        e("error-to-end", "request-error", "end", points=((930, 615), (930, 1055)), style=END_RIGHT),
        e("request-yes", "request-successful", "store-activity", "Yes"),
        e("store-to-events", "store-activity", "events-returned"),
        e("events-no", "events-returned", "empty-state", "No", style=LEFT),
        e("empty-to-end", "empty-state", "end", points=((50, 835), (50, 1055)), style=END_LEFT),
        e("events-yes", "events-returned", "display-activity", "Yes"),
        e("display-to-end", "display-activity", "end"),
    ),
    decision_branches={"request-successful": ("No", "Yes"), "events-returned": ("No", "Yes")},
)


MANAGE_AI = Chart(
    diagram_id="admin-manage-ai-configuration-flowchart",
    page_id="petakerja_flow_admin_manage_ai_configuration",
    page_name="PetaKerja Manage AI Chatbot Configuration",
    file_stem="Flow Chart PetaKerja - Manage AI Chatbot Configuration",
    editor_filename="flowchart-admin-manage-ai-configuration.drawio",
    width=1400,
    height=2050,
    title="PetaKerja Administrator Manage AI Chatbot Configuration Flow Chart",
    subtitle="Provider visibility for administrators and owners; shared-key and model-refresh actions are owner-only.",
    precondition="The Administrator is signed in, has the admin or owner role, and the Admin Dashboard is open.",
    notes=(
        "Individual users' model preferences are outside this administrator use case.",
        "Deployment warning: the refresh handler expects custom_headers, fetched_models, models_fetched_at and fetch_error, but those fields are absent from the live ai_provider_credentials table snapshot.",
    ),
    nodes=(
        n("start", "Start", "start", 666.665, 125, 66.67, 40),
        n("select-providers", "Administrator selects the AI Providers section", "process", 590, 190, 220, 50),
        n("loading-state", "Display the loading state", "process", 610, 260, 180, 50),
        n("request-providers", "Request provider configuration", "process", 590, 330, 220, 50),
        n("retrieve-providers", "Read platform credentials and combine them with the provider registry", "process", 570, 400, 260, 60),
        n("request-successful", "Request successful?", "decision", 640, 490, 120, 70),
        n("request-error", "Clear loading and display the provider loading error", "process", 1080, 495, 250, 60),
        n("display-providers", "Display provider names, key status, model counts and fetch status", "process", 565, 590, 270, 60),
        n("owner-role", "Owner role?", "decision", 640, 680, 120, 70),
        n("read-only", "Display provider information in read-only mode and explain the owner requirement", "process", 80, 685, 300, 65),
        n("owner-action", "Owner action?", "decision", 640, 785, 120, 70),
        n("open-key-modal", "Open the platform-key dialog", "process", 170, 900, 220, 50),
        n("enter-key", "Enter and submit a platform API key", "process", 170, 980, 220, 50),
        n("key-valid", "Provider and key valid?", "decision", 220, 1065, 120, 70),
        n("validation-error", "Display the platform-key validation error", "process", 55, 1170, 245, 60),
        n("save-credential", "Encrypt and save the shared platform credential", "process", 390, 1170, 260, 60),
        n("save-successful", "Credential saved successfully?", "decision", 460, 1270, 120, 70),
        n("save-error", "Display the platform-key request error", "process", 125, 1370, 245, 60),
        n("record-audit", "Record the platform key saved audit event", "process", 390, 1370, 260, 60),
        n("save-success", "Display success for the saved platform key", "process", 400, 1460, 240, 60),
        n("request-refresh", "Request model-list refresh", "process", 1030, 900, 230, 50),
        n("read-credentials", "Read available platform credentials", "process", 1030, 980, 230, 50),
        n("refresh-providers", "Refresh every supported provider and continue after individual failures", "process", 995, 1065, 300, 65),
        n("any-failures", "Any provider failures?", "decision", 1085, 1170, 120, 70),
        n("refresh-complete", "Save model metadata, invalidate caches and display complete success", "process", 820, 1290, 270, 65),
        n("refresh-partial", "Save successful metadata, record errors and display partial results", "process", 1140, 1290, 230, 65),
        n("reload-refresh", "Reload the provider table", "process", 1010, 1420, 270, 55),
        n("reload-providers", "Reload provider information and display the result", "process", 565, 1660, 270, 60),
        n("end", "End", "start", 666.665, 1800, 66.67, 40),
    ),
    edges=(
        e("start-to-select", "start", "select-providers"),
        e("select-to-loading", "select-providers", "loading-state"),
        e("loading-to-request", "loading-state", "request-providers"),
        e("request-to-retrieve", "request-providers", "retrieve-providers"),
        e("retrieve-to-result", "retrieve-providers", "request-successful"),
        e("request-no", "request-successful", "request-error", "No", style=RIGHT),
        e("request-error-to-end", "request-error", "end", points=((1380, 525), (1380, 1820)), style=END_RIGHT),
        e("request-yes", "request-successful", "display-providers", "Yes"),
        e("display-to-owner", "display-providers", "owner-role"),
        e("owner-no", "owner-role", "read-only", "No", style=LEFT),
        e("read-only-to-end", "read-only", "end", points=((20, 717), (20, 1820)), style=END_LEFT),
        e("owner-yes", "owner-role", "owner-action", "Yes"),
        e("action-save", "owner-action", "open-key-modal", "Save key", points=((440, 820), (440, 925)), style=LEFT),
        e("action-refresh", "owner-action", "request-refresh", "Refresh models", points=((960, 820), (960, 925)), style=RIGHT),
        # Keep the label beside the decision.  Without an explicit edge-label
        # position Draw.io centres it on the long outer lane beside the model
        # refresh result, which makes the branch look attached to that box.
        e("action-finish", "owner-action", "end", "Finish", points=((1390, 820), (1390, 1820)),
          style=END_RIGHT, label_x=-0.97, label_y=-8),
        e("modal-to-enter", "open-key-modal", "enter-key"),
        e("enter-to-valid", "enter-key", "key-valid"),
        e("valid-no", "key-valid", "validation-error", "No", style=DOWN_LEFT),
        e("validation-to-end", "validation-error", "end", points=((30, 1200), (30, 1820)), style=END_LEFT),
        e("valid-yes", "key-valid", "save-credential", "Yes", style=DOWN_RIGHT),
        e("save-to-result", "save-credential", "save-successful"),
        e("save-no", "save-successful", "save-error", "No", style=DOWN_LEFT),
        e("save-error-to-end", "save-error", "end", points=((45, 1400), (45, 1820)), style=END_LEFT),
        e("save-yes", "save-successful", "record-audit", "Yes"),
        e("audit-to-success", "record-audit", "save-success"),
        e("save-success-to-reload", "save-success", "reload-providers", points=((520, 1520), (520, 1690)), style=RIGHT),
        e("refresh-to-credentials", "request-refresh", "read-credentials"),
        e("credentials-to-provider", "read-credentials", "refresh-providers"),
        e("provider-to-result", "refresh-providers", "any-failures"),
        e("failures-no", "any-failures", "refresh-complete", "No", style=DOWN_LEFT),
        e("failures-yes", "any-failures", "refresh-partial", "Yes", style=DOWN_RIGHT),
        e("complete-to-refresh-reload", "refresh-complete", "reload-refresh", points=((955, 1390),), style=RIGHT),
        e("partial-to-refresh-reload", "refresh-partial", "reload-refresh", points=((1255, 1390),), style=LEFT),
        e("refresh-reload-to-result", "reload-refresh", "reload-providers", points=((1145, 1690), (860, 1690)), style=LEFT),
        e("reload-to-end", "reload-providers", "end"),
    ),
    decision_branches={
        "request-successful": ("No", "Yes"),
        "owner-role": ("No", "Yes"),
        "owner-action": ("Finish", "Refresh models", "Save key"),
        "key-valid": ("No", "Yes"),
        "save-successful": ("No", "Yes"),
        "any-failures": ("No", "Yes"),
    },
)


ADMIN_SIGN_OUT = Chart(
    diagram_id="admin-sign-out-flowchart",
    page_id="petakerja_flow_admin_sign_out",
    page_name="PetaKerja Administrator Sign Out",
    file_stem="Flow Chart PetaKerja - Administrator Sign Out",
    editor_filename="flowchart-admin-sign-out.drawio",
    width=980,
    height=1100,
    title="PetaKerja Administrator Sign Out Flow Chart",
    subtitle="Better Auth sign-out followed by application-state and administrator-dashboard synchronization.",
    precondition="The Administrator is signed in and an authenticated Sign Out control is available.",
    notes=(
        "If sign-out fails, the current implementation logs the failure, preserves the session and re-enables the available Sign Out control.",
        "After successful sign-out, an open administrator dashboard renders its signed-out access state.",
    ),
    nodes=(
        n("start", "Start", "start", 456.665, 145, 66.67, 40),
        n("select-sign-out", "Administrator selects Sign Out", "process", 390, 220, 200, 50),
        n("pending-state", "Disable the available Sign Out control", "process", 390, 300, 200, 50),
        n("request-sign-out", "Submit the sign-out request to Better Auth", "process", 375, 380, 230, 55),
        n("sign-out-successful", "Sign-out successful?", "decision", 430, 480, 120, 70),
        n("sign-out-failure", "Keep the current session and re-enable Sign Out", "process", 680, 485, 220, 60),
        n("invalidate-session", "Invalidate the session and clear its cookie", "process", 380, 600, 220, 55),
        n("clear-user", "Clear the PetaKerja user state", "process", 390, 685, 200, 50),
        n("notify-subscribers", "Notify authentication subscribers", "process", 390, 765, 200, 50),
        n("display-signed-out", "Display the signed-out dashboard access state and guest menu", "process", 360, 845, 260, 60),
        n("end", "End", "start", 456.665, 960, 66.67, 40),
    ),
    edges=(
        e("start-to-select", "start", "select-sign-out"),
        e("select-to-pending", "select-sign-out", "pending-state"),
        e("pending-to-request", "pending-state", "request-sign-out"),
        e("request-to-result", "request-sign-out", "sign-out-successful"),
        e("result-no", "sign-out-successful", "sign-out-failure", "No", style=RIGHT),
        e("failure-to-end", "sign-out-failure", "end", points=((930, 515), (930, 980)), style=END_RIGHT),
        e("result-yes", "sign-out-successful", "invalidate-session", "Yes"),
        e("session-to-user", "invalidate-session", "clear-user"),
        e("user-to-notify", "clear-user", "notify-subscribers"),
        e("notify-to-display", "notify-subscribers", "display-signed-out"),
        e("display-to-end", "display-signed-out", "end"),
    ),
    decision_branches={"sign-out-successful": ("No", "Yes")},
)


CHARTS = (ACCESS_DASHBOARD, MONITOR_ACTIVITY, MANAGE_AI, ADMIN_SIGN_OUT)


def geometry(cell: ET.Element, *, x: float | None = None, y: float | None = None,
             width: float | None = None, height: float | None = None,
             relative: bool = False, points: tuple[tuple[float, float], ...] = ()) -> ET.Element:
    attrs = {"as": "geometry"}
    if relative:
        attrs["relative"] = "1"
    node = ET.SubElement(cell, "mxGeometry", attrs)
    for name, value in (("x", x), ("y", y), ("width", width), ("height", height)):
        if value is not None:
            node.set(name, f"{value:g}")
    if points:
        array = ET.SubElement(node, "Array", {"as": "points"})
        for px, py in points:
            ET.SubElement(array, "mxPoint", {"x": f"{px:g}", "y": f"{py:g}"})
    return node


def build(chart: Chart) -> ET.ElementTree:
    prefix = chart.diagram_id
    root_id = f"{prefix}-root"
    layer_id = f"{prefix}-layer"
    key_prefix = f"{prefix}/"

    mxfile = ET.Element("mxfile", {"host": "Electron", "agent": "PetaKerja Architecture Explorer", "version": "27.0.2"})
    diagram = ET.SubElement(mxfile, "diagram", {"name": chart.page_name, "id": chart.page_id})
    model = ET.SubElement(diagram, "mxGraphModel", {
        "dx": str(chart.width), "dy": str(chart.height), "grid": "1", "gridSize": "10",
        "guides": "1", "tooltips": "1", "connect": "1", "arrows": "1", "fold": "1",
        "page": "1", "pageScale": "1", "pageWidth": str(chart.width), "pageHeight": str(chart.height),
        "math": "0", "shadow": "0", "background": "light-dark(#ffffff,#0f131a)",
    })
    graph_root = ET.SubElement(model, "root")
    ET.SubElement(graph_root, "mxCell", {"id": root_id})
    ET.SubElement(graph_root, "mxCell", {"id": layer_id, "parent": root_id})

    def add_vertex(key: str, label: str, style: str, x: float, y: float, width: float, height: float,
                   *, interactive: bool = True) -> str:
        object_id = f"{prefix}-{key}"
        attrs = {"id": object_id, "label": label}
        if interactive:
            attrs["petakerjaKey"] = key_prefix + key
        wrapper = ET.SubElement(graph_root, "object", attrs)
        cell = ET.SubElement(wrapper, "mxCell", {"parent": layer_id, "vertex": "1", "style": style})
        geometry(cell, x=x, y=y, width=width, height=height)
        return object_id

    add_vertex("page-background", "", "rounded=0;whiteSpace=wrap;html=1;fillColor=light-dark(#ffffff,#0f131a);strokeColor=none;pointerEvents=0;locked=1;", 0, 0, chart.width, chart.height, interactive=False)
    add_vertex("title", chart.title, TEXT_STYLE + "fontSize=22;fontStyle=1;", 120, 18, chart.width - 240, 38, interactive=False)
    add_vertex("subtitle", chart.subtitle, TEXT_STYLE + "fontSize=11;fontStyle=2;", 100, 58, chart.width - 200, 30, interactive=False)
    add_vertex("precondition", f"Precondition: {chart.precondition}", NOTE_STYLE, 100, 92, chart.width - 200, 32, interactive=False)

    ids: dict[str, str] = {}
    styles = {"start": START_STYLE, "process": PROCESS_STYLE, "decision": DECISION_STYLE}
    for node in chart.nodes:
        ids[node.key] = add_vertex(node.key, node.label, styles[node.kind], node.x, node.y, node.width, node.height)

    for edge in chart.edges:
        wrapper = ET.SubElement(graph_root, "object", {
            "id": f"{prefix}-{edge.key}", "label": edge.label, "petakerjaKey": key_prefix + edge.key,
        })
        cell = ET.SubElement(wrapper, "mxCell", {
            "parent": layer_id, "edge": "1", "source": ids[edge.source], "target": ids[edge.target],
            "style": FLOW_STYLE + edge.style,
        })
        geometry(cell, x=edge.label_x, y=edge.label_y, relative=True, points=edge.points)

    note_y = chart.height - 58 - (len(chart.notes) - 1) * 24
    for index, note in enumerate(chart.notes):
        add_vertex(f"note-{index + 1}", note, NOTE_STYLE, 80, note_y + index * 24, chart.width - 160, 24, interactive=False)
    return ET.ElementTree(mxfile)


def validate(chart: Chart, path: Path) -> None:
    parsed = ET.parse(path).getroot()
    diagrams = parsed.findall("diagram")
    if len(diagrams) != 1 or diagrams[0].get("id") != chart.page_id:
        raise RuntimeError(f"{chart.diagram_id}: expected one normalized page")
    model = diagrams[0].find("mxGraphModel")
    if model is None or model.get("pageWidth") != str(chart.width) or model.get("pageHeight") != str(chart.height):
        raise RuntimeError(f"{chart.diagram_id}: wrong page dimensions")

    wrappers = parsed.findall(".//object")
    ids = [wrapper.get("id", "") for wrapper in wrappers]
    if any(not item for item in ids) or len(ids) != len(set(ids)):
        raise RuntimeError(f"{chart.diagram_id}: missing or duplicate object IDs")
    keyed = [wrapper.get("petakerjaKey", "") for wrapper in wrappers if wrapper.get("petakerjaKey")]
    if any(count > 1 for count in Counter(keyed).values()):
        raise RuntimeError(f"{chart.diagram_id}: duplicate petakerjaKey values")

    prefix = f"{chart.diagram_id}/"
    expected_components = {node.key for node in chart.nodes}
    vertices: dict[str, str] = {}
    edges: list[ET.Element] = []
    for wrapper in wrappers:
        cell = wrapper.find("mxCell")
        if cell is None:
            raise RuntimeError(f"{chart.diagram_id}: object {wrapper.get('id')} has no mxCell")
        if cell.get("vertex") == "1":
            geo = cell.find("mxGeometry")
            if geo is None:
                raise RuntimeError(f"{chart.diagram_id}: vertex {wrapper.get('id')} has no geometry")
            x, y = float(geo.get("x", "0")), float(geo.get("y", "0"))
            width, height = float(geo.get("width", "0")), float(geo.get("height", "0"))
            if min(x, y) < 0 or x + width > chart.width or y + height > chart.height:
                raise RuntimeError(f"{chart.diagram_id}: vertex {wrapper.get('id')} overflows the page")
            stable_key = wrapper.get("petakerjaKey", "")
            if stable_key.startswith(prefix):
                vertices[wrapper.get("id", "")] = stable_key[len(prefix):]
        elif cell.get("edge") == "1":
            edges.append(wrapper)

    if set(vertices.values()) != expected_components or len(vertices) != len(expected_components):
        raise RuntimeError(f"{chart.diagram_id}: canonical component set does not match the specification")
    if len(edges) != len(chart.edges):
        raise RuntimeError(f"{chart.diagram_id}: expected {len(chart.edges)} connectors, found {len(edges)}")

    outgoing: dict[str, list[tuple[str, str]]] = defaultdict(list)
    incoming: dict[str, list[str]] = defaultdict(list)
    for wrapper in edges:
        cell = wrapper.find("mxCell")
        source, target = cell.get("source", ""), cell.get("target", "")
        if source not in vertices or target not in vertices:
            raise RuntimeError(f"{chart.diagram_id}: connector {wrapper.get('id')} has a missing endpoint")
        if "endArrow=classic" not in cell.get("style", "") or "endFill=1" not in cell.get("style", ""):
            raise RuntimeError(f"{chart.diagram_id}: connector {wrapper.get('id')} is not a filled classic flow arrow")
        for point in cell.findall(".//mxPoint"):
            px, py = float(point.get("x", "0")), float(point.get("y", "0"))
            if px < 0 or py < 0 or px > chart.width or py > chart.height:
                raise RuntimeError(f"{chart.diagram_id}: connector point falls outside the page")
        outgoing[source].append((target, wrapper.get("label", "")))
        incoming[target].append(source)

    by_key = {key: object_id for object_id, key in vertices.items()}
    for decision, expected in chart.decision_branches.items():
        labels = tuple(sorted(label for _target, label in outgoing[by_key[decision]]))
        if labels != tuple(sorted(expected)):
            raise RuntimeError(f"{chart.diagram_id}: decision {decision} has branches {labels}, expected {expected}")

    reachable: set[str] = set()
    queue = deque([by_key["start"]])
    while queue:
        current = queue.popleft()
        if current in reachable:
            continue
        reachable.add(current)
        queue.extend(target for target, _label in outgoing[current])
    if reachable != set(vertices):
        missing = sorted(vertices[item] for item in set(vertices) - reachable)
        raise RuntimeError(f"{chart.diagram_id}: components not reachable from Start: {missing}")

    can_reach_end: set[str] = set()
    queue = deque([by_key["end"]])
    while queue:
        current = queue.popleft()
        if current in can_reach_end:
            continue
        can_reach_end.add(current)
        queue.extend(incoming[current])
    if can_reach_end != set(vertices):
        missing = sorted(vertices[item] for item in set(vertices) - can_reach_end)
        raise RuntimeError(f"{chart.diagram_id}: components without a path to End: {missing}")


def write_xml(tree: ET.ElementTree, destination: Path) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    ET.indent(tree, space="  ")
    tree.write(destination, encoding="utf-8", xml_declaration=True)


def export(chart: Chart, source: Path) -> tuple[Path, Path]:
    svg = DIAGRAMS / f"{chart.file_stem}.svg"
    png = DIAGRAMS / f"{chart.file_stem}.png"
    subprocess.run([str(DRAWIO), "--export", "--format", "svg", "--page-index", "0", "--output", str(svg), str(source)], check=True)
    subprocess.run([str(DRAWIO), "--export", "--format", "png", "--page-index", "0", "--scale", "2", "--output", str(png), str(source)], check=True)
    return svg, png


def main() -> None:
    if not TEMPLATE.exists():
        raise FileNotFoundError(TEMPLATE)
    if not DRAWIO.exists():
        raise FileNotFoundError(DRAWIO)
    for chart in CHARTS:
        output = DIAGRAMS / f"{chart.file_stem}.drawio"
        editor = EXPLORER / "assets" / "editor" / chart.editor_filename.replace(".drawio", "-original.drawio")
        write_xml(build(chart), output)
        validate(chart, output)
        editor.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(output, editor)
        svg, png = export(chart, output)
        print(f"{chart.diagram_id}: {len(chart.nodes)} components, {len(chart.edges)} connectors")
        print(f"  Draw.io: {output}")
        print(f"  SVG: {svg}")
        print(f"  PNG: {png}")
        print(f"  Editor: {editor}")


if __name__ == "__main__":
    main()
