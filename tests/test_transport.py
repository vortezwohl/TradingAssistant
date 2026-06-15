"""Verify FastAPI transport facade and session subscription logic."""

from __future__ import annotations

import json
import unittest
from datetime import datetime, timedelta, timezone

from fastapi.testclient import TestClient

from tradingassistant.backend.charting.history import HistoryBackfillService
from tradingassistant.backend.charting.models import RuntimeBar
from tradingassistant.backend.diagnostics import RuntimeMetrics
from tradingassistant.backend.events import KlineEvent, QuoteEvent
from tradingassistant.backend.indicators.engine import IncrementalIndicatorEngine
from tradingassistant.backend.infrastructure.cache import MemoryCacheStore
from tradingassistant.backend.infrastructure.subscription_registry import (
    InMemorySubscriptionRegistry,
)
from tradingassistant.backend.infrastructure.topic_bus import InMemoryTopicBus
from tradingassistant.backend.transport.app import MarketMonitorService, create_app


class FakeGateway:
    """Provide minimal history backfill capability for transport layer tests."""

    def get_stock_history(
        self,
        *,
        region: str,
        code: str,
        period: str,
        limit: int,
        end: str | None = None,
    ):
        base_time = datetime(2026, 6, 7, 9, 30, tzinfo=timezone.utc)
        return [
            RuntimeBar(
                symbol=f"{region.upper()}.{code}",
                period=period,
                bar_time=base_time + timedelta(minutes=index),
                open_price=500.0 + index,
                high_price=501.0 + index,
                low_price=499.0 + index,
                close_price=500.5 + index,
                volume=1000 + index,
                turnover=500000 + index,
                provisional=False,
            )
            for index in range(limit)
        ]


class HistoryGatewayAdapter(FakeGateway):
    """Adapt RuntimeBar results for HistoryBackfillService."""

    def get_stock_history(self, **kwargs):
        return super().get_stock_history(**kwargs)


class TransportAppTests(unittest.TestCase):
    """Test transport facade."""

    def setUp(self) -> None:
        """Prepare test application."""
        self.cache = MemoryCacheStore()
        self.topic_bus = InMemoryTopicBus()
        self.registry = InMemorySubscriptionRegistry()
        self.engine = IncrementalIndicatorEngine()
        self.metrics = RuntimeMetrics()
        self.history = HistoryBackfillService(
            gateway=HistoryGatewayAdapter(),
            cache_store=self.cache,
        )
        self.service = MarketMonitorService(
            history_service=self.history,
            cache_store=self.cache,
            topic_bus=self.topic_bus,
            registry=self.registry,
            indicator_engine=self.engine,
            metrics=self.metrics,
        )
        self.client = TestClient(
            create_app(
                service=self.service,
                topic_bus=self.topic_bus,
                registry=self.registry,
            )
        )

    def test_bootstrap_endpoint_returns_snapshot(self) -> None:
        """bootstrap REST should return chart snapshot."""
        response = self.client.get(
            "/api/chart/bootstrap",
            params={"region": "HK", "code": "00700", "period": "1m", "bars": 3},
        )
        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload["symbol"], "HK.00700")
        self.assertEqual(payload["period"], "1m")
        self.assertEqual(len(payload["bars"]), 3)

    def test_bootstrap_endpoint_allows_frontend_origin(self) -> None:
        """bootstrap REST should allow Reflex frontend cross-origin access."""
        response = self.client.get(
            "/api/chart/bootstrap",
            params={"region": "HK", "code": "00700", "period": "1m", "bars": 3},
            headers={"Origin": "http://127.0.0.1:3000"},
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.headers.get("access-control-allow-origin"),
            "http://127.0.0.1:3000",
        )

    def test_runtime_metrics_endpoint_returns_observability_snapshot(self) -> None:
        """Runtime metrics endpoint should expose minimal observability data."""
        self.client.get(
            "/api/chart/bootstrap",
            params={"region": "HK", "code": "00700", "period": "1m", "bars": 2},
        )
        response = self.client.get("/api/runtime/metrics")
        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertIn("cache_misses", payload)
        self.assertGreaterEqual(payload["cache_misses"], 1)

    def test_chart_websocket_receives_published_update(self) -> None:
        """Chart WS should receive published bar updates after subscription."""
        with self.client.websocket_connect("/ws/chart/session-a") as websocket:
            websocket.send_text(json.dumps({"symbol": "HK.00700", "period": "1m"}))
            ack = websocket.receive_json()
            self.assertEqual(ack["payload_type"], "subscription_ack")
            event = KlineEvent(
                event_type=None,  # type: ignore[arg-type]
                symbol="HK.00700",
                source="itick",
                event_time=datetime(2026, 6, 7, 9, 41, tzinfo=timezone.utc),
                period="1m",
                open_price=501.0,
                high_price=502.0,
                low_price=500.5,
                close_price=501.5,
                volume=1001.0,
                turnover=501500.0,
                bar_time=datetime(2026, 6, 7, 9, 41, tzinfo=timezone.utc),
                provisional=False,
            )
            self.service.publish_chart_update(event=event, indicators={"ma5": 500.4})
            payload = websocket.receive_json()
            self.assertEqual(payload["topic"], "chart:HK.00700:1m")
            self.assertEqual(payload["payload_type"], "bar_update")

    def test_quote_websocket_receives_published_update(self) -> None:
        """Quote list WS should receive quote updates after subscription."""
        with self.client.websocket_connect("/ws/quotes/session-b") as websocket:
            websocket.send_text('{"action":"subscribe","name":"watchlist"}')
            ack = websocket.receive_json()
            self.assertEqual(ack["payload_type"], "subscription_ack")
            event = QuoteEvent(
                event_type=None,  # type: ignore[arg-type]
                symbol="HK.00700",
                source="itick",
                event_time=datetime(2026, 6, 7, 9, 40, tzinfo=timezone.utc),
                last_price=500.5,
                volume=1000.0,
                turnover=500000.0,
            )
            self.service.publish_quote_update(event=event)
            payload = websocket.receive_json()
            self.assertEqual(payload["topic"], "quotes:watchlist")
            self.assertEqual(payload["symbol"], "HK.00700")

    def test_alert_websocket_receives_published_update(self) -> None:
        """Alert WS should receive alert events after subscription."""
        with self.client.websocket_connect("/ws/alerts/session-alert") as websocket:
            websocket.send_text('{"action":"subscribe","name":"default"}')
            ack = websocket.receive_json()
            self.assertEqual(ack["payload_type"], "subscription_ack")
            self.service.publish_alert(
                symbol="HK.00700",
                alert_type="indicator_cross",
                message="MA5 crossed above MA20",
                severity="warning",
            )
            payload = websocket.receive_json()
            self.assertEqual(payload["topic"], "alerts:default")
            self.assertEqual(payload["payload_type"], "alert")
            self.assertEqual(payload["severity"], "warning")

    def test_unsubscribe_releases_topic_registration(self) -> None:
        """Explicit unsubscription should release session-to-topic registration."""
        with self.client.websocket_connect("/ws/chart/session-unsub") as websocket:
            websocket.send_text(json.dumps({"symbol": "HK.00700", "period": "1m"}))
            subscribe_ack = websocket.receive_json()
            self.assertEqual(subscribe_ack["action"], "subscribe")
            self.assertEqual(
                self.registry.topic_subscriber_count("chart:HK.00700:1m"),
                1,
            )
            websocket.send_text(
                json.dumps(
                    {
                        "action": "unsubscribe",
                        "symbol": "HK.00700",
                        "period": "1m",
                    }
                )
            )
            unsubscribe_ack = websocket.receive_json()
            self.assertEqual(unsubscribe_ack["action"], "unsubscribe")
            self.assertEqual(
                self.registry.topic_subscriber_count("chart:HK.00700:1m"),
                0,
            )
            self.assertEqual(
                self.topic_bus.subscriber_count("chart:HK.00700:1m"),
                0,
            )

    def test_two_chart_sessions_receive_shared_broadcast(self) -> None:
        """Two chart sessions sharing same topic should both receive updates."""
        with (
            self.client.websocket_connect("/ws/chart/session-c1") as ws_one,
            self.client.websocket_connect("/ws/chart/session-c2") as ws_two,
        ):
            subscribe_payload = json.dumps({"symbol": "HK.00700", "period": "1m"})
            ws_one.send_text(subscribe_payload)
            ws_two.send_text(subscribe_payload)
            self.assertEqual(ws_one.receive_json()["payload_type"], "subscription_ack")
            self.assertEqual(ws_two.receive_json()["payload_type"], "subscription_ack")
            event = KlineEvent(
                event_type=None,  # type: ignore[arg-type]
                symbol="HK.00700",
                source="itick",
                event_time=datetime(2026, 6, 7, 9, 41, tzinfo=timezone.utc),
                period="1m",
                open_price=501.0,
                high_price=502.0,
                low_price=500.5,
                close_price=501.5,
                volume=1001.0,
                turnover=501500.0,
                bar_time=datetime(2026, 6, 7, 9, 41, tzinfo=timezone.utc),
                provisional=False,
            )
            self.service.publish_chart_update(event=event, indicators={"ma5": 500.4})
            self.assertEqual(ws_one.receive_json()["topic"], "chart:HK.00700:1m")
            self.assertEqual(ws_two.receive_json()["topic"], "chart:HK.00700:1m")


if __name__ == "__main__":
    unittest.main()
