"""
VeriPulse API - Main FastAPI Entry Point.
Production-ready microservice designed for seamless RapidAPI listing.
"""

import asyncio
from typing import Optional
from fastapi import FastAPI, Query, Header, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.config import settings
from app.models import (
    EmailVerificationResponse,
    BatchVerificationRequest,
    BatchVerificationResponse,
    DomainHealthResponse
)
from core.email_checker import EmailChecker
from core.disposable_filter import is_disposable_domain
from core.dns_resolver import check_mx
from core.risk_engine import RiskEngine

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description=settings.DESCRIPTION,
    docs_url="/docs",
    redoc_url="/redoc"
)

# Enable CORS for cross-origin browser queries
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def verify_rapidapi_secret(x_rapidapi_proxy_secret: Optional[str] = Header(None)):
    """
    Validates that incoming request originated from RapidAPI proxy when configured.
    If RAPIDAPI_PROXY_SECRET is unset (e.g. local dev), requests are allowed.
    """
    if settings.RAPIDAPI_PROXY_SECRET:
        if not x_rapidapi_proxy_secret or x_rapidapi_proxy_secret != settings.RAPIDAPI_PROXY_SECRET:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Direct unauthorized access prohibited. Please query via RapidAPI."
            )
    return True

async def _process_single_email(email_str: str) -> EmailVerificationResponse:
    """Core evaluation pipeline for an individual email address."""
    # 1. Parse and validate syntax
    syntax_result = EmailChecker.parse_and_validate_syntax(email_str)
    
    if not syntax_result["is_syntax_valid"]:
        risk = RiskEngine.calculate_risk(
            is_syntax_valid=False,
            is_disposable=False,
            has_mx=False,
            is_free_provider=False,
            is_role_account=False,
            has_typo_suggestion=False
        )
        return EmailVerificationResponse(
            email=email_str,
            normalized_email=syntax_result["normalized_email"],
            is_valid=False,
            is_syntax_valid=False,
            is_disposable=False,
            has_mx_records=False,
            is_free_provider=False,
            is_role_account=False,
            did_you_mean=None,
            risk_score=risk["risk_score"],
            risk_level=risk["risk_level"],
            recommended_action=risk["recommended_action"],
            reasons=risk["reasons"],
            mx_records=[]
        )

    local_part = syntax_result["local_part"]
    domain = syntax_result["domain"]

    # 2. Parallel domain checks: disposable lookup, typo detection, role account, free provider
    is_disposable = is_disposable_domain(domain)
    is_role = EmailChecker.check_role_account(local_part)
    is_free = EmailChecker.check_free_provider(domain)
    typo_suggestion = EmailChecker.suggest_typo_correction(domain)

    # 3. DNS MX resolution
    has_mx, mx_records, primary_host = await check_mx(domain)

    # 4. Overall validity: syntax must be valid AND domain must have active mail routing
    is_valid = syntax_result["is_syntax_valid"] and has_mx and not is_disposable

    # 5. Composite Risk Score
    risk = RiskEngine.calculate_risk(
        is_syntax_valid=True,
        is_disposable=is_disposable,
        has_mx=has_mx,
        is_free_provider=is_free,
        is_role_account=is_role,
        has_typo_suggestion=bool(typo_suggestion)
    )

    return EmailVerificationResponse(
        email=email_str,
        normalized_email=syntax_result["normalized_email"],
        is_valid=is_valid,
        is_syntax_valid=True,
        is_disposable=is_disposable,
        has_mx_records=has_mx,
        is_free_provider=is_free,
        is_role_account=is_role,
        did_you_mean=typo_suggestion,
        risk_score=risk["risk_score"],
        risk_level=risk["risk_level"],
        recommended_action=risk["recommended_action"],
        reasons=risk["reasons"],
        mx_records=mx_records
    )

@app.get("/", tags=["General"])
async def root():
    return {
        "service": settings.PROJECT_NAME,
        "status": "online",
        "version": settings.VERSION,
        "docs": "/docs",
        "endpoints": {
            "verify_single": "/v1/verify?email=user@example.com",
            "verify_batch": "/v1/verify-batch",
            "domain_health": "/v1/domain-health?domain=example.com"
        }
    }

@app.get("/health", tags=["General"])
async def health():
    return {"status": "healthy"}

@app.get("/v1/verify", response_model=EmailVerificationResponse, tags=["Verification"])
async def verify_email(
    email: str = Query(..., description="Email address to evaluate (e.g. user@domain.com)"),
    x_rapidapi_proxy_secret: Optional[str] = Header(None)
):
    """
    Real-time single email verification and fraud risk analysis.
    Evaluates RFC syntax, DNS/MX deliverability, disposable domain blocklists, and role accounts.
    """
    verify_rapidapi_secret(x_rapidapi_proxy_secret)
    return await _process_single_email(email)

@app.post("/v1/verify-batch", response_model=BatchVerificationResponse, tags=["Verification"])
async def verify_batch(
    payload: BatchVerificationRequest,
    x_rapidapi_proxy_secret: Optional[str] = Header(None)
):
    """
    Asynchronous parallel batch verification for up to 50 emails in a single request.
    Ideal for list cleaning and bulk signup validation.
    """
    verify_rapidapi_secret(x_rapidapi_proxy_secret)
    tasks = [_process_single_email(em) for em in payload.emails]
    results = await asyncio.gather(*tasks)
    return BatchVerificationResponse(
        total_processed=len(results),
        results=results
    )

@app.get("/v1/domain-health", response_model=DomainHealthResponse, tags=["Domain Health"])
async def domain_health(
    domain: str = Query(..., description="Domain name to check (e.g. stripe.com)"),
    x_rapidapi_proxy_secret: Optional[str] = Header(None)
):
    """
    Fast domain MX routing inspection and disposable provider status.
    """
    verify_rapidapi_secret(x_rapidapi_proxy_secret)
    domain_clean = domain.lower().strip()
    is_disp = is_disposable_domain(domain_clean)
    has_mx, mx_list, primary_host = await check_mx(domain_clean)

    if is_disp:
        status_label = "DISPOSABLE"
    elif has_mx:
        status_label = "HEALTHY"
    else:
        status_label = "NO_MAIL_SERVER"

    return DomainHealthResponse(
        domain=domain_clean,
        has_mail_server=has_mx,
        is_disposable=is_disp,
        primary_mail_server=primary_host if primary_host else None,
        mx_records=mx_list,
        status=status_label
    )
