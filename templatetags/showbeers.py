from google.appengine.ext.webapp import template

register = template.create_template_register()

# FIXME: It would be much nicer to use an inclusion tag, but thats part of
# the django development branch, and isn't available to app engine yet...
def list_beers(beers, type):
    str = '<h2>' + type + ' Beers</h2><ul>'
    for beer in beers:
        key = "%s" % beer.key()
        str += '<li><a href="/beer/' + key + '">' + beer.name + '</a></li>'
    str += '</ul>'
    return str

register.filter(list_beers)
