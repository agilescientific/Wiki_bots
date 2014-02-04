# -*- coding: utf-8 -*-
# Linknet

import mwclient
from passwords import passwords
import urllib2, urlparse
from cookielib import CookieJar

USER = passwords['seg']['user']
PASS = passwords['seg']['pass']

# First, get the URL token for logging in
response = urllib2.urlopen('http://wiki.seg.org/wiki/Special:UserLogin')
token = urlparse.urlparse(response.geturl()).query

# Now set up the login URL, headers etc.
LOGIN_URL = "https://login.seg.org/LoginTemplates/SEGDefaultLogin.aspx"
HEADERS = {'HTTP_USER_AGENT': 'SEG Wiki user matthall', 'HTTP_ACCEPT':'text/html,application/xhtml+xml,application/xml; q=0.9,*/*; q=0.8','Content-Type': 'application/x-www-form-urlencoded'}
DATA = "{0}&__LASTFOCUS=&__EVENTTARGET=&__EVENTARGUMENT=&__VIEWSTATE=&__EVENTVALIDATION=&LoginTextBox={1}&PasswordTextBox={2}&SubmitButton=Go".format(token,USER,PASS)
cj = CookieJar()
opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))

# Now let's authenticate on seg.org
request = urllib2.Request(LOGIN_URL, DATA, HEADERS)
response = opener.open(request)

######### PROBLEM ###########
# I don't understand the response...
print response.read()
#############################

if ("bangreeting" or "Special:UserLogout") in response.read():
    print "SEG.org login successful"
else:
    print "SEG.org login failed"

# Check if we're authneticated in the wiki
response = urllib2.urlopen('http://wiki.seg.org/wiki/Main_Page')
if ("Special:UserLogout") in response.read():
    print "Wiki login successful"
else:
    print "Wiki login failed"

# Now we can start a wiki session
WIKI_URL = 'wiki.seg.org'
WIKI_PATH = '/' 

site = mwclient.Site(WIKI_URL, path=WIKI_PATH)

# make and fill a dict for the cookies
c = {}
for cookie in cj:
    c[cookie.name] = cookie.value

#site.login(cookies=c)

##### GET ON WITH IT #####
# Use site.allpages, defaults to main namespace
# 500 is the Dictionary namespace

count = 0

for page in site.allpages(namespace=500,minsize=10,filterredir='nonredirects'):

    # Just process two for testing
    if count > 2:
        break
    
    text = page.edit()
        
    if "<center>" in text and "<math>" not in text:
        count += 1
        print page.name.encode('utf-8')
        text += "\n\n[[Category:Pages with unformatted equations]]"
        page.save(text,summary='Categorizing pages with HTML math')
                   
print "Fixed {0} pages with unformatted equations.".format(count)
