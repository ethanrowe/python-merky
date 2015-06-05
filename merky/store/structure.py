import codecs
import collections
import json
from .. import serialization

class Structure(object):
    def populate(self, token_structure_pairs):
        raise NotImplementedError("populate() not implemented.")

    def get(self, key):
        raise NotImplementedError("get() not implemented.")

    def __getitem__(self, key):
        raise NotImplementedError("__getitem()__ not implemented.")



class TokenMapStructure(Structure):
    @staticmethod
    def default_tokenmap():
        return collections.OrderedDict()

    def populate(self, token_structure_pairs):
        self.tokenmap.update(token_structure_pairs)
        self.head = next(iter(reversed(self.tokenmap))) if len(self.tokenmap) > 0 else None

    def get(self, key):
        return self.tokenmap.get(key)

    
    def __getitem__(self, key):
        return self.tokenmap[key]


class InMemoryStructure(TokenMapStructure):
    def __init__(self, tokenmap=None, head=None):
        self.tokenmap = self.default_tokenmap() if tokenmap is None else tokenmap
        self.head = head

    def close(self):
        pass


class JSONStreamReadStructure(TokenMapStructure):
    def __init__(self, stream):
        self.stream = stream
        self.tokenmap, self.head = self.deserialize_from_stream(stream)

    @classmethod
    def deserialize_from_stream(cls, stream):
        return json.load(stream, encoding='utf-8')


class JSONStreamWriteStructure(TokenMapStructure):
    serializer = serialization.json_serializer(sort=False)

    def __init__(self, stream):
        self.tokenmap = self.default_tokenmap()
        self.stream = stream

    def serialize_to_stream(self, stream):
        stream.write(self.serializer([self.tokenmap, self.head]))

    def close(self):
        self.serialize_to_stream(self.stream)
        self.stream.flush()


class JSONFileReadStructure(JSONStreamReadStructure):
    def __init__(self, path):
        self.path = path
        self.tokenmap, self.head = self.deserialize_from_file(self.path)

    @classmethod
    def deserialize_from_file(cls, path):
        with codecs.open(path, encoding="utf-8", mode="rb") as f:
            return cls.deserialize_from_stream(f)


class JSONFileWriteStructure(JSONStreamWriteStructure):
    def __init__(self, path):
        self.tokenmap = self.default_tokenmap()
        self.path = path

    def serialize_to_file(self, path):
        with codecs.open(path, encoding="utf-8", mode="wb") as f:
            self.serialize_to_stream(f)

    def close(self):
        self.serialize_to_file(self.path)


