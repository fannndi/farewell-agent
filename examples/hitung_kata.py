import argparse
import sys

from core import FOOTER


def hitung(teks: str) -> dict:
    return {
        "karakter": len(teks),
        "kata": len(teks.split()),
        "baris": teks.count("\n") + 1 if teks else 0,
    }


def main():
    parser = argparse.ArgumentParser(description="Penghitung kata CLI")
    parser.add_argument("teks", nargs="*", help="Teks yang akan dihitung")
    parser.add_argument("--file", "-f", help="Baca dari file")
    args = parser.parse_args()

    if args.file:
        try:
            with open(args.file, "r", encoding="utf-8") as f:
                teks = f.read()
        except FileNotFoundError:
            print(f"Error: File '{args.file}' tidak ditemukan")
            print(FOOTER)
            sys.exit(1)
    elif args.teks:
        teks = " ".join(args.teks)
    else:
        teks = sys.stdin.read() if not sys.stdin.isatty() else ""

    if not teks:
        print("Tidak ada teks untuk dihitung.")
        print(FOOTER)
        return

    hasil = hitung(teks)
    print(f"Karakter: {hasil['karakter']}")
    print(f"Kata:     {hasil['kata']}")
    print(f"Baris:    {hasil['baris']}")
    print(FOOTER)


if __name__ == "__main__":
    main()
