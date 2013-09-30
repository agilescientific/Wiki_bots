# -*- coding: utf-8 -*-
# Linknet

import mwclient
import re
from passwords import passwords
import urllib, urllib2
from cookielib import CookieJar

USER = passwords['seg']['user']
PASS = passwords['seg']['pass']

# First, set up the login parameters
LOGIN_URL = "https://login.seg.org/LoginTemplates/SEGDefaultLogin.aspx"
HEADERS = {'HTTP_USER_AGENT': 'SEG Wiki user matthall', 'HTTP_ACCEPT':'text/html,application/xhtml+xml,application/xml; q=0.9,*/*; q=0.8','Content-Type': 'application/x-www-form-urlencoded'}
encoded_fields = "__LASTFOCUS=&__EVENTTARGET=&__EVENTARGUMENT=&__VIEWSTATE=&__EVENTVALIDATION=&LoginTextBox={0}&PasswordTextBox={1}&SubmitButton=Go".format(USER,PASS)
cj = CookieJar()
opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))

# Now let's authenticate on seg.org
request = urllib2.Request(LOGIN_URL,encoded_fields,HEADERS)
response = opener.open(request)
result = response.read()
if "bangreeting" in result:
    print "Login successful"
else:
    print "Login failed"

# Now we can start a wiki session
WIKI_URL = 'wiki.seg.org'
WIKI_PATH = '/' 

site = mwclient.Site(WIKI_URL, path=WIKI_PATH)

##### GET ON WITH IT #####
# Use site.allpages, defaults to main namespace
# 500 is the Dictionary namespace

count = 0

for page in site.allpages(namespace=500,minsize=10,filterredir='nonredirects'):

    # Sometimes need to filter or act based on page contents
    if count > 2:
        break
    
    text = page.edit()
        
    if "<center>" in text and "<math>" not in text:
        count += 1
        print page.name.encode('utf-8')
        text += "\n\n[[Category:Pages with unformatted equations]]"
        page.save(text,summary='Categorizing pages with HTML math')
                   
print "Fixed {0} pages with unformatted equations.".format(count)
