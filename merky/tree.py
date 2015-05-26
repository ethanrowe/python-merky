import collections
import functools
import hashlib
import itertools
import json

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
        i = flatten(sorted(item.iteritems()))
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
    current, collector, tokenize = iter((structure,)), lambda x: x, False
    while True:
        try:
            next_item, next_col, next_tok = dispatcher(next(current))
            if next_col:
                stack.append((current, collector, tokenize, accum))
                current, collector, tokenize, accum = next_item, next_col, next_tok, []
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
        return walker(structure, full_nesting_dispatcher, self.tokenizer)


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

