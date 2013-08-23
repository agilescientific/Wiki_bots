# Catedit
# Edit every page in a category

import mwclient
import re

from config import config

# You will need to create a bot user in your wiki
# Create a file 'setup.py', e.g.
# config = {'wiki_url':'subsurfwiki.org',
#           'wiki_path':'/mediawiki/',
#           'exbot':'<password>',
#           'otherbot':'<password>'}

BOT_NAME = 'pricebot'
PASSWORD = config[BOT_NAME]

WIKI_URL = config['wiki_url']
WIKI_PATH = config['wiki_path'] # The script path for your wiki

wiki = mwclient.Site(WIKI_URL, path=WIKI_PATH)
wiki.login(BOT_NAME, PASSWORD)

for page in wiki.Categories['Petrophysics']:
    
    print "Processing {0}".format(page.page_title)
    text = page.edit()
    
    # DO SOMETHING
    # You'll need to add something here, or uncomment one of the existing actions
    
    # Add something to the head of every page
    #text = "{{petrophysics}}\n" + text
    
    # Do a regex replace
    #text = re.sub(r"{{petrophysics}}\n?",r"",text)
    
    # Save the page back to the wiki
    page.save(text,summary='Testing editing pages in category')
