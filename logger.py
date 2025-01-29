import logging

class ConditionalFileHandler(logging.FileHandler):
    """自定义文件处理器，根据条件决定是否记录日志。"""
    def __init__(self, filename, level=logging.NOTSET):
        super().__init__(filename, level)
        self.save_log = False

    def emit(self, record):
        if getattr(record, 'save_log', False):
            super().emit(record)

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
        self.logger.setLevel(logging.DEBUG)  # 设为DEBUG以捕获所有级别的日志

        # 避免重复添加处理器
        if not self.logger.handlers:
            # 创建一个自定义文件处理器
            file_handler = ConditionalFileHandler(log_file)
            file_handler.setLevel(file_level)

            # 创建一个控制台处理器
            console_handler = logging.StreamHandler()
            console_handler.setLevel(console_level)

            # 创建一个格式化器并将其添加到处理器中
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            file_handler.setFormatter(formatter)
            console_handler.setFormatter(formatter)

            # 将处理器添加到 logger 中
            self.logger.addHandler(file_handler)
            self.logger.addHandler(console_handler)

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
        extra = {'save_log': save_to_file}
        self.logger.log(level, message, extra=extra)

# 使用示例
if __name__ == "__main__":
    logger = Logger(__name__, console_level=logging.DEBUG, file_level=logging.DEBUG)
    logger.debug('这是一个调试信息，不保存')
    logger.debug('这是一个调试信息，保存', save_to_file=True)  # 使用参数控制保存到文件
    logger.info('这是一个信息')
    logger.warning('这是一个警告')
    logger.error('这是一个错误')
    logger.critical('这是一个严重错误')
