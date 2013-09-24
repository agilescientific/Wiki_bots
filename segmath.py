# -*- coding: utf-8 -*-
# Linknet

import mwclient
import re
from config import config

# You will need to create a bot user in your wiki
# Create a file 'setup.py'
# config = {'wiki_url':'subsurfwiki.org',
#           'wiki_path':'/mediawiki/',
#           'exbot':'<password>',
#           'otherbot':'<password>'}

BOT_NAME = 'Matthall'
PASSWORD = config[BOT_NAME]

WIKI_URL = config['wiki_url']
WIKI_PATH = config['wiki_path'] # The script path for your wiki

site = mwclient.Site(WIKI_URL, path=WIKI_PATH)

# I can't figure out how to log in with the single-sign on
# So we can't write pages back to the wiki right now
#site.login(BOT_NAME, PASSWORD)

##### GET ON WITH IT #####
# Use site.allpages, defaults to main namespace
# 500 is the Dictionary namespace

count = 0

for page in site.allpages(namespace=500,minsize=10,filterredir='nonredirects'):

    # Sometimes need to filter or act based on page contents
    text = page.edit()
        
    if "<center>" in text and "<math>" not in text:
        count += 1
        print page.name.encode('utf-8')
        #text += "\n\n[[Category:Pages with unformatted equations]]"
        #page.save(price+update_time,summary='Bot finding pages to fix')
                   
print "Found {0} pages with unformatted equations.".format(count)
