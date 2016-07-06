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

import settings
import botos.modules.activity_log.ActivityLogObservable as ActivityLogObservable


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

    def test_add_log(self):
        """
        Test the add log function in observable modules.
        """
        self.log_observable.add_log(20,  # Log level severity
                                    "Test text."
                                    )

        with open(settings.BASE_DIR + settings.LOG_FILENAME,
                  mode='r'
                  ) as file:
            log_line = file.readline().strip()
            test_text = log_line[log_line.index('|') + 2:]

        self.assertEqual(test_text,
                         "Test text."
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

if __name__ == '__main__':
    unittest.main()
