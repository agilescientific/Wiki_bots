# Catedit
# Edit every page in a category

import mwclient
from config import config

BOT_NAME = 'exbot'
PASSWORD = config[BOT_NAME]

WIKI_URL = config['wiki_url']
WIKI_PATH = config['wiki_path'] # The script path for your wiki

wiki = mwclient.Site(WIKI_URL, path=WIKI_PATH)
wiki.login(BOT_NAME, PASSWORD)

# This is the list of cats we will edit
categories = ['Cat 1', 'Cat A']

#cats_in_wiki = [c.page_title for c in wiki.allcategories()]

def edit_page(page):
    
    # Do this in a while loop to retry if there's an edit conflict
    while True:
                
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
            page.save(text,summary='Adding cat Z')

        except EditError:
            print "-- Failed to save {0}: trying again".format(page.page_title)
            continue

        except HTTPRedirectError:
            print "-- Failed to save {0}: redirect error".format(page.page_title)
            
        except ProtectedPageError:
            print "-- Failed to save {0}: page is protected".format(page.page_title)

        break

for cat in categories:
    
    for page in wiki.Categories[cat]:
        
        if page.redirect:
            # Skip redirects
            print "-- Skipping redirect page {0}".format(page.page_title)
            continue
            
        if page.namespace == 14:
            # If the page is a category, add it to the end of the list
            # (it's a bit dodgy changing an object we're iterating over, but it works :)
            print "-- Adding category to list: {0}".format(page.page_title)
            # Comment this out if you DO NOT want to recusively step over categories
            categories.append(wiki.categories[page.page_title].page_title.encode('utf-8'))
            # If you want to edit the category pages themselves as well,
            # COMMENT the next line
            continue

        elif page.namespace != 0:
            # Skip other non-articles
            print "-- Skipping non-article {0}".format(page.page_title)
            continue

        edit_page(page)
