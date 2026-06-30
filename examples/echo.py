import argparse

from core import FOOTER


def main():
    parser = argparse.ArgumentParser(description="Echo CLI sederhana")
    parser.add_argument("pesan", nargs="*", default=["Halo, dunia!"], help="Pesan yang ingin dicetak")
    args = parser.parse_args()

    print(" ".join(args.pesan))
    print(FOOTER)


if __name__ == "__main__":
    main()
