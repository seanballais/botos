# botos/modules/app_data/sqlalchemy_columns.py
# Copyright (C) 2016 Sean Francis N. Ballais
#
# This module is part of Botos and is released under
# the MIT License: http://www.opensource.org/licenses/mit-license.php

"""Custom SQLAlchemy column types.

"""


import json

import sqlalchemy
from sqlalchemy.ext import mutable


class JsonEncodedDict(sqlalchemy.TypeDecorator):
    """
    Custom JSON column type that enables JSON encoding and decoding on the fly.
    """
    impl = sqlalchemy.String

    def process_bind_param(self,
                           value,
                           dialect
                           ):
        return json.dumps(value)

    def process_result_value(self,
                             value,
                             dialect
                             ):
        return json.loads(value)

mutable.MutableDict.associate_with(JsonEncodedDict)