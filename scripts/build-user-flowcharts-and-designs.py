#!/usr/bin/env python3
"""Build PetaKerja user flow charts and editable design diagrams.

The flow charts reuse the TTTE1113 template styles and the readability rules
used by the existing Administrator charts.  The design diagrams faithfully
rebuild the two report D2 views as editable Draw.io documents.
"""

from __future__ import annotations

import importlib.util
import re
import shutil
import subprocess
import sys
import tempfile
import xml.etree.ElementTree as ET
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from paths import DIAGRAMS, DRAWIO


EXPLORER = Path(__file__).resolve().parents[1]
EDITOR = EXPLORER / "assets" / "editor"


def load_flow_module():
    path = Path(__file__).with_name("build-admin-flowcharts.py")
    spec = importlib.util.spec_from_file_location("petakerja_flow_builder", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to import {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


flow = load_flow_module()


def n(key: str, label: str, kind: str, x: float, y: float, width: float, height: float):
    return flow.n(key, label, kind, x, y, width, height)


def e(key: str, source: str, target: str, label: str = "", **kwargs):
    return flow.e(key, source, target, label, **kwargs)


SEARCH_JOBS = flow.Chart(
    diagram_id="user-search-jobs-flowchart",
    page_id="petakerja_flow_user_search_jobs",
    page_name="PetaKerja Search Jobs",
    file_stem="Flow Chart PetaKerja - Search Jobs",
    editor_filename="flowchart-user-search-jobs.drawio",
    width=1100,
    height=1550,
    title="PetaKerja Search Jobs Flow Chart",
    subtitle="Public Daily Index search with fresh-cache, database, stale-cache, empty and failure outcomes.",
    precondition="The User has opened PetaKerja; Google sign-in is not required for Daily Index search.",
    notes=(
        "Daily Index reads public.scraped_jobs through GET /api/jobs/supa and does not trigger live scraping.",
        "View Job Details and Save or Update Job Status are separate use cases and are not included here.",
    ),
    nodes=(
        n("start", "Start", "start", 516.665, 110, 66.67, 40),
        n("open-job-finder", "Open the Job Finder", "process", 440, 180, 220, 50),
        n("enter-criteria", "Enter a job title, location and filters", "process", 425, 255, 250, 55),
        n("select-search", "Select Search", "process", 455, 335, 190, 50),
        n("prepare-search", "Clear previous results and display the loading state", "process", 405, 410, 290, 60),
        n("request-daily-index", "Request matching jobs from the Daily Index", "process", 420, 495, 260, 55),
        n("fresh-cache", "Fresh cached response available?", "decision", 490, 585, 120, 70),
        n("use-fresh-cache", "Use the fresh cached job results", "process", 80, 590, 240, 55),
        n("retrieve-jobs", "Retrieve matching jobs from the database", "process", 420, 700, 260, 55),
        n("request-successful", "Job request successful?", "decision", 490, 790, 120, 70),
        n("filter-rank", "Filter, rank and paginate the job results", "process", 420, 905, 260, 55),
        n("stale-cache", "Stale cached response available?", "decision", 800, 790, 120, 70),
        n("use-stale-cache", "Use the stale cached job results", "process", 750, 905, 220, 55),
        n("display-error", "Clear loading and display the Daily Index error", "process", 820, 1000, 250, 60),
        n("apply-client-filters", "Apply profile matching and selected filters", "process", 420, 1030, 260, 55),
        n("jobs-returned", "Matching jobs returned?", "decision", 490, 1135, 120, 70),
        n("display-results", "Display job cards, result count, sources and map markers", "process", 400, 1250, 300, 65),
        n("empty-state", "Display No matching jobs", "process", 90, 1255, 220, 55),
        n("clear-loading", "Clear the loading state", "process", 450, 1350, 200, 50),
        n("end", "End", "start", 516.665, 1435, 66.67, 40),
    ),
    edges=(
        e("start-open", "start", "open-job-finder"),
        e("open-criteria", "open-job-finder", "enter-criteria"),
        e("criteria-search", "enter-criteria", "select-search"),
        e("search-prepare", "select-search", "prepare-search"),
        e("prepare-request", "prepare-search", "request-daily-index"),
        e("request-cache", "request-daily-index", "fresh-cache"),
        e("cache-yes", "fresh-cache", "use-fresh-cache", "Yes", style=flow.LEFT),
        e("fresh-to-client", "use-fresh-cache", "apply-client-filters", points=((45, 617), (45, 1057), (405, 1057)), style=flow.RIGHT),
        e("cache-no", "fresh-cache", "retrieve-jobs", "No"),
        e("retrieve-result", "retrieve-jobs", "request-successful"),
        e("request-yes", "request-successful", "filter-rank", "Yes"),
        e("rank-to-client", "filter-rank", "apply-client-filters"),
        e("request-no", "request-successful", "stale-cache", "No", style=flow.RIGHT),
        e("stale-yes", "stale-cache", "use-stale-cache", "Yes"),
        e("stale-to-client", "use-stale-cache", "apply-client-filters", points=((720, 932), (720, 1057)), style=flow.LEFT),
        e("stale-no", "stale-cache", "display-error", "No", points=((1050, 825), (1050, 1030)), style=flow.END_RIGHT, label_x=-0.9, label_y=-10),
        e("error-to-end", "display-error", "end", points=((1080, 1030), (1080, 1455)), style=flow.END_RIGHT),
        e("client-to-jobs", "apply-client-filters", "jobs-returned"),
        e("jobs-yes", "jobs-returned", "display-results", "Yes"),
        e("results-clear", "display-results", "clear-loading"),
        e("jobs-no", "jobs-returned", "empty-state", "No", style=flow.LEFT),
        e("empty-clear", "empty-state", "clear-loading", points=((340, 1282), (340, 1375)), style=flow.RIGHT),
        e("clear-end", "clear-loading", "end"),
    ),
    decision_branches={
        "fresh-cache": ("No", "Yes"),
        "request-successful": ("No", "Yes"),
        "stale-cache": ("No", "Yes"),
        "jobs-returned": ("No", "Yes"),
    },
)


EXPLORE_MAP = flow.Chart(
    diagram_id="user-explore-3d-map-flowchart",
    page_id="petakerja_flow_user_explore_3d_map",
    page_name="PetaKerja Explore the 3D Map",
    file_stem="Flow Chart PetaKerja - Explore the 3D Map",
    editor_filename="flowchart-user-explore-3d-map.drawio",
    width=1100,
    height=1500,
    title="PetaKerja Explore the 3D Map Flow Chart",
    subtitle="Public Malaysia workspace, POI loading, optional 3D terrain and building controls.",
    precondition="The User has opened PetaKerja; authentication is not required for map exploration.",
    notes=(
        "When POI data is unavailable, the base MapLibre workspace remains usable.",
        "3D terrain elevation is enabled only on viewports wider than 768 pixels; satellite imagery remains available on smaller screens.",
    ),
    nodes=(
        n("start", "Start", "start", 516.665, 105, 66.67, 40),
        n("select-map", "Select the Malaysia Map workspace", "process", 425, 175, 250, 55),
        n("open-workspace", "Open the map workspace", "process", 445, 255, 210, 50),
        n("wait-map", "Wait for the base map to become ready", "process", 425, 330, 250, 55),
        n("focus-malaysia", "Move the camera to Malaysia", "process", 445, 410, 210, 50),
        n("start-exploration", "Start map exploration", "process", 455, 485, 190, 50),
        n("request-pois", "Request visible POIs and category counts", "process", 420, 560, 260, 55),
        n("data-available", "POI data available?", "decision", 490, 650, 120, 70),
        n("render-pois", "Render POIs and category counts", "process", 435, 765, 230, 55),
        n("base-map-only", "Continue with the base map without unavailable POIs", "process", 70, 655, 280, 60),
        n("display-map", "Display the interactive Malaysia map", "process", 425, 850, 250, 55),
        n("terrain-selected", "3D Terrain selected?", "decision", 490, 945, 120, 70),
        n("wide-viewport", "Viewport wider than 768px?", "decision", 490, 1030, 120, 70),
        n("enable-terrain", "Enable satellite imagery and 3D terrain", "process", 420, 1110, 260, 55),
        n("satellite-only", "Use satellite imagery without terrain elevation", "process", 760, 1110, 270, 60),
        n("keep-basemap", "Keep the selected standard basemap", "process", 70, 1020, 240, 55),
        n("buildings-toggled", "3D Buildings toggled?", "decision", 490, 1185, 120, 70),
        n("update-buildings", "Update 3D building visibility", "process", 425, 1280, 250, 55),
        n("keep-buildings", "Keep the current building state", "process", 70, 1280, 230, 55),
        n("display-final-map", "Display the updated interactive map", "process", 760, 1370, 250, 55),
        n("end", "End", "start", 1010, 1435, 66.67, 40),
    ),
    edges=(
        e("start-select", "start", "select-map"),
        e("select-open", "select-map", "open-workspace"),
        e("open-wait", "open-workspace", "wait-map"),
        e("wait-focus", "wait-map", "focus-malaysia"),
        e("focus-start", "focus-malaysia", "start-exploration"),
        e("start-request", "start-exploration", "request-pois"),
        e("request-data", "request-pois", "data-available"),
        e("data-yes", "data-available", "render-pois", "Yes"),
        e("data-no", "data-available", "base-map-only", "No", style=flow.LEFT),
        e("render-display", "render-pois", "display-map"),
        e("base-display", "base-map-only", "display-map", points=((40, 685), (40, 877), (410, 877)), style=flow.RIGHT),
        e("display-terrain", "display-map", "terrain-selected"),
        e("terrain-yes", "terrain-selected", "wide-viewport", "Yes"),
        e("terrain-no", "terrain-selected", "keep-basemap", "No", points=((400, 980), (400, 1000), (190, 1000)), style="exitX=0;exitY=0.5;entryX=0.5;entryY=0;exitPerimeter=0;entryPerimeter=0;"),
        e("viewport-yes", "wide-viewport", "enable-terrain", "Yes"),
        e("viewport-no", "wide-viewport", "satellite-only", "No", points=((700, 1065), (895, 1065)), style="exitX=1;exitY=0.5;entryX=0.5;entryY=0;exitPerimeter=0;entryPerimeter=0;"),
        e("terrain-buildings", "enable-terrain", "buildings-toggled"),
        e("satellite-buildings", "satellite-only", "buildings-toggled", points=((895, 1180), (1050, 1180), (1050, 1220), (625, 1220)), style="exitX=0.5;exitY=1;entryX=1;entryY=0.5;exitPerimeter=0;entryPerimeter=0;"),
        e("basemap-buildings", "keep-basemap", "buildings-toggled", points=((190, 1090), (35, 1090), (35, 1220), (475, 1220)), style="exitX=0.5;exitY=1;entryX=0;entryY=0.5;exitPerimeter=0;entryPerimeter=0;"),
        e("buildings-yes", "buildings-toggled", "update-buildings", "Yes"),
        e("buildings-no", "buildings-toggled", "keep-buildings", "No", points=((400, 1220), (185, 1260)), style="exitX=0;exitY=0.5;entryX=0.5;entryY=0;exitPerimeter=0;entryPerimeter=0;"),
        e("update-display", "update-buildings", "display-final-map", points=((715, 1307), (715, 1384), (745, 1384)), style="exitX=1;exitY=0.5;entryX=0;entryY=0.25;exitPerimeter=0;entryPerimeter=0;"),
        e("keep-display", "keep-buildings", "display-final-map", points=((185, 1350), (720, 1350), (720, 1411), (745, 1411)), style="exitX=0.5;exitY=1;entryX=0;entryY=0.75;exitPerimeter=0;entryPerimeter=0;"),
        e("display-end", "display-final-map", "end", style=flow.RIGHT),
    ),
    decision_branches={
        "data-available": ("No", "Yes"),
        "terrain-selected": ("No", "Yes"),
        "wide-viewport": ("No", "Yes"),
        "buildings-toggled": ("No", "Yes"),
    },
)


USER_SIGN_OUT = flow.Chart(
    diagram_id="user-sign-out-flowchart",
    page_id="petakerja_flow_user_sign_out",
    page_name="PetaKerja User Sign Out",
    file_stem="Flow Chart PetaKerja - User Sign Out",
    editor_filename="flowchart-user-sign-out.drawio",
    width=980,
    height=1150,
    title="PetaKerja User Sign Out Flow Chart",
    subtitle="Better Auth sign-out followed by application-state and dashboard cleanup.",
    precondition="The User is signed in and the authenticated user menu is available.",
    notes=(
        "If sign-out fails, PetaKerja preserves the current session and re-enables the Sign Out control.",
        "A successful sign-out closes an open User Dashboard, clears its per-user caches and renders guest controls.",
    ),
    nodes=(
        n("start", "Start", "start", 456.665, 115, 66.67, 40),
        n("select-sign-out", "User selects Sign Out", "process", 390, 190, 200, 50),
        n("disable-control", "Disable the Sign Out control", "process", 390, 270, 200, 50),
        n("request-sign-out", "Submit the sign-out request", "process", 390, 350, 200, 50),
        n("sign-out-successful", "Sign-out successful?", "decision", 430, 445, 120, 70),
        n("invalidate-session", "Invalidate the session and clear its cookie", "process", 380, 560, 220, 55),
        n("clear-user", "Clear the signed-in user state", "process", 390, 645, 200, 50),
        n("notify-subscribers", "Notify authentication subscribers", "process", 380, 725, 220, 50),
        n("dashboard-open", "User Dashboard open?", "decision", 430, 815, 120, 70),
        n("close-dashboard", "Close the dashboard and clear per-user caches", "process", 90, 820, 250, 60),
        n("display-guest", "Display the guest Sign in control", "process", 390, 925, 200, 55),
        n("keep-session", "Keep the current session", "process", 690, 450, 200, 50),
        n("display-error", "Re-enable Sign Out and display the error", "process", 680, 535, 220, 55),
        n("end", "End", "start", 456.665, 1030, 66.67, 40),
    ),
    edges=(
        e("start-select", "start", "select-sign-out"),
        e("select-disable", "select-sign-out", "disable-control"),
        e("disable-request", "disable-control", "request-sign-out"),
        e("request-result", "request-sign-out", "sign-out-successful"),
        e("result-yes", "sign-out-successful", "invalidate-session", "Yes"),
        e("invalidate-clear", "invalidate-session", "clear-user"),
        e("clear-notify", "clear-user", "notify-subscribers"),
        e("notify-dashboard", "notify-subscribers", "dashboard-open"),
        e("dashboard-yes", "dashboard-open", "close-dashboard", "Yes", style=flow.LEFT),
        e("close-guest", "close-dashboard", "display-guest", points=((365, 850), (365, 952)), style=flow.RIGHT),
        e("dashboard-no", "dashboard-open", "display-guest", "No"),
        e("guest-end", "display-guest", "end"),
        e("result-no", "sign-out-successful", "keep-session", "No", style=flow.RIGHT),
        e("session-error", "keep-session", "display-error"),
        e("error-end", "display-error", "end", points=((935, 562), (935, 1050)), style=flow.END_RIGHT),
    ),
    decision_branches={"sign-out-successful": ("No", "Yes"), "dashboard-open": ("No", "Yes")},
)


FLOWCHARTS = (SEARCH_JOBS, EXPLORE_MAP, USER_SIGN_OUT)


@dataclass(frozen=True)
class DesignGroup:
    key: str
    label: str
    x: float
    y: float
    width: float
    height: float
    colour: str


@dataclass(frozen=True)
class DesignNode:
    key: str
    label: str
    group: str
    x: float
    y: float
    width: float
    height: float
    interactive: bool = True
    role: str = "responsibility"


@dataclass(frozen=True)
class DesignLink:
    key: str
    source: str
    target: str
    label: str
    points: tuple[tuple[float, float], ...] = ()
    exit_x: float = 0.5
    exit_y: float = 1.0
    entry_x: float = 0.5
    entry_y: float = 0.0
    label_x: float = 0.0
    label_y: float = 0.0
    hierarchy: bool = False


@dataclass(frozen=True)
class DesignDependency:
    source: str
    target: str
    label: str


@dataclass(frozen=True)
class DesignSpec:
    diagram_id: str
    page_id: str
    title: str
    subtitle: str
    file_stem: str
    editor_stem: str
    width: int
    height: int
    groups: tuple[DesignGroup, ...]
    nodes: tuple[DesignNode, ...]
    links: tuple[DesignLink, ...]
    dependencies: tuple[DesignDependency, ...] = ()
    show_group_containers: bool = True
    dependency_panel_y: float | None = None


ARCHITECTURE = DesignSpec(
    diagram_id="architecture",
    page_id="petakerja_layered_architecture",
    title="PetaKerja Layered Architecture",
    subtitle="Current SPA, manager, service, Express and data responsibilities.",
    file_stem="PetaKerja Layered Architecture",
    editor_stem="architecture-layered",
    width=1600,
    height=1000,
    groups=(
        DesignGroup("frontend", "Browser Frontend", 70, 90, 1460, 145, "blue"),
        DesignGroup("managers", "Manager Layer", 70, 250, 1460, 145, "violet"),
        DesignGroup("services", "Service Layer", 70, 410, 1460, 145, "amber"),
        DesignGroup("backend", "Express Backend", 70, 570, 1460, 145, "rose"),
        DesignGroup("data", "Data and External Services", 70, 730, 1460, 170, "green"),
    ),
    nodes=(
        DesignNode("frontend-shell", "src/main.ts\nsrc/MyPetaApp.ts", "frontend", 150, 140, 280, 64),
        DesignNode("frontend-ui", "templates.ts\nstyles.css", "frontend", 655, 140, 280, 64),
        DesignNode("frontend-map", "MapLibre GL JS", "frontend", 1160, 140, 280, 64),
        DesignNode("manager-poi", "POIManager\nSearchManager\nCategoryManager", "managers", 110, 300, 300, 64),
        DesignNode("manager-jobs", "JobFinderManager", "managers", 470, 300, 280, 64),
        DesignNode("manager-insights", "InsightsManager", "managers", 830, 300, 280, 64),
        DesignNode("manager-chatbot", "ChatbotManager", "managers", 1190, 300, 280, 64),
        DesignNode("service-supabase", "Supabase RPC client", "services", 110, 460, 300, 64),
        DesignNode("service-job-client", "supa-api.ts\ngrep-api.ts\napi.ts", "services", 470, 460, 280, 64),
        DesignNode("service-opendata", "OpenDataAPI", "services", 830, 460, 280, 64),
        DesignNode("service-auth", "authenticatedFetch", "services", 1190, 460, 280, 64),
        DesignNode("backend-app", "server/app.ts", "backend", 90, 620, 250, 64),
        DesignNode("backend-supa-jobs", "GET /api/jobs/supa", "backend", 380, 620, 250, 64),
        DesignNode("backend-live-jobs", "POST /api/search-jobs", "backend", 670, 620, 250, 64),
        DesignNode("backend-assistant", "POST /api/assistant/chat", "backend", 960, 620, 250, 64),
        DesignNode("backend-auth", "Better Auth middleware", "backend", 1250, 620, 250, 64),
        DesignNode("data-postgres", "Supabase PostgreSQL\nPostGIS", "data", 110, 790, 300, 70),
        DesignNode("data-jobs", "public.scraped_jobs\npublic.job_listings", "data", 470, 790, 280, 70),
        DesignNode("data-gov", "api.data.gov.my", "data", 830, 790, 280, 70),
        DesignNode("data-pois", "public.pois\ncategory RPCs", "data", 1190, 790, 280, 70),
    ),
    links=(
        DesignLink("frontend-managers", "frontend-shell", "manager-poi", "UI and map interaction"),
        DesignLink("managers-services", "manager-poi", "service-supabase", "Data calls"),
        DesignLink("supabase-data", "service-supabase", "data-postgres", "POI and RPC", ((360, 545), (360, 765)), 0.83, 1.0, 0.83, 0.0),
        DesignLink("jobs-backend", "service-job-client", "backend-supa-jobs", "Job search"),
        DesignLink("auth-backend", "service-auth", "backend-auth", "Protected functions"),
        DesignLink("backend-data", "backend-app", "data-postgres", "Profiles, status and indexes", ((170, 700), (170, 765)), 0.32, 1.0, 0.2, 0.0, -0.45, -13),
        DesignLink("opendata-gov", "service-opendata", "data-gov", "Open data", ((940, 545), (940, 765)), 0.39, 1.0, 0.39, 0.0),
    ),
)


MODULES_ORIGINAL = DesignSpec(
    diagram_id="modules",
    page_id="petakerja_module_hierarchy",
    title="PetaKerja Module Hierarchy",
    subtitle="Current core, job-search, analytics and account module responsibilities.",
    file_stem="PetaKerja Module Hierarchy",
    editor_stem="module-hierarchy",
    width=1500,
    height=1000,
    groups=(
        DesignGroup("core", "Core Application", 70, 100, 640, 350, "blue"),
        DesignGroup("jobs", "Job Search Module", 790, 100, 640, 350, "violet"),
        DesignGroup("account", "Accounts and Administration", 70, 540, 640, 350, "amber"),
        DesignGroup("analysis", "Analytics and Assistance", 790, 540, 640, 350, "green"),
    ),
    nodes=(
        DesignNode("core-shell", "Boot and application shell\nMyPetaApp + templates", "core", 150, 175, 480, 70),
        DesignNode("core-map", "Interactive map\nMapManager + MapLibre", "core", 150, 275, 480, 70),
        DesignNode("core-poi", "POI and categories\nPOIManager + Search + Category", "core", 150, 375, 480, 70),
        DesignNode("jobs-manager", "JobFinderManager", "jobs", 870, 175, 480, 70),
        DesignNode("jobs-modes", "Daily Index\nPipeline Index\nLive Search", "jobs", 870, 275, 480, 70),
        DesignNode("jobs-markers", "Job cards and map markers\nmarkers.ts", "jobs", 870, 375, 480, 70),
        DesignNode("account-auth", "Better Auth", "account", 150, 615, 480, 70),
        DesignNode("account-bridge", "public.users profile bridge", "account", 150, 715, 480, 70),
        DesignNode("account-admin", "Administration, configuration\nand user status", "account", 150, 815, 480, 70),
        DesignNode("analysis-insights", "InsightsManager\nOpenDataAPI", "analysis", 870, 615, 480, 70),
        DesignNode("analysis-highlight", "Area highlighting", "analysis", 870, 715, 480, 70),
        DesignNode("analysis-chatbot", "ChatbotManager\nAI provider routes", "analysis", 870, 815, 480, 70),
    ),
    links=(
        DesignLink("core-jobs", "core-map", "jobs-manager", "Map workspace", ((715, 310), (715, 200)), 1.0, 0.5, 0.0, 0.35, -0.72, -13),
        DesignLink("core-analysis", "core-map", "analysis-insights", "Location context", ((735, 310), (735, 650)), 1.0, 0.5, 0.0, 0.35, 0.64, -13),
        DesignLink("account-jobs", "account-bridge", "jobs-manager", "Save job status", ((775, 750), (775, 220)), 1.0, 0.5, 0.0, 0.75, 0.7, 13),
        DesignLink("account-analysis", "account-auth", "analysis-chatbot", "Protected AI functions", ((755, 650), (755, 850)), 1.0, 0.5, 0.0, 0.5, 0.72, 13),
    ),
)


MODULES = DesignSpec(
    diagram_id="modules",
    page_id="petakerja_module_hierarchy",
    title="PetaKerja Module Hierarchy",
    subtitle="Top-to-bottom ownership hierarchy with cross-module dependencies listed separately.",
    file_stem="PetaKerja Module Hierarchy",
    editor_stem="module-hierarchy",
    width=1600,
    height=1020,
    groups=(
        DesignGroup("core", "Core Application", 30, 230, 340, 70, "blue"),
        DesignGroup("jobs", "Job Search Module", 430, 230, 340, 70, "violet"),
        DesignGroup("account", "Accounts and Administration", 830, 230, 340, 70, "amber"),
        DesignGroup("analysis", "Analytics and Assistance", 1230, 230, 340, 70, "green"),
    ),
    nodes=(
        DesignNode("application-root", "PetaKerja", "core", 650, 100, 300, 64, False, "root"),
        DesignNode("module-core", "Core Application", "core", 30, 230, 340, 70, False, "module"),
        DesignNode("module-jobs", "Job Search Module", "jobs", 430, 230, 340, 70, False, "module"),
        DesignNode("module-account", "Accounts and Administration", "account", 830, 230, 340, 70, False, "module"),
        DesignNode("module-analysis", "Analytics and Assistance", "analysis", 1230, 230, 340, 70, False, "module"),
        DesignNode("core-shell", "Boot and application shell\nMyPetaApp + templates", "core", 60, 340, 280, 66),
        DesignNode("core-map", "Interactive map\nMapManager + MapLibre", "core", 60, 445, 280, 66),
        DesignNode("core-poi", "POI and categories\nPOIManager + SearchManager + CategoryManager", "core", 60, 550, 280, 72),
        DesignNode("jobs-manager", "JobFinderManager", "jobs", 460, 340, 280, 66),
        DesignNode("jobs-modes", "Daily Index\nPipeline Index\nLive Search", "jobs", 460, 445, 280, 72),
        DesignNode("jobs-markers", "Job cards and map markers\nmarkers.ts", "jobs", 460, 550, 280, 72),
        DesignNode("account-auth", "Better Auth", "account", 835, 340, 150, 66),
        DesignNode("account-bridge", "public.users profile bridge", "account", 815, 465, 190, 72),
        DesignNode("account-admin", "Administration, configuration\nand user status", "account", 1010, 340, 185, 72),
        DesignNode("analysis-insights", "InsightsManager\nOpenDataAPI", "analysis", 1225, 340, 180, 72),
        DesignNode("analysis-highlight", "Area highlighting", "analysis", 1225, 465, 180, 66),
        DesignNode("analysis-chatbot", "ChatbotManager\nAI provider routes", "analysis", 1420, 340, 150, 72),
    ),
    links=(
        DesignLink("hierarchy-root-core", "application-root", "module-core", "", ((800, 195), (200, 195)), hierarchy=True),
        DesignLink("hierarchy-root-jobs", "application-root", "module-jobs", "", ((800, 195), (600, 195)), hierarchy=True),
        DesignLink("hierarchy-root-account", "application-root", "module-account", "", ((800, 195), (1000, 195)), hierarchy=True),
        DesignLink("hierarchy-root-analysis", "application-root", "module-analysis", "", ((800, 195), (1400, 195)), hierarchy=True),
        DesignLink("hierarchy-core-shell", "module-core", "core-shell", "", hierarchy=True),
        DesignLink("hierarchy-core-map", "core-shell", "core-map", "", hierarchy=True),
        DesignLink("hierarchy-core-poi", "core-map", "core-poi", "", hierarchy=True),
        DesignLink("hierarchy-jobs-manager", "module-jobs", "jobs-manager", "", hierarchy=True),
        DesignLink("hierarchy-jobs-modes", "jobs-manager", "jobs-modes", "", hierarchy=True),
        DesignLink("hierarchy-jobs-markers", "jobs-modes", "jobs-markers", "", hierarchy=True),
        DesignLink("hierarchy-account-auth", "module-account", "account-auth", "", ((1000, 320), (910, 320)), hierarchy=True),
        DesignLink("hierarchy-account-admin", "module-account", "account-admin", "", ((1000, 320), (1102.5, 320)), hierarchy=True),
        DesignLink("hierarchy-account-bridge", "account-auth", "account-bridge", "", hierarchy=True),
        DesignLink("hierarchy-analysis-insights", "module-analysis", "analysis-insights", "", ((1400, 320), (1315, 320)), hierarchy=True),
        DesignLink("hierarchy-analysis-chatbot", "module-analysis", "analysis-chatbot", "", ((1400, 320), (1495, 320)), hierarchy=True),
        DesignLink("hierarchy-analysis-highlight", "analysis-insights", "analysis-highlight", "", hierarchy=True),
    ),
    dependencies=(
        DesignDependency("Interactive map", "JobFinderManager", "Map workspace"),
        DesignDependency("Interactive map", "InsightsManager / OpenDataAPI", "Location context"),
        DesignDependency("public.users profile bridge", "JobFinderManager", "Save job status"),
        DesignDependency("Better Auth", "ChatbotManager", "Protected AI functions"),
    ),
    show_group_containers=False,
    dependency_panel_y=690,
)


DESIGN_VARIANTS = (
    (ARCHITECTURE, False),
    (ARCHITECTURE, True),
    (MODULES_ORIGINAL, False),
    (MODULES, True),
)


COLOURS = {
    "blue": ("#eef5ff", "#17263a", "#3d6f9e", "#8fb7df"),
    "violet": ("#f5f0ff", "#2b2140", "#6941c6", "#b9a2ff"),
    "amber": ("#fff7df", "#3a2e16", "#9a6700", "#f4c95d"),
    "rose": ("#fff1f2", "#3b1d22", "#b42318", "#ff9b92"),
    "green": ("#ecfdf3", "#133221", "#1f7a4d", "#72d6a1"),
}


def style_text(values: dict[str, str]) -> str:
    return ";".join(f"{key}={value}" for key, value in values.items()) + ";"


def design_tree(spec: DesignSpec, polished: bool) -> ET.ElementTree:
    mxfile = ET.Element("mxfile", {"host": "Electron", "agent": "PetaKerja Architecture Explorer", "version": "27.0.2"})
    suffix = "Polished" if polished else "Original"
    diagram = ET.SubElement(mxfile, "diagram", {"name": f"{spec.title} - {suffix}", "id": spec.page_id})
    model = ET.SubElement(diagram, "mxGraphModel", {
        "dx": str(spec.width), "dy": str(spec.height), "grid": "1", "gridSize": "10", "guides": "1",
        "tooltips": "1", "connect": "1", "arrows": "1", "fold": "1", "page": "1", "pageScale": "1",
        "pageWidth": str(spec.width), "pageHeight": str(spec.height), "math": "0", "shadow": "0",
        "background": "light-dark(#fbfcfe,#0b1118)" if polished else "light-dark(#ffffff,#0f131a)",
    })
    root = ET.SubElement(model, "root")
    root_id, layer_id = f"{spec.diagram_id}-root", f"{spec.diagram_id}-layer"
    ET.SubElement(root, "mxCell", {"id": root_id})
    ET.SubElement(root, "mxCell", {"id": layer_id, "parent": root_id})

    def vertex(identifier: str, label: str, x: float, y: float, width: float, height: float,
               style: str, key: str | None = None) -> str:
        attrs = {"id": identifier, "label": label}
        if key:
            attrs["petakerjaKey"] = f"{spec.diagram_id}/{key}"
        wrapper = ET.SubElement(root, "object", attrs)
        cell = ET.SubElement(wrapper, "mxCell", {"parent": layer_id, "vertex": "1", "style": style})
        ET.SubElement(cell, "mxGeometry", {
            "x": f"{x:g}", "y": f"{y:g}", "width": f"{width:g}", "height": f"{height:g}", "as": "geometry",
        })
        return identifier

    vertex(f"{spec.diagram_id}-page-background", "", 0, 0, spec.width, spec.height,
           "rounded=0;whiteSpace=wrap;html=1;fillColor=light-dark(#fbfcfe,#0b1118);strokeColor=none;pointerEvents=0;locked=1;")
    vertex(f"{spec.diagram_id}-title", spec.title, 160, 22, spec.width - 320, 38,
           "text;html=1;whiteSpace=wrap;strokeColor=none;fillColor=none;align=center;verticalAlign=middle;fontFamily=Arial;fontSize=22;fontStyle=1;fontColor=light-dark(#172033,#f3f6fb);")
    vertex(f"{spec.diagram_id}-subtitle", spec.subtitle, 160, 58, spec.width - 320, 26,
           "text;html=1;whiteSpace=wrap;strokeColor=none;fillColor=none;align=center;verticalAlign=middle;fontFamily=Arial;fontSize=11;fontStyle=2;fontColor=light-dark(#475467,#c5cedb);")

    if spec.show_group_containers:
        for group in spec.groups:
            light_fill, dark_fill, light_stroke, dark_stroke = COLOURS[group.colour]
            if polished:
                fill = f"light-dark({light_fill},{dark_fill})"
                stroke = f"light-dark({light_stroke},{dark_stroke})"
            else:
                fill = "light-dark(#f8fafc,#151a22)"
                stroke = "light-dark(#98a2b3,#7d8796)"
            vertex(
                f"{spec.diagram_id}-group-{group.key}", group.label,
                group.x, group.y, group.width, group.height,
                style_text({
                    "rounded": "1", "arcSize": "8", "whiteSpace": "wrap", "html": "1", "container": "1",
                    "collapsible": "0", "align": "left", "verticalAlign": "top", "spacingTop": "12", "spacingLeft": "14",
                    "fontFamily": "Arial", "fontSize": "14", "fontStyle": "1", "fillColor": fill, "strokeColor": stroke,
                    "fontColor": "light-dark(#172033,#f3f6fb)", "strokeWidth": "2" if polished else "1",
                }),
            )

    node_ids: dict[str, str] = {}
    group_by_key = {group.key: group for group in spec.groups}
    for node in spec.nodes:
        group = group_by_key[node.group]
        light_fill, dark_fill, light_stroke, dark_stroke = COLOURS[group.colour]
        if node.role == "root":
            fill = "light-dark(#17263a,#eef5ff)"
            stroke = "light-dark(#3d6f9e,#8fb7df)"
            font_colour = "light-dark(#ffffff,#172033)"
            font_size, font_style, shadow = "18", "1", "1"
        elif node.role == "module":
            fill = f"light-dark({light_fill},{dark_fill})"
            stroke = f"light-dark({light_stroke},{dark_stroke})"
            font_colour = "light-dark(#172033,#f3f6fb)"
            font_size, font_style, shadow = "14", "1", "1"
        else:
            fill = "light-dark(#ffffff,#1c222c)"
            stroke = f"light-dark({light_stroke},{dark_stroke})" if polished else "light-dark(#667085,#aeb7c7)"
            font_colour = "light-dark(#172033,#f3f6fb)"
            font_size, font_style, shadow = "12", None, "1" if polished else "0"
        node_style = {
            "rounded": "1" if polished else "0", "arcSize": "8", "whiteSpace": "wrap", "html": "1",
            "align": "center", "verticalAlign": "middle", "spacing": "8", "fontFamily": "Arial",
            "fontSize": font_size, "fontColor": font_colour, "fillColor": fill, "strokeColor": stroke,
            "strokeWidth": "2" if polished else "1", "shadow": shadow,
        }
        if font_style:
            node_style["fontStyle"] = font_style
        node_ids[node.key] = vertex(
            f"{spec.diagram_id}-{node.key}", node.label, node.x, node.y, node.width, node.height,
            style_text(node_style), node.key if node.interactive else None,
        )

    if spec.dependencies and spec.dependency_panel_y is not None:
        panel_y = spec.dependency_panel_y
        vertex(
            f"{spec.diagram_id}-dependency-panel", "", 50, panel_y, spec.width - 100, spec.height - panel_y - 40,
            style_text({
                "rounded": "1", "arcSize": "8", "whiteSpace": "wrap", "html": "1", "pointerEvents": "0",
                "fillColor": "light-dark(#f8fafc,#151a22)", "strokeColor": "light-dark(#98a2b3,#7d8796)",
                "strokeWidth": "1", "shadow": "0",
            }),
        )
        vertex(
            f"{spec.diagram_id}-dependency-title", "Cross-module dependencies", 80, panel_y + 14, spec.width - 160, 28,
            "text;html=1;whiteSpace=wrap;strokeColor=none;fillColor=none;align=left;verticalAlign=middle;fontFamily=Arial;fontSize=14;fontStyle=1;fontColor=light-dark(#172033,#f3f6fb);",
        )
        card_width = spec.width - 140
        for index, dependency in enumerate(spec.dependencies):
            x = 70
            y = panel_y + 52 + index * 54
            label = f"{dependency.source} → {dependency.target} — {dependency.label}"
            vertex(
                f"{spec.diagram_id}-dependency-{index + 1}", label, x, y, card_width, 42,
                style_text({
                    "rounded": "1", "arcSize": "6", "whiteSpace": "wrap", "html": "1", "pointerEvents": "0",
                    "align": "center", "verticalAlign": "middle", "spacing": "8", "fontFamily": "Arial",
                    "fontSize": "11", "fontColor": "light-dark(#344054,#d8e0eb)",
                    "fillColor": "light-dark(#ffffff,#1c222c)", "strokeColor": "light-dark(#667085,#aeb7c7)",
                    "strokeWidth": "1", "shadow": "0",
                }),
            )

    for link in spec.links:
        wrapper_attributes = {"id": f"{spec.diagram_id}-{link.key}", "label": link.label}
        if link.hierarchy:
            wrapper_attributes["petakerjaRelation"] = "structural"
        else:
            wrapper_attributes["petakerjaKey"] = f"{spec.diagram_id}/{link.key}"
        wrapper = ET.SubElement(root, "object", wrapper_attributes)
        cell = ET.SubElement(wrapper, "mxCell", {
            "parent": layer_id, "edge": "1", "source": node_ids[link.source], "target": node_ids[link.target],
            "style": style_text({
                "edgeStyle": "orthogonalEdgeStyle", "rounded": "0" if link.hierarchy else ("1" if polished else "0"), "orthogonalLoop": "1",
                "jettySize": "auto", "html": "1", "endArrow": "none" if link.hierarchy else "classic",
                "endFill": "0" if link.hierarchy else "1", "strokeWidth": "2",
                "strokeColor": "light-dark(#344054,#c7d0dd)", "fontFamily": "Arial", "fontSize": "11",
                "fontColor": "light-dark(#344054,#d8e0eb)", "labelBackgroundColor": "light-dark(#fbfcfe,#0b1118)",
                "exitX": f"{link.exit_x:g}", "exitY": f"{link.exit_y:g}", "exitPerimeter": "0",
                "entryX": f"{link.entry_x:g}", "entryY": f"{link.entry_y:g}", "entryPerimeter": "0",
            }),
        })
        geo = ET.SubElement(cell, "mxGeometry", {
            "relative": "1", "as": "geometry",
            "x": f"{link.label_x:g}", "y": f"{link.label_y:g}",
        })
        if link.points:
            points = ET.SubElement(geo, "Array", {"as": "points"})
            for x, y in link.points:
                ET.SubElement(points, "mxPoint", {"x": f"{x:g}", "y": f"{y:g}"})
    return ET.ElementTree(mxfile)


def validate_design(path: Path, spec: DesignSpec) -> None:
    root = ET.parse(path).getroot()
    if len(root.findall("diagram")) != 1:
        raise RuntimeError(f"{spec.diagram_id}: expected one page")
    wrappers = root.findall(".//object")
    ids = [item.get("id", "") for item in wrappers]
    if any(not item for item in ids) or len(ids) != len(set(ids)):
        raise RuntimeError(f"{spec.diagram_id}: duplicate or missing IDs")
    interactive_nodes = [node for node in spec.nodes if node.interactive]
    semantic_links = [link for link in spec.links if not link.hierarchy]
    keys = [item.get("petakerjaKey", "") for item in wrappers if item.get("petakerjaKey")]
    if len(keys) != len(interactive_nodes) + len(semantic_links) or any(value > 1 for value in Counter(keys).values()):
        raise RuntimeError(f"{spec.diagram_id}: stable-key mismatch")
    interactive_node_ids = {
        item.get("id", "") for item in wrappers
        if item.get("petakerjaKey", "").split("/")[-1] in {node.key for node in interactive_nodes}
    }
    all_node_ids = {f"{spec.diagram_id}-{node.key}" for node in spec.nodes}
    edges = [item for item in wrappers if (item.find("mxCell") is not None and item.find("mxCell").get("edge") == "1")]
    if len(interactive_node_ids) != len(interactive_nodes) or len(edges) != len(spec.links):
        raise RuntimeError(f"{spec.diagram_id}: node or relationship count mismatch")
    for wrapper in edges:
        cell = wrapper.find("mxCell")
        if cell is None or cell.get("source") not in all_node_ids or cell.get("target") not in all_node_ids:
            raise RuntimeError(f"{spec.diagram_id}: detached relationship {wrapper.get('id')}")


def write_xml(tree: ET.ElementTree, destination: Path) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    ET.indent(tree, space="  ")
    tree.write(destination, encoding="utf-8", xml_declaration=True)


def light_copy(source: Path, destination: Path) -> None:
    text = source.read_text(encoding="utf-8")
    text = re.sub(r"light-dark\(\s*(#[0-9a-fA-F]{3,8})\s*,\s*(#[0-9a-fA-F]{3,8})\s*\)", r"\1", text)
    destination.write_text(text, encoding="utf-8")


def export_report(source: Path, svg: Path, png: Path) -> None:
    subprocess.run([str(DRAWIO), "--export", "--format", "svg", "--page-index", "0", "--output", str(svg), str(source)], check=True)
    with tempfile.TemporaryDirectory(prefix="petakerja-report-") as temp:
        light = Path(temp) / source.name
        light_copy(source, light)
        subprocess.run([str(DRAWIO), "--export", "--format", "png", "--page-index", "0", "--scale", "2", "--output", str(png), str(light)], check=True)


def build_flowcharts() -> None:
    for chart in FLOWCHARTS:
        output = DIAGRAMS / f"{chart.file_stem}.drawio"
        editor = EDITOR / chart.editor_filename.replace(".drawio", "-original.drawio")
        write_xml(flow.build(chart), output)
        flow.validate(chart, output)
        shutil.copy2(output, editor)
        export_report(output, DIAGRAMS / f"{chart.file_stem}.svg", DIAGRAMS / f"{chart.file_stem}.png")
        print(f"{chart.diagram_id}: {len(chart.nodes)} components, {len(chart.edges)} connectors")


def build_designs() -> None:
    for spec, polished in DESIGN_VARIANTS:
        variant = "Polished" if polished else "Original"
        output = DIAGRAMS / f"{spec.file_stem} - {variant}.drawio"
        svg = DIAGRAMS / f"{spec.file_stem} - {variant}.svg"
        png = DIAGRAMS / f"{spec.file_stem} - {variant}.png"
        editor = EDITOR / f"{spec.editor_stem}{'' if polished else '-original'}.drawio"
        write_xml(design_tree(spec, polished), output)
        validate_design(output, spec)
        shutil.copy2(output, editor)
        export_report(output, svg, png)
        components = sum(1 for node in spec.nodes if node.interactive)
        relationships = sum(1 for link in spec.links if not link.hierarchy) + len(spec.dependencies)
        print(f"{spec.diagram_id}-{variant.lower()}: {components} components, {relationships} semantic relationships")


def main() -> None:
    if not DRAWIO.exists():
        raise FileNotFoundError(DRAWIO)
    build_flowcharts()
    build_designs()


if __name__ == "__main__":
    main()
