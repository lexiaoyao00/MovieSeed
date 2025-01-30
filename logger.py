import logging
from logging.handlers import TimedRotatingFileHandler,RotatingFileHandler
import sys
import os
from datetime import datetime

LOG_DIR = 'logs'


class Logger:
    def __init__(self, name, level=logging.INFO, log_file=None, file_level=logging.DEBUG):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(level)
        self.formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

        # Console handler
        self.console_handler = logging.StreamHandler(sys.stdout)
        self.console_handler.setFormatter(self.formatter)
        self.console_handler.setLevel(level)
        self.logger.addHandler(self.console_handler)

        # File handler (optional)
        self.file_handler = None
        if log_file:
            self.add_file_handler(log_file,file_level)

        self.ui_callback = None

    def set_level(self, level):
        self.logger.setLevel(level)
        self.console_handler.setLevel(level)

    def add_file_handler(self, log_file,file_level=logging.DEBUG):
        if not self.file_handler:
            logs_dir = os.path.join(os.getcwd(), LOG_DIR)
            os.makedirs(logs_dir, exist_ok=True)
            log_file_path = os.path.join(logs_dir, log_file)
            # Use TimedRotatingFileHandler for daily log files
            self.file_handler = TimedRotatingFileHandler(
                log_file_path,
                when="midnight",
                interval=1,
                backupCount=30,  # Keep logs for 30 days
                encoding="utf-8"
            )
            self.file_handler.setFormatter(self.formatter)
            self.file_handler.setLevel(logging.DEBUG)  # Set to lowest level to catch all logs

            # Set a custom naming format for rotated files
            self.file_handler.namer = lambda name: name.replace(".log", "") + "_%Y%m%d.log"

            self.logger.addHandler(self.file_handler)

    def set_ui_callback(self, callback):
        self.ui_callback = callback

    def _log(self, level, message, *args, **kwargs):
        force = kwargs.pop('force', False)

        if force or level >= self.logger.level:
            self.logger.log(level, message, *args, **kwargs)

        if force and self.file_handler:
            self.file_handler.emit(logging.LogRecord(
                name=self.logger.name,
                level=level,
                pathname='',
                lineno=0,
                msg=message,
                args=args,
                exc_info=None
            ))

        if self.ui_callback:
            self.ui_callback(level, message % args if args else message)

    def debug(self, message, *args, **kwargs):
        self._log(logging.DEBUG, message, *args, **kwargs)

    def info(self, message, *args, **kwargs):
        self._log(logging.INFO, message, *args, **kwargs)

    def warning(self, message, *args, **kwargs):
        self._log(logging.WARNING, message, *args, **kwargs)

    def error(self, message, *args, **kwargs):
        self._log(logging.ERROR, message, *args, **kwargs)

    def critical(self, message, *args, **kwargs):
        self._log(logging.CRITICAL, message, *args, **kwargs)



# 使用示例
if __name__ == "__main__":
    # 创建logger实例，设置级别为ERROR
    logger = Logger("MyApp", level=logging.ERROR, log_file="app.log")

    # 正常的日志记录，只有ERROR和CRITICAL会被记录
    logger.debug("This debug message will not be logged")
    logger.info("This info message will not be logged")
    logger.warning("This warning message will not be logged")
    logger.error("This error message will be logged")
    logger.critical("This critical message will be logged")

    # 强制记录低级别的日志
    logger.debug("This debug message will be forced to log", force=True)
    logger.info("This info message will be forced to log", force=True)
    logger.warning("This warning message will be forced to log", force=True)

    # 设置UI回调
    def ui_log_callback(level, message):
        print(f"UI Log: [{logging.getLevelName(level)}] {message}")

    logger.set_ui_callback(ui_log_callback)

    # 记录日志，会同时调用UI回调
    logger.info("This info will not be logged but will show in UI", force=True)
    logger.error("This error will be logged and shown in UI")

