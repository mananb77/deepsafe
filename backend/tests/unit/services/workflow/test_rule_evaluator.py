"""Unit tests for RuleEvaluator."""

import pytest

from src.services.workflow.rule_evaluator import RuleEvaluator


class TestRuleEvaluator:
    """Tests for RuleEvaluator."""

    def setup_method(self):
        self.evaluator = RuleEvaluator()

    def test_empty_conditions(self):
        """Test that empty conditions always match."""
        assert self.evaluator.evaluate({}, {"risk_score": 50}) is True

    def test_simple_equality(self):
        """Test simple field equality."""
        conditions = {"status": "active"}
        assert self.evaluator.evaluate(conditions, {"status": "active"}) is True
        assert self.evaluator.evaluate(conditions, {"status": "inactive"}) is False

    def test_gt_operator(self):
        """Test greater than operator."""
        conditions = {"risk_score": {"$gt": 50}}
        assert self.evaluator.evaluate(conditions, {"risk_score": 75}) is True
        assert self.evaluator.evaluate(conditions, {"risk_score": 50}) is False
        assert self.evaluator.evaluate(conditions, {"risk_score": 25}) is False

    def test_lt_operator(self):
        """Test less than operator."""
        conditions = {"risk_score": {"$lt": 50}}
        assert self.evaluator.evaluate(conditions, {"risk_score": 25}) is True
        assert self.evaluator.evaluate(conditions, {"risk_score": 75}) is False

    def test_gte_operator(self):
        """Test greater than or equal operator."""
        conditions = {"risk_score": {"$gte": 50}}
        assert self.evaluator.evaluate(conditions, {"risk_score": 50}) is True
        assert self.evaluator.evaluate(conditions, {"risk_score": 75}) is True
        assert self.evaluator.evaluate(conditions, {"risk_score": 25}) is False

    def test_lte_operator(self):
        """Test less than or equal operator."""
        conditions = {"risk_score": {"$lte": 50}}
        assert self.evaluator.evaluate(conditions, {"risk_score": 50}) is True
        assert self.evaluator.evaluate(conditions, {"risk_score": 25}) is True
        assert self.evaluator.evaluate(conditions, {"risk_score": 75}) is False

    def test_eq_operator(self):
        """Test equality operator."""
        conditions = {"level": {"$eq": "high"}}
        assert self.evaluator.evaluate(conditions, {"level": "high"}) is True
        assert self.evaluator.evaluate(conditions, {"level": "low"}) is False

    def test_neq_operator(self):
        """Test not equal operator."""
        conditions = {"level": {"$neq": "low"}}
        assert self.evaluator.evaluate(conditions, {"level": "high"}) is True
        assert self.evaluator.evaluate(conditions, {"level": "low"}) is False

    def test_in_operator(self):
        """Test in operator."""
        conditions = {"level": {"$in": ["high", "critical"]}}
        assert self.evaluator.evaluate(conditions, {"level": "high"}) is True
        assert self.evaluator.evaluate(conditions, {"level": "critical"}) is True
        assert self.evaluator.evaluate(conditions, {"level": "low"}) is False

    def test_not_in_operator(self):
        """Test not in operator."""
        conditions = {"level": {"$not_in": ["low", "info"]}}
        assert self.evaluator.evaluate(conditions, {"level": "high"}) is True
        assert self.evaluator.evaluate(conditions, {"level": "low"}) is False

    def test_contains_operator_string(self):
        """Test contains operator with string."""
        conditions = {"message": {"$contains": "urgent"}}
        assert self.evaluator.evaluate(conditions, {"message": "This is urgent"}) is True
        assert self.evaluator.evaluate(conditions, {"message": "Normal message"}) is False

    def test_contains_operator_list(self):
        """Test contains operator with list."""
        conditions = {"tags": {"$contains": "deepfake"}}
        assert self.evaluator.evaluate(conditions, {"tags": ["deepfake", "video"]}) is True
        assert self.evaluator.evaluate(conditions, {"tags": ["normal"]}) is False

    def test_between_operator(self):
        """Test between operator."""
        conditions = {"risk_score": {"$between": [30, 60]}}
        assert self.evaluator.evaluate(conditions, {"risk_score": 45}) is True
        assert self.evaluator.evaluate(conditions, {"risk_score": 30}) is True
        assert self.evaluator.evaluate(conditions, {"risk_score": 60}) is True
        assert self.evaluator.evaluate(conditions, {"risk_score": 70}) is False

    def test_exists_operator(self):
        """Test exists operator."""
        conditions = {"phone_number": {"$exists": True}}
        assert self.evaluator.evaluate(conditions, {"phone_number": "+1234567890"}) is True
        assert self.evaluator.evaluate(conditions, {"phone_number": None}) is False
        assert self.evaluator.evaluate(conditions, {}) is False

    def test_multiple_operators_on_field(self):
        """Test multiple operators on same field (AND)."""
        conditions = {"risk_score": {"$gte": 30, "$lte": 60}}
        assert self.evaluator.evaluate(conditions, {"risk_score": 45}) is True
        assert self.evaluator.evaluate(conditions, {"risk_score": 25}) is False
        assert self.evaluator.evaluate(conditions, {"risk_score": 70}) is False

    def test_multiple_fields(self):
        """Test conditions on multiple fields (implicit AND)."""
        conditions = {
            "risk_score": {"$gte": 50},
            "level": "high",
        }
        assert self.evaluator.evaluate(conditions, {"risk_score": 75, "level": "high"}) is True
        assert self.evaluator.evaluate(conditions, {"risk_score": 75, "level": "low"}) is False
        assert self.evaluator.evaluate(conditions, {"risk_score": 25, "level": "high"}) is False

    def test_and_compound(self):
        """Test explicit AND compound condition."""
        conditions = {
            "$and": [
                {"risk_score": {"$gte": 50}},
                {"level": "high"},
            ]
        }
        assert self.evaluator.evaluate(conditions, {"risk_score": 75, "level": "high"}) is True
        assert self.evaluator.evaluate(conditions, {"risk_score": 75, "level": "low"}) is False

    def test_or_compound(self):
        """Test OR compound condition."""
        conditions = {
            "$or": [
                {"risk_score": {"$gte": 80}},
                {"level": "critical"},
            ]
        }
        assert self.evaluator.evaluate(conditions, {"risk_score": 90, "level": "high"}) is True
        assert self.evaluator.evaluate(conditions, {"risk_score": 50, "level": "critical"}) is True
        assert self.evaluator.evaluate(conditions, {"risk_score": 50, "level": "low"}) is False

    def test_not_compound(self):
        """Test NOT compound condition."""
        conditions = {
            "$not": {"level": "low"}
        }
        assert self.evaluator.evaluate(conditions, {"level": "high"}) is True
        assert self.evaluator.evaluate(conditions, {"level": "low"}) is False

    def test_nested_compounds(self):
        """Test nested compound conditions."""
        conditions = {
            "$and": [
                {"risk_score": {"$gte": 50}},
                {
                    "$or": [
                        {"level": "high"},
                        {"level": "critical"},
                    ]
                },
            ]
        }
        assert self.evaluator.evaluate(conditions, {"risk_score": 75, "level": "high"}) is True
        assert self.evaluator.evaluate(conditions, {"risk_score": 75, "level": "critical"}) is True
        assert self.evaluator.evaluate(conditions, {"risk_score": 75, "level": "low"}) is False
        assert self.evaluator.evaluate(conditions, {"risk_score": 25, "level": "high"}) is False

    def test_dot_notation(self):
        """Test nested field access with dot notation."""
        conditions = {"participant.risk_score": {"$gte": 70}}
        context = {"participant": {"risk_score": 80, "name": "Test"}}
        assert self.evaluator.evaluate(conditions, context) is True

    def test_missing_field(self):
        """Test condition on missing field."""
        conditions = {"missing_field": "value"}
        assert self.evaluator.evaluate(conditions, {}) is False

    def test_type_mismatch_handled(self):
        """Test that type mismatches don't crash."""
        conditions = {"risk_score": {"$gt": 50}}
        # String comparison with number should not crash
        assert self.evaluator.evaluate(conditions, {"risk_score": "not_a_number"}) is False
