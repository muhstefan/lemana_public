import logging
import os
import time

from my_libs.composite_data_base import SingletonMeta


class Logger(metaclass=SingletonMeta):
    _log_dir = None
    _start_time = None

    def __init__(self, log_dir=None):
        if hasattr(self, "_initialized") and self._initialized:
            return

        if log_dir is None and self._log_dir is None:
            log_dir = os.getcwd()

        if self._log_dir is None:
            self._log_dir = log_dir
            self._start_time = time.time()

        self.log_dir = self._log_dir
        os.makedirs(self.log_dir, exist_ok=True)

        log_file_path = os.path.join(self.log_dir, "app_errors.log")
        logging.basicConfig(
            level=logging.INFO,
            filename=log_file_path,
            filemode="a",
            format="%(asctime)s %(levelname)s: %(message)s",
            encoding="utf-8",
        )
        self.logger = logging.getLogger()
        self._initialized = True

    def time(self, mesage):
        if self._start_time is None:
            raise Exception("Вызов time у логера может быть только после его создания.")
        elapsed = time.time() - self._start_time
        self.logger.info(f"{elapsed:.2f} секунд с начала. {mesage}")

    def error(self, message):
        self.logger.error(message)

    def warning(self, message):
        self.logger.warning(message)
