import phonenumbers
from phonenumbers import carrier as phone_carrier
from phonenumbers import geocoder as phone_geocoder
from phonenumbers import timezone as phone_timezone
from typing import List, Optional

from app.models import (
    PhoneValidationResponse,
    FormatsInfo,
    LocationInfo,
    CarrierInfo,
    LineType,
    RiskLevel,
    RecommendedAction
)

KNOWN_VIRTUAL_CARRIERS = {
    "twilio",
    "bandwidth",
    "bandwidth.com",
    "google voice",
    "textnow",
    "skype",
    "telnyx",
    "sinch",
    "voxbone",
    "plivo",
    "vonage",
    "pinger",
    "ooma",
    "magicjack",
    "ringcentral",
    "inteliquent",
    "onvoy",
    "enflick",
    "republic wireless",
    "freedompop"
}

PHONE_TYPE_MAP = {
    phonenumbers.PhoneNumberType.MOBILE: LineType.MOBILE,
    phonenumbers.PhoneNumberType.FIXED_LINE: LineType.FIXED_LINE,
    phonenumbers.PhoneNumberType.FIXED_LINE_OR_MOBILE: LineType.FIXED_LINE_OR_MOBILE,
    phonenumbers.PhoneNumberType.VOIP: LineType.VOIP,
    phonenumbers.PhoneNumberType.TOLL_FREE: LineType.TOLL_FREE,
    phonenumbers.PhoneNumberType.PREMIUM_RATE: LineType.PREMIUM_RATE,
    phonenumbers.PhoneNumberType.SHARED_COST: LineType.SHARED_COST,
    phonenumbers.PhoneNumberType.PERSONAL_NUMBER: LineType.PERSONAL_NUMBER,
    phonenumbers.PhoneNumberType.PAGER: LineType.PAGER,
    phonenumbers.PhoneNumberType.UAN: LineType.UAN,
    phonenumbers.PhoneNumberType.VOICEMAIL: LineType.VOICEMAIL,
    phonenumbers.PhoneNumberType.UNKNOWN: LineType.UNKNOWN,
}

class PhoneChecker:
    @staticmethod
    def validate(phone_str: str, default_country: Optional[str] = "US") -> PhoneValidationResponse:
        phone_cleaned = (phone_str or "").strip()
        reasons: List[str] = []

        if not phone_cleaned:
            return PhoneValidationResponse(
                phone_input=phone_str or "",
                is_valid=False,
                is_possible=False,
                risk_score=100,
                risk_level=RiskLevel.HIGH,
                recommended_action=RecommendedAction.BLOCK,
                reasons=["Empty phone number input"]
            )

        try:
            parsed_number = phonenumbers.parse(phone_cleaned, default_country)
        except phonenumbers.NumberParseException as e:
            return PhoneValidationResponse(
                phone_input=phone_str,
                is_valid=False,
                is_possible=False,
                risk_score=100,
                risk_level=RiskLevel.HIGH,
                recommended_action=RecommendedAction.BLOCK,
                reasons=[f"Invalid phone formatting: {e}"]
            )

        is_possible = phonenumbers.is_possible_number(parsed_number)
        is_valid = phonenumbers.is_valid_number(parsed_number)

        if not is_possible or not is_valid:
            return PhoneValidationResponse(
                phone_input=phone_str,
                is_valid=False,
                is_possible=is_possible,
                risk_score=100,
                risk_level=RiskLevel.HIGH,
                recommended_action=RecommendedAction.BLOCK,
                reasons=["Unassigned or impossible phone number format"]
            )

        # Formats
        e164 = phonenumbers.format_number(parsed_number, phonenumbers.PhoneNumberFormat.E164)
        intl = phonenumbers.format_number(parsed_number, phonenumbers.PhoneNumberFormat.INTERNATIONAL)
        natl = phonenumbers.format_number(parsed_number, phonenumbers.PhoneNumberFormat.NATIONAL)
        rfc = phonenumbers.format_number(parsed_number, phonenumbers.PhoneNumberFormat.RFC3966)
        formats = FormatsInfo(e164=e164, international=intl, national=natl, rfc3966=rfc)

        # Location
        country_code = phonenumbers.region_code_for_number(parsed_number) or "UNKNOWN"
        country_name = phone_geocoder.country_name_for_number(parsed_number, "en") or country_code
        region_desc = phone_geocoder.description_for_number(parsed_number, "en") or None
        timezones = list(phone_timezone.time_zones_for_number(parsed_number))
        location = LocationInfo(
            country_code=country_code,
            country_name=country_name,
            region=region_desc,
            timezones=timezones
        )

        # Line Type & Carrier
        num_type = phonenumbers.number_type(parsed_number)
        line_type = PHONE_TYPE_MAP.get(num_type, LineType.UNKNOWN)
        carrier_name = phone_carrier.name_for_number(parsed_number, "en") or None

        is_mobile = line_type == LineType.MOBILE
        is_landline = line_type == LineType.FIXED_LINE
        is_virtual = line_type == LineType.VOIP

        carrier_lower = (carrier_name or "").lower()
        if any(v in carrier_lower for v in KNOWN_VIRTUAL_CARRIERS):
            is_virtual = True

        carrier_info = CarrierInfo(
            name=carrier_name,
            line_type=line_type,
            is_mobile=is_mobile,
            is_landline=is_landline,
            is_virtual=is_virtual
        )

        # Risk scoring
        risk_score = 0
        if is_virtual or line_type == LineType.VOIP:
            risk_score = 90
            reasons.append("Virtual/VoIP phone number detected (high risk for disposable/temporary signups)")
        elif line_type in (LineType.TOLL_FREE, LineType.PREMIUM_RATE):
            risk_score = 75
            reasons.append(f"High-risk line type: {line_type.value}")
        elif line_type == LineType.FIXED_LINE:
            risk_score = 35
            reasons.append("Landline number detected (cannot receive SMS OTP)")
        elif line_type == LineType.FIXED_LINE_OR_MOBILE:
            risk_score = 15
            reasons.append("Hybrid fixed-line/mobile allocation")
        else:
            risk_score = 0
            reasons.append("Verified mobile carrier (optimal for SMS verification)")

        if risk_score >= 80:
            risk_level = RiskLevel.HIGH
            recommended_action = RecommendedAction.BLOCK
        elif risk_score >= 30:
            risk_level = RiskLevel.MEDIUM
            recommended_action = RecommendedAction.FLAG
        else:
            risk_level = RiskLevel.LOW
            recommended_action = RecommendedAction.ALLOW

        return PhoneValidationResponse(
            phone_input=phone_str,
            is_valid=True,
            is_possible=True,
            formats=formats,
            location=location,
            carrier=carrier_info,
            risk_score=risk_score,
            risk_level=risk_level,
            recommended_action=recommended_action,
            reasons=reasons
        )
