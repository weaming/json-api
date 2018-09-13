def check_middlewares(middlewares, req):
    for md in middlewares:
        md(req)
