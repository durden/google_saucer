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
today = datetime.date.today()
week = datetime.timedelta(weeks=1)
last = today - week
next = today + week

# Helper function for removing url encoding
def __url_decode__(arg):
    arg = re.sub(r'%20', ' ', arg)
    arg = re.sub(r'%28', '(', arg)
    arg = re.sub(r'%29', ')', arg)
    return arg

# Helper function for sorting weekly brews
def __weekly_brews__(query):
    return query.filter("date >= ", last).filter("date < ", next).order("date")

class BrewHandler(webapp.RequestHandler):
    # FIXME: Better way to do this?
    def type(self):
        return None

    def get(self):
        beers = __weekly_brews__(Beer.all().filter("type = ", self.type())).order("name")
        template_values = {'beers' : beers, 'type' : self.type()}

        # FIXME: This template sucks b/c it has 4 loops that are duplicates
        path = os.path.join(os.path.dirname(__file__), 'templates/type.html')
        self.response.out.write(template.render(path, template_values)) 

class CanHandler(BrewHandler):
    def type(self):
        return "Can"

class CaskHandler(BrewHandler):
    def type(self):
        return "Cask"

class DraftHandler(BrewHandler):
    def type(self):
        return "Draft"

class BottleHandler(BrewHandler):
    def type(self):
        return "Bottle"

class Index(webapp.RequestHandler):
    def get(self):
        # Have to filter name afterwards b/c datastore requires the inequality
        # operators to have a order FIRST if there is going to be any order
        # clauses at all (see datastore docs)
        drafts = __weekly_brews__(Beer.all().filter("type = ", "Draft")).order("name")
        bottles = __weekly_brews__(Beer.all().filter("type = ", "Bottle")).order("name")
        cans = __weekly_brews__(Beer.all().filter("type = ", "Can")).order("name")
        casks = __weekly_brews__(Beer.all().filter("type = ", "Cask")).order("name")

        beers = {}
        beers['drafts'] = drafts
        beers['bottles'] = bottles
        beers['cans'] = cans
        beers['casks'] = casks

        template_values = {'beers' : beers}

        # FIXME: This template sucks b/c it has 4 loops that are duplicates
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
    def get(self, req):
        # Use fetch here to make the query actually execute and hope there is
        # only 1 with this name... :)
        beer = Beer.all().filter('name = ', __url_decode__(req)).fetch(1)[0]

        template_values = {'beer' : beer}
        path = os.path.join(os.path.dirname(__file__),
                                'templates/beer_details.html')
        self.response.out.write(template.render(path, template_values)) 
        
class Search(webapp.RequestHandler):
    def get(self, style=None):
        if style is not None and len(style) > 0:

            # Find all the styles by creating a set from all beers b/c
            # app engine won't let us grab just this column from a table
            style = __url_decode__(style)
            beers = __weekly_brews__(Beer.all().filter("style = ", style)).order("name")

            template_values = {'beers' : beers, 'search' : style}
            path = os.path.join(os.path.dirname(__file__),
                                    'templates/beers.html')
            self.response.out.write(template.render(path, template_values)) 
            return

        # Use a list to preserve ordering
        styles = []
        tmp = __weekly_brews__(Beer.all())

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
        beers = __weekly_brews__(Beer.all().filter("name = ", name))

        template_values = {'beers' : beers}
        path = os.path.join(os.path.dirname(__file__), 'templates/beers.html')
        self.response.out.write(template.render(path, template_values))

def main():
    #logging.getLogger().setLevel(logging.DEBUG)

    # URL Mapping
    app = webapp.WSGIApplication([('/', Index),
                                  (r'/update/(\d+)/(\d+)', Update),
                                  (r'/beer/(.*)', BrewDetail),
                                  (r'/search/*(.*)', Search),
                                  (r'/cask/', CaskHandler),
                                  (r'/can/', CanHandler),
                                  (r'/bottle/', BottleHandler),
                                  (r'/draft/', DraftHandler),
                                 ], debug=True)
    run_wsgi_app(app)

if __name__ == '__main__':
    main()
