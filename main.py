#!/usr/bin/env python

import os
import re

from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext.webapp import template
from google.appengine.ext import db

from models.beer import Beer
from api.saucer import Saucer

class Index(webapp.RequestHandler):
    def get(self):
        drafts = Beer.all().filter("type = ", "Draft")
        bottles = Beer.all().filter("type = ", "Bottle")
        template_values = {'drafts' : drafts, 'bottles' : bottles}

        path = os.path.join(os.path.dirname(__file__), 'templates/index.html')
        self.response.out.write(template.render(path, template_values)) 

class Update(webapp.RequestHandler):
    def get(self):
        saucer = Saucer()
        beers = saucer.getAllBeers()

        for beer in beers:
            details = saucer.getBeerDetails(beer['id'])
            tmp = Beer(name=beer['name'], type=beer['type'],
                        style=details['Style:'], descr=details['Description:'])
            db.put(tmp)

        template_values = {}
        path = os.path.join(os.path.dirname(__file__), 'templates/update.html')
        self.response.out.write(template.render(path, template_values)) 


class BrewDetail(webapp.RequestHandler):
    def get(self, request):
        beer = db.get(request)
        template_values = {'beer' : beer}
        path = os.path.join(os.path.dirname(__file__),
                                'templates/beer_details.html')
        self.response.out.write(template.render(path, template_values)) 
        
class Search(webapp.RequestHandler):
    def get(self, style=None):
        if style is not None and len(style) > 0:
            # FIXME: Un-urlize the string
            style = re.sub(r'%20', ' ', style)
            beers = Beer.all().filter("style = ", style)
            template_values = {'beers' : beers, 'search' : style}
            path = os.path.join(os.path.dirname(__file__),
                                    'templates/beers.html')
            self.response.out.write(template.render(path, template_values)) 
            return

        # Find all the styles by creating a set from all beers b/c
        # app engine won't let us grab just this column from a table
        tmp = Beer.all()

        # Use a list to preserve ordering
        styles = []

        for beer in tmp:
            styles.append(beer.style)

        styles = list(set(styles))
        styles.sort()
        template_values = {'styles' : styles}
        path = os.path.join(os.path.dirname(__file__),
                                'templates/search.html')
        self.response.out.write(template.render(path, template_values)) 

    def post(self, name):
        name = self.request.get('name')

        if name is None or not len(name):
            self.redirect("/search")
            return
        beers = Beer.all().filter("name = ", name)
        template_values = {'beers' : beers}
        path = os.path.join(os.path.dirname(__file__),
                                'templates/beers.html')
        self.response.out.write(template.render(path, template_values))


def main():
    #logging.getLogger().setLevel(logging.DEBUG)

    # URL Mapping
    app = webapp.WSGIApplication([('/', Index),
                                  (r'/update/', Update),
                                  (r'/beer/(.*)', BrewDetail),
                                  (r'/search/*(.*)', Search),
                                  #(r'/edit/*(.*)', EditHandler),
                                  #(r'/delete/(.*)', DeleteHandler),
                                 ], debug=True)
    run_wsgi_app(app)

if __name__ == '__main__':
    main()
