import hashlib
import json

def hexdigest(encodable):
    return hashlib.sha1(encodable.encode("utf-8")).hexdigest()


class Transformer(object):
    def __init__(self):
        self.encoder = self.get_encoder()

    def transform(self, structure):
        yield hexdigest(self.encoder.encode(structure)), structure

    def get_encoder(self):
        return json.JSONEncoder(ensure_ascii=False,
                                allow_nan=False,
                                sort_keys=True,
                                separators=(",",":"))

