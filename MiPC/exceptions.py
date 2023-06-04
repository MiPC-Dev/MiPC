import warnings

class MiPCException(Exception):
    pass


class MisskeyAPIException(MiPCException):
    pass


class MisskeyMiAuthFailedException(MiPCException):
    pass