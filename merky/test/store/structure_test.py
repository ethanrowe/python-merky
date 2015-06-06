import codecs
import collections
import os
import tempfile
import shutil
from nose import tools
from six.moves import StringIO
from .. import words
from merky.store import structure

def od(*p, **kw):
    return collections.OrderedDict(*p, **kw)

class TestInMemoryStructure(object):

    HEAD_TOKEN = 'sometoptoken'
    LIST_TOKEN = 'somelisttoken'
    DICT_TOKEN = 'somedicttoken'
    HEAD = od((('a', 'somelisttoken'), ('b', 'somedicttoken')))
    DICT = od(((words.EUROS, words.SHEKELS), (words.EPEES, words.ANGSTROM)))
    LIST = ["some", "list", words.SHEKELS]

    PAIRS = (
            (LIST_TOKEN, LIST),
            (DICT_TOKEN, DICT),
            (HEAD_TOKEN, HEAD),
        )


    def get_read_store(self):
        return structure.InMemoryStructure(od(self.PAIRS), self.HEAD_TOKEN)

    
    def get_write_store(self):
        return structure.InMemoryStructure()


    def verify_dict(self, received, expect):
        tools.assert_equal(expect, received)


    def verify_list(self, received, expect):
        tools.assert_equal(expect, received)


    def verify_head(self, store, head):
        tools.assert_equal(head, store.head)


    def verify_write(self, store, head):
        # In-memory guy has same state before and after close() call.
        tools.assert_equal(od(self.PAIRS), store.tokenmap)
        store.close()
        tools.assert_equal(head, store.head)
        tools.assert_equal(od(self.PAIRS), store.tokenmap)


    def test_head_from_last_by_default(self):
        store = self.get_write_store()
        store.populate(iter(self.PAIRS))
        self.verify_head(store, self.HEAD_TOKEN)
        self.verify_write(store, self.HEAD_TOKEN)


    def test_overriddable_head(self):
        store = self.get_write_store()
        store.populate(iter(self.PAIRS))
        store.head = self.DICT_TOKEN
        self.verify_head(store, self.DICT_TOKEN)
        self.verify_write(store, self.DICT_TOKEN)


    def test_read_operations(self):
        store = self.get_read_store()
        self.verify_head(store, self.HEAD_TOKEN)
        self.verify_dict(store.get(self.HEAD_TOKEN), self.HEAD)
        self.verify_dict(store[self.HEAD_TOKEN], self.HEAD)
        self.verify_list(store.get(self.LIST_TOKEN), self.LIST)
        self.verify_list(store[self.LIST_TOKEN], self.LIST)
        self.verify_dict(store.get(self.DICT_TOKEN), self.DICT)
        self.verify_dict(store[self.DICT_TOKEN], self.DICT)
        tools.assert_equal(None, store.get('no no no'))
        tools.assert_raises(KeyError, lambda: store['no no no'])


q = lambda word: words.unify('"', word, '"')
def commify(*w):
    terms = []
    for word in w[:-1]:
        terms.append(word)
        terms.append(',')
    if len(w) > 0:
        terms.append(w[-1])
    return words.unify(*terms)

jl = lambda *w: words.unify('[', commify(*w), ']')
def jd(*pairs):
    return words.unify('{',
                            commify(*(words.unify(k, ':', w)
                                      for k, w in pairs)),
                        '}')


class TestStreamStructure(TestInMemoryStructure):
    def json(self, head):
        return jl(
            jd(
                (q(self.LIST_TOKEN), jl(*(q(w) for w in self.LIST))),
                (q(self.DICT_TOKEN), jd(*((q(k), q(v)) for k,v in self.DICT.items()))),
                (q(self.HEAD_TOKEN), jd(*((q(k), q(v)) for k,v in self.HEAD.items()))),
            ),
            q(head),
        )
    
    def get_read_store(self):
        self.stream = StringIO(self.json(self.HEAD_TOKEN))
        return structure.JSONStreamReadStructure(self.stream)

    def get_write_store(self):
        self.stream = StringIO()
        return structure.JSONStreamWriteStructure(self.stream)

    def verify_dict(self, received, expect):
        tools.assert_equal(dict(expect), received)

    def verify_list(self, received, expect):
        tools.assert_equal(list(expect), received)

    def verify_write(self, store, head):
        # Nothing written to stream until close().
        tools.assert_equal(0, self.stream.tell())
        tools.assert_equal('', self.stream.read())
        store.close()
        self.stream.seek(0)
        tools.assert_equal(self.json(head), self.stream.read())

    def test_no_close(self):
        store = self.get_read_store()
        tools.assert_raises(AttributeError, getattr, store, 'close')


class TestFileStructure(TestStreamStructure):
    def setup(self):
        self.workdir = tempfile.mkdtemp()
        self.path = os.path.join(self.workdir, "some-file.json")
    
    def teardown(self):
        shutil.rmtree(self.workdir)

    def get_read_store(self):
        with codecs.open(self.path, mode="wb", encoding="utf-8") as f:
            f.write(self.json(self.HEAD_TOKEN))
        return structure.JSONFileReadStructure(self.path)
            
    def get_write_store(self):
        return structure.JSONFileWriteStructure(self.path)

    def verify_write(self, store, head):
        # File doesn't even exist before close.
        tools.assert_false(os.path.exists(self.path))
        # But it will after close()
        store.close()
        tools.assert_true(os.path.exists(self.path))
        with codecs.open(self.path, mode='rb', encoding='utf-8') as f:
            tools.assert_equal(self.json(head), f.read())

