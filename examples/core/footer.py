import logging

log = logging.getLogger(__name__)

FOOTER = """---
### FOOTER
**Project:** 001-farewell-agent
**Next:** Coba `farewell-agent run --help` untuk lihat opsi

---"""


def print_footer():
    """Cetak FOOTER dan log bahwa footer sudah dicetak."""
    print(FOOTER)
    log.debug("Footer dicetak")
