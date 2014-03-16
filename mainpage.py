import os
import urllib

from google.appengine.api import users
from google.appengine.ext import ndb

import jinja2
import webapp2
import urllib2
import Database

import re
import time

from google.appengine.api import urlfetch


JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)

    
def get_feeds():
      feeds_query = Database.Feeds.query()
      return feeds_query.fetch(99)

class JsonPage(webapp2.RequestHandler):
    def get(self):
        template_values = { 'feeds' : get_feeds() }
        template = JINJA_ENVIRONMENT.get_template('templates/main.html')
        self.response.write(template.render(template_values)) 

import datetime
def parse_time_string( str_year, str_month, str_day, str_time ):
   # Fuck, google, they return time that might or might not contain 10:10pm or 10pm
   if ":" in str_time:
      # lets hope locale is en
      strformat = "%Y-%b-%d %I:%M%p"
   else:
      strformat = "%Y-%b-%d %I%p"
   
   timestr = "%s-%s-%s %s" % (str_year, str_month, str_day, str_time)
   timeobj = time.strptime( timestr , strformat )
   
   dateobj = datetime.date( int(time.strftime("%Y", timeobj)) , int(time.strftime("%m", timeobj)), int(time.strftime("%d", timeobj)) )
   timeobj = datetime.time( int(time.strftime("%H", timeobj)), int(time.strftime("%M", timeobj)) )
   #print "CONVERTING: " + str(timestr) + " => " + str(timeobj)
   return (dateobj, timeobj)

class MainPage(webapp2.RequestHandler):
    def get(self):
        template = JINJA_ENVIRONMENT.get_template('templates/index.html')
        self.response.write(template.render( {} ))  
         
   
   
class UpdatePage(webapp2.RequestHandler):
    def get(self):
      feeds = get_feeds() 
      for feed in feeds:
         if feed.feedurl:
            feedurl = feed.feedurl + "?hl=en&max-results=3&orderby=starttime&sortorder=a&futureevents=true"
            print "FETCH: " + feedurl 
            result = urlfetch.fetch( url = feedurl )
            print result.headers
            self.update_feed( feed, result )
            
      self.response.write("OK")   
      
      
    def update_feed( self, feed, result ):
       print "RESULT STATUS: " + str(result.status_code)
       #print "RESULT CONTENT: " + str(result.content)
       from BeautifulSoup import BeautifulStoneSoup
       soup = BeautifulStoneSoup( result.content )
       pattern = re.compile(".*When: (\w+) (\w+) (\d+), (\d+) ([\d\w:]+) to ([\d\w:m]+)&amp.*")
       today_is = datetime.date.today()
       
       for item in soup.findAll("summary"):
          text = item.text
          match = pattern.match( text )
          if match:
            #print "GOT: %s-%s-%s-%s %s->%s" % ( match.group(1), match.group(2), match.group(3), match.group(4),
            #                                    match.group(5), match.group(6) )
            #print "Opens: " + time_open_str + " closes: " + time_close_str
            # Opens: 2014-Aug-24 10am closes: 2014-Aug-24 11am
            
            try: 
              (open_date , open_time)  = parse_time_string( match.group(4), match.group(2), match.group(3), match.group(5) )
              (close_date, close_time) = parse_time_string( match.group(4), match.group(2), match.group(3), match.group(6) ) 
            except ValueError as err: 
              time_open_str  = "%s-%s-%s %s" % (match.group(4), match.group(2), match.group(3), match.group(5))
              time_close_str = "%s-%s-%s %s" % (match.group(4), match.group(2), match.group(3), match.group(6))
              print "Seems like we got bad open/close time, fix format. Got %s,%s" % (time_open_str, time_close_str)
            else:
              #print "OPEN:" + str(open_date) + ":" + str(open_time)
              #print "CLOSE:" + str(close_date) + ":" + str(close_time)
              #strformat = "%Y-%b-%d %H:%M"
              #strformat = "%Y-%b-%d %H:%M"
              if today_is == open_date:
                 feed.open  = open_time.strftime( "%H:%M" )
                 feed.close = close_time.strftime( "%H:%M" )
                 feed.put()
                 break
          else:
            print "No match: '%s'" % text
          
       
    
    
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
    ('/json', JsonPage),
    ('/admin', AdminPage),
    ('/update', UpdatePage),
    ], debug=True)


