import json

def json_serializer(sort=True):
    """
    Returns a function that can serialize to JSON, with unicode enabled,
    nans disallowed, keys sorted, and whitespace-free separators.

    You can override the sorted keys via `sort=False`.
    """
    return json.JSONEncoder(ensure_ascii=False,
                            allow_nan=False,
                            sort_keys=sort,
                            separators=(",",":")).encode

