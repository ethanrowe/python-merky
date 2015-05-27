import json

from . import digest
from . import tree

class Transformer(object):
    def __init__(self):
        self.serializer = self.get_serializer()
        self.tokenizer = self.get_tokenizer()
        self.dispatcher = self.get_dispatcher()

    def walker(self, structure):
        return tree.walker(structure, self.dispatcher, self.tokenizer)


    def transform(self, structure):
        seen = False
        for pair in self.walker(structure):
            yield pair
            seen = True
        if not seen:
            yield (self.tokenizer(structure), structure)

    def get_serializer(self):
        return json.JSONEncoder(ensure_ascii=False,
                                allow_nan=False,
                                sort_keys=True,
                                separators=(",",":")).encode

    def get_dispatcher(self):
        return tree.full_nesting_dispatcher


    def get_tokenizer(self):
        return digest.hexdigester(self.serializer)


class AnnotationTransformer(Transformer):
    def get_dispatcher(self):
        return tree.annotation_dispatcher

    def get_serializer(self):
        self._s = super(AnnotationTransformer, self).get_serializer()
        def s(item):
            v = self._s(item)
            return v
        return s

    def get_tokenizer(self):
        self._t = super(AnnotationTransformer, self).get_tokenizer()
        def t(item):
            v = self._t(item)
            return v
        return t

