import re
import urllib
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

    def getBeerDetails(self, beer):
        xpath= "xpath='//table/tr/td/p'"
        url = urllib.urlencode({"format":"json",
            "q":"select * from html where url=\"http://www.beerknurd.com/store.beers.process.php?brew=%s\" and %s" % (beer, xpath)})

        res = self.__fetch_json__(url)

        # Create a dictionary b/c it's easier to work with
        tmp = dict(zip(res['query']['results']['p'][::2],
                    res['query']['results']['p'][1::2]))

        # Cleanup all the whitespace, etc.
        for k,v in tmp.items():
            tmp[k] = self.__sanitize__(v)

        return tmp
