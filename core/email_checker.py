"""
Email syntax parser, role account detector, free webmail classifier, and typo suggester.
"""

import re
from typing import Optional, Dict, Any, Set
from email_validator import validate_email, EmailNotValidError

FREE_EMAIL_PROVIDERS: Set[str] = {
    "gmail.com", "googlemail.com", "yahoo.com", "ymail.com", "rocketmail.com",
    "hotmail.com", "outlook.com", "live.com", "msn.com", "icloud.com", "me.com",
    "mac.com", "aol.com", "aim.com", "proton.me", "protonmail.com", "zoho.com",
    "gmx.com", "gmx.net", "mail.com", "yandex.com", "yandex.ru", "tutanota.com",
    "tuta.io", "fastmail.com"
}

ROLE_BASED_PREFIXES: Set[str] = {
    "admin", "administrator", "webmaster", "hostmaster", "postmaster",
    "info", "support", "help", "contact", "sales", "marketing", "billing",
    "invoice", "finance", "accounting", "press", "media", "jobs", "careers",
    "hr", "security", "abuse", "compliance", "legal", "team", "office"
}

COMMON_DOMAIN_TYPOS: Dict[str, str] = {
    "gmai.com": "gmail.com",
    "gamil.com": "gmail.com",
    "gmial.com": "gmail.com",
    "gnail.com": "gmail.com",
    "gmaill.com": "gmail.com",
    "hotmial.com": "hotmail.com",
    "hotmai.com": "hotmail.com",
    "hotamail.com": "hotmail.com",
    "outlok.com": "outlook.com",
    "outloo.com": "outlook.com",
    "yaho.com": "yahoo.com",
    "yahooo.com": "yahoo.com",
    "yaho.co": "yahoo.com",
    "iclud.com": "icloud.com",
    "iclou.com": "icloud.com"
}

class EmailChecker:
    @staticmethod
    def parse_and_validate_syntax(email_str: str) -> Dict[str, Any]:
        """
        Validates email format according to RFC 5322.
        Returns detailed syntax breakdown and normalized form.
        """
        if not email_str or not isinstance(email_str, str):
            return {
                "is_syntax_valid": False,
                "normalized_email": "",
                "local_part": "",
                "domain": "",
                "error": "Email address cannot be empty"
            }

        email_str = email_str.strip()

        # Security: Enforce RFC 5321 maximum email length (254 characters) to block ReDoS/payload attacks
        if len(email_str) > 254:
            return {
                "is_syntax_valid": False,
                "normalized_email": email_str[:254],
                "local_part": "",
                "domain": "",
                "error": "Email address exceeds maximum allowed length (254 characters)"
            }

        try:
            # check_deliverability=False because we do asynchronous DNS ourselves
            validation = validate_email(email_str, check_deliverability=False)
            normalized = validation.normalized
            local_part = validation.local_part
            domain = validation.domain.lower()

            return {
                "is_syntax_valid": True,
                "normalized_email": normalized,
                "local_part": local_part,
                "domain": domain,
                "error": None
            }
        except EmailNotValidError as e:
            return {
                "is_syntax_valid": False,
                "normalized_email": email_str.lower(),
                "local_part": email_str.split("@")[0] if "@" in email_str else email_str,
                "domain": email_str.split("@")[1] if "@" in email_str else "",
                "error": str(e)
            }

    @staticmethod
    def check_role_account(local_part: str) -> bool:
        """Returns True if local part is a generic organizational alias like admin, info, etc."""
        if not local_part:
            return False
        clean = local_part.lower().split("+")[0].split(".")[0]
        return clean in ROLE_BASED_PREFIXES

    @staticmethod
    def check_free_provider(domain: str) -> bool:
        """Returns True if domain belongs to a known consumer webmail provider."""
        return domain.lower() in FREE_EMAIL_PROVIDERS

    @staticmethod
    def suggest_typo_correction(domain: str) -> Optional[str]:
        """Checks for common domain misspellings and suggests the correct domain."""
        return COMMON_DOMAIN_TYPOS.get(domain.lower(), None)
