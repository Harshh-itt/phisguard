# PhishGuard Frontend (React + Vite)

This directory will host the React + Vite + Tailwind CSS single-page application, scheduled for development in **Phase 14**.

## Planned Features:
- Single-URL input and static risk assessment form.
- Real-time verdict presentation (Legitimate vs. Phishing) with probability indicator.
- Transparent risk indicator badges derived from observable URL features.
- Side-by-side Decision Tree vs. ANN model comparative views.
- Fully accessible, responsive interface designed for security analysts and end-users.

## Security Constraints:
- No secrets or private tokens in frontend bundles.
- Calls backend API exclusively; does not perform network scraping or model calculations in client memory.
