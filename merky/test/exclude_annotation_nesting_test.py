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
UNANNOTATED_NESTED_DICT_HASH = '616bcc08fa64f4e8ed9cd7395c8981cdff045baf'
UNANNOTATED_NESTED_DICT_TOKENIZED = collections.OrderedDict((
                                      ("dict", BASIC_DICT_HASH),
                                      ("list", BASIC_SEQ_HASH)
                                     ))




def test_simple_unannotated_list():
    # It always does the top level guy regardless of annotation.
    t = merky.ExcludeAnnotationTransformer()
    r = t.transform(BASIC_SEQ)
    tools.assert_equal((BASIC_SEQ_HASH, list(BASIC_SEQ)), next(r))
    tools.assert_raises(StopIteration, next, r)


def test_nested_unannotated_list():
    # Top level always gets done, but this time, the nested guy wil be too.
    t = merky.ExcludeAnnotationTransformer()
    r = t.transform(UNANNOTATED_NESTED_SEQ)
    # We get the inner guy first, who is tokenized due to annotation
    tools.assert_equal((BASIC_SEQ_HASH, list(BASIC_SEQ)), next(r))
    # The outer guy is different this time, as the token replaced the nested list.
    # SHA1 of json of [words.ANGSTROM, BASIC_SEQ_HASH, 213, -315]
    tools.assert_equal(("3e2f759672d412ed84b7359e2613c94cfee250f2", [words.ANGSTROM, BASIC_SEQ_HASH, 213, -315]),
                       next(r))
    tools.assert_raises(StopIteration, next, r)


def test_nested_annotated_list():
    # And again, it always does the top level guy.  But since no members are annotated, it
    # will explode out anything else.
    t = merky.ExcludeAnnotationTransformer()
    r = t.transform((words.ANGSTROM, merky.annotate(BASIC_SEQ), 213, -315))
    tools.assert_equal((UNANNOTATED_NESTED_SEQ_HASH, [words.ANGSTROM, list(BASIC_SEQ), 213, -315]), next(r))
    tools.assert_raises(StopIteration, next, r)


def test_simple_unannotated_dict():
    t = merky.ExcludeAnnotationTransformer()
    r = t.transform(BASIC_DICT)
    tools.assert_equal((BASIC_DICT_HASH, BASIC_DICT_ORDERED), next(r))
    tools.assert_raises(StopIteration, next, r)


def test_nested_unannotated_dict():
    t = merky.ExcludeAnnotationTransformer()
    r = t.transform(UNANNOTATED_NESTED_DICT)
    # We get the inner dict first, who is tokenized due to lack of annotation
    tools.assert_equal((BASIC_DICT_HASH, BASIC_DICT_ORDERED), next(r))
    # We get the inner list second, who is tokenized due to lack of annotation
    tools.assert_equal((BASIC_SEQ_HASH, list(BASIC_SEQ)), next(r))
    # The outer guy is different this time, as tokens replace the nested dict and list
    # SHA1 of json of [words.ANGSTROM, BASIC_SEQ_HASH, 213, -315]
    tools.assert_equal((UNANNOTATED_NESTED_DICT_HASH, UNANNOTATED_NESTED_DICT_TOKENIZED),
                       next(r))
    tools.assert_raises(StopIteration, next, r)


def test_mixed_nesting():
    t = merky.ExcludeAnnotationTransformer()
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
    # x["a"] is annotated and thus won't show up until the final structure.
    # The first guy will be x["b"][1], which does get tokenized.
    # Second guy will be x["b"], which also gets tokenized.
    # Final guy is the full container x.

    # First up: x["b"][1]
    tools.assert_equal(('37c3a03f839031d9a6eb3281b792a0cb6e02e79d',
                        collections.OrderedDict((
                            ('e', 'E'),
                            ('f', 'F'),
                        ))),
                       next(r))

    # Penultimate: x["b"]
    tools.assert_equal(('a6af006f34fec3ea34cf23b6505fd8eed6ccb3d6',
                        [collections.OrderedDict((
                            ('c', 'C'),
                            ('d', 'D')
                         )),
                         '37c3a03f839031d9a6eb3281b792a0cb6e02e79d']
                        ),
                       next(r))

    # Final, top level
    tools.assert_equal(('a723583cedba5006719024f7600301ea76287a36',
        collections.OrderedDict((
            ('a', [
                collections.OrderedDict((
                    ('a', collections.OrderedDict((('a', 'A'), ('b', 'B')))),
                    ('b', 'B'))),
                collections.OrderedDict((('nothing', 'special'),)),
                ]),
            ('b', 'a6af006f34fec3ea34cf23b6505fd8eed6ccb3d6')))),
        next(r))

    tools.assert_raises(StopIteration, next, r)

