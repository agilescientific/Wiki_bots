#!/usr/bin/python
# Pricebot
# Matt Hall, 2013
# Mark A. Hershberger, 2014-2015
# Apache license v2.0
#
# This is a wiki bot for placing exchange rates and crude oil prices
# in a MediaWiki wiki. You need to make pages called
#
#     Exchange_rate/Currencies
#     Crude_price/Benchmarks
#
# to pass the list of ticker symbols to the bot. If the pages don't
# exist, the bot does nothing.
#
# See http://www.subsurfwiki.org/wiki/SubSurfWiki:Pricebot for more
# help and examples.
#
# You may want to add this script to your crontab, to run every hour, say:
# 00 */1 * * * /path/to/scripts/pricebot.py
#
# UPDATES
# Jun 2014 - switched mwclient for wikitools to cope with HTTPS - Matt
# November 2014 - Moved password to yaml file - Mark
# November 2015 - Tidied up code re: linting - Mark
#               - Added -q option
#

# Import libraries
from wikitools import page
from utils import config, setup
import urllib2
import time
import json
import argparse


def maybe_print(str):
    if not config.setting['quiet']:
        print str,


def bot_status(site):
    # Check the bot's status page
    maybe_print("Checking script permission to run...")
    try:
        p = page.Page(site, config.setting['pricebot']['status_page'])
        status = p.getWikiText()

        for word in config.setting['pricebot']['stop_words']:
            if word in status.lower():
                print "Bot stopped by Status page"
                return 0
    except page.NoPage:
        maybe_print("Status page doesn't exist... continuing\n")
    maybe_print("The script has permission to run\n")
    return 1

    # Could also block the bot's user with a button on the bot's page


def set_exchange_rates(site):
    # Prepare the list of currencies to grab
    curr_page = page.Page(site, 'Exchange_rate/Currencies').getWikiText()
    currencies = [str(i.strip()) for i in curr_page.split('*')[1:]]

    # Step over the currencies and write the rates back to the subpages
    for currency in currencies:

        # get the XML from Yahoo Finance
        query = "?q=select%20Rate%20from%20yahoo.finance.xchange%20where" + \
            "%20pair=%22USD{0}%22".format(currency)
        url = config.setting['pricebot']['base_url'] + query + \
            config.setting['pricebot']['formats']

        errors = 0
        while errors < 4:
            try:
                text = urllib2.urlopen(url).read()
                result = json.loads(text)
                break
            except urllib2.HTTPError:
                errors += 1
                time.sleep(config.setting['pricebot']['retry_time'])
                pass

        if result['query']['count'] > 0:
            # Extract the prices from the XML
            rate = result['query']['results']['rate']['Rate']

            if float(rate) > 0.0:
                target = 'Exchange_rate/{0}'.format(currency)
                p = page.Page(site, target)

                update_time = '<noinclude> &mdash; Last updated {0}  ' + \
                    '{{{{subpage}}}}</noinclude>'.format(time.ctime())
                text = rate + update_time
                r = p.edit(text=text,
                           summary='Regular update from Yahoo Finance', bot=1)
                maybe_print(currency + " = " + rate)

                if r['edit']['result'] == 'Success':
                    maybe_print("-- Saved\n")
                else:
                    print '** Save failed for ' + currency

            else:
                print currency, 'rate not retrieved, page not saved'

        else:
            # Timed out
            print currency, "timed out"
            pass

    return None


def set_crude_prices(site):
    # Prepare the list of benchmarks to grab
    bench_page = page.Page(site, 'Crude_price/Benchmarks').getWikiText()
    benchmarks = [str(i.strip()) for i in bench_page.split('*')[1:]]

    # If we want WCC or other differential, we need CL
    # And we need to remember CL to compute them
    if 'WCC' in benchmarks and 'CL' not in benchmarks:
        benchmarks.insert(0, 'CL')
    CL = 0

    # We compute a time 45 days in the future for a price
    future = time.gmtime(time.time() + 45*24*60*60)
    month = future.tm_mon
    month_codes = ['F', 'G', 'H', 'J', 'K', 'M', 'N', 'Q', 'U', 'V', 'X', 'Z']
    month = month_codes[month - 1]
    year = str(future.tm_year)[-2:]

    # Step over the benchmarks and write the prices back to the subpages
    for benchmark in benchmarks:

        # get the XML from Yahoo Finance
        symbol = benchmark + month + year + ".NYM"
        query = "?q=select%20LastTradePriceOnly%20from%20yahoo.finance.quotes" + \
            "%20where%20symbol=%22{0}%22".format(symbol)
        url = config.setting['pricebot']['base_url'] + query + \
            config.setting['pricebot']['formats']

        errors = 0
        while errors < 4:
            try:
                text = urllib2.urlopen(url).read()
                result = json.loads(text)
                break
            except urllib2.HTTPError:
                errors += 1
                time.sleep(config.setting['pricebot']['retry_time'])
                pass

        # Extract the prices from the JSON
        if result['query']['count'] > 0:
            price = result['query']['results']['quote']['LastTradePriceOnly']

            # Capture the CL price
            if benchmark == "CL":
                CL = float(price)

            if benchmark == "WCC":
                if price is None:
                    print "WCC query failed"
                    continue

                if CL == 0:
                    # then CL failed and WCC must fail too
                    print "WCC cannot be computed because CL failed"
                    continue
                else:
                    price = str(CL + float(price))

            if float(price) > 0.0:
                # Save the result back to the relevant subpage
                target = 'Crude_price/{0}'.format(benchmark)
                p = page.Page(site, target)
                update_time = '<noinclude> &mdash; Last updated ' + \
                    '{0} {{{{subpage}}}}</noinclude>'.format(time.ctime())
                text = price + update_time
                r = p.edit(text=text,
                           summary='Regular update from Yahoo Finance', bot=1)

                if r['edit']['result'] == 'Success':
                    maybe_print(benchmark + ' = ' + price + "-- Saved\n")
                else:
                    print benchmark, "=", price, '** Save failed'
            else:
                print benchmark, 'price not retrieved, page not saved'

        else:
            # Timed out
            print benchmark, "timed out"
            pass

    return None


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Pricebot -- update wiki page")
    parser.add_argument('-q', '--quiet', action='store_true',
                        default=False, help='Quiet non-error output')
    args = parser.parse_args()

    config = config(quiet=args.quiet)

    # Now do the work!
    url = config.setting['pricebot']['wiki_url']
    httpuser = config.setting['pricebot']['username']
    httppass = config.setting['pricebot']['password']

    site = setup(url, httpuser, httppass, config)

    # Then check if the bot is disabled, and act accordingly
    if bot_status(site) == 1:
        set_exchange_rates(site)
        set_crude_prices(site)
