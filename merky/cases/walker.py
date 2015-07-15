class Walker(object):
    """
    Explore merky tokenized structures.

    Given a tokenized structure in the form of a reader function (which
    returns the normalized structure as a function of token) and a token,
    the `Walker` exposes the merkified structure as a graph:
        * the `token` attribute is the token
        * the `structure` attribute is the normalized structure
        * the act of looking up by key/index (e.g. `node[key]`) will return
          another `Walker` for the tokenized structure that is referenced
          by the structure at the specified key/index.

    For instance, suppose you have some list of two dicts:

        [{"a": "A"},
         {"b": "B"}]

    Suppose further that it has this merkified structure when transformed:

        # imagine that T0, T1, and T2 are actually SHA1 hexdigest tokens.
        ((T0, {"a": "A"}),
            (T1, {"b": "B"}),
            (T2, [T0, T1]))

    If you provide a `read` function that can look up the corresponding normalized structure
    for a given token (such that `read(T0)` would return `{"a": "A"}`, for instance), then
    a walker would be created:

        w = Walker(read, T2)

    You can now walk this thing top-down (based on the shape of the original list of dicts),
    but see the tokens and partial structures along the way.

        print w.token, w.structure # "T2 [T0, T1]"
        print w[0].token, w[0].structure # "T0 {'a': 'A'}"
        print w[1].token, w[1].structure # "T1 {'b': 'B'}"

    When using the `[]` mechanism, you are expected to know that the value at `w.structure[key]`
    is a token, meaning that the `Walker` will get that token and return a new `Walker` instance
    bound to the structure to which that token refers (looked up via the `read` function in this
    case).
    """
    __slots__ = ('reader', 'token', 'structure')

    def __init__(self, reader, token):
        self.reader = reader
        self.token = token
        self.structure = reader(token)


    def __getitem__(self, key):
        return self.node(self.structure[key])

    
    def node(self, key):
        return type(self)(self.reader, key)


