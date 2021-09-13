from logger_tt import setup_logging, logger
from datetime import datetime
from importlib import resources


def setup_logger():

    now = datetime.now()
    now_str = now.strftime("%Y-%m-%d__%H-%M")
    log_path = f"logs/log__{now_str}.log"

    with resources.path("metaDMG.loggers.loggers", "log_config.yaml") as p:
        config_path = p

    setup_logging(
        config_path=config_path,
        log_path=log_path,
    )

    # return logger
