import re
import urllib
import logging

from django.utils import simplejson

class Saucer():
    BOTTLE = "Bottle"
    DRAFT = "Draft"

    __btl_str__ = r"\(BTL\)"

    def __sanitize__(self, arg):
        ret = "N/A"

        if (isinstance(arg, unicode)):
            # Suppress multiple whitespace characters and leading/trailing
            # whitespace
            ret = re.sub('\s+', ' ', arg).strip()
            #ret = ' '.join(arg.split())

        return ret

    def __fetch_json__(self, url):
        base_url = "http://query.yahooapis.com/v1/public/yql"
        return simplejson.load(urllib.urlopen( "%s?%s" % (base_url, url)))

    def __create_detail_list__(self, res):
        size = len(res)
        ii = 0
        sep = 1
        mylist = []
        dict = {}

        # Loop through resulting list in pairs and collect 6 key,value pairs
        # and then add the dictionary to the returning list
        while ii < size:
            key = self.__sanitize__(res[ii])
            val = self.__sanitize__(res[ii + 1])

            dict[key] = val

            # End of unique pairs
            if not sep % 6:
                mylist.append(dict)
                dict = {}

            ii += 2
            sep += 1

        return mylist

    def getAllBeers(self):
        url = urllib.urlencode({"format":"json",
            "q":"select * from html where url=\"http://www.beerknurd.com/store.sub.php?store=6&sub=beer&groupby=name\" and xpath='//select[@id=\"brews\"]/option'"})

        res = self.__fetch_json__(url)

        # Hide the ugly yql/html parsing and create list of dictionaries 
        beers = []
        regex = re.compile(Saucer.__btl_str__)
        for tmp in res['query']['results']['option']:
            beer = {}

            beer['name'] = self.__sanitize__(tmp['content'])
            beer['id'] = tmp['value'].strip()
            beer['type'] = Saucer.DRAFT 

            # Bottle or draft?
            if regex.search(beer['name']):
                beer['type'] = Saucer.BOTTLE

                # Remove the bottle string in name
                beer['name'] = re.sub(Saucer.__btl_str__, '', beer['name'])

            beers.append(beer)

        return beers

    def getBeerDetails(self, beers):
        xpath= "xpath='//table/tr/td/p'"
        q = "select * from html where ("
        ii = 0

        for beer in beers:
            if ii:
                q += " or "

            q += "url=\"http://www.beerknurd.com/store.beers.process.php?brew=%s\"" % (beer)
            ii = 1

        q += ") and %s " % (xpath)
        logging.debug("beers = %s ....... q = %s" % (beers, q))
        res = self.__fetch_json__(urllib.urlencode({"format":"json", "q": q}))
        return self.__create_detail_list__(res['query']['results']['p'])
