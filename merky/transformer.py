from . import digest
from . import serialization
from . import tree

class Transformer(object):
    """
    Basic merkle tree inpired transform class.

    A `Transformer` can be given a nested data structure of arbitrary
    complexity, and will:
    - Walk the structure depth first
    - Calculate the sha1 (hex digest) of each distinct substructure
    - Yield the ``(sha1, substructure)`` pair to the caller
    - Substitute the sha1 for that substructure within its containing structure
    
    The top-level structure given is always yielded with its hash, whether it
    was complex or not.

    The depth-first walk will traverse anything that looks like a dict
    (that is, it implements ``iteritems``) or things that support
    iteration (implement ``__iter__``), with the exception of strings.  Strings
    are identified as anything that implements ``encode``.  Note that this means
    a ``json.JSONEncoder`` would be treated as a string, for example.

    Each structure is converted into a normal form, such that:
    * Strings, numbers, and booleans are left as is.
    * Dict-like structures get sorted by key and converted to
      ``collections.OrderedDict``.
    * Sequences get converted to `list` objects.

    This gives a result that can in principle produce a deterministic serialized
    form suitable for sha1 hashing.  Note that floating point values cannot be
    relied upon to give a deterministic result, and consequently they should be
    handled with care; consider converting them to string representations of
    fixed scale first.

    JSON is used for the serialization, and allows for unicode characters in
    strings and disallows the use of nan.
    """
    def __init__(self):
        self.serializer = self.get_serializer()
        self.tokenizer = self.get_tokenizer()
        self.dispatcher = self.get_dispatcher()

    def walker(self, structure):
        """
        Returns the `merky.tree.walker` for `structure` given self's `dispatcher` and `tokenizer`.
        """
        return tree.walker(structure, self.dispatcher, self.tokenizer)


    def transform(self, structure):
        """
        Walks the `structure` depth-first and yields `(sha1, normal_structure)` pairs according to
        the rules of `self.dispatcher`.

        If the same substructure appears multiple times within `structure`, it should be yielded
        with its corresponding sha1 hash the same number of times; duplicates are not filtered.
        """
        seen = False
        for pair in self.walker(structure):
            yield pair
            seen = True
        if not seen:
            yield (self.tokenizer(structure), structure)


    def get_serializer(self):
        """
        Returns a function to be used for structure serialization.  This implementation uses
        JSON with unicode support, no nans, and sorted keys.  The serialization must be consistent
        between uses to expect a consistent hash for the same input structure.

        Subclasses could override this to use an alternate serialization approach; the result must
        support `encode()`.
        """
        return serialization.json_serializer()


    def get_dispatcher(self):
        """
        Returns a function to use as the type-handler dispatcher within the object graph walk.
        This implementation uses the `merky.tree.full_nesting_dispatcher`.
        """
        return tree.full_nesting_dispatcher


    def get_tokenizer(self):
        """
        Returns a function to use to convert structures to "tokens" (hashes); this assumes that
        the serializer from `get_serializer` is already available at `self.serializer`.

        This implementation uses the JSON serializer of `get_serializer` and the sha1 hexdigest
        of `merky.digest.hexdigest`.
        """
        return digest.hexdigester(self.serializer)


class AnnotationTransformer(Transformer):
    """
    A merky Transformer that normalizes the input structure, but only yields/tokenizes
    structures that have been "annotated" with the ``__merky__`` attribute with a
    true value.

    The top-level structure is always tokenized and yielded regardless of the presence of the
    annotation.

    See the `merky.util.annotate` helper for annotating your data structures for use with
    this transformer.
    """

    def get_dispatcher(self):
        return tree.annotation_dispatcher


class ExcludeAnnotationTransformer(Transformer):
    """
    A merky Transformer that normalizes the input structure, but excludes
    structures that have been "annotated" with the ``__merky__`` attribute with a
    true value.

    The top-level structure is always tokenized and yielded regardless of the presence of the
    annotation.

    See the `merky.util.annotate` helper for annotating your data structures for use with
    this transformer.
    """
    def get_dispatcher(self):
        return tree.exclude_annotation_dispatcher
