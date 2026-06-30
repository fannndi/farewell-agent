import argparse
import logging

from core import FOOTER, get_logger

log = get_logger(__name__, logging.DEBUG)


def main():
    parser = argparse.ArgumentParser(description="Penyapa CLI sederhana")
    parser.add_argument("nama", nargs="?", default="Dunia", help="Nama yang akan disapa")
    parser.add_argument("--ucapan", "-u", default="Halo", help="Kata sapaan")
    parser.add_argument("--debug", action="store_true", help="Aktifkan logging debug")
    args = parser.parse_args()

    if args.debug:
        log.setLevel(logging.DEBUG)
        log.debug("Mode debug aktif")

    log.info("Menyapa %s dengan ucapan '%s'", args.nama, args.ucapan)
    print(f"{args.ucapan}, {args.nama}!")
    log.info("Selesai")
    print(FOOTER)


if __name__ == "__main__":
    main()
