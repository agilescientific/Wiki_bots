#!/usr/bin/env python
# -*- coding: utf-8 -*-

############################
# patrol
# by Matt, October 2013
# Licensed Apache 2.0
# http://www.apache.org/licenses/LICENSE-2.0.html

############################
# Import libraries
#from paste.fileapp import DirectoryApp
from paste.urlparser import StaticURLParser
from paste.cascade import Cascade
from paste import httpserver

from webapp2 import RequestHandler, WSGIApplication
import mimetypes
import jinja2
import os

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
        abs_path = os.path.abspath(os.path.join(self.app.config.get('webapp2_static.static_file_path', 'static'), path))
        if os.path.isdir(abs_path) or abs_path.find(os.getcwd()) != 0:
            self.response.set_status(403)
            return
        try:
            f = open(abs_path, 'r')
            #self.response.headers.add_header('Content-Type', mimetypes.guess_type(abs_path)[0])
            self.response.content_type = 'text/css'
            self.response.out.write(f.read())
            f.close()
        except:
            self.response.set_status(404)

#############################
# This is where the handlers go
class MainHandler(Handler):
    def get(self):
        self.render("patrol.html")
        
    def post(self):
        worst = patrol.newpages()
        self.render("patrol.html", result=worst)

# The webapp itself...
web_app = WSGIApplication([
    ('/', MainHandler),
    (r'/static/(.+)', StaticHandler)
    # Put other handlers here, if you need them
], debug = True)

# Create an app to serve static files
#static_app = StaticURLParser('static')

# Create a cascade that looks for static files first, then tries the webapp
#app = Cascade([static_app, web_app])

def main():
    httpserver.serve(web_app, host='127.0.0.1', port='8080')

if __name__ == '__main__':
    main()