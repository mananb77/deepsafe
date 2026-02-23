"""
Policy Engine

Core evaluator that receives events, evaluates policies, and returns
matched actions. This is the central piece connecting detection to response.

Flow:
1. Event arrives (risk_score_change, deepfake_detected, etc.)
2. Fetch enabled policies for the company, sorted by priority
3. Filter by trigger type
4. Evaluate conditions using RuleEvaluator
5. Check cooldowns
6. Return matched PolicyMatch objects with actions to execute
"""

import logging
import time
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Callable, Dict, List, Optional

from src.services.workflow.rule_evaluator import RuleEvaluator

logger = logging.getLogger(__name__)


class TriggerType(str, Enum):
    """Events that can trigger policy evaluation."""
    RISK_SCORE_CHANGE = "risk_score_change"
    DEEPFAKE_DETECTED = "deepfake_detected"
    SOCIAL_ENGINEERING_DETECTED = "social_engineering_detected"
    TRANSACTION_REQUESTED = "transaction_requested"
    MEETING_START = "meeting_start"
    PARTICIPANT_JOIN = "participant_join"
    VERIFICATION_FAILED = "verification_failed"
    VERIFICATION_REQUESTED = "verification_requested"


class ActionType(str, Enum):
    """Actions that policies can trigger."""
    VERIFY = "verify"
    ALERT = "alert"
    NOTIFY = "notify"
    BLOCK = "block"
    FLAG = "flag"
    LOG = "log"
    HOLD = "hold"
    RECORD = "record"
    REQUIRE_APPROVAL = "require_approval"


@dataclass
class PolicyDefinition:
    """
    In-memory policy definition for evaluation.

    Can be populated from the Policy DB model or from default_policies.
    """
    policy_id: str
    name: str
    description: str = ""
    trigger: str = ""  # TriggerType value
    priority: int = 100  # Lower = higher priority
    is_enabled: bool = True

    # Conditions
    conditions: Dict[str, Any] = field(default_factory=dict)
    min_risk_score: Optional[float] = None
    max_risk_score: Optional[float] = None
    min_transaction_amount: Optional[float] = None

    # Actions
    actions: List[Dict[str, Any]] = field(default_factory=list)

    # Cooldown
    cooldown_seconds: int = 0
    last_triggered_at: Optional[float] = None  # Unix timestamp

    # Extra
    company_id: str = ""
    extra_data: Dict[str, Any] = field(default_factory=dict)

    def can_trigger(self) -> bool:
        """Check if policy can trigger (not in cooldown)."""
        if not self.is_enabled:
            return False
        if self.cooldown_seconds == 0:
            return True
        if self.last_triggered_at is None:
            return True
        elapsed = time.time() - self.last_triggered_at
        return elapsed >= self.cooldown_seconds

    def record_trigger(self) -> None:
        """Record that policy was triggered."""
        self.last_triggered_at = time.time()


@dataclass
class PolicyMatch:
    """Result of a policy evaluation match."""
    policy: PolicyDefinition
    actions: List[Dict[str, Any]]
    trigger: str
    context: Dict[str, Any]
    matched_at: datetime = field(default_factory=datetime.utcnow)

    def get_action_types(self) -> List[str]:
        """Get list of action type strings."""
        return [a.get("action", a.get("type", "")) for a in self.actions]


class PolicyEngine:
    """
    Core policy evaluation engine.

    Evaluates events against registered policies and returns
    matched actions to be dispatched.

    Usage:
        engine = PolicyEngine()
        engine.register_policy(policy_def)

        matches = engine.evaluate(
            trigger="risk_score_change",
            context={"risk_score": 85, "participant_id": "p1"},
            company_id="company-1",
        )

        for match in matches:
            for action in match.actions:
                dispatcher.dispatch(action, match.context)
    """

    def __init__(self):
        # Policies indexed by company_id
        self._policies: Dict[str, List[PolicyDefinition]] = {}
        self._rule_evaluator = RuleEvaluator()

        # Statistics
        self._evaluations = 0
        self._matches = 0

    @property
    def stats(self) -> Dict[str, Any]:
        """Get engine statistics."""
        total_policies = sum(len(p) for p in self._policies.values())
        return {
            "total_policies": total_policies,
            "companies": len(self._policies),
            "evaluations": self._evaluations,
            "matches": self._matches,
        }

    def register_policy(self, policy: PolicyDefinition) -> None:
        """Register a policy for evaluation."""
        company_id = policy.company_id or "__default__"
        if company_id not in self._policies:
            self._policies[company_id] = []
        self._policies[company_id].append(policy)
        # Keep sorted by priority
        self._policies[company_id].sort(key=lambda p: p.priority)

    def remove_policy(self, policy_id: str, company_id: str = "__default__") -> bool:
        """Remove a policy by ID."""
        if company_id not in self._policies:
            return False
        before = len(self._policies[company_id])
        self._policies[company_id] = [
            p for p in self._policies[company_id] if p.policy_id != policy_id
        ]
        return len(self._policies[company_id]) < before

    def get_policies(self, company_id: str = "__default__") -> List[PolicyDefinition]:
        """Get policies for a company."""
        return list(self._policies.get(company_id, []))

    def evaluate(
        self,
        trigger: str,
        context: Dict[str, Any],
        company_id: str = "__default__",
    ) -> List[PolicyMatch]:
        """
        Evaluate policies against a trigger event.

        Args:
            trigger: Event type (TriggerType value).
            context: Event context (risk_score, participant_id, etc.).
            company_id: Company to evaluate policies for.

        Returns:
            List of PolicyMatch objects for matched policies.
        """
        self._evaluations += 1
        matches: List[PolicyMatch] = []

        # Get policies for company + defaults
        policies = list(self._policies.get(company_id, []))
        if company_id != "__default__":
            policies.extend(self._policies.get("__default__", []))

        # Sort by priority
        policies.sort(key=lambda p: p.priority)

        for policy in policies:
            if not policy.is_enabled:
                continue

            # Filter by trigger type
            if policy.trigger and policy.trigger != trigger:
                continue

            # Check cooldown
            if not policy.can_trigger():
                continue

            # Evaluate conditions
            if not self._evaluate_conditions(policy, context):
                continue

            # Match found
            match = PolicyMatch(
                policy=policy,
                actions=list(policy.actions),
                trigger=trigger,
                context=dict(context),
            )
            matches.append(match)
            policy.record_trigger()
            self._matches += 1

        return matches

    def _evaluate_conditions(
        self,
        policy: PolicyDefinition,
        context: Dict[str, Any],
    ) -> bool:
        """Evaluate all conditions for a policy."""
        # Check risk score thresholds
        if "risk_score" in context:
            risk_score = context["risk_score"]
            if policy.min_risk_score is not None and risk_score < policy.min_risk_score:
                return False
            if policy.max_risk_score is not None and risk_score > policy.max_risk_score:
                return False

        # Check transaction amount
        if "transaction_amount" in context and policy.min_transaction_amount is not None:
            if context["transaction_amount"] < policy.min_transaction_amount:
                return False

        # Evaluate custom conditions via RuleEvaluator
        if policy.conditions:
            if not self._rule_evaluator.evaluate(policy.conditions, context):
                return False

        return True

    def reset(self) -> None:
        """Reset engine state and statistics."""
        self._policies.clear()
        self._evaluations = 0
        self._matches = 0
