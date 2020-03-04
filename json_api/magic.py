import json
from functools import wraps
import traceback

from .validate import validate_request_query
from .signature import get_signature
from .middleware import check_middleware_list
from .errors import MissingRequestDataException


class Magic(object):
    def __init__(self, **kwargs):
        self.first_argument_is_request = True
        self.handler_is_async = False

        self.pre_init()

        for k, v in kwargs.items():
            setattr(self, k, v)

        self.post_init()

    def pre_init(self):
        pass

    def post_init(self):
        pass

    def get_status_code_from_second_return_value(self, second):
        # blank dict or None
        if not second:
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

    def post_process_return_dict(self, data, rv_kw):
        if data is None:
            return

        if isinstance(data, dict):
            if "success" not in data:
                data["success"] = (
                    True
                    if self.get_status_code_from_second_return_value(rv_kw) < 400
                    else False
                )
        return data

    def check_return(self, rv):
        """
        :param rv: the return value of handle functions
        """
        if isinstance(rv, tuple):
            rv, second = rv[0], rv[1]
            if isinstance(second, dict):
                # return kw dict directly
                rv_kw = second
            elif isinstance(second, int):
                # overwrite this method to create kw dict from status returned
                rv_kw = self.new_kw_from_response_status(second)
            else:
                raise Exception(
                    "unaccepted second return value: {}, type: {}".format(
                        second, type(second)
                    )
                )
        else:
            rv_kw = {}

        if isinstance(rv, dict):
            rv = self.post_process_return_dict(rv, rv_kw)
            rv_kw = self.set_default_headers(rv_kw)
            return self.get_final_response_from_dict(rv, rv_kw)
        else:
            # if not dict, return the return value directly
            return rv

    def get_handler_parameters(self, args, kwargs):
        if self.first_argument_is_request:
            # shift the request instance
            return args[1:], kwargs
        else:
            return args, kwargs

    def json_api(self, fn, middleware_list=None):
        """
        :return: return a handler function accept the `request` object as positional argument
        """
        args, kwargs, kwname = get_signature(fn)
        args, kwargs = self.get_handler_parameters(args, kwargs)

        if self.handler_is_async:

            @wraps(fn)
            async def new_fn(request):
                try:
                    q_args, q_kwargs, kwvars = validate_request_query(
                        self.get_handler_arguments(request), kwname, *args, **kwargs
                    )
                except MissingRequestDataException as e:
                    status = getattr(e, "status", 400)
                    rv = (self.error_return_dict(e, status), status)
                    return self.check_return(rv)

                try:
                    check_middleware_list(middleware_list or [], request)
                except Exception as e:
                    status = getattr(e, "status", 400)
                    rv = (self.error_return_dict(e, status), status)
                    return self.check_return(rv)

                try:
                    q_kwargs.update(kwvars)
                    rv = await fn(request, *q_args, **q_kwargs)
                except Exception as e:
                    traceback.print_exc()
                    status = getattr(e, "status", 500)
                    rv = (self.error_return_dict(e, status), status)

                return self.check_return(rv)

        else:

            @wraps(fn)
            def new_fn(request):
                try:
                    q_args, q_kwargs, kwvars = validate_request_query(
                        self.get_handler_arguments(request), kwname, *args, **kwargs
                    )
                except MissingRequestDataException as e:
                    status = getattr(e, "status", 400)
                    rv = (self.error_return_dict(e, status), status)
                    return self.check_return(rv)

                try:
                    check_middleware_list(middleware_list or [], request)
                except Exception as e:
                    status = getattr(e, "status", 400)
                    rv = (self.error_return_dict(e, status), status)
                    return self.check_return(rv)

                try:
                    q_kwargs.update(kwvars)
                    rv = fn(request, *q_args, **q_kwargs)
                except Exception as e:
                    status = getattr(e, "status", 500)
                    rv = (self.error_return_dict(e, status), status)

                return self.check_return(rv)

        return new_fn

    @staticmethod
    def json_dumps(data, **kwargs) -> str:
        kw = {"ensure_ascii": False}
        kw.update(**kwargs)
        return json.dumps(data, **kw)

    def get_handler_arguments(self, request) -> dict:
        if self.is_get(request):
            return self.get_query_args(request)
        elif self.is_post(request):
            return self.get_request_json(request)
        else:
            raise NotImplemented("not implemented for get_handler_arguments()")

    def new_kw_from_response_status(self, status) -> dict:
        raise NotImplemented("not implemented for new_kw_from_response_status()")

    def get_status_code_from_second_return_dict(self, second) -> int:
        raise NotImplemented(
            "not implemented for get_status_code_from_second_return_dict()"
        )

    @staticmethod
    def is_get(request) -> bool:
        raise NotImplemented("not implemented for is_get()")

    @staticmethod
    def is_post(request) -> bool:
        raise NotImplemented("not implemented for is_post()")

    def get_query_args(self, request) -> dict:
        raise NotImplemented("not implemented for get_query_args()")

    def get_request_json(self, request) -> dict:
        raise NotImplemented("not implemented for get_request_json()")

    def add_route(self, pattern, handler_fn, **kwargs):
        raise NotImplemented("not implemented for add_route()")

    def set_default_headers(self, rv_kw):
        raise NotImplemented("not implemented for set_default_headers()")

    def error_return_dict(self, exception, status):
        raise NotImplemented("not implemented for error_return_dict()")

    def get_final_response_from_dict(self, rv, rv_kw):
        raise NotImplemented("not implemented for get_final_response_from_dict()")


class DefaultMagic(Magic):
    def pre_init(self):
        self.server_name = "JSON API"
        self.add_repo_in_headers = False
        self.gh_repo = "https://github.com/weaming/json-api"

    @staticmethod
    def is_get(request):
        return request.method == "GET"

    @staticmethod
    def is_post(request):
        return request.method == "POST"

    def set_default_headers(self, rv_kw):
        headers = rv_kw.setdefault("headers", {})
        headers.update({"X-Served-By": self.server_name})
        headers.update({"Access-Control-Allow-Origin": "*"})
        if self.add_repo_in_headers:
            headers.update({"X-Server-Repo": self.gh_repo})
        return rv_kw

    def new_kw_from_response_status(self, status):
        return {"status": status}

    def error_return_dict(self, exception, status):
        return {
            "success": False,
            "reason": str(exception),
            "type": exception.__class__.__name__,
            "status": status,
        }
