from .errors import MissingRequestDataException


def validate_request_query(request_args, kwname, *args, **kwargs):
    q_args = []
    q_kwargs = {}
    for k in args:
        if k not in request_args:
            raise MissingRequestDataException("missing {}".format(k), status=400)
        else:
            # only need the first
            q_args.append(request_args[k])

    for k, default in kwargs.items():
        # only need the first
        value = request_args.get(k, default)
        if isinstance(default, bool):
            value = bool(parse_boolean_value(value))
        elif isinstance(default, int):
            value = int(value)
        elif isinstance(default, float):
            value = float(value)

        q_kwargs[k] = value

    return (
        q_args,
        q_kwargs,
        {k: v for k, v in request_args.items() if k not in args and k not in kwargs},
    )


def parse_boolean_value(v):
    if not v:
        return None

    types = [float, int]
    for t in types:
        try:
            return t(v)
        except Exception:
            pass

    if v.lower() in ["false", "null", "nil", "none"]:
        return False
    elif v.lower() == "true":
        return True
    return v
