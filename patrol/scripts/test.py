#!/Users/matt/Library/Enthought/Canopy_64bit/User/bin/python

import cgi, cgitb

cgitb.enable()   # traceback handler, for debugging

fs = cgi.FieldStorage()

jquery_input = fs.getvalue('data')

print "Content-type: text/html"
print jquery_input
