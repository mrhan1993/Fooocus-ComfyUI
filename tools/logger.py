import logging
import os


class Logger:
    def __init__(self, log_name: str,
                 log_dir: str = 'logs',
                 log_format = "%(asctime)s - %(levelname)s - %(message)s"):
        """
        :param log_name: 日志文件名
        :param log_dir: 日志文件存放目录
        :param log_format: 日志格式
        """
        os.makedirs(log_dir, exist_ok=True)
        logger = logging.getLogger(log_name)
        logger.setLevel("INFO")

        # 创建一个ERROR级别的handler，将日志记录到error.log文件中
        error_handler = logging.FileHandler(log_dir + '/' + log_name + '_error.log', encoding='utf-8')
        error_handler.setLevel(logging.ERROR)

        # 创建一个WARNING级别的handler，将日志记录到warning.log文件中
        warning_handler = logging.FileHandler(log_dir + '/' + log_name + '_warning.log', encoding='utf-8')
        warning_handler.setLevel(logging.WARNING)

        # 创建一个INFO级别的handler，将日志记录到info.log文件中
        info_handler = logging.FileHandler(log_dir + '/' + log_name + '_info.log', encoding='utf-8')
        info_handler.setLevel(logging.INFO)

        formatter = logging.Formatter(log_format)
        error_handler.setFormatter(formatter)
        warning_handler.setFormatter(formatter)
        info_handler.setFormatter(formatter)

        # 将handler添加到logger中
        logger.addHandler(error_handler)
        logger.addHandler(info_handler)
        logger.addHandler(warning_handler)
        self.logger = logger
    
    def error(self, log):
        self.logger.error(log)

    def info(self, log):
        self.logger.info(log)

    def warning(self, log):
        self.logger.warning(log)


common_logger = Logger('common')
