import six
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

    
    @classmethod
    def attrs_from_token_list(cls, t_list, reader):
        return reader(t_list[0])


    @classmethod
    def members_from_token_list(cls, t_list, reader):
        if t_list is None or len(t_list) < 2:
            return None
        items = reader(t_list[1])
        return type(items)((k, cls.from_token(t, reader))
                           for k, t in six.iteritems(items))


    @classmethod
    def from_token(cls, token, reader):
        tokens = reader(token)
        return cls(attrs=cls.attrs_from_token_list(tokens, reader),
                   members=cls.members_from_token_list(tokens, reader))


