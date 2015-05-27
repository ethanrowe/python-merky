import collections
import itertools

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
    __slots__ = ('_o',)
    __merky__ = True

    def __init__(self, wrapped):
        self._o = wrapped

    def __getattr__(self, attr):
        return getattr(self._o, attr)

    def __iter__(self):
        return iter(self._o)

