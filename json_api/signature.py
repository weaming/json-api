import inspect
from collections import OrderedDict


def get_signature(fn):
    # python 3.5+
    params = inspect.signature(fn).parameters
    args = []
    kwargs = OrderedDict()
    for p in params.values():
        if p.default is p.empty:
            args.append(p.name)
        else:
            kwargs[p.name] = p.default
    return args, kwargs


def test_sig():
    def fn(a, b, c, d=3, e="abc"):
        pass

    assert get_signature(fn) == (
        ["a", "b", "c"], OrderedDict([("d", 3), ("e", "abc")])
    )


test_sig()
