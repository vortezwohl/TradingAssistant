"""定义主题广播抽象与进程内实现。

主题广播用于把图表增量、行情列表更新和预警事件从处理器层分发给订阅方。
当前实现仅提供进程内广播，但调用方必须通过 `TopicBus` 抽象交互，
为未来 Redis Pub/Sub 或其他跨进程总线预留替换空间。
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections import defaultdict
from dataclasses import dataclass
from threading import RLock
from typing import Any, Callable


Subscriber = Callable[[str, Any], None]


@dataclass(slots=True, frozen=True)
class SubscriptionHandle:
    """描述主题订阅句柄。

    Args:
        topic: 订阅主题。
        subscriber_id: 订阅者唯一标识。
    """

    topic: str
    subscriber_id: str


class TopicBus(ABC):
    """定义主题广播统一接口。"""

    @abstractmethod
    def subscribe(
        self,
        topic: str,
        subscriber_id: str,
        callback: Subscriber,
    ) -> SubscriptionHandle:
        """注册主题订阅。"""

    @abstractmethod
    def unsubscribe(self, handle: SubscriptionHandle) -> None:
        """取消主题订阅。"""

    @abstractmethod
    def publish(self, topic: str, payload: Any) -> int:
        """向主题发布消息并返回命中的订阅者数量。"""

    @abstractmethod
    def subscriber_count(self, topic: str) -> int:
        """返回某个主题的订阅数量。"""

    @abstractmethod
    def clear(self) -> None:
        """清空所有订阅。"""


class InMemoryTopicBus(TopicBus):
    """基于进程内回调的主题广播实现。"""

    def __init__(self) -> None:
        """初始化进程内主题总线。"""

        self._topics: dict[str, dict[str, Subscriber]] = defaultdict(dict)
        self._lock = RLock()

    def subscribe(
        self,
        topic: str,
        subscriber_id: str,
        callback: Subscriber,
    ) -> SubscriptionHandle:
        """注册进程内主题订阅。

        Args:
            topic: 主题名。
            subscriber_id: 订阅者标识。
            callback: 收到消息时的回调函数。

        Returns:
            订阅句柄。
        """

        with self._lock:
            self._topics[topic][subscriber_id] = callback
        return SubscriptionHandle(topic=topic, subscriber_id=subscriber_id)

    def unsubscribe(self, handle: SubscriptionHandle) -> None:
        """取消订阅。

        Args:
            handle: 订阅句柄。
        """

        with self._lock:
            topic_subscribers = self._topics.get(handle.topic)
            if topic_subscribers is None:
                return
            topic_subscribers.pop(handle.subscriber_id, None)
            if not topic_subscribers:
                self._topics.pop(handle.topic, None)

    def publish(self, topic: str, payload: Any) -> int:
        """向指定主题广播消息。

        Args:
            topic: 主题名。
            payload: 广播内容。

        Returns:
            成功命中的订阅者数量。
        """

        with self._lock:
            callbacks = list(self._topics.get(topic, {}).items())
        for _, callback in callbacks:
            callback(topic, payload)
        return len(callbacks)

    def subscriber_count(self, topic: str) -> int:
        """获取主题订阅数。

        Args:
            topic: 主题名。

        Returns:
            当前订阅者数量。
        """

        with self._lock:
            return len(self._topics.get(topic, {}))

    def clear(self) -> None:
        """清空所有主题订阅。"""

        with self._lock:
            self._topics.clear()

    def topics(self) -> dict[str, list[str]]:
        """返回当前主题快照，便于测试或调试。

        Returns:
            每个主题下的订阅者标识列表。
        """

        with self._lock:
            return {
                topic: list(subscribers.keys())
                for topic, subscribers in self._topics.items()
            }
