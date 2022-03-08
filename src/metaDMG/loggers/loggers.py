from logger_tt import setup_logging, logger
from datetime import datetime
from importlib import resources
from pathlib import Path
from multiprocessing import parent_process
import random


def is_main_process():
    return parent_process() is None


def setup_logger(log_port=None, log_path=None):

    if log_port is None:
        log_port = get_logger_port()

    if log_path is None:
        log_path = get_logger_path()

    with resources.path("metaDMG.loggers", "log_config.yaml") as p:
        config_path = p

    setup_logging(
        config_path=config_path,
        log_path=log_path,
        port=log_port,
        # full_context=2,
    )

    if is_main_process():
        import metaDMG

        version = metaDMG.__version__
        logger.debug(f"Running metaDMG version {version}.")
        logger.debug(f"Using port {log_port} for logging.")


def port_is_available(log_port):
    from logger_tt.core import LogRecordSocketReceiver

    try:
        LogRecordSocketReceiver("localhost", log_port, [])
        return True
    except OSError:
        return False


def get_logger_port():
    loop = 0
    max__loops = 1000
    while loop < max__loops:
        log_port = random.randint(49152, 65535)
        if port_is_available(log_port):
            return log_port
        else:
            loop += 1


def get_logger_path():
    now = datetime.now()
    now_str = now.strftime("%Y-%m-%d__%H-%M-%S")
    log_path = f"logs/log__{now_str}.log"
    return log_path


def get_logger_port_and_path():
    return get_logger_port(), get_logger_path()
