import json

def json_serializer():
    """
    Returns a function that can serialize to JSON, with unicode enabled,
    nans disallowed, keys sorted, and whitespace-free separators.
    """
    return json.JSONEncoder(ensure_ascii=False,
                            allow_nan=False,
                            sort_keys=True,
                            separators=(",",":")).encode

