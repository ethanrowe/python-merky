import collections
import itertools
import six

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


class annotate(object):
    """
    Tells merky to tokenize a given object.

    Wrap any arbitrary object with this; the wrapper delegates
    to the wrapped object, but provides a `__merky__` attribute of
    value `True`, indicating to transformers that the object should
    be "tokenized".

    The object wrapped is accessible via `__merky_annotated__`.
    """
    __slots__ = ('__merky_annotated__',)
    __merky__ = True

    def __init__(self, wrapped):
        self.__merky_annotated__ = wrapped

    def __getattr__(self, attr):
        return getattr(self.__merky_annotated__, attr)

    def __iter__(self):
        return iter(self.__merky_annotated__)


def annotate_values(dictlike):
    """
    Returns a dictionary based on `dictlike` with each value wrapped by `annotate`.

    The dictionary itself is not wrapped by `annotate`, only the values.
    """
    return dict((k, annotate(v)) for k, v in six.iteritems(dictlike))

