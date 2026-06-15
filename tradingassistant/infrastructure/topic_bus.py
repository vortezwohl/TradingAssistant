"""Topic broadcast abstraction and in-process implementation.

Topic broadcast distributes chart increments, quote list updates, and alert
events from the handler layer to subscribers. The current implementation
only supports in-process broadcast, but callers must interact through the
`TopicBus` abstraction to reserve replacement space for future Redis Pub/Sub
or other cross-process buses.
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
    """Describe a topic subscription handle.

    Args:
        topic: Subscription topic.
        subscriber_id: Unique subscriber identifier.
    """

    topic: str
    subscriber_id: str


class TopicBus(ABC):
    """Define unified topic broadcast interface."""

    @abstractmethod
    def subscribe(
        self,
        topic: str,
        subscriber_id: str,
        callback: Subscriber,
    ) -> SubscriptionHandle:
        """Register a topic subscription."""

    @abstractmethod
    def unsubscribe(self, handle: SubscriptionHandle) -> None:
        """Cancel a topic subscription."""

    @abstractmethod
    def publish(self, topic: str, payload: Any) -> int:
        """Publish a message to a topic and return the number of subscribers reached."""

    @abstractmethod
    def subscriber_count(self, topic: str) -> int:
        """Return the subscriber count for a topic."""

    @abstractmethod
    def clear(self) -> None:
        """Clear all subscriptions."""


class InMemoryTopicBus(TopicBus):
    """In-process callback-based topic broadcast implementation."""

    def __init__(self) -> None:
        """Initialize the in-process topic bus."""
        self._topics: dict[str, dict[str, Subscriber]] = defaultdict(dict)
        self._lock = RLock()

    def subscribe(
        self,
        topic: str,
        subscriber_id: str,
        callback: Subscriber,
    ) -> SubscriptionHandle:
        """Register an in-process topic subscription.

        Args:
            topic: Topic name.
            subscriber_id: Subscriber identifier.
            callback: Callback function invoked on message receipt.

        Returns:
            Subscription handle.
        """
        with self._lock:
            self._topics[topic][subscriber_id] = callback
        return SubscriptionHandle(topic=topic, subscriber_id=subscriber_id)

    def unsubscribe(self, handle: SubscriptionHandle) -> None:
        """Cancel a subscription.

        Args:
            handle: Subscription handle.
        """
        with self._lock:
            topic_subscribers = self._topics.get(handle.topic)
            if topic_subscribers is None:
                return
            topic_subscribers.pop(handle.subscriber_id, None)
            if not topic_subscribers:
                self._topics.pop(handle.topic, None)

    def publish(self, topic: str, payload: Any) -> int:
        """Broadcast a message to a topic.

        Args:
            topic: Topic name.
            payload: Broadcast content.

        Returns:
            Number of subscribers reached.
        """
        with self._lock:
            callbacks = list(self._topics.get(topic, {}).items())
        for _, callback in callbacks:
            callback(topic, payload)
        return len(callbacks)

    def subscriber_count(self, topic: str) -> int:
        """Get topic subscriber count.

        Args:
            topic: Topic name.

        Returns:
            Current subscriber count.
        """
        with self._lock:
            return len(self._topics.get(topic, {}))

    def clear(self) -> None:
        """Clear all topic subscriptions."""
        with self._lock:
            self._topics.clear()

    def topics(self) -> dict[str, list[str]]:
        """Return current topic snapshot for testing or debugging.

        Returns:
            Map of topic to subscriber ID list.
        """
        with self._lock:
            return {
                topic: list(subscribers.keys())
                for topic, subscribers in self._topics.items()
            }
