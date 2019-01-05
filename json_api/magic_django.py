import json
from .magic import DefaultMagic
from .errors import ExceptionWithStatusCode


class MagicDjango(DefaultMagic):
    from django.core.serializers.json import DjangoJSONEncoder

    encoder = DjangoJSONEncoder

    def get_query_args(self, request):
        return {
            k: v[0] if v and isinstance(v, list) and len(v) <= 1 else v
            for k, v in request.GET.items()
        }

    def get_request_json(self, request):
        try:
            return json.loads(request.body)
        except Exception as e:
            raise ExceptionWithStatusCode(str(e), status=400)

    def get_final_response_from_dict(self, rv, rv_kw):
        from django.http import JsonResponse

        _kw = dict(json_dumps_params={"ensure_ascii": False})
        _kw.update(rv_kw or {})
        headers = _kw.pop("headers", {})
        response = JsonResponse(rv, encoder=self.encoder, **_kw)
        response["Content-Type"] += "; charset=UTF-8"
        for k, v in headers.items():
            response[k] = v
        return response
