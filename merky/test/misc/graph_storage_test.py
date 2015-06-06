import os
import tempfile
import shutil

from nose import tools

import merky
from merky.cases import attrgraph
from merky.cases import tokendict
from merky.store import structure

def tempdir(func):
    def wrapper(*p, **kw):
        dir_ = tempfile.mkdtemp()
        try:
            return func(*(p + (dir_,)), **kw)
        finally:
            shutil.rmtree(dir_)
    wrapper.__name__ = func.__name__
    return wrapper


def dag(attrs, members):
    return attrgraph.AttributeGraph(attrs=attrs, members=members)

def getpath(reader, *keys):
    current = reader.get(reader.head)
    for key in keys:
        current = reader.get(current[key])
    return current

@tempdir
def test_versioned_graph_save_and_restore(workdir):
    path = os.path.join(workdir, 'my-graph.json')
    static = dag({"unchanging": "eternal"}, {})

    graph_s0 = dag({"name": "graph", "version": 0}, {
                    "static": static,
                    "changing": dag({"a": "A"}, {}),
                    "removed": dag({"bleep": "blorp"}, {}),
                })

    graph_s1 = dag({"name": "graph", "version": 1}, {
                    "static": static,
                    "changing": dag({"b": "B"}, {}),
                })
    
    version_map = tokendict.TokenDict({"v0": graph_s0,
                                       "v1": graph_s0,
                                       "v2": graph_s1,
                                       "v3": graph_s1})

    transformer = merky.AnnotationTransformer()
    writer = structure.JSONFileWriteStructure(path)
    writer.populate(transformer.transform(version_map))
    writer.close()

    reader = structure.JSONFileReadStructure(path)
    tokens = tokendict.TokenDict.from_token(reader.head, reader.get)

    tools.assert_equal(["v0", "v1", "v2", "v3"], list(tokens.keys()))

    # Same states get same tokens.
    tools.assert_equal(tokens.dict_["v0"], tokens.dict_["v1"])
    tools.assert_equal(tokens.dict_["v2"], tokens.dict_["v3"])
    tools.assert_equal(getpath(reader, "v0", 1, "static"),
                       getpath(reader, "v2", 1, "static"))

    # Different states, different tokens.
    tools.assert_not_equal(tokens.dict_["v1"], tokens.dict_["v2"])
    tools.assert_not_equal(getpath(reader, "v0", 1, "changing"),
                           getpath(reader, "v2", 1, "changing"))


    restored = tokendict.TokenDict.from_token(
        reader.head,
        reader.get,
        attrgraph.AttributeGraph.from_token
    )

    tools.assert_equal(["v0", "v1", "v2", "v3"],
                        list(restored.keys()))

    tools.assert_equal(dict(graph_s0.attrs), dict(restored["v0"].attrs))
    tools.assert_equal(dict(graph_s1.attrs), dict(restored["v2"].attrs))
    tools.assert_equal(["changing", "removed", "static"],
                        list(sorted(restored["v0"].members.keys())))
    tools.assert_equal(["changing", "static"],
                        list(sorted(restored["v2"].members.keys())))
    tools.assert_equal(dict(graph_s0.members["changing"].attrs),
                        dict(restored["v1"].members["changing"].attrs))
    tools.assert_equal(dict(graph_s1.members["changing"].attrs),
                        dict(restored["v3"].members["changing"].attrs))
    tools.assert_equal(dict(restored["v0"].members["static"].attrs),
                        dict(restored["v3"].members["static"].attrs))

