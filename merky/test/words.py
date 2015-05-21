import codecs
import pkg_resources
import six

if six.PY2:
    from .py2 import *
else:
    from .py3 import *

