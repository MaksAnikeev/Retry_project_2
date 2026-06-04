from .base import BaseDomainException

class ObjectNotFoundException(BaseDomainException):
    http_status_code = 404
    error_code = "OBJECT_NOT_FOUND"
    detail = "Object not found"

class ReportNotFoundException(BaseDomainException):
    http_status_code = 404
    error_code = "REPORT_NOT_FOUND"
    detail = "Report not found"
