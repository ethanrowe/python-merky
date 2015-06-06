from nose import tools
from .. import samples
from merky.cases import tokendict
import merky

NAT, ORD, TOK = (samples.TOKENDICT_CASE_NATURAL,
                 samples.TOKENDICT_CASE_ORDERED,
                 samples.TOKENDICT_CASE_TOKENS)


def test_dict_():
    d = {"foo": "bar", "baz": "biz"}
    g = tokendict.TokenDict(d)
    tools.assert_equal(d, g.dict_)


def test_get_and_set():
    d = {"foo": ["bar"]}
    conv = lambda v: list(v) if getattr(v, '__merky__', False) else None
    g = tokendict.TokenDict(d)
    tools.assert_equal(["bar"], conv(g.get("foo")))
    tools.assert_raises(KeyError, g.get, "blah")
    tools.assert_equal("default", g.get("blah", "default"))
    tools.assert_equal(["bar"], conv(g["foo"]))
    g["blah"] = ["somethin"]
    tools.assert_equal(["somethin"], conv(g.get("blah")))


def test_key_sort():
    d = {"z": "Z", "m": "M", "g": "G", "q": "Q", "c": "C", "w": "W", "a": "A"}
    g = tokendict.TokenDict(d)
    tools.assert_equal(list(sorted(d.keys())), [k for k, _ in g.items()])
    tools.assert_equal(list(sorted(d.keys())), list(g.keys()))


def test_value_annotation():
    d = {"a": ["a"], "b": ["b"], "c": ["c"]}
    g = tokendict.TokenDict(d)
    conv = lambda val: list(val) if getattr(val, '__merky__', False) else None

    tools.assert_equal(list(sorted(d.items())),
                       [(k, conv(v)) for k, v in g.items()])

    tools.assert_equal([d[k] for k in sorted(d.keys())],
                       [conv(v) for v in g.values()])



def test_tokenization():
    g = tokendict.TokenDict(NAT)
    i = merky.AnnotationTransformer().transform(g)
    tools.assert_equal((TOK["a"].token, ORD["a"]), next(i))
    tools.assert_equal((TOK["b"].token, ORD["b"]), next(i))
    tools.assert_equal((TOK["c"].token, ORD["c"]), next(i))
    tools.assert_equal((TOK["d"].token, ORD["d"]), next(i))
    tools.assert_equal((TOK.token, TOK.member), next(i))
    tools.assert_raises(StopIteration, next, i)


CACHE = dict((t.token, t.member)
             for t in (TOK["a"], TOK["b"], TOK["c"], TOK["d"], TOK))

def test_restoration():
    g = tokendict.TokenDict.from_token(TOK.token, CACHE.get)
    tools.assert_equal(["a", "b", "c", "d"], list(g.keys()))
    tools.assert_equal(ORD, g.dict_)


def test_restoration_with_builder():
    def wrapper(token, reader):
        def wrapped():
            return ('called me!', reader(token))
        return wrapped

    g = tokendict.TokenDict.from_token(TOK.token, CACHE.get, wrapper)
    tools.assert_equal(["a", "b", "c", "d"], list(g.keys()))
    tools.assert_equal(dict((k, ('called me!', v)) for k, v in ORD.items()),
                       dict((k, v()) for k, v in g.dict_.items()))


