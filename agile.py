# Just some helpful modules

import re
from geography import states, prov_terr, countries

# SENTENCE
# This converts to sentence case
# Except anything in parentheses, which it leaves alone
# TO ADD... And anything that looks like a reference
def sentence(string):
    
    # Allow some exceptions
    # NB We also allow all uppercase-only words, see all-caps heuristic
    DO_NOT_CONVERT = ['SEM', 'CL', 'AVO', 'XF', 'XRF', 'XRD', 'AAPG', 'SPE', 'Campos']
    
    for key, value in states.iteritems():
        DO_NOT_CONVERT.append(value)
        
    for key, value in prov_terr.iteritems():
        DO_NOT_CONVERT.append(value)
        
    for key, value in countries.iteritems():
        DO_NOT_CONVERT.append(value)
        
    result = ""
    
    words = filter(None,re.split(r'[ -,\.]',string))
    words = [word.strip(',').strip('.') for word in words]
    
    number_of_acronyms = len([word for word in words if word in DO_NOT_CONVERT])
    number_of_uppercase_words = sum([word[0].isupper() for word in words])
    number_of_capitalized_words = number_of_uppercase_words - number_of_acronyms
    number_of_words = len(words)
    
    # Apply sentence case heuristic
    # If the string is not pure title case, 
    if not string.istitle():
        # Then decide if it's probably title case with lc 'and', 'in', 'of', etc
        if number_of_capitalized_words >= number_of_words/2.0:
            # It's mostly title case, so let's convert it
            pass # on to rest of function
        else:
            # The string is probably sentence case already, leave it alone
            return string
    
    # Apply all-caps heuristic for words not in DO_NOT_CONVERT list
    # If the string is not pure upper case, 
    if not string.isupper():
        # Then add uppercase words to our DO_NOT_CONVERT list
        DO_NOT_CONVERT += [word for word in words if word.isupper()]
        
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
        partial = ""
        
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
    
    # Re-capitalize acronyms
    for word in DO_NOT_CONVERT:
        # result = re.sub(r'\b({0})\b'.format(word.title()),word,result)
        # result = re.sub(r'\b({0})\b'.format(word.lower()),word,result)
        result = re.sub(r'\b([{0}{1}]{2})\b'.format(word[0],word.lower()[0],word.lower()[1:]),word,result)

    # Re-capitalize initials
    def initial_callback(init_item):
        return init_item.group(1).upper()
    result = re.sub(r'( [a-z]\. )',initial_callback,result)

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
        if re.match("[a-zA-Z0-9_]",c):
            slug += c.lower()
        if c == " ":
            # Don't do else, because we don't want to admit other unmatched characters
            slug += "-"
    return slug

# LEVENSHTEIN
# We can check how similar strings are and maybe deal with misspellings, but it will be slow
# And the best we can probably do is match the first random match we come across
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
