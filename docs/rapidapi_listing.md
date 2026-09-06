# 🚀 RapidAPI Listing Blueprint: VeriPulse Trust Intelligence API

Use this blueprint to configure your listing on the [RapidAPI Provider Studio](https://rapidapi.com/provider) in under 5 minutes.

---

## 1. General Listing Information

* **API Name:** VeriPulse - Trust Intelligence & Fraud Prevention API
* **Short Description (Tagline):** Unified email deliverability, disposable phone & VoIP carrier detection, and 0-100 real-time signup fraud scoring.
* **Category:** Security or Email or Tools
* **Website / Base URL:** Your deployed microservice URL (Render, Railway, or Cloudflare Tunnel)
* **OpenAPI Spec:** Upload [openapi.json](file:///C:/Users/jaspi/.gemini/antigravity/scratch/veripulse/docs/openapi.json) directly into RapidAPI Studio to auto-populate all endpoints!

---

## 2. Long Description / Overview (Copy & Paste for RapidAPI Marketplace)

`markdown
## 🛡️ Stop Bot Signups, Disposable Emails & Fake Phone Numbers with One API Call

**VeriPulse Trust Intelligence** is an ultra-fast (<35ms), unified fraud prevention and signup intelligence engine. Instead of juggling separate vendors for email verification and SMS fraud detection, VeriPulse provides a single composite **0–100 Trust Score** in real time.

### 🔥 Comprehensive Signal Intelligence:
- **📬 Email Deliverability & MX Resolution:** Checks RFC syntax, mailbox routing, and fallback mail servers in real time.
- **🚫 Disposable / Burner Email Detection:** Blocks 50,000+ throwaway mail domains (10MinuteMail, TempMail, Mailinator).
- **📱 Phone Intelligence & E.164 Normalization:** Formats, validates, and geolocates numbers across 240+ countries.
- **☎️ VoIP & Virtual Number Shield:** Identifies burner numbers (Google Voice, Twilio, TextNow, Skype) before you burn SMS OTP budgets.
- **💡 Smart Typo Suggestions:** Detects misspelled domains (e.g., gmial.com -> gmail.com) to save lost conversions.
- **🎯 Unified 0–100 Trust & Fraud Scoring:** Evaluates cross-vector signals with clear recommended actions (ALLOW, FLAG_FOR_REVIEW, BLOCK).

---

### 🚀 Quick Start: Unified Trust Score (cURL)

`ash
curl -X POST "https://veripulse.p.rapidapi.com/v1/trust-score" \
  -H "Content-Type: application/json" \
  -H "X-RapidAPI-Key: YOUR_RAPIDAPI_KEY" \
  -H "X-RapidAPI-Host: veripulse.p.rapidapi.com" \
  -d '{
    "email": "user@gmail.com",
    "phone": "+14155552671"
  }'
`

### 📦 Sample JSON Response
`json
{
  "trust_score": 95,
  "risk_score": 5,
  "risk_level": "LOW",
  "recommended_action": "ALLOW",
  "signals": [
    "Email: Syntax valid and verified active MX servers",
    "Phone: Verified mobile carrier (optimal for SMS OTP)"
  ],
  "email_intelligence": {
    "email": "user@gmail.com",
    "is_valid": true,
    "is_disposable": false,
    "has_mx_records": true,
    "risk_score": 5
  },
  "phone_intelligence": {
    "phone_input": "+14155552671",
    "is_valid": true,
    "carrier": {
      "name": "Verizon Wireless",
      "line_type": "MOBILE",
      "is_virtual": false
    },
    "risk_score": 0
  }
}
`
`

---

## 3. Official Marketplace Pricing Tiers (Configured by Jazz)

Configure this plan in the **Plans & Pricing** tab (Remove all paid tiers):

| Plan | Billing Type | Price | Monthly Quota | Overage Price | Target Audience |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Basic** | **Free** | **$0.00 / month** | **1,000 requests** | Hard Limit (No overage) | Developers, testing, hackathons |

*(All paid tiers—Pro, Ultra, Mega—are permanently disabled to maximize user adoption, traffic, and eliminate payment liability)*

---

## 4. Key Strategic Differentiator

* **The 1,000 Request Free Tier Advantage:** Most competitors (ZeroBounce, Hunter, Numverify) cut developers off after 50 or 100 calls. Offering **1,000 free requests/month** allows developers to build their entire MVP on VeriPulse. Once their app launches into production, they upgrade straight to the **\.99 Pro** plan.
* **All-in-One Synergy:** No need to buy an email API and a separate phone API—VeriPulse does both in a single HTTP roundtrip.
