from functools import partial
from .validate import valida_request_query, MissingQueryException
from .signature import get_signature


class Magic(object):
    def __init__(self, **kwargs):
        self.first_argument_is_request = True
        self.handler_is_async = False

        self.server_name = "JSON API"
        self.add_repo_in_headers = True
        self.gh_repo = "https://github.com/weaming/json-api"

        for k, v in kwargs.items():
            setattr(self, k, v)

        # method to do custom
        self.init()

    def init(self):
        pass

    def new_kw_from_response_status(self, status):
        return {"status": status}

    def set_default_headers(self, rv_kw):
        headers = rv_kw.setdefault("headers", {})
        headers.update({"X-Served-By": self.server_name})
        headers.update({"Access-Control-Allow-Origin": "*"})
        if self.add_repo_in_headers:
            headers.update({"X-Server-Repo": self.gh_repo})
        return rv_kw

    def get_status_code_from_second_return_value(self, second):
        if second is None:
            return 200

        if isinstance(second, int):
            return second

        if isinstance(second, dict):
            if "status" in second:
                return second["status"]
            else:
                return self.get_status_code_from_second_return_dict(second)

        raise NotImplemented(
            "can not handle second value: {}, type {}".format(second, type(second))
        )

    def get_status_code_from_second_return_dict(self, second):
        raise NotImplemented(
            "please overwrite get_status_code_from_second_return_dict() to handle second response dict"
        )

    def post_process_return_dict(self, data, rv_kw):
        if data is None:
            return

        if isinstance(data, dict):
            if "success" not in data:
                data["success"] = True if rv_kw.get("status", 200) < 400 else False

    def get_final_response_from_dict(self, rv, rv_kw):
        raise NotImplemented

    def check_return(self, rv):
        """
        :param rv: the return value of handle functions
        """
        if isinstance(rv, tuple):
            rv, status = rv[0], rv[1]
            if isinstance(status, dict):
                # return kw dict directly
                rv_kw = status
            elif isinstance(status, int):
                # overwrite this method to create kw dict from status returned
                rv_kw = self.new_kw_from_response_status(status)
            else:
                raise Exception(
                    "unaccepted second return value: {}, type: {}".format(
                        status, type(status)
                    )
                )
        else:
            rv_kw = {}

        rv_kw = self.set_default_headers(rv_kw)

        if isinstance(rv, dict):
            return self.get_final_response_from_dict(
                self.post_process_return_dict(rv), rv_kw
            )
        else:
            # if not dict, return the return value directly
            return rv

    def get_handler_parameters(args, kwargs):
        if self.first_argument_is_request:
            # shift the request instance
            return args[1:], kwargs
        else:
            return args, kwargs

    def error_return_dict(self, exception, status):
        return {
            "success": False,
            "reason": exception,
            "type": str(type(exception)),
            "status": status,
        }

    def json_api(self, fn):
        args, kwargs = get_signature(fn)
        args, kwargs = self.get_handler_parameters(args, kwargs)

        if self.handler_is_async:

            async def new_fn(req):
                try:
                    q_args, q_kwargs = valida_request_query(req, *args, **kwargs)
                except MissingQueryException as e:
                    status = 400
                    rv = (self.error_return_dict(e, status), status)
                    return check_return(rv)

                try:
                    rv = await fn(req, *q_args, **q_kwargs)
                except Exception as e:
                    status = 500
                    rv = (self.error_return_dict(e, status), status)

                return check_return(rv)

        else:

            def new_fn(req):
                try:
                    q_args, q_kwargs = valida_request_query(req, *args, **kwargs)
                except MissingQueryException as e:
                    status = 400
                    rv = (self.error_return_dict(e, status), status)
                    return check_return(rv)

                try:
                    rv = fn(req, *q_args, **q_kwargs)
                except Exception as e:
                    status = 500
                    rv = (self.error_return_dict(e, status), status)

                return check_return(rv)

        return new_fn

    def add_route(self, pattern, handler_fn, **kwargs):
        raise NotImplemented("not implemented for add_route")
