import logging
import logging.config

from common.util import parse_yaml


# Set Config
config = parse_yaml("config/logging.yaml")
logging.config.dictConfig(config)


# Get Loggers
AppLogger = logging.getLogger("AppLogger")
AccessLogger = logging.getLogger("AccessLogger")
ErrorLogger = logging.getLogger("ErrorLogger")


# from gunicorn.glogging import Logger 

# class StubbedGunicornLogger(Logger):
#     access_fmt = r"%(asctime)s %(process)d %(thread)d %(message)s"

#     def __init__(self, cfg):
#         super(StubbedGunicornLogger, self).__init__(cfg)
#         self.access_logger = None
#         self.error_logger = None
#         self.fastapi = None

#     def setup(self, cfg):
#         super(StubbedGunicornLogger, self).setup(cfg)
#         self.access_logger = logging.getLogger("gunicorn.access")
#         self.error_logger = logging.getLogger("gunicorn.error")

#         self._set_handler(
#             self.access_logger,
#             cfg.accesslog,
#             logging.Formatter(self.access_fmt, self.datefmt),
#         )
