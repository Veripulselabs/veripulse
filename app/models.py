"""
Pydantic schemas for VeriPulse API requests and responses.
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any

class MXRecord(BaseModel):
    preference: int = Field(..., description="MX priority preference (lower is higher priority)")
    exchange: str = Field(..., description="Mail server hostname")

class EmailVerificationResponse(BaseModel):
    email: str = Field(..., description="The queried email address")
    normalized_email: str = Field(..., description="Standardized lowercase email address")
    is_valid: bool = Field(..., description="Overall deliverability status (syntax valid & active mail server)")
    is_syntax_valid: bool = Field(..., description="Conforms to standard RFC email formatting")
    is_disposable: bool = Field(..., description="True if domain is a known burner/disposable email provider")
    has_mx_records: bool = Field(..., description="True if domain has active mail routing (MX or A fallback)")
    is_free_provider: bool = Field(..., description="True if provided by consumer webmail (Gmail, Yahoo, Outlook, etc.)")
    is_role_account: bool = Field(..., description="True if account is generic alias (e.g., admin, support, sales)")
    did_you_mean: Optional[str] = Field(None, description="Suggested domain correction if a common typo was detected")
    risk_score: int = Field(..., ge=0, le=100, description="Risk rating from 0 (safe) to 100 (high risk/fraudulent)")
    risk_level: str = Field(..., description="Risk tier: LOW, MEDIUM, HIGH, or CRITICAL")
    recommended_action: str = Field(..., description="Recommended signup action: ALLOW, FLAG_FOR_REVIEW, or BLOCK")
    reasons: List[str] = Field(default_factory=list, description="Explanatory signals contributing to the score")
    mx_records: List[Dict[str, Any]] = Field(default_factory=list, description="Discovered mail exchange records")

class BatchVerificationRequest(BaseModel):
    emails: List[str] = Field(..., min_length=1, max_length=50, description="List of emails to verify (max 50 per batch)")

class BatchVerificationResponse(BaseModel):
    total_processed: int = Field(..., description="Number of emails evaluated in the batch")
    results: List[EmailVerificationResponse] = Field(..., description="Individual verification results")

class DomainHealthResponse(BaseModel):
    domain: str = Field(..., description="Domain queried")
    has_mail_server: bool = Field(..., description="Whether the domain can accept emails")
    is_disposable: bool = Field(..., description="Whether the domain is on the disposable blocklist")
    primary_mail_server: Optional[str] = Field(None, description="Primary MX exchange hostname")
    mx_records: List[Dict[str, Any]] = Field(default_factory=list, description="All MX records found")
    status: str = Field(..., description="HEALTHY, NO_MAIL_SERVER, or DISPOSABLE")
