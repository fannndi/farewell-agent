import argparse
import logging
import sys

from core import (
    FOOTER,
    deskripsi,
    format_rupiah,
    get_logger,
    print_footer,
    summary_line,
    tabel_data,
)

log = get_logger("report_cli", logging.DEBUG)


def parse_args():
    parser = argparse.ArgumentParser(description="Laporan data CLI")
    parser.add_argument("angka", nargs="+", type=float, help="Data angka")
    parser.add_argument("--rupiah", action="store_true", help="Format output sebagai rupiah")
    parser.add_argument("--debug", action="store_true", help="Aktifkan debug logging")
    return parser.parse_args()


def main():
    args = parse_args()

    if args.debug:
        log.setLevel(logging.DEBUG)
        log.debug("Mode debug aktif")

    log.info("Memproses %d angka", len(args.angka))

    data = args.angka
    fmt = format_rupiah if args.rupiah else lambda x: f"{x:.2f}"

    print(tabel_data(data, "Input Data"))

    stats = deskripsi(data)
    print(f"\n  {'Statistik':15s} {'Nilai':>10s}")
    print(f"  {'─' * 27}")
    print(f"  {'n':15s} {stats['n']:>10d}")
    print(f"  {'Mean':15s} {fmt(stats['mean']):>10s}")
    print(f"  {'Median':15s} {fmt(stats['median']):>10s}")
    print(f"  {'Min':15s} {fmt(stats['min']):>10s}")
    print(f"  {'Max':15s} {fmt(stats['max']):>10s}")
    print(f"  {'Range':15s} {fmt(stats['range']):>10s}")

    log.info("Ringkasan: %s", summary_line(stats))
    print_footer()


if __name__ == "__main__":
    main()
