"""Unit tests for PolicyEngine."""

import pytest
import time
from unittest.mock import MagicMock

from src.services.workflow.engine import (
    PolicyEngine,
    PolicyDefinition,
    PolicyMatch,
    TriggerType,
    ActionType,
)


class TestPolicyDefinition:
    """Tests for PolicyDefinition."""

    def test_creation(self):
        """Test creating a policy definition."""
        policy = PolicyDefinition(
            policy_id="test-1",
            name="Test Policy",
            trigger="risk_score_change",
            priority=50,
        )
        assert policy.policy_id == "test-1"
        assert policy.name == "Test Policy"
        assert policy.trigger == "risk_score_change"
        assert policy.is_enabled is True

    def test_can_trigger_enabled(self):
        """Test that enabled policy can trigger."""
        policy = PolicyDefinition(
            policy_id="test-1",
            name="Test",
            is_enabled=True,
        )
        assert policy.can_trigger() is True

    def test_can_trigger_disabled(self):
        """Test that disabled policy cannot trigger."""
        policy = PolicyDefinition(
            policy_id="test-1",
            name="Test",
            is_enabled=False,
        )
        assert policy.can_trigger() is False

    def test_can_trigger_no_cooldown(self):
        """Test that policy with no cooldown can always trigger."""
        policy = PolicyDefinition(
            policy_id="test-1",
            name="Test",
            cooldown_seconds=0,
        )
        policy.record_trigger()
        assert policy.can_trigger() is True

    def test_can_trigger_in_cooldown(self):
        """Test that policy in cooldown cannot trigger."""
        policy = PolicyDefinition(
            policy_id="test-1",
            name="Test",
            cooldown_seconds=300,  # 5 minutes
        )
        policy.record_trigger()
        assert policy.can_trigger() is False

    def test_can_trigger_cooldown_expired(self):
        """Test that policy with expired cooldown can trigger."""
        policy = PolicyDefinition(
            policy_id="test-1",
            name="Test",
            cooldown_seconds=1,
        )
        policy.last_triggered_at = time.time() - 2  # 2 seconds ago
        assert policy.can_trigger() is True

    def test_record_trigger(self):
        """Test recording a trigger."""
        policy = PolicyDefinition(
            policy_id="test-1",
            name="Test",
        )
        assert policy.last_triggered_at is None
        policy.record_trigger()
        assert policy.last_triggered_at is not None


class TestPolicyMatch:
    """Tests for PolicyMatch."""

    def test_creation(self):
        """Test creating a policy match."""
        policy = PolicyDefinition(policy_id="p1", name="Test")
        match = PolicyMatch(
            policy=policy,
            actions=[{"action": "alert"}, {"action": "log"}],
            trigger="risk_score_change",
            context={"risk_score": 80},
        )
        assert match.policy == policy
        assert len(match.actions) == 2
        assert match.trigger == "risk_score_change"

    def test_get_action_types(self):
        """Test getting action type strings."""
        policy = PolicyDefinition(policy_id="p1", name="Test")
        match = PolicyMatch(
            policy=policy,
            actions=[{"action": "verify"}, {"action": "alert"}, {"action": "log"}],
            trigger="risk_score_change",
            context={},
        )
        types = match.get_action_types()
        assert types == ["verify", "alert", "log"]


class TestPolicyEngine:
    """Tests for PolicyEngine."""

    def test_creation(self):
        """Test creating an engine."""
        engine = PolicyEngine()
        assert engine.stats["total_policies"] == 0
        assert engine.stats["evaluations"] == 0

    def test_register_policy(self):
        """Test registering a policy."""
        engine = PolicyEngine()
        policy = PolicyDefinition(
            policy_id="p1",
            name="Test",
            company_id="c1",
        )
        engine.register_policy(policy)
        assert engine.stats["total_policies"] == 1

    def test_remove_policy(self):
        """Test removing a policy."""
        engine = PolicyEngine()
        policy = PolicyDefinition(
            policy_id="p1",
            name="Test",
            company_id="c1",
        )
        engine.register_policy(policy)
        assert engine.remove_policy("p1", "c1") is True
        assert engine.stats["total_policies"] == 0

    def test_remove_nonexistent_policy(self):
        """Test removing a nonexistent policy."""
        engine = PolicyEngine()
        assert engine.remove_policy("nonexistent", "c1") is False

    def test_get_policies(self):
        """Test getting policies for a company."""
        engine = PolicyEngine()
        for i in range(3):
            engine.register_policy(PolicyDefinition(
                policy_id=f"p{i}",
                name=f"Policy {i}",
                company_id="c1",
            ))
        policies = engine.get_policies("c1")
        assert len(policies) == 3

    def test_evaluate_no_policies(self):
        """Test evaluation with no policies."""
        engine = PolicyEngine()
        matches = engine.evaluate("risk_score_change", {"risk_score": 50})
        assert len(matches) == 0
        assert engine.stats["evaluations"] == 1

    def test_evaluate_matching_trigger(self):
        """Test evaluation with matching trigger."""
        engine = PolicyEngine()
        engine.register_policy(PolicyDefinition(
            policy_id="p1",
            name="Risk Alert",
            trigger="risk_score_change",
            min_risk_score=50,
            actions=[{"action": "alert"}],
        ))
        matches = engine.evaluate(
            "risk_score_change",
            {"risk_score": 75},
        )
        assert len(matches) == 1
        assert matches[0].actions[0]["action"] == "alert"

    def test_evaluate_non_matching_trigger(self):
        """Test evaluation with non-matching trigger."""
        engine = PolicyEngine()
        engine.register_policy(PolicyDefinition(
            policy_id="p1",
            name="Risk Alert",
            trigger="deepfake_detected",
            actions=[{"action": "alert"}],
        ))
        matches = engine.evaluate(
            "risk_score_change",
            {"risk_score": 75},
        )
        assert len(matches) == 0

    def test_evaluate_risk_score_below_threshold(self):
        """Test that low risk score doesn't match."""
        engine = PolicyEngine()
        engine.register_policy(PolicyDefinition(
            policy_id="p1",
            name="High Risk",
            trigger="risk_score_change",
            min_risk_score=80,
            actions=[{"action": "verify"}],
        ))
        matches = engine.evaluate(
            "risk_score_change",
            {"risk_score": 50},
        )
        assert len(matches) == 0

    def test_evaluate_risk_score_range(self):
        """Test risk score range matching."""
        engine = PolicyEngine()
        engine.register_policy(PolicyDefinition(
            policy_id="p1",
            name="Medium Risk",
            trigger="risk_score_change",
            min_risk_score=30,
            max_risk_score=60,
            actions=[{"action": "alert"}],
        ))
        # In range
        matches = engine.evaluate("risk_score_change", {"risk_score": 45})
        assert len(matches) == 1
        # Above range
        matches = engine.evaluate("risk_score_change", {"risk_score": 70})
        assert len(matches) == 0

    def test_evaluate_transaction_amount(self):
        """Test transaction amount matching."""
        engine = PolicyEngine()
        engine.register_policy(PolicyDefinition(
            policy_id="p1",
            name="Large Transaction",
            trigger="transaction_requested",
            min_transaction_amount=25000,
            actions=[{"action": "hold"}],
        ))
        matches = engine.evaluate(
            "transaction_requested",
            {"transaction_amount": 50000},
        )
        assert len(matches) == 1

    def test_evaluate_transaction_below_threshold(self):
        """Test transaction below threshold doesn't match."""
        engine = PolicyEngine()
        engine.register_policy(PolicyDefinition(
            policy_id="p1",
            name="Large Transaction",
            trigger="transaction_requested",
            min_transaction_amount=25000,
            actions=[{"action": "hold"}],
        ))
        matches = engine.evaluate(
            "transaction_requested",
            {"transaction_amount": 10000},
        )
        assert len(matches) == 0

    def test_evaluate_cooldown_prevents_match(self):
        """Test that cooldown prevents re-matching."""
        engine = PolicyEngine()
        engine.register_policy(PolicyDefinition(
            policy_id="p1",
            name="Alert",
            trigger="risk_score_change",
            actions=[{"action": "alert"}],
            cooldown_seconds=300,
        ))
        # First match
        matches1 = engine.evaluate("risk_score_change", {"risk_score": 50})
        assert len(matches1) == 1

        # Second match should be blocked by cooldown
        matches2 = engine.evaluate("risk_score_change", {"risk_score": 50})
        assert len(matches2) == 0

    def test_evaluate_priority_order(self):
        """Test policies are evaluated in priority order."""
        engine = PolicyEngine()
        engine.register_policy(PolicyDefinition(
            policy_id="low",
            name="Low Priority",
            trigger="risk_score_change",
            priority=100,
            actions=[{"action": "log"}],
        ))
        engine.register_policy(PolicyDefinition(
            policy_id="high",
            name="High Priority",
            trigger="risk_score_change",
            priority=10,
            actions=[{"action": "verify"}],
        ))
        matches = engine.evaluate("risk_score_change", {"risk_score": 50})
        assert len(matches) == 2
        # High priority (10) should be first
        assert matches[0].policy.name == "High Priority"
        assert matches[1].policy.name == "Low Priority"

    def test_evaluate_disabled_policy_skipped(self):
        """Test that disabled policies are skipped."""
        engine = PolicyEngine()
        engine.register_policy(PolicyDefinition(
            policy_id="p1",
            name="Disabled",
            trigger="risk_score_change",
            is_enabled=False,
            actions=[{"action": "alert"}],
        ))
        matches = engine.evaluate("risk_score_change", {"risk_score": 50})
        assert len(matches) == 0

    def test_evaluate_custom_conditions(self):
        """Test custom condition evaluation."""
        engine = PolicyEngine()
        engine.register_policy(PolicyDefinition(
            policy_id="p1",
            name="Custom Condition",
            trigger="risk_score_change",
            conditions={"risk_score": {"$gte": 70}},
            actions=[{"action": "alert"}],
        ))
        matches = engine.evaluate("risk_score_change", {"risk_score": 80})
        assert len(matches) == 1

        matches = engine.evaluate("risk_score_change", {"risk_score": 50})
        assert len(matches) == 0

    def test_evaluate_company_isolation(self):
        """Test that policies are isolated per company."""
        engine = PolicyEngine()
        engine.register_policy(PolicyDefinition(
            policy_id="p1",
            name="Company A Policy",
            company_id="company_a",
            trigger="risk_score_change",
            actions=[{"action": "alert"}],
        ))
        engine.register_policy(PolicyDefinition(
            policy_id="p2",
            name="Company B Policy",
            company_id="company_b",
            trigger="risk_score_change",
            actions=[{"action": "verify"}],
        ))
        matches_a = engine.evaluate("risk_score_change", {}, company_id="company_a")
        assert len(matches_a) == 1
        assert matches_a[0].policy.name == "Company A Policy"

    def test_evaluate_stats(self):
        """Test that evaluation updates statistics."""
        engine = PolicyEngine()
        engine.register_policy(PolicyDefinition(
            policy_id="p1",
            name="Test",
            trigger="risk_score_change",
            actions=[{"action": "alert"}],
        ))
        engine.evaluate("risk_score_change", {})
        assert engine.stats["evaluations"] == 1
        assert engine.stats["matches"] == 1

    def test_reset(self):
        """Test engine reset."""
        engine = PolicyEngine()
        engine.register_policy(PolicyDefinition(
            policy_id="p1",
            name="Test",
        ))
        engine.reset()
        assert engine.stats["total_policies"] == 0
        assert engine.stats["evaluations"] == 0
