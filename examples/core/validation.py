import logging

log = logging.getLogger(__name__)


def validasi_angka(n: str) -> float:
    """Validasi & konversi string ke float."""
    try:
        val = float(n)
        log.debug("Validasi sukses: '%s' -> %s", n, val)
        return val
    except ValueError:
        log.warning("Validasi gagal: '%s' bukan angka", n)
        raise ValueError(f"Input tidak valid: '{n}' bukan angka")
