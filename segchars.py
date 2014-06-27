# -*- coding: utf-8 -*-
# Linknet

import re
import mwclient
from passwords import passwords
from agile import hexchars

import ConfigParser
config = ConfigParser.RawConfigParser()
config.read('segmath.cfg')

# Wiki info
WIKI = config.get('wiki_info', 'wiki')
PATH = config.get('wiki_info', 'path')
USER = config.get('wiki_info', 'bot')
PASS = passwords[WIKI][USER]

# Set up logging
import logging
LOG_FILE = 'segmath.log'
logging.basicConfig(filename=LOG_FILE,
                    level=logging.INFO,
                    filemode='w'
                    )

site = mwclient.Site(WIKI, path=PATH)
site.login(USER, PASS)

nosubs, subs, allsubs = 0, 0, 0

for page in site.allpages(namespace=500,minsize=10,filterredir='nonredirects'):

    # Just process two pages for testing
    if subs == 20:
        break

    text = page.edit()

    subs_in_page = 0

    try:
        for uni, html in hexchars.iteritems():
            text, n = re.subn(uni, html, text)
            subs_in_page += n

    except Exception, e:
        print "{0}: Failed to convert {1} {2}".format(page.name.encode('utf-8'), uni, e)

    for s in re.findall(r'\&\#x[0-9A-Za-z]{4};', text):
        print "{0}".format(s),

    if subs_in_page == 0:
        print '.',
        nosubs += 1
    else:
        print subs_in_page,
        subs += 1
        allsubs += subs_in_page

    #page.save(text, summary='Changing hex characters to named entities')

logging.info("Subbed {0} characters on {1} pages.".format(allsubs, subs))
logging.info("Found nothing on {0} pages, out of {1} pages.".format(nosubs, subs+nosubs))
