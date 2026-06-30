"""Prompt interpreter — refines user input, injects footer, ensures footer in output."""

import re
from . import config

FOOTER_MARKER = "### FOOTER"
FOOTER_VARIANTS = [FOOTER_MARKER, "## FOOTER", "# FOOTER", "FOOTER", "footer"]


def refine(task: str, code: str, name: str, guide_block: str = "") -> str:
    enriched = task
    if guide_block:
        enriched = f"{task}\n\n{guide_block}"
    return enriched


def _next_hint(task: str, task_class: str | None = None) -> str:
    if task_class:
        hints = {
            "feature": "jalankan pengujian atau review kode",
            "fix": "verifikasi bahwa bug telah diperbaiki",
            "audit": "tindak lanjuti temuan audit",
            "learn": "simpan pengetahuan baru ke MEMORY.md",
            "health": "tidak ada tindakan lanjutan — sistem sehat",
            "refactor": "jalankan test untuk memastikan tidak ada yang rusak",
            "deploy": "pantau deployment dan cek log",
            "security-review": "perbaiki kerentanan yang ditemukan",
            "verification-loop": "periksa hasil test coverage",
            "self-heal": "verifikasi build berhasil",
        }
        if task_class in hints:
            return hints[task_class]

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


def build_footer(code: str, name: str, session_id: str | None = None, task_class: str | None = None, task: str | None = None) -> str:
    sid = session_id or "?"
    hint = _next_hint(task or "", task_class)
    return f"\n---\n{FOOTER_MARKER}\nProject: {code}-{name} | Session: {sid}\nNext: {hint}\n"


def is_footer_present(text: str) -> bool:
    for variant in FOOTER_VARIANTS:
        if variant in text:
            return True
    return False


def ensure_footer(text: str, code: str, name: str, session_id: str | None = None,
                   task_class: str | None = None, task: str | None = None) -> str:
    if is_footer_present(text):
        return text
    return text + build_footer(code, name, session_id, task_class, task)


def check_footer(output: str) -> bool:
    return is_footer_present(output)
