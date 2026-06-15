"""验证 FastAPI 传输门面与会话订阅逻辑。"""

from __future__ import annotations

import json
import unittest
from datetime import datetime, timedelta, timezone

from fastapi.testclient import TestClient

from tradingassistant.charting.history import HistoryBackfillService
from tradingassistant.charting.models import RuntimeBar
from tradingassistant.diagnostics import RuntimeMetrics
from tradingassistant.events import KlineEvent, QuoteEvent
from tradingassistant.indicators.engine import IncrementalIndicatorEngine
from tradingassistant.infrastructure.cache import MemoryCacheStore
from tradingassistant.infrastructure.subscription_registry import (
    InMemorySubscriptionRegistry,
)
from tradingassistant.infrastructure.topic_bus import InMemoryTopicBus
from tradingassistant.transport.app import MarketMonitorService, create_app


class FakeGateway:
    """为传输层测试提供最小历史回填能力。"""

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
    """把 RuntimeBar 结果适配给 HistoryBackfillService。"""

    def get_stock_history(self, **kwargs):
        return super().get_stock_history(**kwargs)


class TransportAppTests(unittest.TestCase):
    """验证传输门面。"""

    def setUp(self) -> None:
        """准备测试应用。"""
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
        """bootstrap REST 应返回图表快照。"""
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
        """bootstrap REST 应允许 Reflex 前端跨域访问。"""
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
        """运行态指标接口应暴露最小观测信息。"""
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
        """图表 WS 订阅后应能收到发布的 bar 更新。"""
        with self.client.websocket_connect("/ws/chart/session-a") as websocket:
            websocket.send_text(json.dumps({"symbol": "HK.00700", "period": "1m"}))
            ack = websocket.receive_json()
            self.assertEqual(ack["payload_type"], "subscription_ack")
            event = KlineEvent(
                event_type=None,  # type: ignore[arg-type]
                symbol="HK.00700",
                source="itick",
                event_time=datetime(2026, 6, 7, 9, 40, tzinfo=timezone.utc),
                period="1m",
                open_price=500.0,
                high_price=501.0,
                low_price=499.0,
                close_price=500.5,
                volume=1000.0,
                turnover=500000.0,
                bar_time=datetime(2026, 6, 7, 9, 40, tzinfo=timezone.utc),
                provisional=False,
            )
            self.service.publish_chart_update(
                event=event,
                indicators={"ma5": 500.1},
            )
            payload = websocket.receive_json()
            self.assertEqual(payload["topic"], "chart:HK.00700:1m")
            self.assertEqual(payload["payload_type"], "bar_update")

    def test_quote_websocket_receives_published_update(self) -> None:
        """列表行情 WS 订阅后应能收到 quote 更新。"""
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
            self.service.publish_quote_update(event)
            payload = websocket.receive_json()
            self.assertEqual(payload["topic"], "quotes:watchlist")
            self.assertEqual(payload["symbol"], "HK.00700")

    def test_alert_websocket_receives_published_update(self) -> None:
        """告警 WS 订阅后应能收到告警事件。"""
        with self.client.websocket_connect("/ws/alerts/session-alert") as websocket:
            websocket.send_text('{"action":"subscribe","name":"default"}')
            ack = websocket.receive_json()
            self.assertEqual(ack["payload_type"], "subscription_ack")
            self.service.publish_alert(
                symbol="HK.00700",
                alert_type="indicator_cross",
                message="MA5 crossed above MA20",
                level="warning",
            )
            payload = websocket.receive_json()
            self.assertEqual(payload["topic"], "alerts:default")
            self.assertEqual(payload["payload_type"], "alert_event")
            self.assertEqual(payload["level"], "warning")

    def test_unsubscribe_releases_topic_registration(self) -> None:
        """显式退订后应释放会话到主题的注册关系。"""
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
        """两个图表会话订阅同一 topic 时都应收到更新。"""
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
