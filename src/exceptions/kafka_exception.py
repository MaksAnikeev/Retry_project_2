import http

from src.exceptions import BaseDomainException


class KafkaException(BaseDomainException):
    http_status_code = http.HTTPStatus.SERVICE_UNAVAILABLE
    error_code = "KAFKA_ERROR"
    detail = "Kafka service error"


class KafkaProducerNotStartedError(KafkaException):
    error_code = "KAFKA_PRODUCER_NOT_STARTED"
    detail = "Kafka producer is not started. Call start() or use lifespan context manager."

class KafkaSendError(KafkaException):
    error_code = "KAFKA_SEND_FAILED"
    detail = "Failed to send message to Kafka"