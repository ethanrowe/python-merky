import collections
import hashlib
import itertools
import json

import six

def hexdigest(encodable):
    return hashlib.sha1(encodable.encode("utf-8")).hexdigest()


def hexdigester(serializer):
    def inner(structure):
        return hexdigest(serializer(structure))
    return inner


def string_handler(item):
    if hasattr(item, "encode"):
        return item, None, False
    raise TypeError


def flatten(sequence_of_sequences):
    return itertools.chain.from_iterable(sequence_of_sequences)

def pairwise(sequence):
    sequence = iter(sequence)
    try:
        while True:
            yield next(sequence), next(sequence)
    except StopIteration:
        pass


def ordered_map(sequence):
    return collections.OrderedDict(sorted(pairwise(sequence)))


def map_handler(item):
    try:
        i = flatten(sorted(six.iteritems(item)))
        return i, ordered_map, True
    except AttributeError:
        raise TypeError


def seq_handler(item):
    return iter(item), list, True


def default_handler(item):
    return item, None, False


def dispatcher(*handlers):
    def inner(item):
        for handler in handlers:
            try:
                return handler(item)
            except TypeError:
                pass
        raise TypeError("No handler could be found for item of type %s" % type(item))
    return inner

full_nesting_dispatcher = dispatcher(string_handler,
                                     map_handler,
                                     seq_handler,
                                     default_handler)


def walker(structure, dispatcher, tokenizer):
    stack = []
    accum = []
    top_flag = True
    current, collector, tokenize = iter((structure,)), lambda x: x, False
    while True:
        try:
            next_item, next_col, next_tok = dispatcher(next(current))
            if next_col:
                stack.append((current, collector, tokenize, accum))
                current, collector, tokenize, accum, top_flag = next_item, \
                                                                next_col, \
                                                                (next_tok or top_flag), \
                                                                [], \
                                                                False
            else:
                accum.append(next_item)
        except StopIteration:
            value = collector(accum)
            if tokenize:
                t = tokenizer(value)
                yield (t, value)
                value = t

            if not stack:
                break

            current, collector, tokenize, accum = stack.pop()
            accum.append(value)


class Transformer(object):
    def __init__(self):
        self.serializer = self.get_serializer()
        self.tokenizer = self.get_tokenizer()
        self.dispatcher = self.get_dispatcher()

    def walker(self, structure):
        return walker(structure, self.dispatcher, self.tokenizer)


    def transform(self, structure):
        seen = False
        for pair in self.walker(structure):
            yield pair
            seen = True
        if not seen:
            yield (self.tokenizer(structure), structure)

    def get_serializer(self):
        return json.JSONEncoder(ensure_ascii=False,
                                allow_nan=False,
                                sort_keys=True,
                                separators=(",",":")).encode

    def get_dispatcher(self):
        return full_nesting_dispatcher


    def get_tokenizer(self):
        return hexdigester(self.serializer)


class annotate(object):
    __slots__ = ('_o',)
    __merky__ = True

    def __init__(self, wrapped):
        self._o = wrapped

    def __getattr__(self, attr):
        return getattr(self._o, attr)

    def __iter__(self):
        return iter(self._o)


def annotation_handler(handler, name=None, doc=None):
    def wrapped(item):
        i, collector, _ = handler(item)
        return i, collector, getattr(item, '__merky__', False)
    if name:
        wrapped.__name__ = name
    if doc:
        wrapped.__doc__ = doc
    return wrapped

map_annotation_handler = annotation_handler(map_handler, 'map_annotation_handler')
seq_annotation_handler = annotation_handler(seq_handler, 'seq_annotation_handler')

annotation_dispatcher = dispatcher(string_handler,
                                   map_annotation_handler,
                                   seq_annotation_handler,
                                   default_handler)

class AnnotationTransformer(Transformer):
    def get_dispatcher(self):
        return annotation_dispatcher

    def get_serializer(self):
        self._s = super(AnnotationTransformer, self).get_serializer()
        def s(item):
            v = self._s(item)
            return v
        return s

    def get_tokenizer(self):
        self._t = super(AnnotationTransformer, self).get_tokenizer()
        def t(item):
            v = self._t(item)
            return v
        return t

