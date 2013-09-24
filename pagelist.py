# -*- coding: utf-8 -*-
# Linkgrab
# Grab all the non-sub-page names from the article namespace

import mwclient
from config import config

WIKI_URL = 'wiki.seg.org'
WIKI_PATH = '/' 

site = mwclient.Site(WIKI_URL, path=WIKI_PATH)
# No need to log in to public wikis

OUTFILE = 'segwiki.out'

output = ""
count = 0

# Use site.allpages, defaults to main namespace
for page in site.allpages(namespace = 0,filterredir='nonredirects'):

    # Sometimes need to filte or act based on page contents
    #text = page.edit()
            
    # Filter  subpages    
    if '/' in page.name:
        continue
        
    # Otherwise let's count it and add to the list    
    link = 'Main:{0}\n'.format(page.name.encode('utf-8'))
    output += link
    print link[:-1]
    
for page in site.allpages(namespace = 500,filterredir='nonredirects'):

    # Sometimes need to filte or act based on page contents
    #text = page.edit()
            
    # Filter  subpages    
    if '/' in page.name:
        continue
        
    # Otherwise let's count it and add to the list    
    link = '{0}\n'.format(page.name.encode('utf-8'))
    output += link
    print link[:-1]
    
with open(OUTFILE,'w') as f:
    f.write(output)
