from logger_tt import setup_logging, internal_config, logger
from datetime import datetime
from importlib import resources
from pathlib import Path
from multiprocessing import parent_process


def is_main_process():
    return parent_process() is None


def setup_logger(port=9021):

    now = datetime.now()
    now_str = now.strftime("%Y-%m-%d__%H-%M")
    log_path = f"logs/log__{now_str}.log"

    if Path(log_path).exists() and is_main_process():
        print("Got here")
        print(log_path)
        log_path = log_path.replace(".log", f"-{now.second}.log")

    with resources.path("metaDMG.loggers", "log_config.yaml") as p:
        config_path = p

    internal_config.port = port
    setup_logging(
        config_path=config_path,
        log_path=log_path,
    )

    if is_main_process():
        logger.debug(f"Using port {port}.")


def port_is_available(port):
    from logger_tt.core import LogRecordSocketReceiver

    try:
        LogRecordSocketReceiver("localhost", port, [])
        return True
    except OSError:
        return False


def get_logger_port(port=9021):
    loop = 0
    max__loops = 100
    while loop < max__loops:
        if port_is_available(port):
            return port
        else:
            port += 1
            loop += 1
