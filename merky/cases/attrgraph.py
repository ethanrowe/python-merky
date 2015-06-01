from merky import util

class AttributeGraph(object):
    __slots__ = ('attrs', 'members')
    __merky__ = True

    def __init__(self, attrs=None, members=None):
        if attrs is None:
            attrs = self.get_default_attrs()
        if members is None:
            members = self.get_default_members()

        self.attrs = attrs
        self.members = members

    def __iter__(self):
        yield util.annotate(self.attrs)
        if len(self.members):
            yield util.annotate(util.annotate_values(self.members))


    @classmethod
    def get_default_attrs(cls):
        return {}


    @classmethod
    def get_default_members(cls):
        return {}

