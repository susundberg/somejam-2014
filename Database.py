import cgi
import urllib

from google.appengine.api import users
from google.appengine.ext import ndb

import webapp2


class Feeds(ndb.Model):
    name    = ndb.StringProperty(indexed=False)
    desc    = ndb.StringProperty(indexed=False)
    open    = ndb.StringProperty(indexed=False)
    close   = ndb.StringProperty(indexed=False)
    link    = ndb.StringProperty(indexed=False)
    feedurl = ndb.StringProperty(indexed=False)
    type    = ndb.StringProperty(indexed=False)


