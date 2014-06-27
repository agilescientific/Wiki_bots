# -*- coding: utf-8 -*-
# Just some helpful modules

import re
import pickle
#from geography import states, prov_terr, countries

# Wiki sites
SITES = {
    'petrowiki':  {'url':'petrowiki.spe.org', 'path':'/', 'text':'PetroWiki', 'code':'pw:'},
    'segwiki':    {'url':'wiki.seg.org', 'path':'/', 'text':'SEGWiki', 'code':'seg:'},
    'segdict':    {'url':'wiki.seg.org', 'path':'/', 'text':"Sheriff's Encyclopedic Dictionary", 'code':'seg:Dictionary:'},
    'aapgwiki':   {'url':'wiki.aapg.org', 'path':'/', 'text':'AAPG Wiki', 'code':''},
    'subsurfwiki':{'url':'subsurfwiki.org', 'path':'/mediawiki/', 'text':'SubSurfWiki', 'code':'ssw:'}
    }

# SENTENCE
# This converts to sentence case
# Except anything in parentheses, which it leaves alone
# TO ADD... And anything that looks like a reference
def sentence(string, ignore=[], mid=True):
    '''
    Convert to sentence case, with an initial capital letter, caps for proper
    nouns, and the rest lowercase... except single words in caps, dotted
    abbreviations, CamelCase words, and anything else explicitly excepted. 
    
    '''    
    result = ''
    
    words = filter(None,re.split(r'[-–— ,\.]',string))
    words = [word.strip(',').strip('.') for word in words]
    
    # Allow some exceptions, starting with any passed in as 'ignore' arg
    # NB We also allow all uppercase-only words, see all-caps heuristic
    DO_NOT_CONVERT = ignore + ['SEM', 'CL', 'AVO', 'XF', 'XRF', 'XRD', 'AAPG', 'SPE', 'Carlo', 'Ekofisk', 'Pickett', 'Sorrento']
    
    
    # Use words from the Moby project
    # https://en.wikipedia.org/wiki/Moby_Project
    # This needs optimiztion
    with open('names.pkl','rb') as n:
        names = pickle.load(n)
    
    names_set = set(names)
    word_set = set(words)
    DO_NOT_CONVERT += names_set.intersection(word_set)
        
    #for key, value in states.iteritems():
    #    DO_NOT_CONVERT.append(value)
    #    
    #for key, value in prov_terr.iteritems():
    #    DO_NOT_CONVERT.append(value)
    #    
    #for key, value in countries.iteritems():
    #    DO_NOT_CONVERT.append(value)
    #    
    # Apply all-caps heuristic for words not in DO_NOT_CONVERT list
    # If the string is not pure upper case, 
    if not string.isupper():
        # Then add uppercase words to our DO_NOT_CONVERT list
        DO_NOT_CONVERT += [word for word in words if word.isupper()]

    # Catch the  CamelCase words like iPad and PowerPoint (just looks
    # for cap in middle of word)
    DO_NOT_CONVERT += [word for word in words if (len(word)>1 and not word[1:].islower() and not word.isupper())]

    # Heuristic to decide if string is already in sentence case
    number_of_legit_cap_words = len([word for word in words if word in DO_NOT_CONVERT])
    number_of_init_cap_words = sum([word[0].isupper() for word in words])
    number_of_capitalized_words = number_of_init_cap_words - number_of_legit_cap_words
    if words[0].istitle(): number_of_capitalized_words -= 1
    number_of_words = len(words)
    
    # If the string is not pure title case, 
    if not string.istitle():
        # Then decide if it's probably title case with lc 'and', 'in', 'of', etc
        if number_of_capitalized_words >= 1:
            # It's mostly title case, so let's convert it
            pass # on to rest of function
        else:
            # The string is probably sentence case already, leave it alone
            return string

    # Make a note of leading and trailing spaces to replace later
    if string[-1] == ' ':
        end_space = True
    else:
        end_space = False
    
    # Same for periods    
    if string.strip()[-1] == '.':
        end_point = True
    else:
        end_point = False
    
    # Could probably do with re to not split contents of parens
    # e.g. to avoid (Smith, unpubl. Data, 1988) for example
    # but not worth effort required, due to garbled punctuation.
    sentences = string.split('.')
    
    for sentence in sentences:
        inparens = False
        partial = ''
        
        for c in sentence.strip():
            if re.match(r"[\(\)]",c):
                partial += c
                inparens = not inparens
                continue
            if not inparens:
                partial += c.lower()
            else:
                # Leave everything in parens alone
                partial += c
        
        if partial:
            result += partial[0].upper() + partial[1:] + '. '
    
    result = result.strip(' .')
    
    # Fix everything we said we'd leave alone
    for word in DO_NOT_CONVERT:
        word = word.strip('()')
        result = re.sub(r'\b([{0}{1}]{2})\b'.format(word[0],word.lower()[0],word.lower()[1:]), word, result)

    # Re-capitalize initials
    def initial_callback(init_item):
        return init_item.group(1).upper()
    result = re.sub(r'( [a-z]\. )',initial_callback,result)
    
    # Cap the first letter if we're not explcitly in mid-sentence case
    if mid == "False":
        result = result[0].upper() + result[1:]
    
    # Make sure we give back what we got    
    if end_point:
        result = result + '.'
    if end_space:
        result = result + ' '
    
    return result

# SLUG
# This creates a slug: a lowercase string with no spaces or non-alpha characters
# Useful for creating URLs and probably-unique keys, etc.
def slug(string):
    slug = ""
    for c in string:
        if re.match("[-a-zA-Z0-9_]",c):
            slug += c.lower()
        if c == " ":
            # Don't do else, because we don't want to
            # admit other unmatched characters
            slug += "-"
    return slug

# LEVENSHTEIN
# We can check how similar strings are and maybe deal with misspellings,
# but it will be slow. And the best we can probably do is match the first
# random match we come across
def levenshtein(s,t):
    def matrix(a,b):
        out = []
        for i in range(0,a):
            out.append([])
            for j in range(0,b):
                out[i].append(0)
        return out
    
    # Make a matrix for all string comparisons
    a, b = len(s)+1, len(t)+1
    m = matrix(a,b)
    
    # Populate the null string comparisons
    for i in range(0,a):
        m[i][0] = i
    for j in range(1,b):
        m[0][j] = j
        
    for j in range(1,b):
        for i in range(1,a):
            if s[i-1] == t[j-1]:
                m[i][j] = m[i-1][j-1]
            else:
                dln = m[i-1][j] + 1
                ins = m[i][j-1] + 1
                sub = m[i-1][j-1] + 1
                m[i][j] = min(dln, ins, sub)
        
    # We have the whole matrix but only need the final distance
    return m[a-1][b-1]
    
hexchars = {
'&#x02003;': '', # Weird quad spaces in tables
'&#x2003;': '',  # Weird quad spaces in tables
'&#x0020;': ' ',
'&#x007C;': '|',
'&#x005B;': '[',
'&#x005D;': ']',
'&#x00C1;': '&Aacute;',
'&#x00E1;': '&aacute;',
'&#x00C2;': '&Acirc;',
'&#x00E2;': '&acirc;',
'&#x00B4;': '&acute;',
'&#x00C6;': '&AElig;',
'&#x00E6;': '&aelig;',
'&#x00C0;': '&Agrave;',
'&#x00E0;': '&agrave;',
'&#x2135;': '&alefsym;',
'&#x0391;': '&Alpha;',
'&#x03B1;': '&alpha;',
'&#x0026;': '&amp;',
'&#x2227;': '&and;',
'&#x2220;': '&ang;',
'&#x00C5;': '&Aring;',
'&#x00E5;': '&aring;',
'&#x2248;': '&asymp;',
'&#x00C3;': '&Atilde;',
'&#x00E3;': '&atilde;',
'&#x00C4;': '&Auml;',
'&#x00E4;': '&auml;',
'&#x201E;': '&bdquo;',
'&#x0392;': '&Beta;',
'&#x03B2;': '&beta;',
'&#x00A6;': '&brvbar;',
'&#x2022;': '&bull;',
'&#x2229;': '&cap;',
'&#x00C7;': '&Ccedil;',
'&#x00E7;': '&ccedil;',
'&#x00B8;': '&cedil;',
'&#x00A2;': '&cent;',
'&#x03A7;': '&Chi;',
'&#x03C7;': '&chi;',
'&#x02C6;': '&circ;',
'&#x2663;': '&clubs;',
'&#x2245;': '&cong;',
'&#x00A9;': '&copy;',
'&#x21B5;': '&crarr;',
'&#x222A;': '&cup;',
'&#x00A4;': '&curren;',
'&#x2021;': '&Dagger;',
'&#x2020;': '&dagger;',
'&#x21D3;': '&dArr;',
'&#x2193;': '&darr;',
'&#x00B0;': '&deg;',
'&#x0394;': '&Delta;',
'&#x03B4;': '&delta;',
'&#x2666;': '&diams;',
'&#x00F7;': '&divide;',
'&#x00C9;': '&Eacute;',
'&#x00E9;': '&eacute;',
'&#x00CA;': '&Ecirc;',
'&#x00EA;': '&ecirc;',
'&#x00C8;': '&Egrave;',
'&#x00E8;': '&egrave;',
'&#x2205;': '&empty;',
'&#x2003;': '&emsp;',
'&#x2002;': '&ensp;',
'&#x0395;': '&Epsilon;',
'&#x03B5;': '&epsilon;',
'&#x2261;': '&equiv;',
'&#x0397;': '&Eta;',
'&#x03B7;': '&eta;',
'&#x00D0;': '&ETH;',
'&#x00F0;': '&eth;',
'&#x00CB;': '&Euml;',
'&#x00EB;': '&euml;',
'&#x20AC;': '&euro;',
'&#x2203;': '&exist;',
'&#x0192;': '&fnof;',
'&#x2200;': '&forall;',
'&#x00BD;': '&frac12;',
'&#x00BC;': '&frac14;',
'&#x00BE;': '&frac34;',
'&#x2044;': '&frasl;',
'&#x0393;': '&Gamma;',
'&#x03B3;': '&gamma;',
'&#x2265;': '&ge;',
'&#x003E;': '&gt;',
'&#x21D4;': '&hArr;',
'&#x2194;': '&harr;',
'&#x2665;': '&hearts;',
'&#x2026;': '&hellip;',
'&#x00CD;': '&Iacute;',
'&#x00ED;': '&iacute;',
'&#x00CE;': '&Icirc;',
'&#x00EE;': '&icirc;',
'&#x00A1;': '&iexcl;',
'&#x00CC;': '&Igrave;',
'&#x00EC;': '&igrave;',
'&#x2111;': '&image;',
'&#x221E;': '&infin;',
'&#x222B;': '&int;',
'&#x0399;': '&Iota;',
'&#x03B9;': '&iota;',
'&#x00BF;': '&iquest;',
'&#x2208;': '&isin;',
'&#x00CF;': '&Iuml;',
'&#x00EF;': '&iuml;',
'&#x039A;': '&Kappa;',
'&#x03BA;': '&kappa;',
'&#x039B;': '&Lambda;',
'&#x03BB;': '&lambda;',
'&#x2329;': '&lang;',
'&#x00AB;': '&laquo;',
'&#x21D0;': '&lArr;',
'&#x2190;': '&larr;',
'&#x2308;': '&lceil;',
'&#x201C;': '&ldquo;',
'&#x2264;': '&le;',
'&#x230A;': '&lfloor;',
'&#x2217;': '&lowast;',
'&#x25CA;': '&loz;',
'&#x25A1;': '',
'&#x200E;': '&lrm;',
'&#x2039;': '&lsaquo;',
'&#x2018;': '&lsquo;',
'&#x003C;': '&lt;',
'&#x00AF;': '&macr;',
'&#x2014;': '&mdash;',
'&#x00B5;': '&micro;',
'&#x00B7;': '&middot;',
'&#x2212;': '&minus;',
'&#x039C;': '&Mu;',
'&#x03BC;': '&mu;',
'&#x2207;': '&nabla;',
'&#x00A0;': '&nbsp;',
'&#x2013;': '&ndash;',
'&#x2260;': '&ne;',
'&#x220B;': '&ni;',
'&#x00AC;': '&not;',
'&#x2209;': '&notin;',
'&#x2284;': '&nsub;',
'&#x00D1;': '&Ntilde;',
'&#x00F1;': '&ntilde;',
'&#x039D;': '&Nu;',
'&#x03BD;': '&nu;',
'&#x00D3;': '&Oacute;',
'&#x00F3;': '&oacute;',
'&#x00D4;': '&Ocirc;',
'&#x00F4;': '&ocirc;',
'&#x0152;': '&OElig;',
'&#x0153;': '&oelig;',
'&#x00D2;': '&Ograve;',
'&#x00F2;': '&ograve;',
'&#x203E;': '&oline;',
'&#x03A9;': '&Omega;',
'&#x03C9;': '&omega;',
'&#x039F;': '&Omicron;',
'&#x03BF;': '&omicron;',
'&#x2295;': '&oplus;',
'&#x2228;': '&or;',
'&#x00AA;': '&ordf;',
'&#x00BA;': '&ordm;',
'&#x00D8;': '&Oslash;',
'&#x00F8;': '&oslash;',
'&#x00D5;': '&Otilde;',
'&#x00F5;': '&otilde;',
'&#x2297;': '&otimes;',
'&#x00D6;': '&Ouml;',
'&#x00F6;': '&ouml;',
'&#x00B6;': '&para;',
'&#x2202;': '&part;',
'&#x2030;': '&permil;',
'&#x22A5;': '&perp;',
'&#x03A6;': '&Phi;',
'&#x03C6;': '&phi;',
'&#x03A0;': '&Pi;',
'&#x03C0;': '&pi;',
'&#x03D6;': '&piv;',
'&#x03D5;': '&phi;',
'&#x00B1;': '&plusmn;',
'&#x00A3;': '&pound;',
'&#x2033;': '&Prime;',
'&#x2032;': '&prime;',
'&#x220F;': '&prod;',
'&#x221D;': '&prop;',
'&#x03A8;': '&Psi;',
'&#x03C8;': '&psi;',
'&#x0022;': '&quot;',
'&#x221A;': '&radic;',
'&#x232A;': '&rang;',
'&#x00BB;': '&raquo;',
'&#x21D2;': '&rArr;',
'&#x2192;': '&rarr;',
'&#x2309;': '&rceil;',
'&#x201D;': '&rdquo;',
'&#x211C;': '&real;',
'&#x00AE;': '&reg;',
'&#x230B;': '&rfloor;',
'&#x03A1;': '&Rho;',
'&#x03C1;': '&rho;',
'&#x200F;': '&rlm;',
'&#x203A;': '&rsaquo;',
'&#x2019;': "'",
'&#x201A;': '&sbquo;',
'&#x0160;': '&Scaron;',
'&#x0161;': '&scaron;',
'&#x22C5;': '&sdot;',
'&#x00A7;': '&sect;',
'&#x00AD;': '&shy;',
'&#x03A3;': '&Sigma;',
'&#x03C3;': '&sigma;',
'&#x03C2;': '&sigmaf;',
'&#x223C;': '&sim;',
'&#x2660;': '&spades;',
'&#x2282;': '&sub;',
'&#x2286;': '&sube;',
'&#x2211;': '&sum;',
'&#x2283;': '&sup;',
'&#x00B9;': '&sup1;',
'&#x00B2;': '&sup2;',
'&#x00B3;': '&sup3;',
'&#x2287;': '&supe;',
'&#x00DF;': '&szlig;',
'&#x03A4;': '&Tau;',
'&#x03C4;': '&tau;',
'&#x2234;': '&there4;',
'&#x0398;': '&Theta;',
'&#x03B8;': '&theta;',
'&#x03D1;': '&thetasym;',
'&#x2009;': '&thinsp;',
'&#x00DE;': '&THORN;',
'&#x00FE;': '&thorn;',
'&#x02DC;': '&tilde;',
'&#x00D7;': '&times;',
'&#x2122;': '&trade;',
'&#x00DA;': '&Uacute;',
'&#x00FA;': '&uacute;',
'&#x21D1;': '&uArr;',
'&#x2191;': '&uarr;',
'&#x00DB;': '&Ucirc;',
'&#x00FB;': '&ucirc;',
'&#x00D9;': '&Ugrave;',
'&#x00F9;': '&ugrave;',
'&#x00A8;': '&uml;',
'&#x03D2;': '&upsih;',
'&#x03A5;': '&Upsilon;',
'&#x03C5;': '&upsilon;',
'&#x00DC;': '&Uuml;',
'&#x00FC;': '&uuml;',
'&#x2118;': '&weierp;',
'&#x039E;': '&Xi;',
'&#x03BE;': '&xi;',
'&#x00DD;': '&Yacute;',
'&#x00FD;': '&yacute;',
'&#x00A5;': '&yen;',
'&#x0178;': '&Yuml;',
'&#x00FF;': '&yuml;',
'&#x0396;': '&Zeta;',
'&#x03B6;': '&zeta;',
'&#x200D;': '&zwj;',
'&#x200C;': '&zwnj;'
}
