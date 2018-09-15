class APIBaseException(Exception):
    pass


class ExceptionWithStatusCode(APIBaseException):
    def __init__(self, *args, status=500, **kwargs):
        Exception.__init__(self, *args, **kwargs)
        self.status = status


class MissingRequestDataException(ExceptionWithStatusCode):
    pass


class MissingQueryException(MissingRequestDataException):
    pass


class MissingBodyDataException(MissingRequestDataException):
    pass
