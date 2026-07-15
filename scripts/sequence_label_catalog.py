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
        key = wrapper.get("petakerjaKey", "")
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
    diagrams = Path(r"C:\Users\iamal\Desktop\Semester 8\TTTM4172 Usulan Projek\Akmal\Diagrams")
    return [
        diagrams / "Sequence Diagram PetaKerja - Search Jobs.drawio",
        diagrams / "Sequence Diagram PetaKerja - Sign in Google OAuth.drawio",
        diagrams / "Sequence Diagram PetaKerja - Manage Users.drawio",
        diagrams / "Sequence Diagram PetaKerja - Manage AI Chatbot Configuration.drawio",
        diagrams / "Sequence Diagram PetaKerja - Access Administrator Dashboard.drawio",
        diagrams / "Sequence Diagram PetaKerja - Monitor System Activity Logs.drawio",
        diagrams / "Sequence Diagram PetaKerja - Administrator Sign Out.drawio",
        diagrams / "Sequence Diagram PetaKerja - Explore the 3D Map.drawio",
        diagrams / "Sequence Diagram PetaKerja - User Sign Out.drawio",
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
