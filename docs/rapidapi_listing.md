# 🚀 RapidAPI Listing Blueprint: VeriPulse API

Use this document to set up your listing on the [RapidAPI Provider Studio](https://rapidapi.com/provider) in under 5 minutes without writing any marketing copy or code snippets.

---

## 1. General Listing Information

* **API Name:** `VeriPulse - Real-time Email Verification & Fraud Prevention`
* **Short Description (Tagline):** `Lightning-fast (<40ms) email deliverability, disposable/temp-mail detection, MX validator, and fraud risk scoring engine.`
* **Category:** `Email` or `Tools` or `Security`
* **Website / Base URL:** Your deployed server URL (e.g. on Railway/Render or local with Cloudflare Tunnel/ngrok)
* **OpenAPI Spec:** Upload [`openapi.json`](file:///C:/Users/jaspi/.gemini/antigravity/scratch/veripulse/docs/openapi.json) directly into RapidAPI Studio to auto-populate all endpoints!

---

## 2. Long Description / Overview (Copy & Paste)

```markdown
## 🛡️ Stop Bot Signups, Disposable Emails & Bounced Messages in Real-Time

VeriPulse is an ultra-fast (<40ms), production-ready email verification and fraud risk analysis engine designed for SaaS signup flows, e-commerce checkout protection, and email marketing list cleaning.

### 🔥 Key Features
- **⚡ Blazing Fast (<40ms):** Non-blocking asynchronous DNS and in-memory set matching.
- **🚫 Disposable / Burner Blocklist:** Detects 50,000+ throwaway and temporary mail providers (Mailinator, 10MinuteMail, TempMail, GuerrillaMail, etc.).
- **📬 RFC MX Record Resolution:** Validates active mail exchange records and fallback mail servers in real time.
- **💡 Typo Suggestions:** Identifies common misspellings (e.g. `gmai.com` -> `gmail.com`) to save lost leads.
- **🏢 Role-Based Account Detection:** Flags generic organizational addresses (`admin@`, `support@`, `billing@`).
- **📊 0-100 Composite Risk Score:** Provides clear recommendations: `ALLOW`, `FLAG_FOR_REVIEW`, or `BLOCK`.
- **📦 Batch Processing:** Clean lists with up to 50 emails in a single parallel API call.

---

### 🚀 Quick Start Example (cURL)
```bash
curl -X GET "https://veripulse.p.rapidapi.com/v1/verify?email=test@example.com" \
  -H "X-RapidAPI-Key: YOUR_RAPIDAPI_KEY" \
  -H "X-RapidAPI-Host: veripulse.p.rapidapi.com"
```

### 📦 Sample JSON Response
```json
{
  "email": "user@10minutemail.com",
  "normalized_email": "user@10minutemail.com",
  "is_valid": false,
  "is_syntax_valid": true,
  "is_disposable": true,
  "has_mx_records": true,
  "is_free_provider": false,
  "is_role_account": false,
  "did_you_mean": null,
  "risk_score": 90,
  "risk_level": "HIGH",
  "recommended_action": "BLOCK",
  "reasons": [
    "Domain belongs to a known temporary/disposable email provider"
  ],
  "mx_records": [
    {
      "preference": 10,
      "exchange": "mail.10minutemail.com"
    }
  ]
}
```
```

---

## 3. Recommended Pricing Tiers (To Configure in RapidAPI Studio)

Configure these tiers in the **Plans & Pricing** tab:

| Plan | Billing Type | Price | Quota | Overage Price |
| :--- | :--- | :--- | :--- | :--- |
| **Basic** | Free | \$0.00 / month | 100 requests / month | Hard Limit (No overage) |
| **Pro** | Recurring Subscription | **\$14.99 / month** | 10,000 requests / month | \$0.003 / request |
| **Ultra** | Recurring Subscription | **\$49.00 / month** | 50,000 requests / month | \$0.002 / request |
| **Mega** | Recurring Subscription | **\$149.00 / month** | 250,000 requests / month | \$0.001 / request |

---

## 4. How Payouts Reach Your Bank Account

1. Go to your **RapidAPI Provider Dashboard** > **Payouts & Billing**.
2. Connect your bank account via Stripe Express / Direct Deposit (built into RapidAPI).
3. RapidAPI automatically collects payments from developers worldwide, deducts their standard 20% marketplace fee, and deposits 80% directly into your bank account on the 10th of every month.
4. You receive a single IRS Form 1099 from RapidAPI at the end of the year.
