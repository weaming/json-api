import json
from .magic import DefaultMagic
from .errors import ExceptionWithStatusCode


class MagicDjango(DefaultMagic):
    def get_query_args(self, request):
        return {
            k: v[0] if v and isinstance(v, list) else v for k, v in request.args.items()
        }

    def get_request_json(self, request):
        try:
            return json.loads(request.body)
        except Exception as e:
            raise ExceptionWithStatusCode(str(e), status=400)

    def get_final_response_from_dict(self, rv, rv_kw):
        from django.http import HttpResponse

        dump_kwargs = rv_kw.get("dump_kwargs", {})
        data = self.json_dumps(rv, **dump_kwargs)
        return HttpResponse(content=data, content_type="application/json", **rv_kw)
