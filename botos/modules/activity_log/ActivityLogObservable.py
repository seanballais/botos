# botos/modules/ActivityLog/LogObservable.py
# Copyright (C) 2016 Sean Francis N. Ballais
#
# This module is part of Botos and is released under
# the MIT License: http://www.opensource.org/licenses/mit-license.php

"""Observable class that will be observed by the log observer.

"""


from botos.modules.activity_log.ActivityLogObserver import ActivityLogObserver


class ActivityLogObservable(object):
    """Class that the observer will use to know what to add to the log."""

    def add_log(self,
                level,
                message,
                *args,
                **kwargs
                ):
        """
        Append the log file of the app.

        :param message: The log message that will be added.
        :param args: An arbitrary set of positional arguments.
        :param level: Level of the log text.
        :param kwargs: An arbitrary set of keyword arguments.
        :return: Return True if successful.
        """
        if level == 0:
            level = 20

        self.log_observer.write_log(level,
                                    message,
                                    *args,
                                    **kwargs
                                    )
        return True

    def __init__(self,
                 log_observable_name
                 ):
        """
        Initialize the observable object and use it to alert the observer
        of any new logs to add.

        :param log_observable_name: Log name of the observable.
        """
        self.log_observer = ActivityLogObserver(log_observable_name)