import random
from datetime import datetime
from importlib import resources
from multiprocessing import parent_process
from pathlib import Path
from typing import Optional, Tuple

from logger_tt import logger, setup_logging


def is_main_process() -> bool:
    return parent_process() is None


def setup_logger(
    log_port: Optional[int] = None,
    log_path: Optional[str] = None,
) -> None:

    if log_port is None:
        log_port = get_logger_port()

    if log_path is None:
        log_path = get_logger_path()

    with resources.path("metaDMG.loggers", "log_config.yaml") as p:
        log_config_path = p

    setup_logging(
        config_path=str(log_config_path),
        log_path=log_path,
        port=log_port,
        # full_context=2,
    )

    if is_main_process():
        import metaDMG

        version = metaDMG.__version__
        logger.debug(f"Running metaDMG version {version}.")
        logger.debug(f"Using port {log_port} for logging.")


def port_is_available(log_port) -> bool:
    from logger_tt.core import LogRecordSocketReceiver

    try:
        LogRecordSocketReceiver("localhost", log_port, [])
        return True
    except OSError:
        return False


def get_logger_port() -> int:
    loop = 0
    max__loops = 1000
    while loop < max__loops:
        log_port = random.randint(49152, 65535)
        if port_is_available(log_port):
            return log_port
        else:
            loop += 1

    raise AssertionError("Couldn't find a port")


def get_logger_path() -> str:
    now = datetime.now()
    now_str = now.strftime("%Y-%m-%d__%H-%M-%S")
    log_path = f"logs/log__{now_str}.log"
    return log_path


def get_logger_port_and_path() -> Tuple[int, Optional[str]]:
    return get_logger_port(), get_logger_path()
