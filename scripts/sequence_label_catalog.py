#!/usr/bin/env python3
"""Apply bilingual Simple/Code metadata to canonical sequence sources."""

from __future__ import annotations

import re
import xml.etree.ElementTree as ET
from pathlib import Path


SIMPLE_EN = {
    "sequence": [
        "Enter search terms, location and filters", "Select Search", "Start the job search",
        "Show loading and clear previous results", "Search the Daily Index", "Send the search criteria",
        "Request matching jobs", "Check the request and cache", "Return cached jobs",
        "Retrieve matching job records", "Return the job records", "Apply location, technology and salary filters",
        "Filter jobs by search relevance", "Return the ranked jobs", "Prepare results and the source summary",
        "Return fresh job results", "Handle the failed data request", "Return older cached results",
        "Return the job results", "Apply profile scoring and selected filters", "Prepare job cards and the source summary",
        "Prepare map markers", "Display job cards, result count and markers", "Return an empty job list",
        "Prepare the empty result", "Display no matching jobs", "Return the request error",
        "Report the Daily Index failure", "Show the Daily Index error", "Display the error and keep guest access",
        "Clear the loading state",
    ],
    "google-oauth-sequence": [
        "Select Sign in", "Check whether sign-in is required", "Open the sign-in prompt",
        "Display the Google sign-in prompt", "Select Continue with Google", "Start Google sign-in",
        "Send the Google sign-in request", "Request social sign-in", "Redirect to Google OAuth",
        "Show account selection and consent", "Select an account and grant consent", "Return to PetaKerja",
        "Create or update the account and session", "Confirm the account and session are saved",
        "Set the session cookie and return to PetaKerja", "Return OAuth rejection or cancellation",
        "Keep the guest state and show the sign-in error", "Initialize authentication", "Request the current session",
        "Retrieve the current session", "Read the saved session and user", "Return the session and user",
        "Return the Better Auth session", "Return the signed-in user", "Return no authenticated session",
        "Display the guest sign-in control", "Request the PetaKerja profile", "Verify the Better Auth session",
        "Return the verified Better Auth user", "Find the linked PetaKerja profile", "Return the linked profile",
        "Find an existing profile by email", "Link the existing profile", "Create a new PetaKerja profile",
        "Return the created profile", "Return the PetaKerja user profile", "Update the signed-in user",
        "Notify subscribed interface components", "Display the authenticated user menu",
    ],
}

SIMPLE_MS = {
    "sequence": [
        "Masukkan kata carian, lokasi dan penapis", "Pilih Cari", "Mulakan carian pekerjaan",
        "Paparkan pemuatan dan kosongkan hasil terdahulu", "Cari dalam Daily Index", "Hantar kriteria carian",
        "Minta pekerjaan yang sepadan", "Semak permintaan dan cache", "Pulangkan pekerjaan daripada cache",
        "Dapatkan rekod pekerjaan yang sepadan", "Pulangkan rekod pekerjaan", "Gunakan penapis lokasi, teknologi dan gaji",
        "Tapis pekerjaan mengikut perkaitan carian", "Pulangkan pekerjaan yang disusun", "Sediakan hasil dan ringkasan sumber",
        "Pulangkan hasil pekerjaan baharu", "Kendalikan kegagalan permintaan data", "Pulangkan hasil daripada cache lama",
        "Pulangkan hasil pekerjaan", "Gunakan skor profil dan penapis pilihan", "Sediakan kad pekerjaan dan ringkasan sumber",
        "Sediakan penanda peta", "Paparkan kad, jumlah hasil dan penanda", "Pulangkan senarai pekerjaan kosong",
        "Sediakan hasil kosong", "Paparkan tiada pekerjaan sepadan", "Pulangkan ralat permintaan",
        "Laporkan kegagalan Daily Index", "Paparkan ralat Daily Index", "Paparkan ralat dan kekalkan akses tetamu",
        "Kosongkan keadaan pemuatan",
    ],
    "google-oauth-sequence": [
        "Pilih Log masuk", "Semak sama ada log masuk diperlukan", "Buka prompt log masuk",
        "Paparkan prompt log masuk Google", "Pilih Teruskan dengan Google", "Mulakan log masuk Google",
        "Hantar permintaan log masuk Google", "Minta log masuk sosial", "Ubah hala ke Google OAuth",
        "Paparkan pemilihan akaun dan persetujuan", "Pilih akaun dan beri persetujuan", "Kembali ke PetaKerja",
        "Cipta atau kemas kini akaun dan sesi", "Sahkan akaun dan sesi telah disimpan",
        "Tetapkan kuki sesi dan kembali ke PetaKerja", "Pulangkan penolakan atau pembatalan OAuth",
        "Kekalkan keadaan tetamu dan paparkan ralat log masuk", "Mulakan pengesahan", "Minta sesi semasa",
        "Dapatkan sesi semasa", "Baca sesi dan pengguna yang disimpan", "Pulangkan sesi dan pengguna",
        "Pulangkan sesi Better Auth", "Pulangkan pengguna yang log masuk", "Pulangkan tiada sesi yang disahkan",
        "Paparkan kawalan log masuk tetamu", "Minta profil PetaKerja", "Sahkan sesi Better Auth",
        "Pulangkan pengguna Better Auth yang disahkan", "Cari profil PetaKerja yang dipaut", "Pulangkan profil yang dipaut",
        "Cari profil sedia ada melalui e-mel", "Pautkan profil sedia ada", "Cipta profil PetaKerja baharu",
        "Pulangkan profil yang dicipta", "Pulangkan profil pengguna PetaKerja", "Kemas kini pengguna yang log masuk",
        "Maklumkan komponen antara muka", "Paparkan menu pengguna yang disahkan",
    ],
}


# Non-message labels for the four active User sequence diagrams. Technical
# identifiers intentionally use the same value in both languages and therefore
# do not need metadata here. The Draw.io label remains the English projection;
# editor-core.js derives the visible BM/EN value at runtime.
NON_MESSAGE_LABELS = {
    "google-oauth-sequence/title": (
        "PetaKerja Sign in with Google OAuth Sequence",
        "Jujukan Log Masuk PetaKerja dengan Google OAuth",
    ),
    "google-oauth-sequence/participant-user-label": ("User", "Pengguna"),
    "google-oauth-sequence/participant-ui": (
        'PetaKerja UI<div><font style="font-size: 8px;">UserMenuManager / AuthModalManager</font></div>',
        'Antara Muka PetaKerja<div><font style="font-size: 8px;">UserMenuManager / AuthModalManager</font></div>',
    ),
    "google-oauth-sequence/participant-better-auth": (
        'Better Auth API<div><font style="font-size: 8px;">Express /api/auth/*</font></div>',
        'API Better Auth<div><font style="font-size: 8px;">Express /api/auth/*</font></div>',
    ),
    "google-oauth-sequence/participant-profile-api": (
        'PetaKerja Profile API<div><font style="font-size: 8px;">/api/me/auth-profile</font></div>',
        'API Profil PetaKerja<div><font style="font-size: 8px;">/api/me/auth-profile</font></div>',
    ),
    "google-oauth-sequence/oauth-success": ("[OAuth authorized]", "[OAuth dibenarkan]"),
    "google-oauth-sequence/oauth-failure": (
        "[else: rejected / cancelled / error]",
        "[selainnya: ditolak / dibatalkan / ralat]",
    ),
    "google-oauth-sequence/session-success": ("[session user exists]", "[pengguna sesi wujud]"),
    "google-oauth-sequence/session-empty": ("[else: no session]", "[selainnya: tiada sesi]"),
    "google-oauth-sequence/profile-found": (
        "[better_auth_user_id found]",
        "[better_auth_user_id ditemui]",
    ),
    "google-oauth-sequence/profile-email": ("[else: email match]", "[selainnya: e-mel sepadan]"),
    "google-oauth-sequence/profile-create": ("[else: no profile]", "[selainnya: tiada profil]"),
    "google-oauth-sequence/note": (
        "Google OAuth only. Password sign-in is intentionally unavailable in PetaKerja.",
        "Google OAuth sahaja. Log masuk dengan kata laluan memang tidak disediakan dalam PetaKerja.",
    ),
    "sequence/title": ("PetaKerja Search Jobs Sequence", "Jujukan Carian Pekerjaan PetaKerja"),
    "sequence/participant-user-label": ("User", "Pengguna"),
    "sequence/participant-ui": ("PetaKerja Job Finder UI", "Antara Muka Pencari Kerja PetaKerja"),
    "sequence/participant-route": (
        'Supa Jobs Route<div><font style="font-size: 8px;">GET /api/jobs/supa</font></div>',
        'Laluan Supa Jobs<div><font style="font-size: 8px;">GET /api/jobs/supa</font></div>',
    ),
    "sequence/participant-results": ("Job Results / MapLibre", "Hasil Pekerjaan / MapLibre"),
    "sequence/cache-hit": ("[fresh 60-second cache]", "[cache baharu dalam tempoh 60 saat]"),
    "sequence/cache-miss": ("[cache miss or refresh]", "[cache tiada atau perlu disegar semula]"),
    "sequence/cache-stale": (
        "[fetch failure and stale cache exists]",
        "[pengambilan gagal dan cache lama tersedia]",
    ),
    "sequence/query-present": ("[query supplied]", "[kata carian diberikan]"),
    "sequence/results-found": ("[jobs returned]", "[pekerjaan dipulangkan]"),
    "sequence/results-empty": ("[no matching jobs]", "[tiada pekerjaan yang sepadan]"),
    "sequence/results-error": (
        "[request fails without usable cache]",
        "[permintaan gagal tanpa cache yang boleh digunakan]",
    ),
    "sequence/note": (
        "Daily Index is public. Google sign-in is not required for this search path.",
        "Daily Index boleh digunakan oleh orang awam. Log masuk Google tidak diperlukan untuk aliran carian ini.",
    ),
    "user-explore-3d-map-sequence/title": (
        "PetaKerja User Explore the 3D Map Sequence",
        "Jujukan Pengguna Meneroka Peta 3D PetaKerja",
    ),
    "user-explore-3d-map-sequence/participant-user": ("User", "Pengguna"),
    "user-explore-3d-map-sequence/participant-ui": (
        "PetaKerja Workspace UI",
        "Antara Muka Ruang Kerja PetaKerja",
    ),
    "user-explore-3d-map-sequence/participant-data-api": (
        'PetaKerja Data API<div><font style="font-size: 8px;">supabase.ts</font></div>',
        'API Data PetaKerja<div><font style="font-size: 8px;">supabase.ts</font></div>',
    ),
    "user-explore-3d-map-sequence/participant-database": (
        'Supabase / PostgreSQL<div><font style="font-size: 8px;">POI data</font></div>',
        'Supabase / PostgreSQL<div><font style="font-size: 8px;">data POI</font></div>',
    ),
    "user-explore-3d-map-sequence/data-available": (
        "[map data available]",
        "[data peta tersedia]",
    ),
    "user-explore-3d-map-sequence/data-unavailable": (
        "[data request fails]",
        "[permintaan data gagal]",
    ),
    "user-explore-3d-map-sequence/terrain-selected": (
        "[user enables 3D terrain]",
        "[pengguna mengaktifkan rupa bumi 3D]",
    ),
    "user-explore-3d-map-sequence/buildings-selected": (
        "[user toggles 3D buildings]",
        "[pengguna menukar paparan bangunan 3D]",
    ),
    "user-explore-3d-map-sequence/implementation-note": (
        "Implementation note: map exploration is public. 3D terrain uses satellite imagery plus a DEM on screens wider than 768px; building extrusions appear within their configured zoom range.",
        "Nota pelaksanaan: penerokaan peta ialah fungsi awam. Rupa bumi 3D menggunakan imej satelit bersama DEM pada skrin yang lebih lebar daripada 768px; bentuk bangunan 3D dipaparkan dalam julat zum yang ditetapkan.",
    ),
    "user-sign-out-sequence/title": (
        "PetaKerja User Sign Out Sequence",
        "Jujukan Pengguna Log Keluar PetaKerja",
    ),
    "user-sign-out-sequence/participant-user": ("User", "Pengguna"),
    "user-sign-out-sequence/participant-ui": ("PetaKerja User Menu", "Menu Pengguna PetaKerja"),
    "user-sign-out-sequence/participant-api": (
        'Better Auth API<div><font style="font-size: 8px;">POST /api/auth/sign-out</font></div>',
        'API Better Auth<div><font style="font-size: 8px;">POST /api/auth/sign-out</font></div>',
    ),
    "user-sign-out-sequence/participant-session": ("Better Auth Session", "Sesi Better Auth"),
    "user-sign-out-sequence/sign-out-success": ("[sign-out succeeds]", "[log keluar berjaya]"),
    "user-sign-out-sequence/sign-out-failed": ("[sign-out fails]", "[log keluar gagal]"),
    "user-sign-out-sequence/implementation-note": (
        "Implementation note: on successful sign-out, UserDashboardManager closes and clears per-user caches. AdminDashboardManager currently remains on screen but re-renders its signed-out access state.",
        "Nota pelaksanaan: selepas log keluar berjaya, UserDashboardManager ditutup dan cache khusus pengguna dikosongkan. AdminDashboardManager masih kekal pada skrin tetapi memaparkan semula keadaan akses selepas log keluar.",
    ),
}

MISSING_STABLE_KEYS = {
    "job-search-participant-user-label": "sequence/participant-user-label",
}


def message_index(key: str) -> int | None:
    match = re.search(r"/message-(\d+)$", key)
    return int(match.group(1)) if match else None


def clean_code_label(label: str) -> str:
    return re.sub(r"^\s*\d+\.\s*", "", label or "").strip()


def apply_label_modes_to_file(path: Path) -> int:
    if not path.exists():
        return 0
    tree = ET.parse(path)
    changed = 0
    for wrapper in tree.getroot().findall(".//object"):
        if not wrapper.get("petakerjaKey") and wrapper.get("id") in MISSING_STABLE_KEYS:
            wrapper.set("petakerjaKey", MISSING_STABLE_KEYS[wrapper.get("id", "")])
        key = wrapper.get("petakerjaKey", "")
        if key in NON_MESSAGE_LABELS:
            label_en, label_ms = NON_MESSAGE_LABELS[key]
            wrapper.set("labelEn", label_en)
            wrapper.set("labelMs", label_ms)
            wrapper.set("label", label_en)
            changed += 1
        index = message_index(key)
        if index is None:
            continue
        prefix = key.rsplit("/message-", 1)[0]
        code_en = wrapper.get("codeLabelEn") or clean_code_label(wrapper.get("label", ""))
        simple_en_values = SIMPLE_EN.get(prefix, [])
        simple_ms_values = SIMPLE_MS.get(prefix, [])
        simple_en = wrapper.get("simpleLabelEn") or (simple_en_values[index - 1] if index <= len(simple_en_values) else code_en)
        simple_ms = wrapper.get("simpleLabelMs") or (simple_ms_values[index - 1] if index <= len(simple_ms_values) else simple_en)
        wrapper.set("simpleLabelEn", simple_en)
        wrapper.set("simpleLabelMs", simple_ms)
        wrapper.set("codeLabelEn", code_en)
        wrapper.set("codeLabelMs", wrapper.get("codeLabelMs") or code_en)
        wrapper.set("label", simple_en)
        changed += 1
    ET.indent(tree, space="  ")
    tree.write(path, encoding="utf-8", xml_declaration=False)
    return changed


def canonical_sources(root: Path) -> list[Path]:
    return [
        root / "assets" / "editor" / "sequence-job-search.drawio",
        root / "assets" / "editor" / "sequence-google-oauth.drawio",
        root / "assets" / "editor" / "sequence-admin-manage-users.drawio",
        root / "assets" / "editor" / "sequence-admin-manage-ai-configuration.drawio",
        root / "assets" / "editor" / "sequence-admin-access-dashboard.drawio",
        root / "assets" / "editor" / "sequence-admin-monitor-activity.drawio",
        root / "assets" / "editor" / "sequence-admin-sign-out.drawio",
        root / "assets" / "editor" / "sequence-user-explore-3d-map.drawio",
        root / "assets" / "editor" / "sequence-user-sign-out.drawio",
    ]


def apply_all(root: Path) -> int:
    return sum(apply_label_modes_to_file(path) for path in canonical_sources(root))


if __name__ == "__main__":
    explorer = Path(__file__).resolve().parents[1]
    print(f"Updated {apply_all(explorer)} sequence messages")
