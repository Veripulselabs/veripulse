"""
Composite Risk Scoring Engine for VeriPulse.
Synthesizes syntax, DNS/MX validity, disposable domain detection, role accounts,
and provider classification into an intuitive 0-100 risk score with action advice.
"""

from typing import Dict, Any, List

class RiskEngine:
    @staticmethod
    def calculate_risk(
        is_syntax_valid: bool,
        is_disposable: bool,
        has_mx: bool,
        is_free_provider: bool,
        is_role_account: bool,
        has_typo_suggestion: bool
    ) -> Dict[str, Any]:
        """
        Calculates a deterministic risk score from 0 (pristine/safe) to 100 (high risk/fraudulent).
        """
        reasons: List[str] = []
        score: int = 0

        # Critical failure: Invalid syntax
        if not is_syntax_valid:
            return {
                "risk_score": 100,
                "risk_level": "CRITICAL",
                "recommended_action": "REJECT",
                "reasons": ["Invalid RFC email syntax"]
            }

        # Critical failure: Known disposable / burner address
        if is_disposable:
            score += 90
            reasons.append("Domain belongs to a known temporary/disposable email provider")

        # Critical failure: No mail server (cannot receive email)
        if not has_mx:
            score += 85
            reasons.append("Domain does not have valid MX or host records; emails will bounce")

        # Minor flags
        if has_typo_suggestion:
            score += 25
            reasons.append("Domain appears to be a common misspelling of a popular provider")

        if is_role_account:
            score += 15
            reasons.append("Email is a generic organizational role account (e.g. admin, sales, support)")

        # Cap score at 100
        final_score = min(100, score)

        # Classify risk level
        if final_score >= 70:
            risk_level = "HIGH"
            recommended_action = "BLOCK"
        elif final_score >= 25:
            risk_level = "MEDIUM"
            recommended_action = "FLAG_FOR_REVIEW"
        else:
            risk_level = "LOW"
            recommended_action = "ALLOW"

        if not reasons:
            reasons.append("Valid deliverable address on an active mail server")

        return {
            "risk_score": final_score,
            "risk_level": risk_level,
            "recommended_action": recommended_action,
            "reasons": reasons
        }
