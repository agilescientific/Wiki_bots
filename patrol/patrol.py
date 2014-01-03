# -*- coding: utf-8 -*-

import mwclient
import re
import time

MAX_TRIES = 5

def tag_page(site, page):

    # Keep track of attempts
    tries = 0
    
    # Do this in a while loop to retry if there's an edit conflict
    while True:
        
        tries += 1
        
        page = site.Pages[page]
        
        # Grab the text on the page
        text = page.edit()
        
        # Add something to the end of every page, if it's not there already
        if '{{quality}}' not in text:
            text = '{{quality}}\n' + text
            print ' - Tagged {0}'.format(page.page_title)
            
            # Save the page back to the wiki
            try:
                page.save(text,"Tagged on Patrol") # Really need a username here
                print ' - Saved {0}'.format(page.page_title)

            except mwclient.EditError:
                if tries == MAX_TRIES:
                    print " * Giving up after {0} tries".format(tries)
                else:
                    print " * Failed to save {0}: trying again".format(page.page_title)
                    time.sleep(2)
                    continue

            except mwclient.HTTPRedirectError:
                print " * Failed to save {0}: redirect error".format(page.page_title)
            
            except mwclient.ProtectedPageError:
                print " * Failed to save {0}: page is protected".format(page.page_title)

        else:
            print ' * {0} is already tagged; skipped'.format(page.page_title)
            
        break

def newpages(site, categories=None, threshold=10, days=14):
    
    # Get the list of new pages' titles
    # Using a rather long list comprehension
    print "-- Getting new pages"
    new_pages = [new_page['title'] for new_page in site.recentchanges() if new_page['type'] == u'new' and new_page['ns'] == 0 and (time.gmtime()[7] - new_page['timestamp'][7]) < days]
    
    if not new_pages:
        print "** Got nothing"
        
    # Build a dict of pages with their scores on various axes
    results = {}
    for p in new_pages:
    
        print "-- Evaluating {0}".format(p)
        
        page = site.Pages[p]
    
        # Skip redirects and subpages
        if page.redirect or ('/' in p):
            continue

        if categories:
            if p not in [c.page_title for c in page.categories()]:
                print "** Skipping page not in category list,", p.encode('utf-8')
                continue

        # Length: 0 bytes scores 0, 1000 bytes or more scores 5
        try:
            results[p] = [min(int(page.length/200),5)]
            print " - Scored {0} on Length".format(results[p][-1])

        except Exception, e:
            print "** Skipping page, probably deleted,", p.encode('utf-8'), e
            continue
           
        # Categories: 1 per cat, up to max of 3
        results[p].append(min(len([c for c in page.categories()]),3))
        print " - Scored {0} on Categories".format(results[p][-1])
    
        # Images: 1 per image, up to a max of 3
        results[p].append(min(len([c for c in page.images()]),3))
        print " - Scored {0} on Images".format(results[p][-1])
    
        # Backlinks: 1 per link, up to a max of 3
        results[p].append(min(len([c for c in page.backlinks()]),3))
        print " - Scored {0} on Backlinks".format(results[p][-1])
    
        # Links: 1 per link, up to a max of 3
        results[p].append(min(len([c for c in page.links()]),3))
        print " - Scored {0} on Links".format(results[p][-1])
    
        # References: 1 per ref, up to a max of 3
        results[p].append(min(len(re.findall(r"<ref>",page.edit())),3))
        print " - Scored {0} on References".format(results[p][-1])
    
        # Title case name: 0 or 1
        # This could be much improved!
        words = filter(None,re.split(r'[ -,\.]',p))
        titlecase = sum([word.istitle() for word in words[1:]])
        total = len(words)-1.05  # Protect against div by 0
        proportion = int( 5 * titlecase / total )
        results[p].append(proportion)  # Anything above 1 could well be title case
        print " - Scored {0} on Title case".format(results[p][-1])
        
    
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
    
    print "-- Done scoring, returning to app."
    
    return worst_new_pages, possibly_titlecase, new_pages
    
