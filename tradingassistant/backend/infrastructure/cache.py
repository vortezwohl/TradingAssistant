"""Cache abstraction and in-memory cache implementation.

The cache layer stores chart bootstrap data, K-line snapshots, indicator
snapshots, and other runtime hot data. The current implementation defaults
to in-process memory, but business layers must only access through the
``CacheStore`` abstraction, preserving a stable interface for future smooth
replacement with Redis or other external backends.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from threading import RLock
from typing import Any


def utc_now() -> datetime:
    """Return the current UTC time."""
    return datetime.now(timezone.utc)


@dataclass(slots=True)
class CacheEntry:
    """Describe a single cache entry.

    Args:
        value: Cached value.
        created_at: Write time.
        expires_at: Expiry time; ``None`` means no expiry.
    """

    value: Any
    created_at: datetime = field(default_factory=utc_now)
    expires_at: datetime | None = None

    def is_expired(self, now: datetime | None = None) -> bool:
        """Check whether the entry has expired."""
        if self.expires_at is None:
            return False
        now = now or utc_now()
        return now >= self.expires_at


class CacheStore(ABC):
    """Define unified runtime cache interface."""

    @abstractmethod
    def get(self, key: str) -> Any | None:
        """Read a cached value."""

    @abstractmethod
    def set(self, key: str, value: Any, ttl_seconds: int | None = None) -> None:
        """Write a cached value."""

    @abstractmethod
    def delete(self, key: str) -> None:
        """Delete a cached value."""

    @abstractmethod
    def has(self, key: str) -> bool:
        """Check whether a cache key exists and is not expired."""

    @abstractmethod
    def clear(self) -> None:
        """Clear all cache entries."""

    @abstractmethod
    def evict_expired(self) -> int:
        """Proactively evict expired entries and return evicted count."""


class MemoryCacheStore(CacheStore):
    """In-process memory-based cache implementation."""

    def __init__(self, *, max_entries: int | None = 2048) -> None:
        """Initialize in-memory cache.

        Args:
            max_entries: Maximum allowed cache entries; ``None`` means unlimited.
        """
        self._entries: dict[str, CacheEntry] = {}
        self._lock = RLock()
        self._max_entries = max_entries

    def get(self, key: str) -> Any | None:
        """Read cached value; remove and return None if expired."""
        with self._lock:
            entry = self._entries.get(key)
            if entry is None:
                return None
            if entry.is_expired():
                self._entries.pop(key, None)
                return None
            return entry.value

    def set(self, key: str, value: Any, ttl_seconds: int | None = None) -> None:
        """Write a cached value."""
        expires_at = None
        if ttl_seconds is not None:
            expires_at = utc_now() + timedelta(seconds=ttl_seconds)
        with self._lock:
            self._entries[key] = CacheEntry(value=value, expires_at=expires_at)
            self._evict_if_necessary_locked()

    def delete(self, key: str) -> None:
        """Delete a cache key."""
        with self._lock:
            self._entries.pop(key, None)

    def has(self, key: str) -> bool:
        """Check whether a cache key exists and is readable."""
        return self.get(key) is not None

    def clear(self) -> None:
        """Clear all cache entries."""
        with self._lock:
            self._entries.clear()

    def evict_expired(self) -> int:
        """Evict expired cache entries."""
        removed = 0
        now = utc_now()
        with self._lock:
            for key in list(self._entries):
                if self._entries[key].is_expired(now=now):
                    self._entries.pop(key, None)
                    removed += 1
        return removed

    def snapshot(self) -> dict[str, CacheEntry]:
        """Return a cache snapshot for debugging or testing."""
        with self._lock:
            return dict(self._entries)

    def _evict_if_necessary_locked(self) -> None:
        """Evict expired entries first when over capacity, then evict oldest."""
        if self._max_entries is None or len(self._entries) <= self._max_entries:
            return

        now = utc_now()
        for key in list(self._entries):
            if len(self._entries) <= self._max_entries:
                break
            if self._entries[key].is_expired(now=now):
                self._entries.pop(key, None)

        while len(self._entries) > self._max_entries:
            oldest_key = min(
                self._entries,
                key=lambda item_key: self._entries[item_key].created_at,
            )
            self._entries.pop(oldest_key, None)
