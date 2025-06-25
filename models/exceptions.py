from fastapi import HTTPException


class RateLimited(Exception):
    def __init__(self, json, headers):
        self.json = json
        self.headers = headers
        self.message = json["message"]
        self.retry_after = json["retry_after"]
        super().__init__(self.message)


class BadRequest(HTTPException):
    def __init__(self, message: str = "Bad Request", status_code=400, *args):
        super().__init__(status_code, detail=message, *args)


class Forbidden(HTTPException):
    def __init__(
        self, message: str = "Insufficient Permissions", status_code=403, *args
    ):
        super().__init__(status_code, detail=message, *args)


class Unauthorized(HTTPException):
    def __init__(self, message: str = "Unauthorized", status_code=403, *args):
        super().__init__(status_code, detail=message, *args)


class NotFound(HTTPException):
    def __init__(self, message: str = "Object not found", status_code=404, *args):
        super().__init__(status_code, detail=message, *args)
