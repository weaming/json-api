from json import dumps
from functools import partial
from .magic import DefaultMagic
from .errors import ExceptionWithStatusCode


json_dumps = partial(dumps, separators=(",", ":"), ensure_ascii=False)


class MagicSanic(DefaultMagic):
    def post_init(self):
        self.handler_is_async = True
        self.add_repo_in_headers = True

    def set_app(self, app):
        self.app = app

    def get_query_args(self, request):
        return {
            k: v[0] if v and isinstance(v, list) else v for k, v in request.args.items()
        }

    def get_request_json(self, request):
        try:
            return request.json
        except Exception as e:
            raise ExceptionWithStatusCode(str(e), status=400)

    def add_route(self, pattern, handler_fn, middleware_list=None, **kwargs):
        self.app.route(pattern, **kwargs)(
            self.json_api(handler_fn, middleware_list=middleware_list)
        )

    def get_final_response_from_dict(self, rv, rv_kw):
        from sanic.response import json

        return json(rv, dumps=json_dumps, **rv_kw)
