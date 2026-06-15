"""Subscription registration abstraction and in-process implementation.

The subscription registry layer manages session-to-topic and topic-to-session
mappings. It differs from TopicBus: TopicBus handles message broadcast while
SubscriptionRegistry answers "who subscribed to what". This separates concerns
like resource release, empty topic reclamation, and future cross-process
shared registration state.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections import defaultdict
from threading import RLock


class SubscriptionRegistry(ABC):
    """Define unified session subscription registration interface."""

    @abstractmethod
    def register(self, session_id: str, topic: str) -> None:
        """Register a session subscription to a topic."""

    @abstractmethod
    def unregister(self, session_id: str, topic: str) -> None:
        """Cancel a session subscription to a topic."""

    @abstractmethod
    def unregister_all(self, session_id: str) -> list[str]:
        """Cancel all subscriptions for a session and return affected topic list."""

    @abstractmethod
    def topics_for_session(self, session_id: str) -> set[str]:
        """Return the set of topics currently subscribed by a session."""

    @abstractmethod
    def sessions_for_topic(self, topic: str) -> set[str]:
        """Return the set of sessions currently associated with a topic."""

    @abstractmethod
    def topic_subscriber_count(self, topic: str) -> int:
        """Return the subscriber count for a topic."""

    @abstractmethod
    def clear(self) -> None:
        """Clear the registry."""


class InMemorySubscriptionRegistry(SubscriptionRegistry):
    """In-process set-mapping-based subscription registry implementation."""

    def __init__(self) -> None:
        """Initialize in-process subscription registry."""
        self._session_topics: dict[str, set[str]] = defaultdict(set)
        self._topic_sessions: dict[str, set[str]] = defaultdict(set)
        self._lock = RLock()

    def register(self, session_id: str, topic: str) -> None:
        """Register a subscription relationship.

        Args:
            session_id: Session identifier.
            topic: Topic identifier.
        """
        with self._lock:
            self._session_topics[session_id].add(topic)
            self._topic_sessions[topic].add(session_id)

    def unregister(self, session_id: str, topic: str) -> None:
        """Remove a subscription relationship.

        Args:
            session_id: Session identifier.
            topic: Topic identifier.
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
        """Remove all subscriptions for a session.

        Args:
            session_id: Session identifier.

        Returns:
            List of topics that were unlinked.
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
        """Return the topic set for a session.

        Args:
            session_id: Session identifier.

        Returns:
            Copy of the topic set.
        """
        with self._lock:
            return set(self._session_topics.get(session_id, set()))

    def sessions_for_topic(self, topic: str) -> set[str]:
        """Return the session set for a topic.

        Args:
            topic: Topic identifier.

        Returns:
            Copy of the session set.
        """
        with self._lock:
            return set(self._topic_sessions.get(topic, set()))

    def topic_subscriber_count(self, topic: str) -> int:
        """Return the topic subscriber count.

        Args:
            topic: Topic identifier.

        Returns:
            Current topic subscriber count.
        """
        with self._lock:
            return len(self._topic_sessions.get(topic, set()))

    def clear(self) -> None:
        """Clear all registration relationships."""
        with self._lock:
            self._session_topics.clear()
            self._topic_sessions.clear()

    def snapshot(self) -> dict[str, dict[str, list[str]]]:
        """Return registry snapshot for testing or debugging.

        Returns:
            Serializable snapshot of current registration state.
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
