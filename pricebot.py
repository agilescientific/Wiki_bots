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
import mwclient
import urllib2
import time

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

# Set globals
BASE_URL = "http://query.yahooapis.com/v1/public/yql"
FORMATS = "&format=xml&diagnostics=false&env=http%3A%2F%2Fdatatables.org%2Falltables.env"
RETRY_TIME = 3.0
STOP_WORDS = ['off', 'stop', 'shutdown']
STATUS_PAGE  = 'User:Pricebot/Status'

# You will need to create a user for Pricebot in your wiki
USERNAME = 'Pricebot'
PASSWORD = passwords.pricebot

# You will need to change these too
WIKI_URL = 'subsurfwiki.org'
WIKI_PATH = '/mediawiki/' # The script path for your wiki

def bot_status(site):
    # Check the bot's status page
    for word in STOP_WORDS:
        if word in site.Pages[STATUS_PAGE].edit().lower():
            print "Bot stopped by Status page"
            return 0
    return 1
	
    # Could also block the bot's user with a button on the bot's page	

def set_exchange_rates(site):
    # Prepare the list of currencies to grab
    curr_page  = site.Pages['Exchange_rate/Currencies'].edit()
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

            # Save the result back to the relevant subpage
            page = site.Pages[ 'Exchange_rate/'+currency ]
            update_time = '<noinclude> &mdash; Last updated {0}</noinclude>'.format(time.ctime())
            page.save(rate+update_time,summary='Regular update from Yahoo Finance')
            print currency, "=", rate

        else:
            # Timed out
            print currency, "failed"
            continue

    return None

def set_crude_prices(site):
    # Prepare the list of benchmarks to grab
    bench_page  = site.Pages['Crude_price/Benchmarks'].edit()
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
            page = site.Pages['Crude_price/'+benchmark ]
            update_time = '<noinclude> &mdash; Last updated {0}</noinclude>'.format(time.ctime())
            page.save(price+update_time,summary='Regular update from Yahoo Finance')
            print benchmark, "=", price
            
        else:
            # Timed out
            print benchmark, "failed"
            continue

    return None

# Now do the work!
# First, pass credentials
wiki = mwclient.Site(WIKI_URL, path=WIKI_PATH)
wiki.login(BOT_NAME, PASSWORD)

# Then check if the bot is disabled, and act accordingly
if bot_status(wiki) == 1:
    set_exchange_rates(wiki)
    set_crude_prices(wiki)
