import codecs
import collections
import json
from .. import serialization

class Structure(object):
    """
    Basic interface for a serializ(ed/able) "structure".

    Without providing specifics for read/write operations, gives
    the basic interface that these things should have in common.

    The purpose of the structure is to combine:
    * The map of token/structure pairs one gets from transformation
    * A "head" token indicating which structure is the top-level
      structure.

    The combination of the `head` token and the `get` method would
    allow for load of specific cases like the
    `merky.cases.attrgraph.AttributeGraph` and similar (the `from_token`
    classmethod).
    """
    def populate(self, token_structure_pairs):
        raise NotImplementedError("populate() not implemented.")

    def get(self, key):
        raise NotImplementedError("get() not implemented.")

    def __getitem__(self, key):
        raise NotImplementedError("__getitem()__ not implemented.")



class TokenMapStructure(Structure):
    """
    Maintains an internal in-memory map of token/structure pairs.

    While the `head` can be explicitly set, the `head` defaults to the
    last token seen via `populate()`.
    """
    @staticmethod
    def default_tokenmap():
        return collections.OrderedDict()

    def populate(self, token_structure_pairs):
        """
        Ingests the `token_structure_pairs` into the internal token map.

        Sets `head` to the last token seen, regardless of the current state of `head`.
        """
        self.tokenmap.update(token_structure_pairs)
        self.head = next(iter(reversed(self.tokenmap))) if len(self.tokenmap) > 0 else None

    def get(self, key):
        """
        Returns the corresponding structure from the internal map given the token `key`.
        """
        return self.tokenmap.get(key)

    
    def __getitem__(self, key):
        """
        Returns the corresponding structure from the internal map given the token 'key'.
        """
        return self.tokenmap[key]


class InMemoryStructure(TokenMapStructure):
    """
    An in-memory "store" that has both the read and write interfaces.
    """
    def __init__(self, tokenmap=None, head=None):
        self.tokenmap = self.default_tokenmap() if tokenmap is None else tokenmap
        self.head = head

    def close(self):
        pass


class JSONStreamReadStructure(TokenMapStructure):
    """
    Reads merkified structure from a utf-8 JSON stream.
    """
    def __init__(self, stream):
        self.stream = stream
        self.tokenmap, self.head = self.deserialize_from_stream(stream)

    @classmethod
    def deserialize_from_stream(cls, stream):
        return json.load(stream, encoding='utf-8')


class JSONStreamWriteStructure(TokenMapStructure):
    """
    Writes merkified structure to a utf-8 JSON stream.

    The instance accumulates state internally and only serializes to stream
    at close().
    """
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
    """
    Reads merkified structure from utf-8 JSON file.
    """
    def __init__(self, path):
        self.path = path
        self.tokenmap, self.head = self.deserialize_from_file(self.path)

    @classmethod
    def deserialize_from_file(cls, path):
        with codecs.open(path, encoding="utf-8", mode="rb") as f:
            return cls.deserialize_from_stream(f)


class JSONFileWriteStructure(JSONStreamWriteStructure):
    """
    Writes merkified structure to utf-8 JSON file.

    The instance accumulates state internally and only serializes to the file
    at close().
    """
    def __init__(self, path):
        self.tokenmap = self.default_tokenmap()
        self.path = path

    def serialize_to_file(self, path):
        """
        Writes the current state to the `path` specified.
        """
        with codecs.open(path, encoding="utf-8", mode="wb") as f:
            self.serialize_to_stream(f)

    def close(self):
        """
        Writes the state out to the file at `self.path`.
        """
        self.serialize_to_file(self.path)


