"""
Unit tests for VeriPulse core engines.
"""

import pytest
from core.email_checker import EmailChecker
from core.disposable_filter import DisposableFilter
from core.risk_engine import RiskEngine

@pytest.fixture
def disposable_filter():
    return DisposableFilter()

def test_syntax_validation():
    # Valid email
    res1 = EmailChecker.parse_and_validate_syntax("clean.user@example.com")
    assert res1["is_syntax_valid"] is True
    assert res1["local_part"] == "clean.user"
    assert res1["domain"] == "example.com"

    # Invalid email
    res2 = EmailChecker.parse_and_validate_syntax("not-an-email")
    assert res2["is_syntax_valid"] is False

    # Empty email
    res3 = EmailChecker.parse_and_validate_syntax("")
    assert res3["is_syntax_valid"] is False

    # Security check: Reject oversized string (payload bombing)
    res4 = EmailChecker.parse_and_validate_syntax("a" * 300 + "@example.com")
    assert res4["is_syntax_valid"] is False
    assert "maximum allowed length" in res4["error"]

def test_disposable_domain_detection(disposable_filter):
    # Common disposable domains
    assert disposable_filter.is_disposable("mailinator.com") is True
    assert disposable_filter.is_disposable("10minutemail.com") is True
    assert disposable_filter.is_disposable("tempmail.com") is True
    assert disposable_filter.is_disposable("sub.mailinator.com") is True

    # Legitimate domains
    assert disposable_filter.is_disposable("google.com") is False
    assert disposable_filter.is_disposable("microsoft.com") is False
    assert disposable_filter.is_disposable("stripe.com") is False

def test_typo_suggestion():
    assert EmailChecker.suggest_typo_correction("gmai.com") == "gmail.com"
    assert EmailChecker.suggest_typo_correction("hotmial.com") == "hotmail.com"
    assert EmailChecker.suggest_typo_correction("google.com") is None

def test_role_account_detection():
    assert EmailChecker.check_role_account("admin") is True
    assert EmailChecker.check_role_account("support") is True
    assert EmailChecker.check_role_account("billing") is True
    assert EmailChecker.check_role_account("john.doe") is False

def test_risk_scoring():
    # Safe corporate email
    safe = RiskEngine.calculate_risk(
        is_syntax_valid=True,
        is_disposable=False,
        has_mx=True,
        is_free_provider=False,
        is_role_account=False,
        has_typo_suggestion=False
    )
    assert safe["risk_score"] < 25
    assert safe["risk_level"] == "LOW"
    assert safe["recommended_action"] == "ALLOW"

    # Burner disposable email
    burner = RiskEngine.calculate_risk(
        is_syntax_valid=True,
        is_disposable=True,
        has_mx=True,
        is_free_provider=False,
        is_role_account=False,
        has_typo_suggestion=False
    )
    assert burner["risk_score"] >= 70
    assert burner["risk_level"] == "HIGH"
    assert burner["recommended_action"] == "BLOCK"
