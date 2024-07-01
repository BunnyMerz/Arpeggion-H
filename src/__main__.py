from main import main
import logging
from scene.scene_reader import AudioSceneConfig

try:
    from rich.logging import RichHandler
except ImportError:
    RichHandler = None

if RichHandler is not None:
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

# main()

a = AudioSceneConfig.start_parsing("tmp/config/scene_state.xml")
