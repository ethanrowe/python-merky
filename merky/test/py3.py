# Since not all python 3 versions support the "u" prefix, we just use the
# normal literal (which is unicode)
EUROS = "\u20ac20"
ANGSTROM = "\xc5ngstr\xf6m"
EPEES = "\xe9p\xe9es"
SHEKELS = "\u20aa20"

def unify(*segments):
    return ''.join(segments)

