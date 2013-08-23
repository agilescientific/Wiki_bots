# -*- coding: utf-8 -*-
# Linknet

import mwclient
from config import config

# You will need to create a bot user in your wiki
# Create a file 'setup.py'
# config = {'wiki_url':'subsurfwiki.org',
#           'wiki_path':'/mediawiki/',
#           'exbot':'<password>',
#           'otherbot':'<password>'}

BOT_NAME = 'exbot'
PASSWORD = config[BOT_NAME]

WIKI_URL = config['wiki_url']
WIKI_PATH = config['wiki_path'] # The script path for your wiki

site = mwclient.Site(WIKI_URL, path=WIKI_PATH)
site.login(BOT_NAME, PASSWORD)

OUTFILE = WIKI_URL + '.dl'

FILE_HEADER = """DL n=500
format = edgelist1
labels embedded:
data:
"""

def slug(string):
    slug = ""
    for c in string:
        if re.match("[-a-zA-Z0-9éè]",c):
            slug += c.lower()
        if c == " ":
            slug += "_"
    return slug

##### GET ON WITH IT #####
with open(OUTFILE,'w') as f:
    f.write(FILE_HEADER)

# Use site.allpages, defaults to main namespace
for page in site.allpages(namespace=0,minsize=10,filterredir='nonredirects'):

    # Sometimes need to filte or act based on page contents
    #text = page.edit()
    
    # Filter subpages
    if "/" in page.name:
        continue
        
    count = 0
    file_segment = ""
        
    for link in page.links():
        
        # Filter non-articles
        if link.namespace != 0:
            continue
        
        # Filter  subpages    
        if '/' in link.name:
            continue
        
        # Otherwise let's count it and add to the list    
        count += 1
        file_segment += '{0} {1}\n'.format(slug(page.name.encode('utf-8')),slug(link.name.encode('utf-8')))
        
    if count > 0:
        # Not sure why I get the extra newline character
        print file_segment[:-1]

        with open(OUTFILE,'a') as f:
            f.write(file_segment)
