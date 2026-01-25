from domain.exceptions import CustomException


class NotFoundException(CustomException):
    pass


class AlreadyExistsException(CustomException):
    pass


class PermissionDenied(CustomException):
    pass
