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
    KafkaConnectionError,
    KafkaTimeoutError,
    LeaderNotAvailableError,
    NotLeaderForPartitionError,
    OperationalError,
    InterfaceError,
    ConnectionError,
    TimeoutError,
    OSError,
)

NON_RETRYABLE_ERRORS: tuple[type[Exception], ...] = (
    MessageSizeTooLargeError,
    UnknownTopicOrPartitionError,
    IntegrityError,
    ProgrammingError,
    DataError,
    JSONDecodeError,
    UnicodeDecodeError,
    ValidationError,
    ValueError,
    KeyError,
    JSONDecodeError,
)
