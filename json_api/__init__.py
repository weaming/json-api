try:
    import sanic
    from .magic_sanic import MagicSanic
except ImportError:
    pass

try:
    import django
    from .magic_django import MagicDjango
except ImportError:
    pass
