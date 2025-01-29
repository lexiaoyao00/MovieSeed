import logging
from logging.handlers import TimedRotatingFileHandler
import os

LOG_DIR = 'logs'

class Logger:
    def __init__(self, name, log_file='app.log', console_level=logging.DEBUG, file_level=logging.INFO):
        """
        初始化 Logger 类。

        :param name: Logger 的名称。
        :param log_file: 日志文件的路径。
        :param console_level: 控制台日志记录的级别。
        :param file_level: 文件日志记录的级别。
        """
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.DEBUG)  # 捕获所有级别的日志
        if not os.path.exists(LOG_DIR):
            os.makedirs(LOG_DIR)

        # 避免重复添加处理器
        if not self.logger.handlers:
            # 创建一个文件处理器，指定编码为 UTF-8
            # self.file_handler = logging.FileHandler(log_file, encoding='utf-8')
            self.file_handler = TimedRotatingFileHandler(log_file, when='S', interval=1, backupCount=7, encoding='utf-8')
            self.file_handler.setLevel(file_level)
            # self.file_handler.suffix = "%Y%m%d"

            # 创建一个控制台处理器
            self.console_handler = logging.StreamHandler()
            self.console_handler.setLevel(console_level)

            # 创建一个格式化器并将其添加到处理器中
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            self.file_handler.setFormatter(formatter)
            self.console_handler.setFormatter(formatter)

            # 将处理器添加到 logger 中
            self.logger.addHandler(self.console_handler)
            self.logger.addHandler(self.file_handler)

    def debug(self, message, save_to_file=False):
        self._log(logging.DEBUG, message, save_to_file)

    def info(self, message, save_to_file=False):
        self._log(logging.INFO, message, save_to_file)

    def warning(self, message, save_to_file=False):
        self._log(logging.WARNING, message, save_to_file)

    def error(self, message, save_to_file=False):
        self._log(logging.ERROR, message, save_to_file)

    def critical(self, message, save_to_file=False):
        self._log(logging.CRITICAL, message, save_to_file)

    def _log(self, level, message, save_to_file):
        """
        通用日志记录方法。

        :param level: 日志级别（如 DEBUG, INFO, WARNING）。
        :param message: 日志消息。
        :param save_to_file: 是否强制保存到文件。
        """
        if save_to_file and (level < self.file_handler.level):
            # 临时降低文件处理器的级别以保存此条日志
            original_level = self.file_handler.level
            self.file_handler.setLevel(level)  # 设置为当前日志的级别
            self.logger.log(level, message)  # 记录日志
            self.file_handler.setLevel(original_level)  # 恢复原级别
        else:
            # 如果不要求保存到文件，直接记录日志
            self.logger.log(level, message)


# 使用示例
if __name__ == "__main__":
    log_filename = 'test.log'
    full_path = os.path.join(LOG_DIR, log_filename)
    logger = Logger(__name__, log_file =full_path)

    # DEBUG 级别日志
    logger.debug('这是一个调试信息，不保存')
    logger.debug('这是一个调试信息，手动保存', save_to_file=True)  # 保存到文件

    # INFO 级别日志
    logger.info('这是一个信息，自动保存')
    logger.info('这是一个信息，手动保存', save_to_file=True)  # 强制保存到文件

    # WARNING 级别日志
    logger.warning('这是一个警告，自动保存')
    logger.warning('这是一个警告，手动保存', save_to_file=True)  # 强制保存到文件

    # ERROR 级别日志
    logger.error('这是一个错误，自动保存')

    # CRITICAL 级别日志
    logger.critical('这是一个严重错误，自动保存')
