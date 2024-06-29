from main import main
import logging

try:
    from rich.logging import RichHandler
except ImportError:
    RichHandler = None

if RichHandler is not None:
    log_format = "%(message)s"
    log_handler = RichHandler(rich_tracebacks=True, omit_repeated_times=False)
    logging.basicConfig(level=logging.INFO, format=log_format, handlers=[log_handler])
else:
    log_format = (
        "[%(levelname)-7s] %(asctime)s | "
        "%(name)-30s:%(lineno)4d "
        # "[%(process)d %(processName)s | %(thread)d %(threadName)s] "
        "> %(message)s"
    ),
    logging.basicConfig(level=logging.INFO, format=log_format)

main()
