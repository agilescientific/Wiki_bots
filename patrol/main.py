#!/usr/bin/env python
# -*- coding: utf-8 -*-

############################
# patrol
# by Matt, October 2013
# Licensed Apache 2.0
# http://www.apache.org/licenses/LICENSE-2.0.html

############################
# Import libraries

# Main handlers and server
from webapp2 import RequestHandler, WSGIApplication
from paste import httpserver
import mimetypes

import jinja2
import os
import re
from urlparse import urlparse
import time
TIME = {}

# Import the wiki processing stuff
import mwclient
import patrol

# Import the config with the wiki settings
from config import config

#######
# This is gross, but I can't see how else to instantiate the site variable
site = None

############################
# Set up the authentication
BOT_USERNAME = config['username']
BOT_PASSWORD = config['password']
DEFAULT_WIKI = config['defaultwiki']
DEFAULT_PATH = config['defaultpath']

#############################
# Set up the template stuff
template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir),
                               autoescape = True)

def datetimeformat(value, format='%H:%M on %d.%m.%Y'):
    return value.strftime(format)

jinja_env.filters['datetimeformat'] = datetimeformat

class Handler(RequestHandler):
    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)

    def render_str(self, template, **params):
        t = jinja_env.get_template(template)
        return t.render(params)

    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))

#############################
# Deal with static resources like CSS, JS, etc.
class StaticHandler(Handler):
    def get(self, file):
        abs_path = os.path.abspath(os.path.join(os.path.dirname(__file__),'assets', file))
        if os.path.isdir(abs_path) or abs_path.find(os.getcwd()) != 0:
            self.response.set_status(403)
            return
        try:
            f = open(abs_path, 'r')
            self.response.content_type = mimetypes.guess_type(abs_path)[0]
            self.response.out.write(f.read())
            f.close()
        except:
            self.response.set_status(404)

#############################
# This is where the handlers go
class MainHandler(Handler):
    def get(self):
        self.render('patrol.html')
        
    def post(self):
    
        TIME['start'] = time.time()
            
        url = self.request.get('url')
        categories = self.request.get('categories')        
        categories = re.sub(r"[,\.\n]+", r"\n", categories)
        
        cats = [c.strip().title() for c in categories.split('\n')]
        cats = filter(None,cats)
        
        if cats:
            print "-- Categories provided; working on categories", cats
        else:
            print "-- No categories; working on all pages"                
                                
        try:
            threshold = int(self.request.get('threshold'))
        except:
            threshold = 10
            
        try:
            days = int(self.request.get('days'))
        except:
            days = 14
        
        if url:
            o = urlparse(url)
            domain = o.netloc
            path = re.sub(r'api.php',r'',o.path)
            print "-- AWESOME, the URL is {0}".format(url)
        else:
            domain, path = DEFAULT_WIKI,DEFAULT_PATH
            url = 'http://{0}{1}api.php'.format(domain, path)
            print "-- No URL provided, using {0}".format(url)

        # Authenticate in the wiki
        global site
        
        try:
            site = mwclient.Site(domain, path=path)
            print '-- Connected to API at {0}'.format(domain)
            
        except Exception, e:
            print '** Failed to connect to {0}: {1}'.format(domain,e)

        result = patrol.newpages(site=site,categories=cats,threshold=threshold,days=days)
    
        worst = result[0]
        bad = result[1]
        
        everything = result[2]
                        
        # Build the URL to pass to the HTML page for making links
        page_url = re.sub(r'api.php',r'index.php',url)
        
        query_time = str(round(time.time() - TIME['start'],1))

        self.render('result.html', worst=worst, bad=bad, url=domain, page_url=page_url, results=everything, threshold=threshold, time=query_time)
        
class TagHandler(Handler):
        
    def post(self):
    
        page = self.request.get('page')

        print "-- Request to tag article '{0}'; using bot user {1}".format(page, BOT_USERNAME)

        global site
        site.login(BOT_USERNAME, BOT_PASSWORD)

        patrol.tag_page(site, page)

        self.response.write('Done')
        # self.redirect('/result')
        
# The webapp itself...
app = WSGIApplication([
    ('/', MainHandler),
    (r'/result', MainHandler),
#     (r'/result#<page:(.+)>', TagHandler),
     (r'/tag', TagHandler),
    (r'/patrol/assets/(.+)', StaticHandler),
], debug = True)

def main():
    httpserver.serve(app, host='127.0.0.1', port='8081')

if __name__ == '__main__':
    main()
