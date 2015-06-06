import six
from merky import util

NO_DEFAULT=object()

class TokenDict(object):
    """
    A `dict`-like structure that annotates its values and ensures order.

    While the `TokenDict` looks and acts like a `dict`, its values are always
    annotated.  To access the "real" values, use the `dict_` member, which is
    the underlying dictionary itself.

    You can mutate that dictionary directly, and subsequent calls to
    `items`, `iteritems`, `keys`, `values` on the `TokenDict` will reflect
    those changes.

    As always, mutate with discretion.
    """
    __merky__ = True

    def __init__(self, dict_):
        self.dict_ = dict_

    def get(self, item, default=NO_DEFAULT):
        """
        Returns the annotated value associated with `key`.

        Raises a `KeyError` if the key is missing, unless a `default` is
        provided.  When the default is used, it is returned as-is without
        additional annotation.
        """
        try:
            return util.annotate(self.dict_[item])
        except KeyError:
            if default is NO_DEFAULT:
                raise
            return default


    def __getitem__(self, key):
        return self.get(key)

    def __setitem__(self, key, val):
        self.dict_[key] = val

    def _pairs(self):
        return sorted(six.iteritems(self.dict_))

    def keys(self):
        """
        Iterates over the keys in sorted order.
        """
        return iter(k for k, _ in self._pairs())

    def values(self):
        """
        Iterates over the annotated values in sorted-key order.
        """
        return iter(util.annotate(v) for _, v in self._pairs())

    def items(self):
        """
        Iterates over the `(key, value)` pairs in sorted-key order.
        """
        for k, v in self._pairs():
            yield k, util.annotate(v)

    def iteritems(self):
        """
        See `items()`.
        """
        return self.items()

    @classmethod
    def from_token(cls, token, reader, builder=None):
        """
        Assembles a `TokenDict` by walking a graph of tokens.

        Parameters:
            `token`:   the "token" identifying the top-level structure
                       to be converted to a `TokenDict`.
            `reader`:  a function that, given a "token", returns the
                       corresponding structure.
            `builder`: (Optional) a function to apply to each token in the
                       `TokenDict` when assembling; it will be called with the
                       token seen and the `reader` above.  Ue this to, for instance,
                       convert each value into a more specific object.

        Returns a new `TokenDict` instance.
        """
        dict_ = reader(token)
        handler = reader if builder is None else lambda val: builder(val, reader)
        return cls(dict((k, handler(v)) for k, v in six.iteritems(dict_)))

