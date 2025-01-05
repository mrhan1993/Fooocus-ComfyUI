import logging
import os


ROOT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
class Logger:
    def __init__(self, log_name: str,
                 log_dir: str = 'logs',
                 log_format="%(asctime)s - %(levelname)s - %(message)s"):
        """
        :param log_name: 日志文件名
        :param log_dir: 日志文件存放目录
        :param log_format: 日志格式
        """
        log_dir = os.path.join(ROOT_DIR, log_dir)
        try:
            os.makedirs(log_dir, exist_ok=True)
        except Exception as e:
            raise RuntimeError(f'Failed to create log directory {log_dir}: {e}') from e

        self.logger = logging.getLogger(log_name)
        self.logger.setLevel(logging.DEBUG)  # Set to DEBUG to capture all levels

        # Define handlers and their corresponding log levels and filenames
        handlers = {
            logging.ERROR: f"{log_name}_error.log",
            logging.WARNING: f"{log_name}_warning.log",
            logging.INFO: f"{log_name}_info.log"
        }

        formatter = logging.Formatter(log_format)

        for level, filename in handlers.items():
            handler = logging.FileHandler(os.path.join(log_dir, filename), encoding='utf-8')
            handler.setLevel(level)
            handler.setFormatter(formatter)

            # Add a filter to ensure that only messages of the exact level are logged
            class ExactLevelFilter(logging.Filter):
                def __init__(self, log_level):
                    super().__init__()
                    self.level = log_level

                def filter(self, record):
                    return record.levelno == self.level

            handler.addFilter(ExactLevelFilter(level))

            self.logger.addHandler(handler)

    def error(self, message):
        self.logger.error(message)

    def info(self, message):
        self.logger.info(message)

    def warning(self, message):
        self.logger.warning(message)


common_logger = Logger('common')
