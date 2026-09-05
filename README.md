<div align="center">

<img src="assets/veripulse_logo.png" alt="VeriPulse Labs Logo" width="620" />

<br />

# ⚡ VeriPulse Labs
### Ultra-Fast Real-Time Trust Intelligence & Fraud Prevention API

[![RapidAPI](https://img.shields.io/badge/RapidAPI-Marketplace%20Live-0052CC?style=for-the-badge&logo=rapidapi)](https://rapidapi.com/jasdebarreau3/api/veripulse-email-verification-and-fraud-detection)
[![Latency](https://img.shields.io/badge/Latency-%3C40ms-brightgreen?style=for-the-badge)](https://rapidapi.com/jasdebarreau3/api/veripulse-email-verification-and-fraud-detection)
[![Python](https://img.shields.io/badge/Python-3.11+-blue?style=for-the-badge&logo=python)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-Framework-009688?style=for-the-badge&logo=fastapi)](https://fastapi.tiangolo.com)
[![Docker](https://img.shields.io/badge/Docker-Ready-2496ED?style=for-the-badge&logo=docker)](https://docker.com)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=for-the-badge)](LICENSE)

<br />

**Protect your signup funnels, eradicate disposable bot accounts, and ensure high email deliverability with a single API call.**

[Get Free API Key on RapidAPI](https://rapidapi.com/jasdebarreau3/api/veripulse-email-verification-and-fraud-detection) • [API Documentation](https://rapidapi.com/jasdebarreau3/api/veripulse-email-verification-and-fraud-detection/details) • [Pricing Plans](https://rapidapi.com/jasdebarreau3/api/veripulse-email-verification-and-fraud-detection/pricing)

</div>

---

## 🎯 What is VeriPulse?

Every SaaS, e-commerce store, and newsletter suffers from the same headache: **fake signups, burner emails, and high bounce rates that destroy email sender reputations**.

**VeriPulse** is a lightning-fast email verification and fraud prevention microservice engineered for high-throughput applications. In under 40 milliseconds, VeriPulse executes multi-layer heuristics to score the fraud risk of any incoming email address and recommends an actionable decision (`ALLOW`, `FLAG`, or `BLOCK`).

### 🛡️ Core Capabilities

- **Strict RFC 5322 Syntax Checking:** Catches broken formats, consecutive dots, and illegal characters.
- **Disposable Domain Blacklist:** Instantly identifies temporary inboxes (Mailinator, 10MinuteMail, GuerrillaMail, TempMail, and 3,000+ others).
- **Asynchronous Live MX Resolution:** Verifies that the recipient domain has active, listening mail exchange servers.
- **Role-Based Account Detection:** Flags shared organizational inboxes (`admin@`, `support@`, `billing@`, `sales@`) to prevent wasted outreach.
- **Free Provider Flagging:** Distinguishes between corporate/work emails and public webmail providers (Gmail, Outlook, Yahoo).
- **Intelligent Risk Scoring (0–100):** Provides a composite numerical risk score and deterministic action recommendation.

---

## 🚀 Quickstart (Under 60 Seconds)

### 1. Get your API Key
Subscribe to the **Free Basic Tier** (100 free requests/month) on [RapidAPI](https://rapidapi.com/jasdebarreau3/api/veripulse-email-verification-and-fraud-detection).

### 2. Make your first request

#### Python (`requests`)
```python
import requests

url = "https://veripulse-email-verification-and-fraud-detection.p.rapidapi.com/v1/verify"
querystring = {"email": "user@example.com"}

headers = {
    "x-rapidapi-key": "YOUR_RAPIDAPI_KEY",
    "x-rapidapi-host": "veripulse-email-verification-and-fraud-detection.p.rapidapi.com"
}

response = requests.get(url, headers=headers, params=querystring)
print(response.json())
```

#### Node.js / JavaScript (`fetch`)
```javascript
const url = 'https://veripulse-email-verification-and-fraud-detection.p.rapidapi.com/v1/verify?email=user@example.com';
const options = {
    method: 'GET',
    headers: {
        'x-rapidapi-key': 'YOUR_RAPIDAPI_KEY',
        'x-rapidapi-host': 'veripulse-email-verification-and-fraud-detection.p.rapidapi.com'
    }
};

const response = await fetch(url, options);
const data = await response.json();
console.log(data);
```

#### cURL
```bash
curl --request GET \
  --url 'https://veripulse-email-verification-and-fraud-detection.p.rapidapi.com/v1/verify?email=user@example.com' \
  --header 'x-rapidapi-host: veripulse-email-verification-and-fraud-detection.p.rapidapi.com' \
  --header 'x-rapidapi-key: YOUR_RAPIDAPI_KEY'
```

---

## 📦 Sample API Responses

### Low Risk / Legitimate Business Email
```json
{
  "email": "ceo@apple.com",
  "normalized_email": "ceo@apple.com",
  "is_valid": true,
  "is_syntax_valid": true,
  "is_disposable": false,
  "has_mx_records": true,
  "is_free_provider": false,
  "is_role_account": false,
  "did_you_mean": null,
  "risk_score": 0,
  "risk_level": "LOW",
  "recommended_action": "ALLOW",
  "reasons": [
    "Valid deliverable address on an active mail server"
  ],
  "mx_records": [
    { "preference": 10, "exchange": "mail-in.apple.com" }
  ]
}
```

### High Risk / Disposable Burner Email
```json
{
  "email": "fakeuser123@mailinator.com",
  "normalized_email": "fakeuser123@mailinator.com",
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
    "Disposable/temporary email provider detected"
  ],
  "mx_records": [
    { "preference": 10, "exchange": "mail.mailinator.com" }
  ]
}
```

---

## 💳 Commercial Plans & Pricing

VeriPulse is accessible on RapidAPI with flexible pricing for individual builders up to enterprise applications:

| Tier | Price | Monthly Quota | Overage Rate | Ideal For |
| :--- | :--- | :--- | :--- | :--- |
| **Basic** | **\$0.00** / mo | 100 requests | None (Hard Cap) | Prototyping & testing |
| **Pro** | **\$14.99** / mo | 10,000 requests | \$0.003 / request | SaaS startups & form validation |
| **Ultra** | **\$49.00** / mo | 50,000 requests | \$0.002 / request | Growth engines & high-volume funnels |

👉 **[Subscribe and Start Building](https://rapidapi.com/jasdebarreau3/api/veripulse-email-verification-and-fraud-detection/pricing)**

---

## 🛠️ Self-Hosting (Docker)

If you wish to self-host your own cluster:

```bash
# Clone the repository
git clone https://github.com/jasdebarreau3-cell/veripulse.git
cd veripulse

# Build the Docker image
docker build -t veripulse-api .

# Run container on port 8000
docker run -p 8000:8000 veripulse-api
```

Visit `http://localhost:8000/docs` for the interactive Swagger UI.

---

## 📄 License

This repository is licensed under the [MIT License](LICENSE).

Developed and maintained by **VeriPulse Labs**.
