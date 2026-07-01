import argparse
from core import FOOTER

def main():
    parser = argparse.ArgumentParser(description="Sapa CLI sederhana")
    parser.add_argument("nama", nargs="?", default="Dunia", help="Nama yang ingin disapa")
    args = parser.parse_args()

    print(f"Selamat tinggal, {args.nama}!")
    print(FOOTER)

if __name__ == "__main__":
    main()
