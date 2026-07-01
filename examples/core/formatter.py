import logging

log = logging.getLogger(__name__)


def tabel_data(data: list[float], label: str = "Data") -> str:
    log.debug("Format tabel untuk %d items", len(data))
    lines = [f"\n--- {label} ---"]
    for i, val in enumerate(data, 1):
        lines.append(f"  {i:3d}. {val:>8.2f}")
    lines.append(f"  {'=' * 14}")
    return "\n".join(lines)


def format_rupiah(amount: float) -> str:
    formatted = f"Rp{amount:,.2f}"
    log.debug("Format rupiah: %s -> %s", amount, formatted)
    return formatted


def summary_line(stats: dict) -> str:
    log.debug("Buat summary dari %s", stats)
    return (
        f"n={stats['n']} | mean={stats['mean']:.2f} | "
        f"median={stats['median']:.2f} | range=[{stats['min']:.2f}, {stats['max']:.2f}]"
    )
