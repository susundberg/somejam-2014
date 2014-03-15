import os
import urllib

from google.appengine.api import users
from google.appengine.ext import ndb

import jinja2
import webapp2
import urllib2
import Database

import re

from google.appengine.api import urlfetch


JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)

    
def get_feeds():
      feeds_query = Database.Feeds.query()
      return feeds_query.fetch(99)

class MainPage(webapp2.RequestHandler):
    def get(self):
        template_values = { 'feeds' : get_feeds() }
        template = JINJA_ENVIRONMENT.get_template('templates/main.html')
        self.response.write(template.render(template_values)) 
        
class UpdatePage(webapp2.RequestHandler):
    def get(self):
      feeds = get_feeds() 
      for feed in feeds:
         if feed.feedurl:
            print "FETCH: " + feed.feedurl 
            result = urlfetch.fetch( url = feed.feedurl + "?hl=en&max-results=4&orderby=starttime")
            print result.headers
            self.update_feed( feed, result )
            
      self.response.write("OK")   
    def update_feed( self, feed, result ):
       print "RESULT STATUS: " + str(result.status_code)
       #print "RESULT CONTENT: " + str(result.content)
       from BeautifulSoup import BeautifulStoneSoup
       soup = BeautifulStoneSoup( result.content )
       pattern = re.compile(".*When: (.*)&amp.*")
       for item in soup.findAll("summary"):
          text = item.text
          match = pattern.match( text )
          if match:
            print "GOT: " + match.group(1)
          else:
            print "No match"
          
       
    
    
class AdminPage(webapp2.RequestHandler):
    def get(self):
    
        template = JINJA_ENVIRONMENT.get_template('templates/admin.html')
        self.response.write(template.render( {} )) 
    def post(self):
        feed = Database.Feeds()
        feed.name = self.request.get('name')
        feed.desc = self.request.get('desc')
        feed.link = self.request.get('url')
        feed.feedurl  = self.request.get('feedurl')
        feed.type     = self.request.get('type')
        feed.put()
        self.response.write("OK")

        
        
        
application = webapp2.WSGIApplication([
    ('/', MainPage),
    ('/admin', AdminPage),
    ('/update', UpdatePage),
    ], debug=True)


