def check_middleware_list(middleware_list, req):
    for md in middleware_list:
        md(req)
