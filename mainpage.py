import os
import urllib

from google.appengine.api import users
from google.appengine.ext import ndb

import jinja2
import webapp2

import Database

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)

    
def get_feeds():
      feeds_query = Database.Feeds.query()
      feeds = feeds_query.fetch(99)
      template_values = { "feeds" : feeds }
      return template_values

class MainPage(webapp2.RequestHandler):
    def get(self):
        template_values = get_feeds()
        template = JINJA_ENVIRONMENT.get_template('templates/main.html')
        self.response.write(template.render(template_values)) 

        
class AdminPage(webapp2.RequestHandler):
    def get(self):
    
        template = JINJA_ENVIRONMENT.get_template('templates/admin.html')
        self.response.write(template.render( {} )) 
    def post(self):
        feed = Database.Feeds()
        feed.name = self.request.get('name')
        feed.desc = self.request.get('desc')
        feed.link = self.request.get('url')
        feed.feed_url = self.request.get('feed_url')
        feed.type     = self.request.get('type')
        feed.put()
        self.response.write("OK")
        
        
application = webapp2.WSGIApplication([
    ('/', MainPage),
    ('/admin', AdminPage),
    ('/update', Updatepage),
    ], debug=True)


