# Catedit
# Edit every page in a category

import mwclient
from config import config
import time

##################
# Authentication
BOT_NAME = 'exbot'
PASSWORD = config[BOT_NAME]

WIKI_URL = config['wiki_url']
WIKI_PATH = config['wiki_path'] # The script path for your wiki

wiki = mwclient.Site(WIKI_URL, path=WIKI_PATH)
wiki.login(BOT_NAME, PASSWORD)

# This is the list of cats we will edit
# If using 'Recursive' then bot will crawl down subcats
categories = ['Cat 1', 'Cat A']

##################
# OPTIONS

RECURSIVE = True           # Set to True if want to crawl down into subcats
EDIT_CAT_PAGES = True      # Set to True if you want to edit the cat pages too
SUMMARY = 'Editing pages'  # Use something useful
TRIES = 10                 # Number of times to wait for edit conflict

##################
# Function to make edits
def edit_page(page):
    
    # Keep track of attempts
    tries = 0
    
    # Do this in a while loop to retry if there's an edit conflict
    while True:
        
        tries += 1
        
        # Grab the text on the page
        text = page.edit()
        
        # Add something to the end of every page, if it's not there already
        if not '[[Category:Cat Y]]' in text:
            text += "\n[[Category:Cat Y]]"
            print 'Processed {0}'.format(page.page_title)
        else:
            action = '-- Skipped {0}'.format(page.page_title)
        
        # Save the page back to the wiki
        try:
            page.save(text,summary=SUMMARY)
            print 'Processed {0}'.format(page.page_title)

        except mwclient.EditError:
            if tries == TRIES:
                print "-- Giving up after {0} tries".format(TRIES)
            else:
                print "-- Failed to save {0}: trying again".format(page.page_title)
                time.sleep(2)
                continue

        except mwclient.HTTPRedirectError:
            print "-- Failed to save {0}: redirect error".format(page.page_title)
            
        except mwclient.ProtectedPageError:
            print "-- Failed to save {0}: page is protected".format(page.page_title)

        break

##################
# Main loop
for cat in categories:
    
    for page in wiki.Categories[cat]:
        
        if page.redirect:
            # Skip redirects
            print "-- Skipping redirect page {0}".format(page.page_title)
            continue
            
        if RECURSIVE and (page.namespace == 14):
            # If the page is a category, add it to the end of the list
            # (it's a bit dodgy changing an object we're iterating over, but it works :)
            categories.append(wiki.categories[page.page_title].page_title.encode('utf-8'))
            print "-- Added category to list: {0}".format(page.page_title)

            if not EDIT_CAT_PAGES:
                continue

        elif page.namespace != 0:
            # Skip other non-articles
            print "-- Skipping non-article {0}".format(page.page_title)
            continue

        edit_page(page)
