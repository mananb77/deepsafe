"""Unit tests for ActionDispatcher."""

import pytest
from unittest.mock import MagicMock, AsyncMock

from src.services.workflow.action_dispatcher import (
    ActionDispatcher,
    ActionResult,
    ActionStatus,
)


class TestActionResult:
    """Tests for ActionResult."""

    def test_creation(self):
        """Test creating an action result."""
        result = ActionResult(
            action_type="alert",
            status=ActionStatus.COMPLETED,
            message="Alert sent",
        )
        assert result.action_type == "alert"
        assert result.status == ActionStatus.COMPLETED
        assert result.message == "Alert sent"

    def test_to_dict(self):
        """Test serialization."""
        result = ActionResult(
            action_type="verify",
            status=ActionStatus.DISPATCHED,
        )
        d = result.to_dict()
        assert d["action_type"] == "verify"
        assert d["status"] == "dispatched"
        assert "action_id" in d
        assert "dispatched_at" in d

    def test_default_values(self):
        """Test default values."""
        result = ActionResult()
        assert result.status == ActionStatus.PENDING
        assert result.error is None


class TestActionDispatcher:
    """Tests for ActionDispatcher."""

    def test_creation(self):
        """Test creating a dispatcher."""
        dispatcher = ActionDispatcher()
        assert dispatcher.stats["handlers_registered"] == 0
        assert dispatcher.stats["dispatched"] == 0

    def test_register_handler(self):
        """Test registering a handler."""
        dispatcher = ActionDispatcher()
        handler = MagicMock()
        dispatcher.register_handler("alert", handler)
        assert dispatcher.stats["handlers_registered"] == 1

    def test_unregister_handler(self):
        """Test unregistering a handler."""
        dispatcher = ActionDispatcher()
        handler = MagicMock()
        dispatcher.register_handler("alert", handler)
        dispatcher.unregister_handler("alert")
        assert dispatcher.stats["handlers_registered"] == 0

    @pytest.mark.asyncio
    async def test_dispatch_sync_handler(self):
        """Test dispatching to a sync handler."""
        dispatcher = ActionDispatcher()
        handler = MagicMock(return_value={"sent": True})
        dispatcher.register_handler("alert", handler)

        results = await dispatcher.dispatch_actions(
            actions=[{"action": "alert", "channels": ["websocket"]}],
            context={"meeting_id": "m1"},
        )

        assert len(results) == 1
        assert results[0].status == ActionStatus.COMPLETED
        handler.assert_called_once()

    @pytest.mark.asyncio
    async def test_dispatch_async_handler(self):
        """Test dispatching to an async handler."""
        dispatcher = ActionDispatcher()
        handler = AsyncMock(return_value={"verified": True})
        dispatcher.register_handler("verify", handler, is_async=True)

        results = await dispatcher.dispatch_actions(
            actions=[{"action": "verify", "channel": "sms"}],
            context={"participant_id": "p1"},
        )

        assert len(results) == 1
        assert results[0].status == ActionStatus.COMPLETED
        handler.assert_called_once()

    @pytest.mark.asyncio
    async def test_dispatch_no_handler(self):
        """Test dispatching when no handler is registered."""
        dispatcher = ActionDispatcher()

        results = await dispatcher.dispatch_actions(
            actions=[{"action": "unknown_action"}],
            context={},
        )

        assert len(results) == 1
        assert results[0].status == ActionStatus.SKIPPED

    @pytest.mark.asyncio
    async def test_dispatch_multiple_actions(self):
        """Test dispatching multiple actions."""
        dispatcher = ActionDispatcher()
        alert_handler = MagicMock(return_value={})
        log_handler = MagicMock(return_value={})
        dispatcher.register_handler("alert", alert_handler)
        dispatcher.register_handler("log", log_handler)

        results = await dispatcher.dispatch_actions(
            actions=[
                {"action": "alert"},
                {"action": "log"},
            ],
            context={"meeting_id": "m1"},
        )

        assert len(results) == 2
        assert all(r.status == ActionStatus.COMPLETED for r in results)
        alert_handler.assert_called_once()
        log_handler.assert_called_once()

    @pytest.mark.asyncio
    async def test_dispatch_handler_error(self):
        """Test handling of handler errors."""
        dispatcher = ActionDispatcher()
        handler = MagicMock(side_effect=RuntimeError("Handler failed"))
        dispatcher.register_handler("alert", handler)

        results = await dispatcher.dispatch_actions(
            actions=[{"action": "alert"}],
            context={},
        )

        assert len(results) == 1
        assert results[0].status == ActionStatus.FAILED
        assert results[0].error == "Handler failed"

    @pytest.mark.asyncio
    async def test_dispatch_async_handler_error(self):
        """Test handling of async handler errors."""
        dispatcher = ActionDispatcher()
        handler = AsyncMock(side_effect=RuntimeError("Async failed"))
        dispatcher.register_handler("verify", handler, is_async=True)

        results = await dispatcher.dispatch_actions(
            actions=[{"action": "verify"}],
            context={},
        )

        assert len(results) == 1
        assert results[0].status == ActionStatus.FAILED
        assert results[0].error == "Async failed"

    @pytest.mark.asyncio
    async def test_dispatch_handler_returns_action_result(self):
        """Test handler that returns an ActionResult directly."""
        dispatcher = ActionDispatcher()
        custom_result = ActionResult(
            action_type="custom",
            status=ActionStatus.COMPLETED,
            message="Custom handling",
        )
        handler = MagicMock(return_value=custom_result)
        dispatcher.register_handler("custom", handler)

        results = await dispatcher.dispatch_actions(
            actions=[{"action": "custom"}],
            context={},
        )

        assert len(results) == 1
        assert results[0].message == "Custom handling"

    @pytest.mark.asyncio
    async def test_dispatch_empty_actions(self):
        """Test dispatching with empty action list."""
        dispatcher = ActionDispatcher()

        results = await dispatcher.dispatch_actions(
            actions=[],
            context={},
        )

        assert len(results) == 0

    @pytest.mark.asyncio
    async def test_dispatch_action_without_type(self):
        """Test dispatching action without type key is skipped."""
        dispatcher = ActionDispatcher()

        results = await dispatcher.dispatch_actions(
            actions=[{"channels": ["websocket"]}],  # No "action" key
            context={},
        )

        assert len(results) == 0

    @pytest.mark.asyncio
    async def test_stats_tracking(self):
        """Test that stats are tracked correctly."""
        dispatcher = ActionDispatcher()
        handler = MagicMock(return_value={})
        dispatcher.register_handler("alert", handler)

        await dispatcher.dispatch_actions(
            actions=[{"action": "alert"}, {"action": "alert"}],
            context={},
        )

        assert dispatcher.stats["dispatched"] == 2
        assert dispatcher.stats["completed"] == 2

    def test_reset(self):
        """Test resetting stats."""
        dispatcher = ActionDispatcher()
        dispatcher._dispatched = 10
        dispatcher._completed = 8
        dispatcher._failed = 2
        dispatcher.reset()
        assert dispatcher.stats["dispatched"] == 0
        assert dispatcher.stats["completed"] == 0
        assert dispatcher.stats["failed"] == 0
