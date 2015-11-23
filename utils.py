# Various utilities for bots
# Matt Hall, Mark Hershberger
# Summer, Fall 2014
# Further changes in Fall 2015

# Import the config with the wiki settings
import yaml
import sys
import os


def config(conffile=None, quiet=False):
    if not hasattr(config, "conffile") or getattr(config, "conffile") is None:
        if conffile is None:
            setattr(config, "conffile", 'config.yaml')
        else:
            setattr(config, "conffile", conffile)

        if not os.path.isfile(config.conffile):
            print "Configuration file not found: %s" % config.conffile
            sys.exit(1)
        if not quiet:
            print "Reading config file: %s\n" % config.conffile
        setattr(config, "setting", yaml.load(open(config.conffile)))
        try:
            config.setting['quiet']
        except:
            config.setting['quiet'] = quiet

    return config

# Import the wiki processing stuff
from wikitools import wiki


def setup(wiki_url, httpuser, httppass, config):

    if not config.setting['quiet']:
        print "Authenticating at", wiki_url
    site = wiki.Wiki(url=wiki_url,
                     httpuser=httpuser,
                     httppass=httppass,
                     preauth=True)

    if site:
        if not config.setting['quiet']:
            print "Successfully logged in!"
    else:
        print "Failed to log in."
        sys.exit(1)

    return site
