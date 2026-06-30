"""Prompt interpreter — refines user input, injects footer, ensures footer in output."""

import re
from . import config

FOOTER_MARKER = "### FOOTER"

def refine(task: str, code: str, name: str, guide_block: str = "") -> str:
    enriched = task
    if guide_block:
        enriched = f"{task}\n\n{guide_block}"
    return enriched


def _next_hint(task: str) -> str:
    lower = task.lower()
    if any(w in lower for w in ("test", "verify", "cek")):
        return "jalankan perintah untuk verifikasi"
    if any(w in lower for w in ("buat", "bikin", "tambah", "add", "create", "new")):
        return "lanjutkan dengan pengujian atau review"
    if any(w in lower for w in ("perbaiki", "fix", "bug", "error", "rusak")):
        return "verifikasi bahwa bug telah diperbaiki"
    if any(w in lower for w in ("refactor", "rapihin", "bersihin", "clean")):
        return "jalankan test untuk memastikan tidak ada yang rusak"
    if any(w in lower for w in ("belajar", "learn", "cari", "riset", "research")):
        return "simpan pengetahuan baru ke MEMORY.md"
    return "lanjutkan dengan task berikutnya"


def build_footer(code: str, name: str, session_id: str | None = None) -> str:
    sid = session_id or "?"
    next_step = "lanjutkan dengan task berikutnya"
    return f"\n---\n{FOOTER_MARKER}\nProject: {code}-{name} | Session: {sid}\nNext: {next_step}\n"


def is_footer_present(text: str) -> bool:
    return FOOTER_MARKER in text


def ensure_footer(text: str, code: str, name: str, session_id: str | None = None) -> str:
    if is_footer_present(text):
        return text
    return text + build_footer(code, name, session_id)


def check_footer(output: str) -> bool:
    """Parse output for footer presence. Returns True if footer found."""
    return is_footer_present(output)
