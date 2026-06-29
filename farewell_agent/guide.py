"""Guide (buku panduan) — search and browse the Obsidian knowledge base."""

from . import config
from .context import _vault_dir, search, is_ready
from .helpers import c, ok, info


def show_status():
    """Show guide book status."""
    if is_ready():
        vault = _vault_dir()
        total_files = len(list(vault.rglob("*.md"))) if vault else 0
        ecc_count = len(list((vault / "ecc").rglob("*.md"))) if vault and (vault / "ecc").exists() else 0
        print(f"\n  {c('Buku Panduan (Obsidian)', 'cyan')}")
        print(f"  Lokasi: {vault}")
        print(f"  Total: {total_files} artikel ({ecc_count} ECC skills)")
        print(f"  Search: {c('farewell-agent cari <query>', 'yellow')}")
        print(f"  Buka:   {c('farewell-agent panduan', 'yellow')}\n")
    else:
        print(f"\n  {c('Buku Panduan: Belum dikonfigurasi', 'yellow')}")
        info("Set OBSIDIAN_VAULT di api-key.txt, lalu jalankan: py -m farewell_agent extract-knowledge\n")


def search_and_show(query: str):
    """Search vault and show results."""
    if not is_ready():
        print(f"\n  {c('[PANDUAN] Obsidian vault belum dikonfigurasi', 'yellow')}")
        print("  Set OBSIDIAN_VAULT=path di api-key.txt\n")
        return

    print(f"\n  {c('Membuka buku panduan...', 'cyan')}")
    print(f"  Mencari: {query}\n")

    results = search(query, max_results=10)
    if not results:
        print("  Tidak ada hasil yang cocok.\n")
        return

    for r in results:
        icon = "[F]"
        if "ecc/" in r.get("path", ""):
            if "ECC-" in r["file"]:
                icon = "[D]"
            else:
                icon = "[S]"
        title = c(r["title"], "cyan")
        print(f"  {icon} {title}")
        print(f"      {r['snippet'][:150]}")
        print(f"      {c(r['path'], 'gray')}\n")


def open_index():
    """Show the guide index (_Index.md content)."""
    if not is_ready():
        print("  Obsidian vault belum dikonfigurasi.\n")
        return

    vault = _vault_dir()
    idx = vault / "_Index.md"
    if idx.exists():
        print(f"\n  {c('=== Buku Panduan ===', 'cyan')}")
        print(idx.read_text(encoding="utf-8", errors="ignore"))
        print(f"\n  {c('Cari: farewel-agent cari <topik>', 'yellow')}\n")
    else:
        print("  Index belum ada. Jalankan: farewel-agent extract-knowledge\n")
