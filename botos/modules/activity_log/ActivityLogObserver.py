# botos/modules/ActivityLog/LogObserver.py
# Copyright (C) 2016 Sean Francis N. Ballais
#
# This module is part of Botos and is released under
# the MIT License: http://www.opensource.org/licenses/mit-license.php

"""Observer for the observable modules.

"""


import logging
import settings


class ActivityLogObserver(object):
    """The class that will be responsible for appending to the log."""

    def write_log(self,
                  level,
                  message,
                  *args,
                  **kwargs
                  ):
        """
        Write a log to the log file as defined in the settings.

        :param message: The log message.
        :param args: Arguments that might be used for the log.
        :param level: Level of the log.
        :return: Returns True when log finishes.
        """
        if level == 0:
            level = 20

        self.logger.log(level,
                        message,
                        *args,
                        exc_info=True,
                        **kwargs
                        )
        return True

    def __init__(self,
                 logger_name
                 ):
        """
        Initialize the LogObserver and use it for logging purposes.

        :param logger_name: Name of the activity_log.
        """
        self.logger = logging.getLogger(logger_name)
        self.logger.setLevel(settings.LOG_LEVEL)

        _log_file_handler = logging.FileHandler(settings.LOG_FILENAME)
        _log_file_handler.setLevel(settings.LOG_LEVEL)

        # create a formatter and set the formatter for the handler.
        _log_format = logging.Formatter(
            '%(asctime)s.%(msecs)d (%(name)s) | %(levelname)s: %(funcName)20s() - %(message)s'
        )
        _log_file_handler.setFormatter(_log_format)

        self.logger.addHandler(_log_file_handler)

    def __repr__(self):
        return '<LogObserver>'