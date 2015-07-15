import collections

from nose import tools
from .. import samples
from merky import transformer
from merky.cases import walker

def s(sample_name, suffix):
    return getattr(samples, "%s_%s" % (sample_name, suffix))


def get_sample(sample_name):
    return [s(sample_name, suffix) for suffix
            in ('NATURAL', 'ORDERED', 'TOKENS')]


def reader_func(collection):
    return lambda t: collection[t]


def get_walker_inputs(structure):
    d = collections.OrderedDict(
            transformer.Transformer().transform(structure))

    # The "head" is the last token added to the collection.
    return reader_func(d), list(d.keys())[-1]


def scenario(sample_name):
    def decorator(func):
        def wrapper():
            natural, ordered, tokens = get_sample(sample_name)
            reader, head = get_walker_inputs(natural)
            target = walker.Walker(reader, head)
            return func(natural, ordered, tokens, target)
        wrapper.__name__ = func.__name__
        return wrapper
    decorator.__name__ = "scenario_%s" % sample_name
    return decorator


def has_structure(n, exp):
    tools.assert_equal(exp, n.structure)


def has_token(n, exp):
    tools.assert_equal(exp, n.token)


def extract(o, keys):
    for key in keys:
        o = o[key]
    return o


def match(tok, wlk, *keys):
    tok = extract(tok, keys)
    wlk = extract(wlk, keys)
    has_structure(wlk, tok.member)
    has_token(wlk, tok.token)


def unnested(wlk, *keys):
    tools.assert_raises(KeyError, extract, wlk, keys)


def matcher(name):
    def builder(nat, ord_, tok, wlk):
        return lambda *keys: match(tok, wlk, *keys)
    return scenario(name)(builder)()


def unnested_checker(name):
    def builder(nat, ord_, tok, wlk):
        return lambda *keys: unnested(wlk, *keys)
    return scenario(name)(builder)()


def test_list():
    m = matcher('WALKER_LIST_CASE')
    u = unnested_checker('WALKER_LIST_CASE')
    yield m
    yield u, 0 # This guy is a string.
    yield u, 1 # This guy is a number.
    yield m, 2 # This guy is a list.
    yield m, 3 # This guy is a dict.

    # Explore the nested list.
    yield u, 2, 0 # A string
    yield u, 2, 1 # A number
    yield m, 2, 2 # A dict.
    yield m, 2, 3 # A list.

    # The second-level dict is just strings.
    yield u, 2, 2, 'a'

    # The second-level list is also just strings.
    yield u, 2, 3, 0
    yield u, 2, 3, 1
    yield u, 2, 3, 2

    # Explore the first nested dict.
    yield u, 3, 'string' # A string
    yield u, 3, 'number' # A number
    yield m, 3, 'list' # A list
    yield m, 3, 'dict' # A dict
    
    # The second-level list is again just strings
    yield u, 3, 'list', 0
    yield u, 3, 'list', 1

    # And the second-level dict is as well.
    yield u, 3, 'dict', 'a'


def test_dict():
    m = matcher('WALKER_DICT_CASE')
    u = unnested_checker('WALKER_DICT_CASE')
    yield m
    yield m, 'list' # A list.
    yield m, 'dict' # A dict.
    yield u, 'string' # A string.
    yield u, 'number' # A number.

    # Explore the first level list.
    yield u, 'list', 0 # A string
    yield u, 'list', 1 # A number
    yield m, 'list', 2 # A dict
    yield m, 'list', 3 # A list.

    # Explore the second-tier dict.
    yield u, 'list', 2, 'string'
    yield u, 'list', 2, 'number'
    yield m, 'list', 2, 'list'
    yield m, 'list', 2, 'dict'
    # And the substructures are just strings.
    yield u, 'list', 2, 'list', 0
    yield u, 'list', 2, 'list', 1
    yield u, 'list', 2, 'dict', 'a'

    # Now explore the second-tier list.
    yield u, 'list', 3, 0 # A string
    yield u, 'list', 3, 1 # A number
    yield m, 'list', 3, 2 # A dict of string
    yield u, 'list', 3, 2, 'a'
    yield m, 'list', 3, 3 # A list of strings
    yield u, 'list', 3, 3, 0
    yield u, 'list', 3, 3, 1

    # Explore the first level dict.
    yield u, 'dict', 'string'
    yield u, 'dict', 'number'
    yield m, 'dict', 'list' # A list of strings
    yield u, 'dict', 'list', 0
    yield u, 'dict', 'list', 1
    yield m, 'dict', 'dict' # A dict of strings
    yield u, 'dict', 'dict', 'a'


