class BaseAPIError(Exception):
    pass

class NotFoundError(BaseAPIError):
    pass

class AlreadyExistsError(BaseAPIError):
    pass

class ForbiddenError(BaseAPIError):
    pass

class BadRequestError(BaseAPIError):
    pass

