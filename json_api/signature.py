import inspect
from collections import OrderedDict
from .errors import APIBaseException


def get_signature(fn):
    # python 3.5+
    params = inspect.signature(fn).parameters
    args = []
    kwargs = OrderedDict()
    varkw = None
    for p in params.values():
        t = str(p.kind)
        if p.default is p.empty:
            if t == 'VAR_POSITIONAL':
                raise APIBaseException(f'does not support signature auto anaylysis of *{p.name}')
            if t == 'VAR_KEYWORD':
                varkw = p.name
            else:
                args.append(p.name)
        else:
            kwargs[p.name] = p.default
    return args, kwargs, varkw


def test_get_sinature():
    def fn(a, b, c, d=3, e="abc", **kw):
        pass

    assert get_signature(fn) == (
        ["a", "b", "c"], OrderedDict([("d", 3), ("e", "abc")]), 'kw'
    )


test_get_sinature()
