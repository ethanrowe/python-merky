import six
from merky import util

class TokenDict(object):
    __merky__ = True

    def __init__(self, dict_):
        self.dict_ = dict_

    def get(self, item):
        pass

    def set(self, item, value):
        pass

    def _pairs(self):
        return sorted(six.iteritems(self.dict_))

    def keys(self):
        return iter(k for k, _ in self._pairs())

    def values(self):
        return iter(util.annotate(v) for _, v in self._pairs())

    def items(self):
        for k, v in self._pairs():
            yield k, util.annotate(v)

    def iteritems(self):
        return self.items()

    @classmethod
    def from_token(cls, token, reader, builder=None):
        dict_ = reader(token)
        handler = reader if builder is None else lambda val: builder(reader(val))
        return cls(dict((k, handler(v)) for k, v in six.iteritems(dict_)))

