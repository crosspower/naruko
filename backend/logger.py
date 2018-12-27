from rest_framework.request import Request
from logging import getLogger


class NarukoLogging:

    def __init__(self, request: Request):
        self.request = request

    def get_logger(self, logger_name: str):
        return NarukoLogger(logger_name, self.request)


class NarukoLogger:

    MESSAGE_FORMAT = "[USER_ID: {}, URL: {} {}]  {}"

    def __init__(self, logger_name, request: Request):
        self.logger = getLogger(logger_name)
        self.request = request

    def _build_message(self, message):
        query_string = self.request.META.get("QUERY_STRING")
        return NarukoLogger.MESSAGE_FORMAT.format(
            self.request.user.id,
            self.request.method,
            self.request.path + ("?" + query_string if query_string else "")
            ,
            message
        )

    def debug(self, message):
        self.logger.debug(self._build_message(message))

    def info(self, message):
        self.logger.info(self._build_message(message))

    def error(self, message):
        self.logger.error(self._build_message(message))

    def warning(self, message):
        self.logger.warning(self._build_message(message))

    def critical(self, message):
        self.logger.critical(self._build_message(message))

    def exception(self, exception: Exception):
        self.logger.error(self._build_message(str(exception)), exc_info=True)
