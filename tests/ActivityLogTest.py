#!/usr/bin/python3
# botos/test/ActivityLogTest.py
# Copyright (C) 2016 Sean Francis N. Ballais
#
# This module is part of Botos and is released under
# the MIT License: http://www.opensource.org/licenses/mit-license.php

"""Unit test for the ActivityLog module.

"""


import unittest
import os

from botos.modules.activity_log import ActivityLogObservable
from botos.modules.activity_log import _log_levels

import settings


class ActivityLogObservableTest(unittest.TestCase):
    """
    The observable test class for the Logger module.
    """

    def setUp(self):
        # Backup the file first.
        if os.path.exists(settings.BASE_DIR + settings.LOG_FILENAME):
            os.rename(settings.LOG_FILENAME,
                      settings.LOG_FILENAME + '.bak'
                      )

        self.log_observable = ActivityLogObservable.ActivityLogObservable(__name__)

        print('Testing ActivityLog...', end='')

    def _clear_log_file(self):
        """
        Clear the contents of the log file.
        """
        open(settings.BASE_DIR + settings.LOG_FILENAME,
             'w'
             ).close()

    def _get_log_first_line(self):
        """
        Get the first line of the log file.

        :return: A string of the first line of the log file.
        """
        with open(settings.BASE_DIR + settings.LOG_FILENAME,
                  mode='r'
                  ) as _log_file:
            _log_line = _log_file.readline().strip()
            return _log_line[_log_line.index('|') + 2:]

    def test_add_log(self):
        """
        Test the add log function in observable modules.
        """
        for _log_level in _log_levels:
            self._clear_log_file()
            self.log_observable.add_log(_log_level[0],  # Log level severity INFO
                                        'Test text.'
                                        )
            self.assertEqual(self._get_log_first_line(),
                             _log_level[1] + ': Test text.'
                             )

    def tearDown(self):
        """
        Clean up the mess we made.
        """
        os.remove(settings.LOG_FILENAME)

        if os.path.exists(settings.BASE_DIR + settings.LOG_FILENAME):
            os.rename(settings.LOG_FILENAME + '.bak',
                      settings.LOG_FILENAME
                      )

        print(' DONE')

if __name__ == '__main__':
    unittest.main()
