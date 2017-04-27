import six

from . import util

def string_handler(item):
    if hasattr(item, "encode"):
        return item, None, False
    raise TypeError


def map_handler(item):
    try:
        i = util.flatten(sorted(six.iteritems(item)))
        return i, util.ordered_map, True
    except AttributeError:
        raise TypeError


def seq_handler(item):
    return iter(item), list, True


def default_handler(item):
    return item, None, False


def annotation_handler(handler, name=None, doc=None):
    def wrapped(item):
        i, collector, _ = handler(item)
        return i, collector, getattr(item, '__merky__', False)
    if name:
        wrapped.__name__ = name
    if doc:
        wrapped.__doc__ = doc
    return wrapped



def dispatcher(*handlers):
    def inner(item):
        for handler in handlers:
            try:
                return handler(item)
            except TypeError:
                pass
        raise TypeError("No handler could be found for item of type %s" % type(item))
    return inner


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


map_annotation_handler = annotation_handler(map_handler, 'map_annotation_handler')
seq_annotation_handler = annotation_handler(seq_handler, 'seq_annotation_handler')

full_nesting_dispatcher = dispatcher(string_handler,
                                     map_handler,
                                     seq_handler,
                                     default_handler)

annotation_dispatcher = dispatcher(string_handler,
                                   map_annotation_handler,
                                   seq_annotation_handler,
                                   default_handler)

def excluder_handler(handler, converter, collector, name):
    def handle(item):
        next_item, next_col, next_tok = handler(item)
        if next_tok:
            next_item = converter(next_item)
            next_col = collector
        return next_item, next_col, not next_tok
    handle.__name__ = name
    return handle

def _unmerk(items):
    for i in items:
        yield getattr(i, '__merky_annotated__', i)

exclude_annotation_dispatcher = dispatcher(
        string_handler,
        excluder_handler(
            map_annotation_handler,
            lambda m: util.flatten((k, util.annotate(v))
                for k, v in util.pairwise(m)),
            lambda i: util.ordered_map(_unmerk(i)),
            'map_exclude_handler'),
        excluder_handler(
            seq_annotation_handler,
            lambda s: (util.annotate(v) for v in s),
            lambda i: list(_unmerk(i)),
            'seq_exclude_handler'),
        default_handler)

