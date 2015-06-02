import itertools
import six
from merky import util

class AttributeGraph(object):
    """
    Represent a hierarchy of nodes with attributes.

    An `AttributeGraph` can be thought of as a pair of dictionaries:
    * A dictionary of arbitrary key/value pairs; the "attributes" of a node.
    * A dictionary of "members"; the nodes that "belong" to the node or are logically "under" the node.

    The keys of the members dictionary identify the member nodes within that dictionary but do not have
    any other requirements (in terms of uniqueness) outside the scope of that dictionary.  Such concerns
    are left to the user.

    The values of the members dictionary are expected to be instances of `AttributeGraph`.  It is not
    required that they be; they will be annotated in any case.  However, when restoring a graph from
    a hash-to-structure mapping, they will be restored as `AttributeGraph` instances, so they must be of
    the appropriate shape.

    Both dictionaries will be annotated for use with the `merky.AnnotationTransformer`.  However, the
    expectation is that the "attributes" dictionary does not require further annotation (even if it has
    nested structures), while the values of the "members" dictionary will be annotated and thus tokenized.

    Suppose we have some logical structure like:

               -----------
               |  PARENT |
               | - attrs |
               -----------
                 /    \ 
            (has a)  (has a)
              /          \ 
             \/          \/
        -----------   -----------
        | CHILD_A |   | CHILD_B |
        | - attrs |   | - attrs |
        -----------   -----------

    We might represent that thus:

        AttributeGraph(
            attrs=PARENT_ATTRS_DICT,
            members={
                "a": AttributeGraph(attrs=CHILD_A_ATTRS_DICT),
                "b": AttributeGraph(attrs=CHILD_B_ATTRS_DICT),
            }
        )

    The logical annotation transformer output would look something like:

                               PARENT_TOKEN
                                     |
                                    \|
                                   PARENT: [PARENT_ATTRS_TOKEN, CHILDREN_TOKEN]
                                            /                      /
                                           /                      /
                                          /                      /
                                         /                      /
                                       |/                      /
        PARENT_ATTRS: OrderedDict([...])                      /
                                                             /
                                                           |/
            CHILDREN: OrderedDict([('a', CHILD_A_TOKEN), ('b', CHILD_B_TOKEN)])
                                         /                      |
                                        /                       |
                                      |/                        |/
        CHILD_A: [CHILD_A_ATTRS_TOKEN]      CHILD_B: [CHILD_B_ATTRS_TOKEN]
                    /                                      |
                  |/                                       |/
        CHILD_A_ATTRS: OrderedDict([...])   CHILD_B_ATTRS: OrderedDict([...])


    The basic rules for annotation (and thus annotated transformation):
    * The `AttributeGraph` will be represented as a list.
    * The first member of the list will be the tokenized `attrs` dictionary.
    * The optional second member of the list will be the tokenized `members`
      dictionary, the values of which are also tokenized; it's optional because
      it's excluded from the list when the dictionary is empty.
    """

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
        """
        Produces an `AttributeGraph` from the given `token` and `reader`.

        Parameters:
            `reader`:  a callable that, when given a "token" (the sha1 hash)
                       of a structure, returns the corresponding structure
                       (presumably from storage or cache or whatever).
            `token`:   the "token" corresponding to the list structure for the
                       `AttributeGraph`.

        If the structure has a non-empty members dictionary structure, each
        member (the values of the dictionary) will be recursively expanded
        using this same method.

        Returns an `AttributeGraph` with attributes and members fully realized.
        """
        tokens = reader(token)
        return cls(attrs=cls.attrs_from_token_list(tokens, reader),
                   members=cls.members_from_token_list(tokens, reader))


    def walk(self, prior, key, predicate=lambda o, p, k: True):
        chain = list(itertools.chain(((key, self),), prior))
        if predicate(self, prior, key):
            yield iter(chain)

        if self.members:
            for k, v in sorted(six.iteritems(self.members)):
                for result in v.walk(chain, k, predicate=predicate):
                    yield result

    def nodes(self):
        """
        Iterate over all nodes (and their ancestry) in the graph.

        Walks the AttributeGraph and per node, yields an iterator of
        `(key, node)` pairs.  That sequence of pairs is in depth-first
        order, starting with the specific node and its corresponding key
        within its parent, followed by the parent node and that node's key
        within its own parent, and so on all the way to the root of the tree.

        If you're only interested in each node in isolation, then you need
        only use the first item in each such group.  However, this model lets
        you see each node's "ancestry" or path through the hierarchy, which
        is helpful for various uses.

        The root node's key is always `None` within this scheme.

        Given some AttributeGraph A with child members B and C (and corresponding
        keys "b" and "c", respectively), then:

            [list(s) for s in A.nodes()]

        would produce:

            [
                [(None, A)],
                [("b", B), (None, A)],
                [("c", C), (None, A)],
            ]
    
        """

        return self.walk((), None)

    def leaves(self):
        """
        Iterate over all leaf nodes (and their ancestry) in the graph

        Like `nodes`, but only the sequences for leaf nodes are yielded; each
        sequence has the full ancestry, but the intermediary nodes do not
        yield a sequence.

        Given the A, B, C scenario described for `nodes()`,

            [list(s) for s in A.leaves()]

        would produce:

            [
                [("b", B), (None, A)],
                [("c", C), (None, A)],
            ]

        """
        return self.walk((), None, predicate=lambda o, p, k: (o.members is None or len(o.members) < 1))


