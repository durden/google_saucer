#!/usr/bin/python

import datetime
from google.appengine.ext import db
from google.appengine.tools import bulkloader
from models.beer import Beer
from google.appengine.api import datastore_types

class BeerLoader(bulkloader.Loader):
  def __init__(self):
    bulkloader.Loader.__init__(self, 'Beer',
                               [('name', str),
                                ('type', str),
                                ('style', str),
                                ('descr', lambda s: datastore_types.Text(s, encoding="UTF-8")),
                               ])

loaders = [BeerLoader]
