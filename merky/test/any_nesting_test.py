from nose import tools
from . import words
from merky import tree

# Need to sort out how to do this with six compatibility layer
BASIC_JSON = words.unify('{"false":false,"negative integer":-17,"positive integer":25000,"string":"some string","true":true,"unicode":"',
                         words.SHEKELS,
                         '"}')

# The result of hashlib.sha1(BASIC_JSON.encode("utf-8")).hexdigest()
BASIC_HASH = '1fdd21a94597f8df08e75f67100e1fdcf5714a14'

BASIC = {"string": "some string",
         "true": True,
         "false": False,
         "positive integer": 25000,
         "negative integer": -17,
         "unicode": words.SHEKELS,
        }


def test_basic_dict():
    t = tree.Transformer()
    r = t.transform(BASIC)
    tools.assert_equal((BASIC_HASH, BASIC), next(r))
    tools.assert_raises(StopIteration, next, r)

