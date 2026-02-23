"""Unit tests for workflow Celery tasks."""

import pytest
from unittest.mock import MagicMock, patch

from src.services.workflow.default_policies import get_default_policies


class TestDefaultPolicies:
    """Tests for default policy definitions."""

    def test_get_default_policies(self):
        """Test getting default policies."""
        policies = get_default_policies("test_company")
        assert len(policies) == 6

    def test_default_policy_names(self):
        """Test default policy names."""
        policies = get_default_policies("test_company")
        names = [p.name for p in policies]
        assert "Low Risk Monitoring" in names
        assert "Medium Risk Alert" in names
        assert "High Risk Verification" in names
        assert "Critical Risk Intervention" in names
        assert "Deepfake Detected" in names
        assert "High Value Transaction Guard" in names

    def test_low_risk_monitoring(self):
        """Test low risk monitoring policy."""
        policies = get_default_policies("c1")
        policy = next(p for p in policies if "Low Risk" in p.name)
        assert policy.min_risk_score == 0
        assert policy.max_risk_score == 30
        assert policy.trigger == "risk_score_change"
        assert any(a["action"] == "log" for a in policy.actions)

    def test_medium_risk_alert(self):
        """Test medium risk alert policy."""
        policies = get_default_policies("c1")
        policy = next(p for p in policies if "Medium Risk" in p.name)
        assert policy.min_risk_score == 31
        assert policy.max_risk_score == 60
        assert policy.cooldown_seconds == 300  # 5 minutes
        assert any(a["action"] == "alert" for a in policy.actions)

    def test_high_risk_verification(self):
        """Test high risk verification policy."""
        policies = get_default_policies("c1")
        policy = next(p for p in policies if "High Risk" in p.name)
        assert policy.min_risk_score == 61
        assert policy.max_risk_score == 85
        assert policy.cooldown_seconds == 600  # 10 minutes
        assert any(a["action"] == "verify" for a in policy.actions)
        assert any(a["action"] == "flag" for a in policy.actions)

    def test_critical_risk_intervention(self):
        """Test critical risk intervention policy."""
        policies = get_default_policies("c1")
        policy = next(p for p in policies if "Critical Risk" in p.name)
        assert policy.min_risk_score == 86
        assert policy.max_risk_score == 100
        assert any(a["action"] == "block" for a in policy.actions)
        assert any(a["action"] == "notify" for a in policy.actions)

    def test_deepfake_detected(self):
        """Test deepfake detection policy."""
        policies = get_default_policies("c1")
        policy = next(p for p in policies if "Deepfake" in p.name)
        assert policy.trigger == "deepfake_detected"
        assert policy.cooldown_seconds == 0  # No cooldown
        assert any(a["action"] == "verify" for a in policy.actions)
        assert any(a["action"] == "record" for a in policy.actions)

    def test_high_value_transaction(self):
        """Test high value transaction policy."""
        policies = get_default_policies("c1")
        policy = next(p for p in policies if "Transaction" in p.name)
        assert policy.trigger == "transaction_requested"
        assert policy.min_transaction_amount == 25000
        assert any(a["action"] == "require_approval" for a in policy.actions)
        assert any(a["action"] == "hold" for a in policy.actions)

    def test_priority_ordering(self):
        """Test that policies have sensible priority ordering."""
        policies = get_default_policies("c1")
        deepfake = next(p for p in policies if "Deepfake" in p.name)
        critical = next(p for p in policies if "Critical" in p.name)
        high = next(p for p in policies if "High Risk" in p.name)
        medium = next(p for p in policies if "Medium" in p.name)
        low = next(p for p in policies if "Low Risk" in p.name)

        # Lower number = higher priority
        assert deepfake.priority < critical.priority
        assert critical.priority < high.priority
        assert high.priority < medium.priority
        assert medium.priority < low.priority

    def test_all_policies_enabled(self):
        """Test that all default policies are enabled."""
        policies = get_default_policies("c1")
        for policy in policies:
            assert policy.is_enabled is True

    def test_company_id_set(self):
        """Test that company_id is set on all policies."""
        policies = get_default_policies("my_company")
        for policy in policies:
            assert policy.company_id == "my_company"
