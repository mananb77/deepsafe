"""
Rule Evaluator

Extends policy condition matching with operator support
and compound conditions (AND/OR groups).

Operators: gt, lt, gte, lte, eq, neq, in, not_in, contains, between
Compound: {"and": [...]}, {"or": [...]}
"""

import logging
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class RuleEvaluator:
    """
    Evaluates policy conditions against a context dictionary.

    Supports:
    - Simple equality: {"field": "value"}
    - Operators: {"field": {"$gt": 50}}
    - Compound conditions: {"$and": [...]}, {"$or": [...]}
    """

    OPERATORS = {
        "$gt": lambda a, b: a > b,
        "$lt": lambda a, b: a < b,
        "$gte": lambda a, b: a >= b,
        "$lte": lambda a, b: a <= b,
        "$eq": lambda a, b: a == b,
        "$neq": lambda a, b: a != b,
        "$ne": lambda a, b: a != b,
        "$in": lambda a, b: a in b,
        "$not_in": lambda a, b: a not in b,
        "$nin": lambda a, b: a not in b,
        "$contains": lambda a, b: b in a if isinstance(a, (str, list, dict)) else False,
        "$between": lambda a, b: b[0] <= a <= b[1] if isinstance(b, (list, tuple)) and len(b) == 2 else False,
        "$exists": lambda a, b: (a is not None) == b,
    }

    def evaluate(self, conditions: Dict[str, Any], context: Dict[str, Any]) -> bool:
        """
        Evaluate conditions against context.

        Args:
            conditions: Condition dictionary.
            context: Context dictionary with values to check.

        Returns:
            True if all conditions are met.
        """
        if not conditions:
            return True

        return self._evaluate_node(conditions, context)

    def _evaluate_node(self, node: Any, context: Dict[str, Any]) -> bool:
        """Evaluate a condition node (may be compound or simple)."""
        if not isinstance(node, dict):
            return bool(node)

        # Check for compound operators
        if "$and" in node:
            return self._evaluate_and(node["$and"], context)
        if "$or" in node:
            return self._evaluate_or(node["$or"], context)
        if "$not" in node:
            return not self._evaluate_node(node["$not"], context)

        # Evaluate each field condition (implicit AND)
        for field, condition in node.items():
            if field.startswith("$"):
                continue
            if not self._evaluate_field(field, condition, context):
                return False

        return True

    def _evaluate_and(self, conditions: List[Dict], context: Dict[str, Any]) -> bool:
        """Evaluate AND group."""
        if not conditions:
            return True
        return all(self._evaluate_node(c, context) for c in conditions)

    def _evaluate_or(self, conditions: List[Dict], context: Dict[str, Any]) -> bool:
        """Evaluate OR group."""
        if not conditions:
            return True
        return any(self._evaluate_node(c, context) for c in conditions)

    def _evaluate_field(
        self,
        field: str,
        condition: Any,
        context: Dict[str, Any],
    ) -> bool:
        """
        Evaluate a single field condition.

        Args:
            field: Context field name (supports dot notation).
            condition: Expected value or operator dict.
            context: Context dictionary.
        """
        value = self._get_nested_value(context, field)

        # Operator dict: {"$gt": 50, "$lt": 100}
        if isinstance(condition, dict):
            for op, expected in condition.items():
                if op in self.OPERATORS:
                    try:
                        if not self.OPERATORS[op](value, expected):
                            return False
                    except (TypeError, ValueError):
                        return False
                else:
                    # Nested field comparison
                    if not self._evaluate_field(op, expected, context):
                        return False
            return True

        # Simple equality
        return value == condition

    def _get_nested_value(self, data: Dict[str, Any], path: str) -> Any:
        """Get value from nested dict using dot notation."""
        keys = path.split(".")
        current = data
        for key in keys:
            if isinstance(current, dict) and key in current:
                current = current[key]
            else:
                return None
        return current
