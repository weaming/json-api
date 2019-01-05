import json
from .magic import DefaultMagic
from .errors import ExceptionWithStatusCode


class MagicDjango(DefaultMagic):
    from django.core.serializers.json import DjangoJSONEncoder

    encoder = DjangoJSONEncoder

    def get_query_args(self, request):
        rv = {}
        for k in request.GET.keys():
            v: list = request.GET.getlist(k)
            if len(v) <= 1:
                v = v[0]
            rv[k] = v
        return rv

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
