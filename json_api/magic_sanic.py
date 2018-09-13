from .magic import Magic


class MgaicSanic(Magic):
    def init(self):
        self.handler_is_async = True

    def set_app(self, app):
        self.app = app

    def add_route(self, pattern, handler_fn, **kwargs):
        self.app.route(pattern, **kwargs)(handler_fn)

    def get_final_response_from_dict(self, rv, rv_kw):
        from sanic.response import json

        return json(rv, **rv_kw)
