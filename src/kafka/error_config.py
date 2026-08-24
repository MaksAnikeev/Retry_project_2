from json import JSONDecodeError

from aiokafka.errors import (
    KafkaConnectionError,
    KafkaTimeoutError,
    LeaderNotAvailableError,
    NotLeaderForPartitionError,
    MessageSizeTooLargeError,
    UnknownTopicOrPartitionError,
)
from pydantic import ValidationError
from sqlalchemy.exc import (
    OperationalError,
    InterfaceError,
    IntegrityError,
    ProgrammingError,
    DataError,
)

RETRYABLE_ERRORS: tuple[type[Exception], ...] = (
    # Kafka
    KafkaConnectionError,
    KafkaTimeoutError,
    LeaderNotAvailableError,
    NotLeaderForPartitionError,
    # БД
    OperationalError,
    InterfaceError,
    # Сеть
    ConnectionError,
    TimeoutError,
    OSError,
)

NON_RETRYABLE_ERRORS: tuple[type[Exception], ...] = (
    # Kafka
    MessageSizeTooLargeError,
    UnknownTopicOrPartitionError,
    # БД
    IntegrityError,
    ProgrammingError,
    DataError,
    # Данные
    JSONDecodeError,
    UnicodeDecodeError,
    # Валидация
    ValidationError,
    ValueError,
    KeyError,
    JSONDecodeError,
)
