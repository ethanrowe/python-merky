import hashlib

def hexdigest(encodable):
    return hashlib.sha1(encodable.encode("utf-8")).hexdigest()


def hexdigester(serializer):
    def inner(structure):
        return hexdigest(serializer(structure))
    return inner

