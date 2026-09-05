import asyncio
from typing import Optional
from fastapi import FastAPI, Query, Header, HTTPException, status, Body, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse

from app.config import settings
from app.models import (
    EmailVerificationResponse,
    BatchVerificationRequest,
    BatchVerificationResponse,
    DomainHealthResponse,
    PhoneValidationResponse,
    TrustScoreRequest,
    TrustScoreResponse
)
from core.email_checker import EmailChecker
from core.disposable_filter import is_disposable_domain
from core.dns_resolver import check_mx
from core.risk_engine import RiskEngine
from core.phone_checker import PhoneChecker

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description=settings.DESCRIPTION,
    docs_url="/docs",
    redoc_url="/redoc"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from fastapi.staticfiles import StaticFiles
import os
assets_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "assets")
site_assets_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "site", "assets")
if os.path.exists(assets_dir):
    app.mount("/assets", StaticFiles(directory=assets_dir), name="assets")
if os.path.exists(site_assets_dir):
    app.mount("/site/assets", StaticFiles(directory=site_assets_dir), name="site_assets")

def verify_rapidapi_secret(x_rapidapi_proxy_secret: Optional[str] = Header(None)):
    if settings.RAPIDAPI_PROXY_SECRET:
        if not x_rapidapi_proxy_secret or x_rapidapi_proxy_secret != settings.RAPIDAPI_PROXY_SECRET:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Direct unauthorized access prohibited. Please query via RapidAPI."
            )
    return True

async def _process_single_email(email_str: str) -> EmailVerificationResponse:
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

    is_disposable = is_disposable_domain(domain)
    is_role = EmailChecker.check_role_account(local_part)
    is_free = EmailChecker.check_free_provider(domain)
    typo_suggestion = EmailChecker.suggest_typo_correction(domain)

    has_mx, mx_records, primary_host = await check_mx(domain)
    is_valid = syntax_result["is_syntax_valid"] and has_mx and not is_disposable

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
async def root(request: Request):
    accept_header = request.headers.get("accept", "")
    site_index = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "site", "index.html")
    if "text/html" in accept_header and os.path.exists(site_index):
        return FileResponse(site_index, media_type="text/html")

    return {
        "service": settings.PROJECT_NAME,
        "status": "online",
        "version": settings.VERSION,
        "docs": "/docs",
        "endpoints": {
            "trust_score": "/v1/trust-score (GET & POST)",
            "verify_email": "/v1/verify?email=user@example.com",
            "validate_phone": "/v1/phone/validate?phone=+14155552671",
            "domain_health": "/v1/domain-health?domain=example.com"
        }
    }

@app.get("/index.html", include_in_schema=False)
async def serve_index_html():
    site_index = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "site", "index.html")
    if os.path.exists(site_index):
        return FileResponse(site_index, media_type="text/html")
    raise HTTPException(status_code=404, detail="Page not found")

@app.get("/health", tags=["General"])
async def health():
    return {"status": "healthy"}

# --- Flagship Trust Intelligence Endpoint ---

@app.post("/v1/trust-score", response_model=TrustScoreResponse, tags=["Trust Intelligence"])
@app.get("/v1/trust-score", response_model=TrustScoreResponse, tags=["Trust Intelligence"])
async def evaluate_trust_score(
    email: Optional[str] = Query(None, description="Email address to evaluate"),
    phone: Optional[str] = Query(None, description="Phone number to evaluate"),
    country_code: Optional[str] = Query("US", description="Default ISO country code for phone number"),
    payload: Optional[TrustScoreRequest] = Body(None),
    x_rapidapi_proxy_secret: Optional[str] = Header(None)
):
    """
    Unified Signup Protection & Fraud Scoring Engine.
    Combines email deliverability, disposable domain checks, phone line intelligence,
    and VoIP carrier detection into a single, definitive 0-100 Trust Score.
    """
    verify_rapidapi_secret(x_rapidapi_proxy_secret)
    
    # Support both GET query params and POST JSON body
    target_email = (payload.email if payload and payload.email else email) or None
    target_phone = (payload.phone if payload and payload.phone else phone) or None
    target_country = (payload.country_code if payload and payload.country_code else country_code) or "US"

    if not target_email and not target_phone:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="At least one identifier (email or phone) must be provided for trust evaluation."
        )

    email_res: Optional[EmailVerificationResponse] = None
    phone_res: Optional[PhoneValidationResponse] = None
    signals = []

    # Run evaluations concurrently
    tasks = []
    if target_email:
        tasks.append(_process_single_email(target_email))
    if target_phone:
        tasks.append(asyncio.to_thread(PhoneChecker.validate, target_phone, target_country))

    results = await asyncio.gather(*tasks)

    idx = 0
    if target_email:
        email_res = results[idx]
        idx += 1
    if target_phone:
        phone_res = results[idx]

    # Calculate Composite Trust & Risk Score
    composite_risk = 0
    if email_res and phone_res:
        # Cross-signal synthesis
        composite_risk = max(email_res.risk_score, phone_res.risk_score)
        if email_res.is_disposable and (phone_res.carrier and phone_res.carrier.is_virtual):
            composite_risk = 98
            signals.append("CRITICAL: Both email and phone belong to disposable/virtual services (bot pattern)")
        elif email_res.is_disposable:
            composite_risk = max(composite_risk, 90)
            signals.append("Disposable/burner email domain detected")
        elif phone_res.carrier and phone_res.carrier.is_virtual:
            composite_risk = max(composite_risk, 85)
            signals.append("VoIP/virtual phone number detected")
            
        signals.extend([f"Email: {r}" for r in email_res.reasons])
        signals.extend([f"Phone: {r}" for r in phone_res.reasons])
        
    elif email_res:
        composite_risk = email_res.risk_score
        signals.extend([f"Email: {r}" for r in email_res.reasons])
        
    elif phone_res:
        composite_risk = phone_res.risk_score
        signals.extend([f"Phone: {r}" for r in phone_res.reasons])

    trust_score = max(0, min(100, 100 - composite_risk))

    if composite_risk >= 80:
        risk_level = "HIGH"
        action = "BLOCK"
    elif composite_risk >= 30:
        risk_level = "MEDIUM"
        action = "FLAG_FOR_REVIEW"
    else:
        risk_level = "LOW"
        action = "ALLOW"

    return TrustScoreResponse(
        trust_score=trust_score,
        risk_score=composite_risk,
        risk_level=risk_level,
        recommended_action=action,
        signals=signals,
        email_intelligence=email_res,
        phone_intelligence=phone_res
    )

# --- Individual Micro-Endpoints ---

@app.get("/v1/verify", response_model=EmailVerificationResponse, tags=["Email Intelligence"])
async def verify_email(
    email: str = Query(..., description="Email address to evaluate"),
    x_rapidapi_proxy_secret: Optional[str] = Header(None)
):
    verify_rapidapi_secret(x_rapidapi_proxy_secret)
    return await _process_single_email(email)

@app.post("/v1/verify-batch", response_model=BatchVerificationResponse, tags=["Email Intelligence"])
async def verify_batch(
    payload: BatchVerificationRequest,
    x_rapidapi_proxy_secret: Optional[str] = Header(None)
):
    verify_rapidapi_secret(x_rapidapi_proxy_secret)
    tasks = [_process_single_email(em) for em in payload.emails]
    results = await asyncio.gather(*tasks)
    return BatchVerificationResponse(total_processed=len(results), results=results)

@app.get("/v1/phone/validate", response_model=PhoneValidationResponse, tags=["Phone Intelligence"])
async def validate_phone(
    phone: str = Query(..., description="Phone number to evaluate (e.g. +14155552671)"),
    country_code: Optional[str] = Query("US", description="Default ISO country code"),
    x_rapidapi_proxy_secret: Optional[str] = Header(None)
):
    verify_rapidapi_secret(x_rapidapi_proxy_secret)
    return PhoneChecker.validate(phone, country_code)

@app.get("/v1/domain-health", response_model=DomainHealthResponse, tags=["Domain Intelligence"])
async def domain_health(
    domain: str = Query(..., description="Domain name to check (e.g. stripe.com)"),
    x_rapidapi_proxy_secret: Optional[str] = Header(None)
):
    verify_rapidapi_secret(x_rapidapi_proxy_secret)
    domain_clean = domain.lower().strip()
    is_disp = is_disposable_domain(domain_clean)
    has_mx, mx_list, primary_host = await check_mx(domain_clean)

    status_label = "DISPOSABLE" if is_disp else ("HEALTHY" if has_mx else "NO_MAIL_SERVER")

    return DomainHealthResponse(
        domain=domain_clean,
        has_mail_server=has_mx,
        is_disposable=is_disp,
        primary_mail_server=primary_host if primary_host else None,
        mx_records=mx_list,
        status=status_label
    )
