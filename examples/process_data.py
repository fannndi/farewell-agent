import logging

from examples.core import get_logger, print_footer
from examples.core.processor import filter_positive, summarize, transform

log = get_logger("process_data", level=logging.DEBUG)


def main() -> None:
    data = [10, -5, 3, 0, -1, 7, -8, 2]

    log.info("Starting data processing pipeline")
    log.debug("Input data: %s", data)

    transformed = transform(data, factor=3)
    positive = filter_positive(transformed)
    stats = summarize(positive)

    print(f"\nResults: {stats}")
    log.info("Pipeline selesai — %d item setelah filter", stats["count"])

    print_footer()


if __name__ == "__main__":
    main()
