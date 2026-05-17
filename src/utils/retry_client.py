import logging
import random

from aiohttp import ClientConnectorError, ServerDisconnectedError, ClientConnectionError, ClientOSError
from asyncio import TimeoutError as AsyncTimeoutError
from tenacity import retry, stop_after_attempt, retry_if_exception_type, RetryCallState

logger = logging.getLogger(__name__)


def create_wait_exponential_with_jitter(
    min_wait: float = 2,
    max_wait: float = 60,
    jitter_percent: float = 0.25,
):
    """Фабрика функции задержки: экспонента + джиттер (%)"""

    def wait_exponential_with_jitter(retry_state: RetryCallState) -> float:
        exp = retry_state.attempt_number - 1
        base = 2 ** exp
        base = max(min_wait, min(base, max_wait))
        jitter = random.uniform(0, base * jitter_percent)
        return base + jitter

    return wait_exponential_with_jitter


def create_retry_decorator(
    max_attempts: int = 5,
    min_wait: float = 2,
    max_wait: float = 60,
    jitter_percent: float = 0.25,
):
    wait_func = create_wait_exponential_with_jitter(
        min_wait=min_wait,
        max_wait=max_wait,
        jitter_percent=jitter_percent,
    )

    return retry(
        stop=stop_after_attempt(max_attempts),
        wait=wait_func,
        retry=retry_if_exception_type((
            ConnectionError,
            TimeoutError,
            ClientConnectorError,  # Не может подключиться
            ClientConnectionError,  # Общее соединение
            ServerDisconnectedError,  # Сервер оборвал соединение
            AsyncTimeoutError,  # Таймаут asyncio
            ClientOSError,
            AsyncTimeoutError
        )),
        reraise=True,
        before_sleep=lambda rs: logger.warning(
            f"🔁 RETRY {rs.attempt_number}/{max_attempts} | "
            f"wait={rs.idle_for:.1f}s | "
            f"error={type(rs.outcome.exception()).__name__}"
        ),
    )


retry_standard = create_retry_decorator()

retry_fast = create_retry_decorator(
    max_attempts = 3,
    min_wait =  2,
    max_wait = 30,
    jitter_percent = 0.25
)