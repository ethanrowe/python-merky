from nose import tools

from .. import samples
from merky.cases import attrgraph
from merky import transformer
from merky import util

def dag(attrs=None, members=None):
    return attrgraph.AttributeGraph(attrs, members)

def transform(subject):
    return transformer.AnnotationTransformer().transform(subject)

t = transform

def a(t):
    return util.annotate(t)

def accum_assert(expected, iterable):
    i = iter(iterable)
    accum = []
    for expect in expected:
        try:
            received = next(i)
            tools.assert_equal(expect, received)
            accum.append(received)
        except StopIteration:
            raise StopIteration("Expected: %s", repr(expect))
    tools.assert_raises(StopIteration, next, i)
    return accum

aa = accum_assert

def test_attributes_only():
    g = dag(attrs=samples.D_A_NATURAL)
    aa([(samples.D_A_TOKENS.token, samples.D_A_ORDERED),
        (samples.L_D_A_TOKENS.token, samples.L_D_A_TOKENS.member)],
        t(g))


def test_annotation():
    # This verifies that the attribute graph itself is "annotated" by default.
    g = [dag(attrs=samples.D_B_NATURAL)]
    i = iter(t(g))
    tools.assert_equal((samples.D_B_TOKENS.token, samples.D_B_ORDERED), next(i))
    # We're ignoring the hash of the list, just verifying that it exploded things out.
    graph = next(i)
    tools.assert_equal([samples.D_B_TOKENS.token], graph[1])
    # Again, don't care about hash, only that it references the previous
    tools.assert_equal([graph[0]], next(i)[1])
    # That's all, folks!
    tools.assert_raises(StopIteration, next, i)


def test_nested_attributes():
    g = dag(attrs=samples.D_A_IN_B_NATURAL)
    aa([(samples.D_A_IN_B_TOKENS.token, samples.D_A_IN_B_ORDERED), # Doesn't recurse attrs
         (samples.L_D_A_IN_B_TOKENS.token, samples.L_D_A_IN_B_TOKENS.member)],
        t(g))


def test_with_kids():
    nat = samples.L_NEST_PARTIAL_NATURAL
    ord_ = samples.L_NEST_PARTIAL_ORDERED
    tok = samples.L_NEST_PARTIAL_TOKENS

    g = dag(attrs=nat[0],
            members={
                "bro": dag(attrs=nat[1]["bro"][0]),
                "sis": dag(attrs=nat[1]["sis"][0]),
                })

    r = aa(
            [
                (tok[0].token, ord_[0]), # top-level attrs
                (tok[1]["bro"][0].token, ord_[1]["bro"][0]), # bro attrs
                (tok[1]["bro"].token, tok[1]["bro"].member), # bro attr-only token list
                (tok[1]["sis"][0].token, ord_[1]["sis"][0]), # sis attrs
                (tok[1]["sis"].token, tok[1]["sis"].member), # sis attr-only token list
                (tok[1].token, tok[1].member), # top member token dict
                (tok.token, tok.member), # top attrs/members token list
            ],
            t(g))

def test_with_grandkids():
    n = samples.L_MULTI_NEST_PARTIAL_NATURAL
    o = samples.L_MULTI_NEST_PARTIAL_ORDERED
    t = samples.L_MULTI_NEST_PARTIAL_TOKENS

    g = dag(attrs=n[0],
            members={
                "1-0": dag(attrs=n[1]["1-0"][0],
                           members={
                               "2-0": dag(attrs=n[1]["1-0"][1]["2-0"][0]),
                               "2-1": dag(attrs=n[1]["1-0"][1]["2-1"][0]),
                               }),
                "1-1": dag(attrs=n[1]["1-1"][0],
                           members={
                               "2-0": dag(attrs=n[1]["1-1"][1]["2-0"][0]),
                               "2-1": dag(attrs=n[1]["1-1"][1]["2-1"][0]),
                               }),
                })

    r = aa(
        [
            (t[0].token, o[0]), # top attrs
            (t[1]["1-0"][0].token, o[1]["1-0"][0]), # 1-0 attrs
            (t[1]["1-0"][1]["2-0"][0].token, o[1]["1-0"][1]["2-0"][0]), # 1-0/2-0 attrs
            (t[1]["1-0"][1]["2-0"].token, t[1]["1-0"][1]["2-0"].member), # 1-0/2-0 attr-only token list
            (t[1]["1-0"][1]["2-1"][0].token, o[1]["1-0"][1]["2-1"][0]), # 1-0/2-1 attrs
            (t[1]["1-0"][1]["2-1"].token, t[1]["1-0"][1]["2-1"].member), # 1-0/2-1 attr-only token list
            (t[1]["1-0"][1].token, t[1]["1-0"][1].member), # 1-0 member token dict
            (t[1]["1-0"].token, t[1]["1-0"].member), # 1-0 attr/member token list
            (t[1]["1-1"][0].token, o[1]["1-1"][0]), # 1-1 attrs
            (t[1]["1-1"][1]["2-0"][0].token, o[1]["1-1"][1]["2-0"][0]), # 1-1/2-0 attrs
            (t[1]["1-1"][1]["2-0"].token, t[1]["1-1"][1]["2-0"].member), # 1-1/2-0 attr-only token list
            (t[1]["1-1"][1]["2-1"][0].token, o[1]["1-1"][1]["2-1"][0]), # 1-1/2-1 attrs
            (t[1]["1-1"][1]["2-1"].token, t[1]["1-1"][1]["2-1"].member), # 1-1/2-1 attr-only token list
            (t[1]["1-1"][1].token, t[1]["1-1"][1].member), # 1-1 member token dict
            (t[1]["1-1"].token, t[1]["1-1"].member), # 1-1 attr/member token list
            (t[1].token, t[1].member), # top member token dict
            (t.token, t.member), # top attr/member token list
        ],
        transform(g))


