import argparse
import logging
import sys

from core import FOOTER, get_logger

log = get_logger(__name__, logging.DEBUG)


def simpan(catatan: str, file: str = "catatan.txt"):
    with open(file, "a", encoding="utf-8") as f:
        f.write(catatan + "\n")
    log.info("Catatan disimpan ke %s", file)


def baca(file: str = "catatan.txt"):
    try:
        with open(file, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return ""


def main():
    parser = argparse.ArgumentParser(description="Pencatat CLI sederhana")
    parser.add_argument("catatan", nargs="?", help="Catatan yang ingin disimpan")
    parser.add_argument("--baca", "-b", action="store_true", help="Tampilkan semua catatan")
    parser.add_argument("--file", "-f", default="catatan.txt", help="File catatan")
    parser.add_argument("--debug", action="store_true", help="Aktifkan logging debug")
    args = parser.parse_args()

    if args.debug:
        log.setLevel(logging.DEBUG)
        log.debug("Mode debug aktif")

    if args.baca:
        isi = baca(args.file)
        if isi:
            print("=== CATATAN ===")
            print(isi.strip())
        else:
            print("Tidak ada catatan.")
    elif args.catatan:
        simpan(args.catatan, args.file)
        log.info("Catatan: %s", args.catatan)
        print(f"Catatan disimpan: {args.catatan}")
    else:
        print("Usage: python pencatat.py <catatan>")
        print("       python pencatat.py --baca")
        print(FOOTER)
        return

    print(FOOTER)


if __name__ == "__main__":
    main()
