class APIBaseException(Exception):
    pass


class ExceptionWithStatusCode(APIBaseException):
    def __init__(self, *args, status=500, **kwargs):
        Exception.__init__(self, *args, **kwargs)
        self.status = status


class MissingQueryException(ExceptionWithStatusCode):
    pass
