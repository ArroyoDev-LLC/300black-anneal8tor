# -*- coding: utf-8 -*-

"""300black Models"""

from ucollections import OrderedDict
import btreedb as uorm

db = uorm.DB('black.db')


class Config(uorm.Model):
    __db__ = db
    __table__ = 'config'
    __schema__ = OrderedDict([
        ("key", ("TEXT", "")),
        ("value", ("TEXT", "")),
    ])
