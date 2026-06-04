from .base import BaseDomainException

class AlreadyExistsException(BaseDomainException):
    http_status_code = 409
    error_code = "ALREADY_EXISTS"
    detail = "Object already exists"

class ReportAlreadyExistsException(BaseDomainException):
    http_status_code = 409
    error_code = "REPORT_ALREADY_EXISTS"
    detail = "Report with this id already exists"
