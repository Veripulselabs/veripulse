"""
Configuration settings for VeriPulse API.
"""

import os
from pydantic import BaseModel

class Settings(BaseModel):
    PROJECT_NAME: str = "VeriPulse API"
    VERSION: str = "1.0.0"
    DESCRIPTION: str = "High-speed B2B email verification, disposable domain detection, and fraud risk scoring API."
    
    # RapidAPI integration secret. If set, requires matching header 'X-RapidAPI-Proxy-Secret'
    # In development/local testing, if left blank, requests are accepted openly.
    RAPIDAPI_PROXY_SECRET: str = os.getenv("RAPIDAPI_PROXY_SECRET", "")
    
    # DNS timeout in seconds
    DNS_TIMEOUT: float = float(os.getenv("DNS_TIMEOUT", "2.0"))
    
    # Host & Port configuration
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", "8000"))

settings = Settings()
