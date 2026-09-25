# Security and Ethical Boundaries

## Defensive Posture
PhishGuard is strictly a defensive cybersecurity analysis tool. Its sole purpose is to detect and analyze potentially malicious URLs to protect users and systems.

## Core Operational Directives

### 1. Static URL Analysis Only
The system **never** performs HTTP GET/POST requests, crawls, follows redirects, renders HTML/JS, or downloads resources from submitted URLs. 

**Why server-side URL fetching is strictly excluded:**
- **Server-Side Request Forgery (SSRF)**: Fetching URLs submitted by untrusted parties exposes local networks, internal microservices, and cloud metadata endpoints (`169.254.169.254`).
- **Malware & Drive-By Exploits**: Automated scrapers can trigger drive-by downloads or browser engine zero-days.
- **Denial of Service**: Malicious actors could submit "tarpits", massive gzip bombs, or unending video streams.
- **Privacy & Honeypots**: Reaching out to attacker infrastructure confirms that an attack target or email address was active and alerted the adversary.

### 2. Strict Prohibition on Credential & Secret Ingestion
- PhishGuard will **never** collect, handle, log, or persist user passwords, cookies, authorization tokens, or session headers.
- Submitted URLs are sanitized to strip any inline user credentials (e.g. `http://user:password@domain.com`).

### 3. Untrusted Input Handling
- URLs submitted to the API are subject to strict maximum-length limits (e.g. 2048 characters).
- URL parsing is performed defensively with strict exception boundaries.

### 4. Privacy-Preserving Telemetry
- Structured application logs capture request IDs, response latency, HTTP status codes, and model versions.
- Raw user-submitted URLs are not recorded in persistent server logs by default.
