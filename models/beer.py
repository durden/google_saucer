import re
from google.appengine.ext import db

class Beer(db.Model):
    name = db.StringProperty()
    type = db.StringProperty()
    style = db.StringProperty()
    descr = db.StringProperty(multiline=True)
    date = db.DateTimeProperty(auto_now_add=True)

    #def __str__(self):
    #    return "%s (%s):\n    %s\n    %s" % (self.name, self.type,
    #                                        self.style, self.descr)

    def pre_write(self):
       self.name = self.__sanitize__(self.name)
       self.type = self.__sanitize__(self.type)
       self.style = self.__sanitize__(self.style)
       self.descr = self.__sanitize__(self.descr)

    def __sanitize__(self, arg):
        # Verify the object is a string, otherwise default it
        if (not isinstance(arg, db.StringProperty())):
            return "N/A"
        # Suppress multiple spaces and newlines
        return re.sub(' +', ' ', re.sub('\n', '', arg)).strip()

    def _populate_internal_entity(self, *args, **kwds):
        """Introduces hooks into the entity storing process."""
        self.pre_write()
        return db.Model._populate_internal_entity(self, *args, **kwds)
