import re
from google.appengine.ext import db

class Beer(db.Model):
    name = db.StringProperty()
    type = db.StringProperty()
    style = db.StringProperty()
    descr = db.TextProperty()
    date = db.DateTimeProperty(auto_now_add=True)

    #def __str__(self):
    #    return "%s (%s):\n    %s\n    %s" % (self.name, self.type,
    #                                        self.style, self.descr)
