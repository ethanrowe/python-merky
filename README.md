# python-merky

A python module for Merkle tree inspired operations (flexibility over efficiency).

[![Build Status](https://travis-ci.org/ethanrowe/python-merky.svg)](https://travis-ci.org/ethanrowe/python-merky)

# Overview

The [Merkle tree](https://en.wikipedia.org/wiki/Merkle_tree) has been around since the 1970s
and is useful for all sorts of marvelous things.  A couple notable examples of their application
within the free software world:
* The [git version control system](https://git-svm.com) data model uses a form of Merkle tree
  to efficiently represent a repository as a graph of discrete states.  The deterministic identifiers
  of each state enables easy, efficient, straightforward branch management, ultimately leading to
  the possibility of distributed version control.
* The [cassandra distributed database](http://cassandra.apache.org/) uses Merkle trees to
  [detect inconsistencies between nodes](http://www.datastax.com/dev/blog/advanced-repair-techniques).

The `merky` module provides tools for calculating the components of a hash tree, initially intended
to provide a sort of "git for data structures".  It is not adhering to a particular formal definition
of a tree or a particular data structure form; it works with arbitrary data structures and gives the
user control over how the data structures are transformed.

# Concepts

## Tokenization

When `merky` transforms a data structure, it performs a depth-first walk over the structure.
For a given nested data structure, `merky`:
* Calculates a canonical form of that data structure.
* Serializes that canonical form (currently using UTF-8 JSON serialization).
* Calculates a hash for that serialized form (currenly using the SHA1 hexdigest).
* *Yields* the `(hash, canonical)` pair to the caller.
* *Substitutes* the hash for the original structure within its containing structure for the
  remainder of the calculation.

Tokenization is the basic function of `merky`.

### Canonical forms

The hash calculation for a given data structure needs to be deterministic, which in turn requires
that the serialization of structures be deterministic.

Data structures like python's `dict` do not guarantee a deterministic ordering; `merky` therefore
must provide such guarantees itself.  The default rules:
* dict-like things are sorted and converted to the standard library's `OrderedDict`.
* list-like things are converted to a list.
* everything else passes through unaltered.

`Merky` relies on duck typing rather than inspecting types.
* If it has an `encode` attribute, assume it's a string.  (This is important to distinguish between
  strings and sequences).
* If it has an iterator over key/value pairs (`six.iteritems`), assume it's a dict.
* If it supports iteration (`iter(foo)`), assume it's a list.

### Example transformation

Code leaves less room for interpretive error than does prose.

```python
import merky
import six

structure = {
    "first": ("a", "b", "c"),
    "second": {"first": "1st!", "second": "2nd!"}
}

t = merky.Transformer().transform(structure)

# Depth-first, sorted key order; the ("a", "b", "c") is tokenized first.
# Note that the tuple is canonicalized as a list.
# ('e13460afb1e68af030bb9bee8344c274494661fa', ['a', 'b', 'c'])
six.print_(next(t))

# According to sorted key order, the {"first": "1st!"...} dict is tokenized second.
# Note that the dict is canonicalized as an OrderedDict.
# ('555cf5554cbd46144bd01851ebb278d32d4dc538', OrderedDict([('first', '1st!'), ('second', '2nd!')]))
six.print_(next(t))

# The outer container is last.  Note that substructures have been replaced by
# their SHA1 digests.  They've been "tokenized".
# ('4c928a93cd9af338c722acfdc8daf09d186e621f', OrderedDict([('first', 'e13460afb1e68af030bb9bee8344c274494661fa'), ('second', '555cf5554cbd46144bd01851ebb278d32d4dc538')]))
six.print_(next(t))

# Reached the end; raises StopIteration
next(t)
```

## Annotation

While the basic `merky.Transformer` will tokenize all dict-like and sequence-like
structures, from bottom to top, this isn't necessarily what you want for a given
use case.

The annotation interface of `merky` gives the user control over the tokenization of
a complex data structure.  In effect, the user annotates the data structure to instruct
`merky` on which portions should be tokenized.

Using the `merky.AnnotationTransformer`:
* All structures convert to their canonical forms.
* The top-level structure passed to `transform()` is always tokenized.
* Nested structures are only tokenized if they have a `__merky__` attribute with a
  truthy value.

The `merky.annotate` helper can wrap any arbitrary structure such that the
`__merky__` truth requirement is met, causing the `AnnotationTransformer` to tokenize
that wrapped structure.

### Example annotated transformations

Riffing further on our earlier transformation example, suppose now that we use
annotation.  While the top structure passed to `transform()` will always be
tokenized, only the annotated contents are subject to tokenization.

```python
import merky
import six

# The inner tuple is annotated, but the inner dict is not.
with_list = {
    "first": merky.annotate(("a", "b", "c")),
    "second": {"first": "1st!", "second": "2nd!"}
}

# The inner dict is annotated, but the inner tuple is not.
with_dict = {
    "first": ("a", "b", "c"),
    "second": merky.annotate({"first": "1st!", "second": "2nd!"})
}

transformer = merky.AnnotationTransformer()

# Here we expect the tuple to be tokenized and the sibling dict to not be.
t = transformer.transform(with_list)

# The tuple, canonicalized to list as before.  Note the identical hash value.
# ('e13460afb1e68af030bb9bee8344c274494661fa', ['a', 'b', 'c']
six.print_(next(t))

# The top dict, w/ tuple replaced by token but inner dict merely canonicalized.
# ('cfbe067935615515ba69aecc60c1cdd64e1cdc5d', OrderedDict([('first', 'e13460afb1e68af030bb9bee8344c274494661fa'), ('second', OrderedDict([('first', '1st!'), ('second', '2nd!')]))])) 
six.print_(next(t))

# Here we expect the tuple to be canonicalized and the sibling dict to be tokenized.
t = transformer.transform(with_dict)

# The inner dict, canonicalized to OrderedDict as in the original example.
# ('555cf5554cbd46144bd01851ebb278d32d4dc538', OrderedDict([('first', '1st!'), ('second', '2nd!')]))
six.print_(next(t))

# The top dict, w/ dict replaced by token but inner tuple merely canonicalized.
# ('3f9970218863154d777983ca60bfd3d3318462fa', OrderedDict([('first', ['a', 'b', 'c']), ('second', '555cf5554cbd46144bd01851ebb278d32d4dc538')]))
six.print_(next(t))
```

Thus the user can control the manner in which a given data structure is transformed.

# Use-case classes

## Attribute graph

Suppose you have a hierarchy of things, where each node has (in addition to its children) attributes of its own.

The `merky.cases.attrgraph.AttributeGraph` class provides a data structure for this that, in combination with the
`merky.AnnotationTransformer`:
* Defines the tokenized form of a node as the combination of its attributes token and its members/children token.
* Defines its attributes token as the annotated transformation of an `attrs` dictionary (the dictionary will be
  canonicalized but its members are not).
* Defines its members token as the annotated transformation of a `members` dictionary, the values of which are
  each annotated as well.

If a user uses the `AttributeGraph` for all nodes in the hierarchy, then `AttributeGraph` via the
`AnnotationTransformer` can go back and forth between tokenized form and object form.

The separation of node attributes from membership (graph edges) within the structure means that:
* A child's tokenized form is unaffected by the properties of its parent or container.
* The parent or container's tokenized form *is* affected by the properties of its members/children.

See `merky.cases.attrgraph.AttributeGraph` for more.

## Simple map

The `merky.cases.tokendict.TokenDict` class provides what is probably the most obvious basic
use of `merky` functionality, and perhaps one of the more natural data structures when thinking
of a hash tree.  Namely: a dictionary that ensures its values will be annotated when used with
the `merky.AnnotationTransformer`.

Some example uses of this:
* A traditional hash tree, where you want to identify which portions of two dicts are different
  without exchanging/comparing the entire data structures.
* A keyed collection of objects that you want to ensure receive tokenization, where the keys
  serve merely as identifiers and do not convey any additional meaning.
* A version history for a given structure, in which each key represents a version marker
  (a tag, a timestamp, a simple incremented number, whatever) and the value is the state for
  the structure as of that version.

See `merky.cases.tokendict.TokenDict` for more.

## Walker

You can explore a transformed structure to walk the tokens and associated structures
as a graph using the `merky.cases.walker.Walker` class.  Refer to its docs for more.

# Storage options

Complex storage options are outside the scope of `merky`.  However, for convenience, `merky
does provide some minimal storage options that can serve for some cases.

An arbitrary transformed structure can be stored/restored using various classes found in the
`merky.store.structure` module.  For instance:

```python
# Suppose this gives me some `merky.cases.attrgraph.AttributeGraph` instance.
g = get_my_graph()

# Now I'm going to store it a file.
transformed = merky.AnnotationTransformer().transform(g)

# Get a JSON file writer for the path 'my-graph.json'
store = merky.store.structure.JSONFileWriteStructure('my-graph.json')

# Populate the writer with the transformed data.
store.populate(transformed)

# Write the file.
store.close()
```

Now later you want to restore it.  Like so:

```python
# Get the reader.
store = merky.store.structure.JSONFileReadStructure('my-graph.json')

# And away we go.
g = merky.cases.attrgraph.AttributeGraph.from_token(store.head, store.get)
```

For a more complex example, see `merky.test.misc.graph_storage_test`, which
assembles a `TokenDict` of `AttributeGraphs`, writes to JSON, then restores from JSON.

# Don't wear a tie.

It's an anachronistic absurdity that needs to be abolished.  Direct your respect elsewhere.

## Nor a suit.

Even more so.
