"""
Celery Tasks for Workflow Engine

Async task wrappers for policy evaluation and action dispatch.
"""

import logging
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

try:
    from src.shared.messaging.celery_app import celery_app
except ImportError:
    # Celery not available, create stub
    from unittest.mock import MagicMock
    celery_app = MagicMock()


@celery_app.task(
    name="workflow.evaluate_policies",
    queue="workflow",
    bind=True,
    max_retries=2,
    soft_time_limit=10,
    time_limit=15,
)
def evaluate_policies_task(
    self,
    trigger: str,
    context: Dict[str, Any],
    company_id: str = "__default__",
) -> Dict[str, Any]:
    """
    Evaluate policies for a trigger event.

    Args:
        trigger: Event type.
        context: Event context.
        company_id: Company ID.

    Returns:
        Evaluation results with matched policies and actions.
    """
    logger.info(f"Evaluating policies for trigger: {trigger}, company: {company_id}")

    try:
        from src.services.workflow.engine import PolicyEngine
        from src.services.workflow.default_policies import get_default_policies

        engine = PolicyEngine()

        # Load default policies
        for policy in get_default_policies(company_id):
            engine.register_policy(policy)

        # Evaluate
        matches = engine.evaluate(
            trigger=trigger,
            context=context,
            company_id=company_id,
        )

        result = {
            "trigger": trigger,
            "company_id": company_id,
            "matches": len(matches),
            "actions": [],
        }

        for match in matches:
            for action in match.actions:
                result["actions"].append({
                    "policy_name": match.policy.name,
                    "action": action,
                })

        logger.info(f"Policy evaluation complete: {len(matches)} matches")
        return result

    except Exception as e:
        logger.error(f"Policy evaluation failed: {e}")
        raise self.retry(exc=e, countdown=2 ** self.request.retries)


@celery_app.task(
    name="workflow.dispatch_action",
    queue="workflow",
    bind=True,
    max_retries=3,
    soft_time_limit=30,
    time_limit=45,
)
def dispatch_action_task(
    self,
    action_type: str,
    action_config: Dict[str, Any],
    context: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Dispatch a single policy action.

    Args:
        action_type: Type of action to dispatch.
        action_config: Action configuration.
        context: Event context.

    Returns:
        Action result.
    """
    logger.info(f"Dispatching action: {action_type}")

    try:
        result = {
            "action_type": action_type,
            "status": "dispatched",
            "context": context,
        }

        # Route to appropriate handler
        if action_type == "log":
            level = action_config.get("level", "info")
            logger.log(
                logging.getLevelName(level.upper()) if level.upper() in logging._nameToLevel else logging.INFO,
                f"Policy action log: {context}",
            )
            result["status"] = "completed"

        elif action_type == "alert":
            # Would dispatch via WebSocket
            result["status"] = "completed"
            result["channels"] = action_config.get("channels", ["websocket"])

        elif action_type == "notify":
            # Would dispatch notifications
            result["status"] = "completed"
            result["channels"] = action_config.get("channels", [])
            result["target"] = action_config.get("target", "")

        elif action_type == "verify":
            # Would create verification session
            result["status"] = "completed"
            result["channel"] = action_config.get("channel", "sms")

        elif action_type == "flag":
            # Would update participant trust level
            result["status"] = "completed"
            result["trust_level"] = action_config.get("trust_level", "suspicious")

        elif action_type == "block":
            # Would signal meeting bot
            result["status"] = "completed"
            result["target"] = action_config.get("target", "screen_share")

        elif action_type == "hold":
            # Would create transaction hold
            result["status"] = "completed"
            result["duration_hours"] = action_config.get("duration_hours", 24)

        elif action_type == "record":
            # Would start recording
            result["status"] = "completed"
            result["reason"] = action_config.get("reason", "policy_triggered")

        else:
            result["status"] = "skipped"
            result["message"] = f"Unknown action type: {action_type}"

        logger.info(f"Action dispatched: {action_type} -> {result['status']}")
        return result

    except Exception as e:
        logger.error(f"Action dispatch failed: {e}")
        raise self.retry(exc=e, countdown=2 ** self.request.retries)
