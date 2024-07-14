from sys import argv
from main import main
import logging

try_import = False
try:
    from rich.logging import RichHandler
    try_import = True
except ImportError:
    pass

if try_import is not None:
    log_format = "%(message)s"
    log_handler = RichHandler(rich_tracebacks=True, omit_repeated_times=False)
    logging.basicConfig(level=logging.ERROR, format=log_format, handlers=[log_handler])
else:
    log_format = (
        "[%(levelname)-7s] %(asctime)s | "
        "%(name)-30s:%(lineno)4d "
        # "[%(process)d %(processName)s | %(thread)d %(threadName)s] "
        "> %(message)s"
    )
    logging.basicConfig(level=logging.ERROR, format=log_format)

logger = logging.getLogger(__name__)

file_name = None
for i, arg in enumerate(argv):
    if arg == "-file":
        if i+1 >= len(argv):
            raise Exception("Missing <file_name> in -file")
        file_name = argv[i+1]
if file_name is None:
    file_name = ""
    # raise Exception("Missing -file <file_name>")
main(file_name)
