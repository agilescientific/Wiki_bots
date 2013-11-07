#!/usr/bin/env python
# -*- coding: utf-8 -*-

############################
# patrol
# by Matt, October 2013
# Licensed Apache 2.0
# http://www.apache.org/licenses/LICENSE-2.0.html

############################
# Import libraries

# One approach to static files: DirectoryApp
#from paste.fileapp import DirectoryApp

# Another approach: Cascade
#from paste.urlparser import StaticURLParser
#from paste.cascade import Cascade

# Yet another approach
#from webapp2_static import StaticFileHandler

# Main handlers and server
from webapp2 import RequestHandler, WSGIApplication
from paste import httpserver
import mimetypes

import jinja2
import os
import re
from urlparse import urlparse

# Import the file with the wiki client and processor in it
import patrol

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

class StaticHandler(Handler):
    def get(self, path):
        abs_path = os.path.abspath(os.path.join(os.path.dirname(__file__),'static', path))
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
        self.render('patrol_nojs.html')
        
    def post(self):
        url = self.request.get('url')
        
        try:
            threshold = int(self.request.get('threshold'))
        except:
            threshold = 10
            
        try:
            days = int(self.request.get('days'))
        except:
            days = 14
        
        # TO ALSO GET
        # A category to drill into (e.g., only Geophysics)
        # New pages or all edited pages (could be slow)
        # Whether to score various parameters?
        
        if url:
            o = urlparse(url)
            domain = o.netloc
            path = re.sub(r'api.php',r'',o.path)
            print "AWESOME, the URL is {0}{1}".format(domain,path)
        else:
            domain, path = 'subsurfwiki.org','/mediawiki/'
            print "SOMETHING WRONG, no URL"
            url = 'http://{0}{1}api.php'.format(domain, path)

        result = patrol.newpages(domain=domain,path=path,threshold=threshold,days=days)
        
        worst = result[0]
        bad = result[1]
        
        everything = result[2]
                        
        # Build the URL to pass to the HTML page for making links
        page_url = re.sub(r'api.php',r'index.php',url)
        
        self.render('patrol_nojs.html', worst=worst, bad=bad, url=url, page_url=page_url, results=everything, threshold=threshold)

# The webapp itself...
app = WSGIApplication([
    ('/', MainHandler),
    (r'/patrol/static/(.+)', StaticHandler)
], debug = True)

def main():
    httpserver.serve(app, host='127.0.0.1', port='8080')

if __name__ == '__main__':
    main()