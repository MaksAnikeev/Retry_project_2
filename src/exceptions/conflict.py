import http

from .base import BaseDomainException

class AlreadyExistsException(BaseDomainException):
    http_status_code = http.HTTPStatus.CONFLICT
    error_code = "ALREADY_EXISTS"
    detail = "Object already exists"

class ReportAlreadyExistsException(BaseDomainException):
    http_status_code = http.HTTPStatus.CONFLICT
    error_code = "REPORT_ALREADY_EXISTS"
    detail = "Report with this id already exists"
