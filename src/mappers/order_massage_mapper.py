import json
from datetime import UTC, datetime

from aiokafka.structs import ConsumerRecord

from src.mappers.kafka_mapper import to_headers_dict, to_payload_dict
from src.schemas.dql_schemas import DqlErrorSchema
from src.schemas.order_dql_schemas import DqlOrderMessageSchema
from src.schemas.order_incoming_schemas import OrderPayloadSchema, IncomingOrderHeadersSchema


def to_dql_error_schema(
    error: Exception,
    is_retryable: bool,
) -> DqlErrorSchema:
    return DqlErrorSchema(
        message=f"{type(error).__name__}: {str(error)}",
        is_retryable=is_retryable,
        timestamp=datetime.now(UTC),
    )


def to_order_dql_message(
    record: ConsumerRecord,
    error: Exception,
    is_retryable: bool,
) -> DqlOrderMessageSchema:
    partition_key = (
        record.key.decode("utf-8")
        if isinstance(record.key, bytes)
        else (record.key if record.key is not None else "")
    )
    return DqlOrderMessageSchema(
        original_topic=record.topic,
        original_payload=to_payload_dict(record.value),
        original_headers=to_headers_dict(list(record.headers)),
        original_partition_key=partition_key,
        original_offset=record.offset,
        error=to_dql_error_schema(error, is_retryable),
    )


def to_order_payload_schema(value: bytes) -> OrderPayloadSchema:
    payload_dict = json.loads(value.decode("utf-8"))
    return OrderPayloadSchema.model_validate(payload_dict)


def to_order_headers_schema(
    kafka_headers: list[tuple[str, bytes]] | None,
    retry_count: int | None = None,
) -> IncomingOrderHeadersSchema:
    headers_dict = to_headers_dict(kafka_headers)
    if retry_count is not None:
        headers_dict["retry_count"] = str(retry_count)
    return IncomingOrderHeadersSchema.model_validate(headers_dict)
