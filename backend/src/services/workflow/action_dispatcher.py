"""
Action Dispatcher

Routes policy actions to their respective service handlers.

Action types and their handlers:
- VERIFY  → VerificationEngine.create_verification()
- ALERT   → WebSocket broadcast via ConnectionManager
- NOTIFY  → Multi-channel notification (push/email/SMS)
- BLOCK   → Signal meeting bot to block screen share
- FLAG    → Update participant trust_level in DB
- LOG     → Create Incident record
- HOLD    → Create transaction hold
- RECORD  → Start meeting recording
"""

import logging
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Callable, Dict, List, Optional
from uuid import uuid4

logger = logging.getLogger(__name__)


class ActionStatus(str, Enum):
    """Status of a dispatched action."""
    PENDING = "pending"
    DISPATCHED = "dispatched"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


@dataclass
class ActionResult:
    """Result of an action dispatch."""
    action_id: str = field(default_factory=lambda: str(uuid4()))
    action_type: str = ""
    status: ActionStatus = ActionStatus.PENDING
    message: str = ""
    details: Dict[str, Any] = field(default_factory=dict)
    dispatched_at: datetime = field(default_factory=datetime.utcnow)
    error: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "action_id": self.action_id,
            "action_type": self.action_type,
            "status": self.status.value,
            "message": self.message,
            "details": self.details,
            "dispatched_at": self.dispatched_at.isoformat(),
            "error": self.error,
        }


# Type for action handlers
ActionHandler = Callable[[Dict[str, Any], Dict[str, Any]], ActionResult]


class ActionDispatcher:
    """
    Dispatches policy actions to service handlers.

    Usage:
        dispatcher = ActionDispatcher()
        dispatcher.register_handler("verify", verify_handler)
        dispatcher.register_handler("alert", alert_handler)

        results = await dispatcher.dispatch_actions(
            actions=[{"action": "verify", "channel": "sms"}],
            context={"participant_id": "p1", "meeting_id": "m1"},
        )
    """

    def __init__(self):
        self._handlers: Dict[str, ActionHandler] = {}
        self._async_handlers: Dict[str, Callable] = {}

        # Statistics
        self._dispatched = 0
        self._completed = 0
        self._failed = 0

    @property
    def stats(self) -> Dict[str, Any]:
        return {
            "handlers_registered": len(self._handlers) + len(self._async_handlers),
            "dispatched": self._dispatched,
            "completed": self._completed,
            "failed": self._failed,
        }

    def register_handler(
        self,
        action_type: str,
        handler: ActionHandler,
        is_async: bool = False,
    ) -> None:
        """Register a handler for an action type."""
        if is_async:
            self._async_handlers[action_type] = handler
        else:
            self._handlers[action_type] = handler
        logger.info(f"Registered handler for action: {action_type}")

    def unregister_handler(self, action_type: str) -> None:
        """Remove a handler."""
        self._handlers.pop(action_type, None)
        self._async_handlers.pop(action_type, None)

    async def dispatch_actions(
        self,
        actions: List[Dict[str, Any]],
        context: Dict[str, Any],
    ) -> List[ActionResult]:
        """
        Dispatch a list of actions with the given context.

        Args:
            actions: List of action dicts, each with "action" or "type" key.
            context: Context from the policy match.

        Returns:
            List of ActionResult objects.
        """
        results = []

        for action_def in actions:
            action_type = action_def.get("action", action_def.get("type", ""))
            if not action_type:
                continue

            result = await self._dispatch_single(action_type, action_def, context)
            results.append(result)

        return results

    async def _dispatch_single(
        self,
        action_type: str,
        action_def: Dict[str, Any],
        context: Dict[str, Any],
    ) -> ActionResult:
        """Dispatch a single action."""
        self._dispatched += 1

        result = ActionResult(
            action_type=action_type,
            status=ActionStatus.DISPATCHED,
        )

        # Check for async handler
        if action_type in self._async_handlers:
            try:
                handler_result = await self._async_handlers[action_type](action_def, context)
                if isinstance(handler_result, ActionResult):
                    return handler_result
                result.status = ActionStatus.COMPLETED
                result.message = f"Action '{action_type}' completed"
                result.details = handler_result if isinstance(handler_result, dict) else {}
                self._completed += 1
            except Exception as e:
                logger.error(f"Async action '{action_type}' failed: {e}")
                result.status = ActionStatus.FAILED
                result.error = str(e)
                self._failed += 1
            return result

        # Check for sync handler
        if action_type in self._handlers:
            try:
                handler_result = self._handlers[action_type](action_def, context)
                if isinstance(handler_result, ActionResult):
                    return handler_result
                result.status = ActionStatus.COMPLETED
                result.message = f"Action '{action_type}' completed"
                result.details = handler_result if isinstance(handler_result, dict) else {}
                self._completed += 1
            except Exception as e:
                logger.error(f"Action '{action_type}' failed: {e}")
                result.status = ActionStatus.FAILED
                result.error = str(e)
                self._failed += 1
            return result

        # No handler found
        logger.warning(f"No handler registered for action: {action_type}")
        result.status = ActionStatus.SKIPPED
        result.message = f"No handler for action '{action_type}'"
        return result

    def reset(self) -> None:
        """Reset statistics."""
        self._dispatched = 0
        self._completed = 0
        self._failed = 0
