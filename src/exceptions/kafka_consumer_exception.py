from src.exceptions.base_kafka_exception import BaseKafkaException


class KafkaConsumerNotStartedError(BaseKafkaException):
    error_code = "KAFKA_CONSUMER_NOT_STARTED"
    detail = "Kafka consumer is not started. Call start() or use lifespan context manager."