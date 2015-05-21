
EUROS = u"\u20ac20"
ANGSTROM = u"\xc5ngstr\xf6m"
EPEES = u"\xe9p\xe9es"
SHEKELS = u"\u20aa20"

def unify(*segments):
    return u''.join(unicode(segment) for segment in segments)

