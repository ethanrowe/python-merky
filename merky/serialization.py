import json

def _json_default(item):
    try:
        return item.__merky_annotated__
    except:
        raise TypeError(
                "object of type %s is not JSON-serializable." % str(type(item)))

def json_serializer(sort=True):
    """
    Returns a function that can serialize to JSON, with unicode enabled,
    nans disallowed, keys sorted, and whitespace-free separators.

    The function will handle merky-annotated objects according to the particulars
    of the underlying annotated structure.

    You can override the sorted keys via `sort=False`.
    """
    return json.JSONEncoder(ensure_ascii=False,
                            allow_nan=False,
                            sort_keys=sort,
                            separators=(",",":"),
                            default=_json_default).encode

