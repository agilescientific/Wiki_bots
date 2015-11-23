# Various utilities for bots
# Matt Hall, Mark Hershberger
# Summer, Fall 2014

# Import the config with the wiki settings
import yaml
import sys
import os


def config(conffile=None):
    if not hasattr(config, "conffile") or getattr(config, "conffile") is None:
        if conffile is None:
            setattr(config, "conffile", 'config.yaml')
        else:
            setattr(config, "conffile", conffile)

        if not os.path.isfile(config.conffile):
            print "Configuration file not found: %s" % config.conffile
            sys.exit(1)
        print "Reading config file: %s\n" % config.conffile
        setattr(config, "setting", yaml.load(open(config.conffile)))

    return config

# Import the wiki processing stuff
from wikitools import wiki


def setup(wiki_url, httpuser, httppass):

    print "Authenticating at", wiki_url
    site = wiki.Wiki(url=wiki_url,
                     httpuser=httpuser,
                     httppass=httppass,
                     preauth=True)

    if site:
        print "Successfully logged in!"
    else:
        print "Failed to log in."

    return site
