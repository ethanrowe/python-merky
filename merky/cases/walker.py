class Walker(object):
    __slots__ = ('reader', 'token', 'structure')

    def __init__(self, reader, token):
        self.reader = reader
        self.token = token
        self.structure = reader(token)


    def __getitem__(self, key):
        return self.node(self.structure[key])

    
    def node(self, key):
        return type(self)(self.reader, key)


