"""定义订阅注册抽象与进程内实现。

订阅注册层关注会话到主题、主题到会话的映射关系。它与 TopicBus 的区别是：
TopicBus 负责消息广播，SubscriptionRegistry 负责回答“谁订阅了什么”。
这样可以把资源释放、空主题回收和未来跨进程共享注册状态的需求独立出来。
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections import defaultdict
from threading import RLock


class SubscriptionRegistry(ABC):
    """定义会话订阅注册统一接口。"""

    @abstractmethod
    def register(self, session_id: str, topic: str) -> None:
        """注册会话对主题的订阅。"""

    @abstractmethod
    def unregister(self, session_id: str, topic: str) -> None:
        """取消会话对主题的订阅。"""

    @abstractmethod
    def unregister_all(self, session_id: str) -> list[str]:
        """取消会话的所有订阅，并返回受影响的主题列表。"""

    @abstractmethod
    def topics_for_session(self, session_id: str) -> set[str]:
        """返回会话当前订阅的主题集合。"""

    @abstractmethod
    def sessions_for_topic(self, topic: str) -> set[str]:
        """返回主题当前关联的会话集合。"""

    @abstractmethod
    def topic_subscriber_count(self, topic: str) -> int:
        """返回主题订阅者数量。"""

    @abstractmethod
    def clear(self) -> None:
        """清空注册表。"""


class InMemorySubscriptionRegistry(SubscriptionRegistry):
    """基于进程内集合映射的订阅注册实现。"""

    def __init__(self) -> None:
        """初始化进程内订阅注册表。"""

        self._session_topics: dict[str, set[str]] = defaultdict(set)
        self._topic_sessions: dict[str, set[str]] = defaultdict(set)
        self._lock = RLock()

    def register(self, session_id: str, topic: str) -> None:
        """注册订阅关系。

        Args:
            session_id: 会话标识。
            topic: 主题标识。
        """

        with self._lock:
            self._session_topics[session_id].add(topic)
            self._topic_sessions[topic].add(session_id)

    def unregister(self, session_id: str, topic: str) -> None:
        """移除订阅关系。

        Args:
            session_id: 会话标识。
            topic: 主题标识。
        """

        with self._lock:
            if session_id in self._session_topics:
                self._session_topics[session_id].discard(topic)
                if not self._session_topics[session_id]:
                    self._session_topics.pop(session_id, None)
            if topic in self._topic_sessions:
                self._topic_sessions[topic].discard(session_id)
                if not self._topic_sessions[topic]:
                    self._topic_sessions.pop(topic, None)

    def unregister_all(self, session_id: str) -> list[str]:
        """移除会话的所有订阅。

        Args:
            session_id: 会话标识。

        Returns:
            被解除关联的主题列表。
        """

        with self._lock:
            topics = list(self._session_topics.pop(session_id, set()))
            for topic in topics:
                sessions = self._topic_sessions.get(topic)
                if sessions is None:
                    continue
                sessions.discard(session_id)
                if not sessions:
                    self._topic_sessions.pop(topic, None)
            return topics

    def topics_for_session(self, session_id: str) -> set[str]:
        """返回会话的订阅主题集合。

        Args:
            session_id: 会话标识。

        Returns:
            主题集合副本。
        """

        with self._lock:
            return set(self._session_topics.get(session_id, set()))

    def sessions_for_topic(self, topic: str) -> set[str]:
        """返回主题下的会话集合。

        Args:
            topic: 主题标识。

        Returns:
            会话集合副本。
        """

        with self._lock:
            return set(self._topic_sessions.get(topic, set()))

    def topic_subscriber_count(self, topic: str) -> int:
        """返回主题订阅数。

        Args:
            topic: 主题标识。

        Returns:
            当前主题订阅数。
        """

        with self._lock:
            return len(self._topic_sessions.get(topic, set()))

    def clear(self) -> None:
        """清空全部注册关系。"""

        with self._lock:
            self._session_topics.clear()
            self._topic_sessions.clear()

    def snapshot(self) -> dict[str, dict[str, list[str]]]:
        """返回注册表快照，便于测试或调试。

        Returns:
            当前注册状态的可序列化快照。
        """

        with self._lock:
            return {
                "session_topics": {
                    session_id: sorted(topics)
                    for session_id, topics in self._session_topics.items()
                },
                "topic_sessions": {
                    topic: sorted(session_ids)
                    for topic, session_ids in self._topic_sessions.items()
                },
            }
