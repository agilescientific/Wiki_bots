# Pricebot
# Matt Hall, 2013
# Apache license v2.0
#
# This is a wiki bot for placing exchange rates and crude oil prices in a MediaWiki wiki
# You need to make pages Exchange_rate/Currencies and Crude_price/Benchmarks to pass the
# list of ticker symbols to the bot. If the pages don't exist, the bot does nothing.
# 
# See http://www.subsurfwiki.org/wiki/SubSurfWiki:Pricebot for more help and examples.
# 
# You may want to add this script to your crontab, to run every hour, say:
# 00 */1 * * * /path/to/scripts/pricebot.py
# 

# Import libraries
import urllib2
import time
from wikitools import wiki, page

from config import config

# You will need to create a bot user in your wiki
# Create a file 'setup.py'
# config = {'mywiki': {url':'http://subsurfwiki.org/',
#             'exbot':'<password>',
#             'otherbot':'<password>'},
#           'yourwiki':{url':'http://yourwiki.org/',
#             'mybot':'<password>'}
#           }

WIKI = 'subsurfwiki'
BOT_NAME = 'pricebot'
PASSWORD = config[WIKI][BOT_NAME]
WIKI_URL = config[WIKI]['url'].strip('/') + '/api.php'

# Set globals
BASE_URL = "http://query.yahooapis.com/v1/public/yql"
FORMATS = "&format=xml&diagnostics=false&env=http%3A%2F%2Fdatatables.org%2Falltables.env"
RETRY_TIME = 3.0
STOP_WORDS = ['off', 'stop', 'shutdown', 'false', 'no']
STATUS_PAGE  = 'User:Pricebot/Status'

def bot_status(site):
    # Check the bot's status page
    p = page.Page(site, STATUS_PAGE)
    status = p.getWikiText()

    for word in STOP_WORDS:
        if word in status.lower():
            print "Bot stopped by Status page"
            return 0
    return 1
	
    # Could also block the bot's user with a button on the bot's page	

def set_exchange_rates(site):
    # Prepare the list of currencies to grab
    curr_page = page.Page(site, 'Exchange_rate/Currencies').getWikiText()
    currencies = [ str(i.strip()) for i in curr_page.split('*')[1:] ]

    # Step over the currencies and write the rates back to the subpages
    for currency in currencies:

        # get the XML from Yahoo Finance
        query = "?q=select%20Rate%20from%20yahoo.finance.xchange%20where%20pair=%22USD{0}%22".format(currency)
        url = BASE_URL + query + FORMATS

        errors = 0
        while errors < 4:
            try:
                text = urllib2.urlopen(url).read()
                break
            except urllib2.HTTPError:
                errors += 1
                time.sleep(RETRY_TIME)
                pass                

        if '<Rate>' in text:
            # Extract the prices from the XML
            rate = text.split('<Rate>')[1].split('</Rate>')[0]

            target = 'Exchange_rate/{0}'.format(currency)
            p = page.Page(site, target)

            update_time = '<noinclude> &mdash; Last updated {0}</noinclude>'.format(time.ctime())
            text = rate + update_time

            r = p.edit(text=text, summary='Regular update from Yahoo Finance')
            print currency, "=", rate,

            try:
                if r['edit']['result'] == 'Success':
                    print '-- Saved'
                else:
	                print '-- Save failed'
            except Exception as e:
                print 'Save failed:', e

        else:
            # Timed out
            print currency, "failed"
            continue

    return None

def set_crude_prices(site):
    # Prepare the list of benchmarks to grab
    bench_page  = page.Page(site, 'Crude_price/Benchmarks').getWikiText()
    benchmarks = [ str(i.strip()) for i in bench_page.split('*')[1:] ]
	
    # If we want WCC or other differential, we need CL
    # And we need to remember CL to compute them
    if 'WCC' in benchmarks and 'CL' not in benchmarks:
        benchmarks.insert(0,'CL')
    CL = 0

    # We compute a time 45 days in the future for a price
    future = time.gmtime( time.time() + 45*24*60*60 ) 
    month = future.tm_mon
    month_codes = ['F','G','H','J','K','M','N','Q','U','V','X','Z']
    month = month_codes[month - 1]
    year = str(future.tm_year)[-2:]

    # Step over the benchmarks and write the prices back to the subpages
    for benchmark in benchmarks:
        
        # get the XML from Yahoo Finance
        symbol = benchmark + month + year + ".NYM"
        query = "?q=select%20LastTradePriceOnly%20from%20yahoo.finance.quotes%20where%20symbol=%22{0}%22".format(symbol)
        url = BASE_URL + query + FORMATS

        errors = 0
        while errors < 4:
            try:
                text = urllib2.urlopen(url).read()
                break
            except urllib2.HTTPError:
                errors += 1
                time.sleep(RETRY_TIME)
                pass                

        # Extract the prices from the XML
        if '<LastTradePriceOnly>' in text:
            price = text.split("<LastTradePriceOnly>")[1].split("</LastTradePriceOnly>")[0]
        
            # Capture the CL price
            if benchmark == "CL":
                CL = float(price)

            if benchmark == "WCC":
                if CL == 0:
                    # then CL failed and WCC must fail too
                    print "WCC cannot be computed because CL failed"
                    continue
                else:
                    price = str(CL + float(price))

            # Save the result back to the relevant subpage
            target = 'Crude_price/{0}'.format(benchmark)
            p = page.Page(site, target)
            update_time = '<noinclude> &mdash; Last updated {0}</noinclude>'.format(time.ctime())
            text = price + update_time
            r = p.edit(text=text, summary='Regular update from Yahoo Finance')
            print benchmark, "=", price,

            if r['edit']['result'] == 'Success':
            	print '-- Saved'
            else:
            	print '-- Save failed'
            
        else:
            # Timed out
            print benchmark, "failed"
            continue

    return None

# Now do the work!
# First, pass credentials
site = wiki.Wiki(WIKI_URL) 
# login - required for read-restricted wikis
site.login(BOT_NAME, PASSWORD)

# Then check if the bot is disabled, and act accordingly
if bot_status(site) == 1:
    set_exchange_rates(site)
    set_crude_prices(site)
