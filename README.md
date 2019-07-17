# JSON API

Make you focus on writting business logic code, just return dict data for API, or other Response directly.

What you need to do is inherit the Magic class and overwrite several methods, then use method it provides to add route to your framework app.

The key point is it's api `magic.json_api(view_func)` wraps your logic code, then check the request data and reponse data.

```
pip3 install json-api
```

## Usage Examples
### Sanic Framework

```
import os
from sanic import Sanic

from json_api.magic_sanic import MagicSanic

magic = MagicSanic()
app = Sanic()
magic.set_app(app)


async def index(request, name="world"):
    return {"hello": name}


async def register(request, name, email, password):
    password = password or generate_random_password()
    user = new_user(name, email, password)
    return user.to_dict()

async def get_user_information(request, name):
    user = get_user_by_name(name)
    if not user:
        return {'reason': 'not found'}, 404
    return user.to_dict()


magic.add_route("/", index)
magic.add_route("/api/user/register", register, methods=["POST"])
magic.add_route("/api/user/info", get_user_information)


if __name__ == "__main__":
    debug = bool(os.getenv("DEBUG"))
    app.run(host="0.0.0.0", port=8000, debug=debug)
```

### Django Example

```
from json_api.magic_django import MagicDjango
from .utils import JSONEncoder

magic = MagicDjango()
magic.encoder = JSONEncoder

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include([
        path('translate', magic.json_api(trans))
    ]))
]
```
