import collections

from nose import tools
from . import words
import merky

BASIC_SEQ = (words.SHEKELS, words.EUROS, words.EPEES)
BASIC_SEQ_JSON = words.unify('[',
                                '"', words.SHEKELS, '",',
                                '"', words.EUROS, '",',
                                '"', words.EPEES, '"',
                             ']')
BASIC_SEQ_HASH = '8129cb64b06e72be46eec5037eafc1583586325a'

UNANNOTATED_NESTED_SEQ = (words.ANGSTROM, BASIC_SEQ, 213, -315)
UNANNOTATED_NESTED_SEQ_JSON = words.unify('[',
                                            '"', words.ANGSTROM, '",',
                                            BASIC_SEQ_JSON, ',',
                                            '213,',
                                            '-315',
                                          ']')
UNANNOTATED_NESTED_SEQ_HASH = '14fe00c4e749eb96b8c66370902ac90a4f0d52fe'

BASIC_DICT = {words.SHEKELS: words.EUROS, words.ANGSTROM: words.EPEES}
BASIC_DICT_ORDERED = collections.OrderedDict((
                        (words.ANGSTROM, words.EPEES),
                        (words.SHEKELS, words.EUROS),
                     ))
BASIC_DICT_JSON = words.unify('{',
                                '"', words.ANGSTROM, '":"', words.EPEES, '",',
                                '"', words.SHEKELS, '":"', words.EUROS, '"',
                              '}')
BASIC_DICT_HASH = 'b22023acbbc3af979ba46d986706d8da7614f722'

UNANNOTATED_NESTED_DICT = {"dict": dict(BASIC_DICT), "list": BASIC_SEQ}
UNANNOTATED_NESTED_DICT_ORDERED = collections.OrderedDict((
                                    ("dict", BASIC_DICT_ORDERED),
                                    ("list", list(BASIC_SEQ))
                                  ))
UNANNOTATED_NESTED_DICT_JSON = words.unify('{',
                                            '"dict":', BASIC_DICT_JSON, ',',
                                            '"list":', BASIC_SEQ_JSON,
                                           '}')
UNANNOTATED_NESTED_DICT_HASH = '7e5c9d9334702c025e185a9f63e380d16b85b083'


def test_simple_unannotated_list():
    # It always does the top level guy regardless of annotation.
    t = merky.AnnotationTransformer()
    r = t.transform(BASIC_SEQ)
    tools.assert_equal((BASIC_SEQ_HASH, list(BASIC_SEQ)), next(r))
    tools.assert_raises(StopIteration, next, r)


def test_nested_unannotated_list():
    # And again, it always does the top level guy.  But since no members are annotated, it
    # won't explode out anything else.
    t = merky.AnnotationTransformer()
    r = t.transform(UNANNOTATED_NESTED_SEQ)
    tools.assert_equal((UNANNOTATED_NESTED_SEQ_HASH, [words.ANGSTROM, list(BASIC_SEQ), 213, -315]), next(r))
    tools.assert_raises(StopIteration, next, r)

def test_nested_annotated_list():
    # Top level always gets done, but this time, the nested guy wil be too.
    t = merky.AnnotationTransformer()
    r = t.transform((words.ANGSTROM, merky.annotate(BASIC_SEQ), 213, -315))
    # We get the inner guy first, who is tokenized due to annotation
    tools.assert_equal((BASIC_SEQ_HASH, list(BASIC_SEQ)), next(r))
    # The outer guy is different this time, as the token replaced the nested list.
    # SHA1 of json of [words.ANGSTROM, BASIC_SEQ_HASH, 213, -315]
    tools.assert_equal(("3e2f759672d412ed84b7359e2613c94cfee250f2", [words.ANGSTROM, BASIC_SEQ_HASH, 213, -315]),
                       next(r))
    tools.assert_raises(StopIteration, next, r)

def test_simple_unannotated_dict():
    t = merky.AnnotationTransformer()
    r = t.transform(BASIC_DICT)
    tools.assert_equal((BASIC_DICT_HASH, BASIC_DICT_ORDERED), next(r))
    tools.assert_raises(StopIteration, next, r)


def test_nested_unannotated_dict():
    t = merky.AnnotationTransformer()
    r = t.transform(UNANNOTATED_NESTED_DICT)
    tools.assert_equal((UNANNOTATED_NESTED_DICT_HASH, UNANNOTATED_NESTED_DICT_ORDERED),
                       next(r))
    tools.assert_raises(StopIteration, next, r)


def test_mixed_nesting():
    t = merky.AnnotationTransformer()
    x = {"a": merky.annotate([
                    {"a": merky.annotate({"a": "A", "b": "B"}), "b": "B"},
                    {"nothing": "special"},
                ]),
         "b": [
                merky.annotate({"c": "C", "d": "D"}),
                {"e": "E", "f": "F"},
              ],
        }
    r = t.transform(x)
    # Lowest level: x["a"][0]["a"]
    tools.assert_equal(('5985f150e6c8051a45ba0082f0724ef983a56bc5',
                            collections.OrderedDict((('a', 'A'), ('b', 'B')))),
                       next(r))

    # Next up: x["a"]
    tools.assert_equal(('13b6b33de8c689ad12f99e2974a4f25ea4260aa9',
                            [
                                collections.OrderedDict((
                                    ('a', '5985f150e6c8051a45ba0082f0724ef983a56bc5'),
                                    ('b', 'B'),
                                )),
                                collections.OrderedDict((
                                    ('nothing', 'special'),
                                )),
                            ]),
                        next(r))

    # Penultimate: x["b"][0]
    tools.assert_equal(('4b78de319d1cf5639a8eb396a8cd6cdbb9fe784c',
                        collections.OrderedDict((
                            ('c', 'C'),
                            ('d', 'D'),
                        ))),
                       next(r))

    # Final, top level
    tools.assert_equal(('c6d5f854dca6a1e46d2d1c1d91aaab21bd484359',
                        collections.OrderedDict((
                            ('a', '13b6b33de8c689ad12f99e2974a4f25ea4260aa9'),
                            ('b', ['4b78de319d1cf5639a8eb396a8cd6cdbb9fe784c',
                                    collections.OrderedDict((
                                        ('e', 'E'),
                                        ('f', 'F'),
                                    )),
                                  ]),
                        ))),
                       next(r))

    tools.assert_raises(StopIteration, next, r)

