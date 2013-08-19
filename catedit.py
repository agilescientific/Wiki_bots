# Catedit
# Edit every page in a category

import mwclient
import re

# Put the bot's password in a file called passwords.py
# containing one line per bot:
#    username = "<password>"
import passwords

# You will need to create a user for Pricebot in your wiki
USERNAME = 'Exbot'
PASSWORD = passwords.exbot

# You will need to change these too
WIKI_URL = 'subsurfwiki.org'
WIKI_PATH = '/mediawiki/' # The script path for your wiki

wiki = mwclient.Site(WIKI_URL, path=WIKI_PATH)
wiki.login(USERNAME, PASSWORD)

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
