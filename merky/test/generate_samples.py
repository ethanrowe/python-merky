import collections
import hashlib
import json
import sys
import six

COMMON_CODE = """
from collections import OrderedDict

class Tokenset(object):
    def __init__(self, tokens, token):
        self.tokens = tokens
        self.token = token
        self.member = tokens[token]

    def __getitem__(self, key):
        return Tokenset(self.tokens, token=self.member[key])

    def __repr__(self):
        return "Tokenset(%s, token=%s)" % (repr(self.tokens), repr(self.token))

    def __str__(self):
        return self.__repr__()

"""

exec(COMMON_CODE)

def op_or_ident(target, op, **passthru):
    try:
        return getattr(target, op)(**passthru)
    except AttributeError:
        return target

JSON_ENCODER = json.JSONEncoder(allow_nan=False,
                                sort_keys=True,
                                separators=(",",":"),
                                ensure_ascii=False)


def tokenize(value):
    j = JSON_ENCODER.encode(value)
    return hashlib.sha1(j.encode('utf-8')).hexdigest()


class Node(object):
    def __init__(self, vals, recurse=True):
        self.vals = vals
        self.recurse = recurse

    def natural(self):
        return self.generate('natural')

    def ordered(self):
        v = self.generate('ordered')
        return self.apply_ordering(v)

    def tokenized(self, accum=None):
        if accum is None:
            accum = collections.OrderedDict()

        if self.recurse:
            v = self.apply_ordering(self.generate('tokenized', accum=accum))
        else:
            v = self.ordered()

        t = tokenize(v)

        accum[t] = v
        return tokenize(v)


class D(Node):
    def generate(self, op, **passthru):
        return dict((k, op_or_ident(v, op, **passthru)) for k, v in six.iteritems(self.vals))

    def apply_ordering(self, v):
        return collections.OrderedDict((k, v[k]) for k in sorted(v.keys()))


class L(Node):
    def generate(self, op, **passthru):
        return tuple(op_or_ident(v, op, **passthru) for v in self.vals)

    def apply_ordering(self, v):
        return list(v)

def p_ordered_dict(o, indent, outdent):
    return 'OrderedDict([\n' + \
                indent + \
                (',\n%s' % indent).join(pretty(kvp, indent) for kvp in six.iteritems(o)) + \
            '\n%s])' % outdent

def p_dict(o, indent, outdent):
    return '{\n' + \
                indent + \
                ('\n%s' % indent).join("%s: %s," % (pretty(k, indent), pretty(v, indent))
                                       for k, v in six.iteritems(o)) + \
            '\n%s}' % outdent

def p_list(o, indent, outdent):
    return '[\n' + \
                indent + \
                (',\n%s' % indent).join(pretty(v, indent) for v in o) + \
            '\n%s]' % outdent

def p_tuple(o, indent, outdent):
    if len(o) == 1:
        return '(%s,)' % pretty(o[0], indent)
    return '(\n' + \
                indent + \
                (',\n%s' % indent).join(pretty(v, indent) for v in o) + \
            '\n%s)' % outdent

def p_tokenset(o, indent, outdent):
    return 'Tokenset(\n%s%s,\n%stoken=%s\n%s)' % (
            indent,
            pretty(o.tokens, indent),
            indent,
            pretty(o.token, indent),
            outdent)


PRINTERS = (
        (Tokenset, p_tokenset),
        (OrderedDict, p_ordered_dict),
        (dict, p_dict),
        (list, p_list),
        (tuple, p_tuple),
    )


def pretty(struct, indent=''):
    outdent = indent
    indent = outdent + '    '
    for type_, handler in PRINTERS:
        if isinstance(struct, type_):
            return handler(struct, indent, outdent)
    return repr(struct)


def name(var, suffix):
    return '%s_%s' % (var.upper(), suffix.upper())


def constant(var, graph):
    return '%s = %s' % (var, pretty(graph))



def variable_set(varname, graph):
    yield constant(name(varname, 'natural'), graph.natural())
    yield constant(name(varname, 'ordered'), graph.ordered())
    tokens = collections.OrderedDict()
    graph.tokenized(tokens)
    yield constant(name(varname, 'tokens'), Tokenset(tokens, list(tokens.keys())[-1]))


def variables():
    dict_a = D({"a": "aye!", "A": "Eh."})
    yield ('d_a', dict_a)

    yield ('d_b',
           D({"b": "bi", "B": "Bee!"}))

    yield ('l_d_a', L([dict_a]))

    d_a_in_b = D({"b": "b", "a": dict_a}, recurse=False)
    yield 'd_a_in_b', d_a_in_b

    yield 'l_d_a_in_b', L([d_a_in_b])

    yield ('l_nest_partial',
           L([
               D({"abc": 123, "bcd": 234}, recurse=False),
               D({"bro": L([D({"name": "johnny", "gender": "male"}, recurse=False)]),
                  "sis": L([D({"name": "sissy", "gender": "female"}, recurse=False)])}),
            ]))

    yield ('l_multi_nest_partial',
           L([
               D({123: L(["one", "two", "three"])}, recurse=False),
               D({"1-0": L([
                    D({"a dict": D({"a": "b"}), "a list": L(["a", "b"])}, recurse=False),
                    D({"2-0": L([D({"eins": 1, "zwei": 2}, recurse=False)]),
                        "2-1": L([D({"foo": "bar", "baz": L(["blah"])}, recurse=False)]),
                    }),
                  ]),
                  "1-1": L([
                    D({"cracktopolis": "methboro", "inner": D({"gar": "bage"})}, recurse=False),
                    D({"2-0": L([D({"some": "thing", "inner": D({"or": L(["other"])})}, recurse=False)]),
                        "2-1": L([D({"goat": "milk"}, recurse=False)]),
                    }),
                  ]),
                }),
           ]))

    yield 'readme_full_transform', D({"first": L(["a", "b", "c"]),
                                      "second": D({"first": "1st!", "second": "2nd!"})})

    yield 'tokendict_case', D({"a": D({
                                        "a-0": L(["a0", "a1", "a2"]),
                                        "a-1": D({"a1": "A1", "a2": "A2"}),
                                    }, recurse=False),
                                "b": L([
                                        D({"b-0-0": "b00", "b-0-1": "b01"}),
                                        L(["b-1-0", "b-1-1", "b-1-2"]),
                                    ], recurse=False),
                                "c": L(["c0", "c1", "c2"], recurse=False),
                                "d": D({"d-0": "D0", "d-1": "D1", "d-2": "D2"}, recurse=False),
                            })

    yield ('walker_list_case',
            L([
                "string",
                57,
                L(["string", 30, D({"a": "b"}), L(["a", "b", "c"])]),
                D({"string": "stringy",
                    "number": 20,
                    "dict": D({"a": "b"}),
                    "list": L(["another", "list"])})
            ]))

    yield ('walker_dict_case',
            D({
                "string": "stringy",
                "number": 30000,
                "dict": D({
                        "string": "stringy",
                        "number": -52,
                        "dict": D({"a": "b"}),
                        "list": L(["another", "list"]),
                    }),
                "list": L([
                        "string",
                        23423,
                        D({
                            "string": "stringy",
                            "number": -12,
                            "dict": D({"a": "b"}),
                            "list": L(["another", "list"]),
                            }),
                        L([
                            "string",
                            1234,
                            D({"a": "b"}),
                            L(["another", "list"]),
                            ]),
                    ]),
            }))

def generate(stream):
    six.print_(COMMON_CODE, file=stream)
    for name, structure in variables():
        for definition in variable_set(name, structure):
            six.print_(definition, file=stream)

if __name__ == '__main__':
    generate(sys.stdout)

