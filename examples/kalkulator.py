import logging
import sys

from core import FOOTER, get_logger, validasi_angka

log = get_logger(__name__, logging.DEBUG)


def hitung(a: float, b: float, op: str) -> float:
    if op == "+":
        hasil = a + b
    elif op == "-":
        hasil = a - b
    elif op == "*":
        hasil = a * b
    elif op == "/":
        if b == 0:
            log.error("Pembagian dengan nol")
            raise ZeroDivisionError("Pembagian dengan nol tidak diperbolehkan")
        hasil = a / b
    else:
        log.error("Operator tak dikenal: '%s'", op)
        raise ValueError(f"Operator '{op}' tidak dikenal. Gunakan +, -, *, /")

    log.info("%s %s %s = %s", a, op, b, hasil)
    return hasil


def main():
    if len(sys.argv) != 4:
        print("Usage: python kalkulator.py <angka1> <operator> <angka2>")
        print(FOOTER)
        return

    try:
        a = validasi_angka(sys.argv[1])
        op = sys.argv[2]
        b = validasi_angka(sys.argv[3])
        result = hitung(a, b, op)
        print(f"{a} {op} {b} = {result}")
    except (ValueError, ZeroDivisionError) as e:
        print(f"Error: {e}")
    finally:
        print(FOOTER)


if __name__ == "__main__":
    main()
