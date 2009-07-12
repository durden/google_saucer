#!/usr/bin/env python

import os
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext.webapp import template
#from google.appengine.ext import db
from models.beer import Beer
from api.saucer import Saucer

class Index(webapp.RequestHandler):
    def get(self):
        saucer = Saucer()
        beers = saucer.getAllBeers()
        template_values = {'beers' : beers}

        path = os.path.join(os.path.dirname(__file__), 'templates/index.html')
        self.response.out.write(template.render(path, template_values)) 




def main():
    # URL Mapping
    app = webapp.WSGIApplication([('/', Index),
                                  #(r'/view/*(.*)', RootHandler),
                                  #(r'/edit/*(.*)', EditHandler),
                                  #(r'/delete/(.*)', DeleteHandler),
                                 ], debug=True)
    run_wsgi_app(app)

if __name__ == '__main__':
    main()
