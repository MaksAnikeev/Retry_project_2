import json
from typing import Any, Sequence

from pydantic import BaseModel

from src.schemas.kafka_schemas import BaseKafkaHeadersSchema


def payload_to_bytes(payload: BaseModel) -> bytes:
    return payload.model_dump_json().encode("utf-8")


def headers_to_kafka_format(headers: BaseKafkaHeadersSchema | None) -> list[tuple[str, bytes]] | None:
    if headers is None:
        return None
    return headers.to_kafka_format()


def decode_key(key: bytes | None) -> str | None:
    if key is None:
        return None
    return key.decode("utf-8")


def to_headers_dict(
    headers: Sequence[tuple[str, bytes]] | None,
) -> dict[str, str]:
    if headers is None:
        return {}

    result: dict[str, str] = {}
    for key, value in headers:
        if value is None:
            result[key] = ""
        elif isinstance(value, bytes):
            try:
                result[key] = value.decode("utf-8")
            except UnicodeDecodeError:
                result[key] = value.hex()
        else:
            result[key] = str(value)

    return result


def to_payload_dict(value: Any) -> dict[str, Any]:
    if value is None:
        return {"raw": None}
    if isinstance(value, bytes):
        try:
            decoded = value.decode("utf-8")
        except UnicodeDecodeError:
            return {"raw_bytes": value.hex()}
        try:
            return json.loads(decoded)
        except json.JSONDecodeError:
            return {"raw": decoded}
    if isinstance(value, dict):
        return value
    return {"raw": str(value)}
