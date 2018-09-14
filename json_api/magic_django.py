import json
from json_api.magic import Magic


class MagicDjango(Magic):
    def get_final_response_from_dict(self, rv, rv_kw):
        from django.http import HttpResponse

        json_kwargs = rv_kw.get("json_kwargs", {})
        json_kwargs.update(ensure_ascii=False)
        data = json.dumps(rv, **json_kwargs)
        return HttpResponse(content=data, content_type="application/json", **rv_kw)
