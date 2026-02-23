"""
Default Policy Definitions

6 default policies per the TDD:
1. low_risk_monitoring (0-30%): Log only
2. medium_risk_alert (31-60%): Dashboard + overlay alert, 5min cooldown
3. high_risk_verification (61-85%): SMS verification + flag, 10min cooldown
4. critical_risk_intervention (86-100%): All channels + block + notify security team
5. deepfake_detected: Immediate verification + recording on deepfake incidents
6. high_value_transaction: Approval required for >$25K transactions
"""

from typing import List

from src.services.workflow.engine import PolicyDefinition


def get_default_policies(company_id: str = "__default__") -> List[PolicyDefinition]:
    """
    Get the 6 default policy definitions.

    Args:
        company_id: Company to associate policies with.

    Returns:
        List of PolicyDefinition objects.
    """
    return [
        # 1. Low Risk Monitoring (0-30%)
        PolicyDefinition(
            policy_id=f"{company_id}_low_risk_monitoring",
            name="Low Risk Monitoring",
            description="Log activity when risk score is between 0-30%",
            trigger="risk_score_change",
            priority=100,
            is_enabled=True,
            min_risk_score=0,
            max_risk_score=30,
            conditions={},
            actions=[
                {"action": "log", "level": "info"},
            ],
            cooldown_seconds=0,
            company_id=company_id,
        ),

        # 2. Medium Risk Alert (31-60%)
        PolicyDefinition(
            policy_id=f"{company_id}_medium_risk_alert",
            name="Medium Risk Alert",
            description="Dashboard + overlay alert when risk is 31-60%",
            trigger="risk_score_change",
            priority=80,
            is_enabled=True,
            min_risk_score=31,
            max_risk_score=60,
            conditions={},
            actions=[
                {"action": "alert", "channels": ["websocket", "dashboard"]},
                {"action": "log", "level": "warning"},
            ],
            cooldown_seconds=300,  # 5 minutes
            company_id=company_id,
        ),

        # 3. High Risk Verification (61-85%)
        PolicyDefinition(
            policy_id=f"{company_id}_high_risk_verification",
            name="High Risk Verification",
            description="SMS verification + flag participant when risk is 61-85%",
            trigger="risk_score_change",
            priority=50,
            is_enabled=True,
            min_risk_score=61,
            max_risk_score=85,
            conditions={},
            actions=[
                {"action": "verify", "channel": "sms"},
                {"action": "flag", "trust_level": "suspicious"},
                {"action": "alert", "channels": ["websocket", "notification"]},
                {"action": "log", "level": "high"},
            ],
            cooldown_seconds=600,  # 10 minutes
            company_id=company_id,
        ),

        # 4. Critical Risk Intervention (86-100%)
        PolicyDefinition(
            policy_id=f"{company_id}_critical_risk_intervention",
            name="Critical Risk Intervention",
            description="All channels + block + notify security team for critical risk",
            trigger="risk_score_change",
            priority=10,
            is_enabled=True,
            min_risk_score=86,
            max_risk_score=100,
            conditions={},
            actions=[
                {"action": "verify", "channel": "all"},
                {"action": "block", "target": "screen_share"},
                {"action": "flag", "trust_level": "blocked"},
                {"action": "notify", "channels": ["sms", "email", "push"], "target": "security_team"},
                {"action": "alert", "channels": ["websocket", "notification", "sms"]},
                {"action": "log", "level": "critical"},
            ],
            cooldown_seconds=60,  # 1 minute (urgent, short cooldown)
            company_id=company_id,
        ),

        # 5. Deepfake Detected
        PolicyDefinition(
            policy_id=f"{company_id}_deepfake_detected",
            name="Deepfake Detected",
            description="Immediate verification + recording on deepfake detection",
            trigger="deepfake_detected",
            priority=5,
            is_enabled=True,
            conditions={},
            actions=[
                {"action": "verify", "channel": "sms"},
                {"action": "record", "reason": "deepfake_detected"},
                {"action": "flag", "trust_level": "suspicious"},
                {"action": "alert", "channels": ["websocket", "notification", "sms"]},
                {"action": "notify", "channels": ["email"], "target": "security_team"},
                {"action": "log", "level": "critical"},
            ],
            cooldown_seconds=0,  # No cooldown for deepfake detection
            company_id=company_id,
        ),

        # 6. High Value Transaction
        PolicyDefinition(
            policy_id=f"{company_id}_high_value_transaction",
            name="High Value Transaction Guard",
            description="Require approval for transactions exceeding $25,000",
            trigger="transaction_requested",
            priority=20,
            is_enabled=True,
            min_transaction_amount=25000,
            conditions={},
            actions=[
                {"action": "require_approval", "approvers": ["security_team", "finance_team"]},
                {"action": "hold", "duration_hours": 24},
                {"action": "notify", "channels": ["email", "sms"], "target": "finance_team"},
                {"action": "log", "level": "high"},
            ],
            cooldown_seconds=0,
            company_id=company_id,
        ),
    ]
