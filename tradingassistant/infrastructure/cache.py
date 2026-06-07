"""定义缓存抽象与内存缓存实现。

缓存层负责保存图表 bootstrap 数据、K 线快照、指标快照和其他运行态热数据。
当前实现默认使用进程内内存，但业务层只能通过 ``CacheStore`` 抽象访问，
从而为后续平滑替换为 Redis 等外部后端保留稳定接口。
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from threading import RLock
from typing import Any


def utc_now() -> datetime:
    """返回当前 UTC 时间。"""

    return datetime.now(timezone.utc)


@dataclass(slots=True)
class CacheEntry:
    """描述缓存中的单条记录。

    Args:
        value: 缓存值。
        created_at: 写入时间。
        expires_at: 过期时间；为 ``None`` 表示不过期。
    """

    value: Any
    created_at: datetime = field(default_factory=utc_now)
    expires_at: datetime | None = None

    def is_expired(self, now: datetime | None = None) -> bool:
        """判断记录是否已经过期。"""

        if self.expires_at is None:
            return False
        now = now or utc_now()
        return now >= self.expires_at


class CacheStore(ABC):
    """定义运行态缓存统一接口。"""

    @abstractmethod
    def get(self, key: str) -> Any | None:
        """读取缓存值。"""

    @abstractmethod
    def set(self, key: str, value: Any, ttl_seconds: int | None = None) -> None:
        """写入缓存值。"""

    @abstractmethod
    def delete(self, key: str) -> None:
        """删除缓存值。"""

    @abstractmethod
    def has(self, key: str) -> bool:
        """判断缓存键是否存在且未过期。"""

    @abstractmethod
    def clear(self) -> None:
        """清空缓存。"""

    @abstractmethod
    def evict_expired(self) -> int:
        """主动清理过期记录并返回清理数量。"""


class MemoryCacheStore(CacheStore):
    """基于进程内内存的缓存实现。"""

    def __init__(self, *, max_entries: int | None = 2048) -> None:
        """初始化内存缓存。

        Args:
            max_entries: 允许保留的最大缓存条目数；为 ``None`` 表示不限制。
        """

        self._entries: dict[str, CacheEntry] = {}
        self._lock = RLock()
        self._max_entries = max_entries

    def get(self, key: str) -> Any | None:
        """读取缓存值；若已过期则移除并返回空。"""

        with self._lock:
            entry = self._entries.get(key)
            if entry is None:
                return None
            if entry.is_expired():
                self._entries.pop(key, None)
                return None
            return entry.value

    def set(self, key: str, value: Any, ttl_seconds: int | None = None) -> None:
        """写入缓存值。"""

        expires_at = None
        if ttl_seconds is not None:
            expires_at = utc_now() + timedelta(seconds=ttl_seconds)
        with self._lock:
            self._entries[key] = CacheEntry(value=value, expires_at=expires_at)
            self._evict_if_necessary_locked()

    def delete(self, key: str) -> None:
        """删除缓存键。"""

        with self._lock:
            self._entries.pop(key, None)

    def has(self, key: str) -> bool:
        """判断缓存键是否存在且可读。"""

        return self.get(key) is not None

    def clear(self) -> None:
        """清空全部缓存。"""

        with self._lock:
            self._entries.clear()

    def evict_expired(self) -> int:
        """清理已过期缓存项。"""

        removed = 0
        now = utc_now()
        with self._lock:
            for key in list(self._entries):
                if self._entries[key].is_expired(now=now):
                    self._entries.pop(key, None)
                    removed += 1
        return removed

    def snapshot(self) -> dict[str, CacheEntry]:
        """返回缓存快照，便于调试或测试。"""

        with self._lock:
            return dict(self._entries)

    def _evict_if_necessary_locked(self) -> None:
        """在超过容量时优先清理过期项，再淘汰最旧记录。"""

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
