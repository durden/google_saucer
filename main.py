#!/usr/bin/env python

import os
import re
import logging
import datetime

from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext.webapp import template
from google.appengine.ext import db

from models.beer import Beer
from api.saucer import Saucer

today = datetime.date.today()

class Index(webapp.RequestHandler):
    def get(self):
        drafts = Beer.all().filter("date = ", today).filter("type = ", "Draft").order("name")
        bottles = Beer.all().filter("date = ", today).filter("type = ", "Bottle").order("name")
        template_values = {'drafts' : drafts, 'bottles' : bottles}

        path = os.path.join(os.path.dirname(__file__), 'templates/index.html')
        self.response.out.write(template.render(path, template_values)) 

class Update(webapp.RequestHandler):
    def get(self, start=None, fetch=None):
        ids = []
        ii = 0
        added = 0
        skip = 10
        saucer = Saucer()
        saucer.reset_stats()
        all_beers = saucer.getAllBeers()
        num_beers = len(all_beers)

        if fetch is not None:
            num_beers = int(fetch)

        if start is not None:
            ii = int(start)

        # Don't skip by more than requested
        if num_beers < skip:
            skip = num_beers

        while added < num_beers:
            beers = all_beers[ii:ii + skip]
            for beer in beers:
                ids.append(beer['id'])

            details = saucer.getBeerDetails(ids)
            num_details = len(details)
            if not num_details:
                break

            jj = 0
            for det in details:
                tmp = Beer(name=beers[jj]['name'], type=beers[jj]['type'],
                            style=det['Style:'], descr=det['Description:'])
                db.put(tmp)
                jj += 1

            added += num_details
            ii += skip
            ids = []

        template_values = {'fetch' : Saucer.fetch, 'san' : Saucer.san,
                            'details' : Saucer.create_details, 'added' : added,
                            'start' : start, 'requested' : fetch}
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
            style = re.sub(r'%28', '(', style)
            style = re.sub(r'%29', ')', style)

            # Find all the styles by creating a set from all beers b/c
            # app engine won't let us grab just this column from a table
            beers = Beer.all().filter("date = ", today).filter("style = ", style)
            template_values = {'beers' : beers, 'search' : style}
            path = os.path.join(os.path.dirname(__file__),
                                    'templates/beers.html')
            self.response.out.write(template.render(path, template_values)) 
            return

        # Use a list to preserve ordering
        styles = []
        tmp = Beer.all().filter("date = ", today)

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
        beers = Beer.all().filter("date = ", today).filter("name = ", name)

        template_values = {'beers' : beers}
        path = os.path.join(os.path.dirname(__file__),
                                'templates/beers.html')
        self.response.out.write(template.render(path, template_values))


def main():
    #logging.getLogger().setLevel(logging.DEBUG)

    # URL Mapping
    app = webapp.WSGIApplication([('/', Index),
                                  (r'/update/(\d+)/(\d+)', Update),
                                  (r'/beer/(.*)', BrewDetail),
                                  (r'/search/*(.*)', Search),
                                  #(r'/edit/*(.*)', EditHandler),
                                  #(r'/delete/(.*)', DeleteHandler),
                                 ], debug=True)
    run_wsgi_app(app)

if __name__ == '__main__':
    main()
