# -*- coding: utf-8 -*-
from peewee import SqliteDatabase, Model, TextField
from playhouse.shortcuts import RetryOperationalError
import os
import json


class JSONField(TextField):
    def db_value(self, value):
        return super(JSONField, self).db_value(
            json.dumps(value)
        )

    def python_value(self, value):
        return json.loads(value)


class TupleField(TextField):
    def db_value(self, value):
        if not (value is None or isinstance(value, (list, tuple))):
            raise ValueError("Value must be a tuple: {}".format(value))
        return super(JSONField, self).db_value(
            json.dumps(value)
        )

    def python_value(self, value):
        return tuple(json.loads(value))


class RetryDatabase(RetryOperationalError, SqliteDatabase):
    pass


database = RetryDatabase(None)
