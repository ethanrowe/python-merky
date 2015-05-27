import collections

from nose import tools
from . import words
import merky

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

BASIC_ORDERED = collections.OrderedDict((
                    ('false', False),
                    ('negative integer', -17),
                    ('positive integer', 25000),
                    ('string', 'some string'),
                    ('true', True),
                    ('unicode', words.SHEKELS),
                ))

NESTING_DICT = {
        "another string": "more strings!",
        "honesty": True,
        "lies": False,
        "a": dict(BASIC),
        "c": dict(BASIC),
       }

NESTING_DICT_ORDERED = collections.OrderedDict((
                            ('a', BASIC_HASH),
                            ('another string', 'more strings!'),
                            ('c', BASIC_HASH),
                            ('honesty', True),
                            ('lies', False),
                       ))

NESTING_DICT_JSON = words.unify('{',
                                  '"a":"', BASIC_HASH, '",',
                                  '"another string":"more strings!"', ',',
                                  '"c":"', BASIC_HASH, '",'
                                  '"honesty":true,',
                                  '"lies":false',
                                '}')

# hashlib.sha1(NESTING_DICT_JSON.encode("utf-8")).hexdigest()
NESTING_DICT_HASH = '593a122791ea25479cc6b2c16d69a5fb81241edb'

LIST = ["blah", words.ANGSTROM, words.EUROS]
LIST_JSON = words.unify('["blah",',
                        '"', words.ANGSTROM, '",',
                        '"', words.EUROS, '"',
                        ']')
LIST_HASH = '447f4779bf4a9865c600da63256eab9c827e48b0'

NESTING_LIST = ["something",
                dict(BASIC),
                list(LIST),
                words.EPEES]

NESTING_LIST_JSON = words.unify('[',
                                '"something",'
                                '"', BASIC_HASH, '",',
                                '"', LIST_HASH, '",',
                                '"', words.EPEES, '"',
                                ']')

NESTING_LIST_HASH = 'd724e888872c0a0545b13c0f16980953df360bf9'

def test_string():
    t = merky.Transformer()
    r = t.transform("what?")
    tools.assert_equal(("74417e40273f06624262871962bd9e738162da47", "what?"), next(r))
    tools.assert_raises(StopIteration, next, r)

def test_integer():
    t = merky.Transformer()
    r = t.transform(54321)
    tools.assert_equal(("348162101fc6f7e624681b7400b085eeac6df7bd", 54321), next(r))
    tools.assert_raises(StopIteration, next, r)

def test_basic_dict():
    t = merky.Transformer()
    r = t.transform(BASIC)
    tools.assert_equal((BASIC_HASH, BASIC_ORDERED), next(r))
    tools.assert_raises(StopIteration, next, r)

def test_nesting_dict():
    t = merky.Transformer()
    r = t.transform(NESTING_DICT)
    # We know the order because its depth-first traversal.
    # We also expect the hash to be the same for each copy of BASIC.

    # For the "a" member.
    tools.assert_equal((BASIC_HASH, BASIC_ORDERED), next(r))
    # For the "c" member.
    tools.assert_equal((BASIC_HASH, BASIC_ORDERED), next(r))
    # For the top container.  Note substituion of hashes.
    tools.assert_equal((NESTING_DICT_HASH, dict(NESTING_DICT, a=BASIC_HASH, c=BASIC_HASH)), next(r))
    tools.assert_raises(StopIteration, next, r)

def test_basic_list():
    t = merky.Transformer()
    r = t.transform(LIST)
    tools.assert_equal((LIST_HASH, LIST), next(r))
    tools.assert_raises(StopIteration, next, r)

def test_nesting_list():
    t = merky.Transformer()
    r = t.transform(NESTING_LIST)

    tools.assert_equal((BASIC_HASH, BASIC_ORDERED), next(r))
    tools.assert_equal((LIST_HASH, LIST), next(r))
    tools.assert_equal((NESTING_LIST_HASH, ["something", BASIC_HASH, LIST_HASH, words.EPEES]), next(r))
    tools.assert_raises(StopIteration, next, r)

