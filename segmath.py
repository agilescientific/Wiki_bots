# -*- coding: utf-8 -*-
# Linknet

import re
import mwclient
from passwords import passwords

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

added, removed, inspected = 0, 0, 0

for page in site.allpages(namespace=500,minsize=10,filterredir='nonredirects'):

    # Just process two for testing
    #if added + removed == 2:
    #    break

    inspected += 1

    text = page.edit()

    # Deal with pages that have the tag already.
    if re.search(r'\[\[Category:Pages with unformatted equations\]\]', text):
        if "<center>" in text and "<math>" not in text:
            # Then it's already tagged and we're good.
            print ':',
            continue
        else:
            # Remove the tag and save.
            text = re.sub(r'\n*?\[\[Category:Pages with unformatted equations\]\]', '', text)
            page.save(text, summary='Removing category tag')
            removed += 1
            logging.info('Untagging {0}'.format(page.name.encode('utf-8')))
            print '-',

    else:
        if "<center>" in text and "<math>" not in text:
            text += "\n\n[[Category:Pages with unformatted equations]]"
            page.save(text,summary='Categorizing pages with HTML math')
            added += 1
            logging.info('Tagging {0}'.format(page.name.encode('utf-8')))
            print '+',

        else:
            # The page has no tag and no HTML equation.
            print '.',
            continue
                       
logging.info("Inspected {0} pages for unformatted equations.".format(inspected))
logging.info("Found {0} pages with unformatted equations.".format(added))
logging.info("Removed cat tag from {0} pages with no unformatted equations.".format(removed))
