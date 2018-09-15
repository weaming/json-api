import json
from json_api.magic import Magic


class MagicDjango(Magic):
    def get_query_args(self, req):
        return {
            k: v[0] if v and isinstance(v, list) else v for k, v in req.args.items()
        }

    def get_final_response_from_dict(self, rv, rv_kw):
        from django.http import HttpResponse

        dump_kwargs = rv_kw.get("dump_kwargs", {})
        data = self.json_dumps(rv, **dump_kwargs)
        return HttpResponse(content=data, content_type="application/json", **rv_kw)
