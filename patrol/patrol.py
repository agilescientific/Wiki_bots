# -*- coding: utf-8 -*-

import mwclient
import re
import time

# Authenticate
#import config

#BOT_NAME = 'exbot'
#PASSWORD = config.config[BOT_NAME]

#WIKI_URL = config.config['wiki_url']
#WIKI_PATH = config.config['wiki_path'] # The script path for your wiki

def newpages(domain, path, categories=None, threshold=10, days=14):
    
    site = mwclient.Site(domain, path=path)
    print 'connecting to {0}'.format(domain)
    #site.login(BOT_NAME, PASSWORD)
    
    # Get the list of new pages' titles
    new_pages = [new_page['title'] for new_page in site.recentchanges() if new_page['type'] == u'new' and new_page['ns'] == 0  and (time.gmtime()[7] - new_page['timestamp'][7]) < days]
    
    
    
    # Build a dict of pages with their scores on various axes
    results = {}
    for p in new_pages:
        page = site.Pages[p]
    
        # Skip redirects and subpages
        if page.redirect or ('/' in p):
            continue
    
        # Length: 0 bytes scores 0, 1000 bytes or more scores 5
        try:
            results[p] = [min(int(page.length/200),5)]
        except Exception, e:
            print "Skipping page, probably deleted, ", p, e
            continue
           
        # Categories: 1 per cat, up to max of 3
        results[p].append(min(len([c for c in page.categories()]),3))
    
        # Images: 1 per image, up to a max of 3
        results[p].append(min(len([c for c in page.images()]),3))
    
        # Backlinks: 1 per link, up to a max of 3
        results[p].append(min(len([c for c in page.backlinks()]),3))
    
        # Links: 1 per link, up to a max of 3
        results[p].append(min(len([c for c in page.links()]),3))
    
        # References: 1 per ref, up to a max of 3
        results[p].append(min(len(re.findall(r"<ref>",page.edit())),3))
    
        # Title case name: 0 or 1
        # This could be much improved!
        words = filter(None,re.split(r'[ -,\.]',p))
        titlecase = sum([word.istitle() for word in words[1:]])
        total = len(words)-1.05  # Protect against div by 0
        proportion = int( 5 * titlecase / total )
        results[p].append(proportion)  # Anything above 1 could well be title case
    
    # Parse the results and generate lists of pages needing attention
    good, bad = {}, {}
    new_pages = {}
    
    best_score = 0
    
    for p in results:
        score = sum(results[p])
        
        new_pages[p] = [score]
        
        if results[p][6] >= 2:
            new_pages[p].append(True)
        else:
            new_pages[p].append(False)
        
        if score >= threshold:
            good[p] = results[p]
            if score > best_score:
                # best = p
                best_score = score
        else:
            bad[p] = results[p]
    
    # Generate list of pages flagged as possibly named with title case 
    possibly_titlecase = [p for p in results if results[p][6]>=2]

    # Generate ordered list of worst pages, scoring under 10
    worst_new_pages = sorted(bad, key=lambda p : sum(bad[p]))
    
    return worst_new_pages, possibly_titlecase, new_pages
    
