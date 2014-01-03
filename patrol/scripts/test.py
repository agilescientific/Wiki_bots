#!/Users/matt/Library/Enthought/Canopy_64bit/User/bin/python

import cgi, cgitb

def main():

    cgitb.enable()   # traceback handler, for debugging

    fs = cgi.FieldStorage()

    jquery_input = fs.getvalue('input')

    print jquery_input
    
    do_it(jquery_input)
    
    out = open('tmp.txt','w')
    out.write(jquery_input)
    out.close()

    return
        
def do_it(whatever):
    
    print "Content-Type: text/html\n" 
    print "do_it() ran!\n"
    print whatever
    
    return

if __name__ == "__main__":
    main()