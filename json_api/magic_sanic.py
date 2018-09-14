from .magic import Magic


class MagicSanic(Magic):
    def init(self):
        self.handler_is_async = True

    def set_app(self, app):
        self.app = app

    def add_route(self, pattern, handler_fn, middleware_list=None, **kwargs):
        self.app.route(pattern, **kwargs)(
            self.json_api(handler_fn, middleware_list=middleware_list)
        )

    def get_final_response_from_dict(self, rv, rv_kw):
        from sanic.response import json

        return json(rv, **rv_kw)
