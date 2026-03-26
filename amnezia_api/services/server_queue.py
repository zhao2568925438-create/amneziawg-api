from __future__ import annotations

from contextlib import contextmanager
from threading import Lock
from typing import Iterator


class ServerQueueTimeoutError(TimeoutError):
    pass


class ServerCommandQueue:
    def __init__(self) -> None:
        self._locks_guard = Lock()
        self._locks: dict[int, Lock] = {}

    def _get_lock(self, server_id: int) -> Lock:
        with self._locks_guard:
            if server_id not in self._locks:
                self._locks[server_id] = Lock()
            return self._locks[server_id]

    @contextmanager
    def acquire(self, server_id: int, timeout: int) -> Iterator[None]:
        lock = self._get_lock(server_id)
        acquired = lock.acquire(timeout=timeout)
        if not acquired:
            raise ServerQueueTimeoutError(
                f"Сервер {server_id} сейчас занят другой операцией. Попробуй ещё раз чуть позже."
            )
        try:
            yield
        finally:
            lock.release()
