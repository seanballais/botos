#!/usr/bin/python3
# test.py
# Copyright (C) 2016 Sean Francis N. Ballais
#
# This module is part of Botos and is released under
# the MIT License: http://www.opensource.org/licenses/mit-license.php

"""Test runner for all the tests.

"""

import unittest

suite = unittest.TestSuite()

test_modules = [
    'tests.ActivityLogTest.ActivityLogObservableTest'
]

for test in test_modules:
    try:
        # If the module defines a suite() function, call it to get the suite.
        mod = __import__(test,
                         globals(),
                         locals(),
                         ['suite']
                         )
        suite_function = getattr(mod,
                                 'suite'
                                 )
        suite.addTest(suite_function())
    except (ImportError,
            AttributeError
            ):
        # else, just load all the test cases from the module.
        suite.addTest(unittest.defaultTestLoader.loadTestsFromName(test))

unittest.TextTestRunner().run(suite)
