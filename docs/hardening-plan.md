# Hardening Plan

This file maps each deliberate vulnerability to a concrete fix for Phase 5. Apply these fixes after exploitation evidence has been captured.

| Vulnerability | Required Fix | Re-test Proof |
|---|---|---|
| SQL injection in login/search/API | Replace string-concatenated SQL with parameterized queries for every user-controlled input. | Re-run the same payloads and show no bypass/data extraction. |
| Stored XSS in profile/announcements/admin table | Remove `| safe`, encode output by default, and optionally sanitize rich text with an allowlist. | Re-enter the original script payload and show it renders as text or is rejected. |
| IDOR invoice access | Enforce ownership: students can only load invoices where `payments.user_id == current_user.id`; admins may access all. | Student requests another user's invoice ID and receives `403` or `404`. |
| Unsafe upload | Enforce extension and MIME allowlist, randomize stored filename, store outside web root, and scan or quarantine files. | Upload a blocked script file and show rejection. |
| Weak SSH credentials | Disable password SSH, disable root login, rotate credentials, or remove SSH from the container entirely. | Nmap still sees no SSH or login attempt fails. |
| Exposed Adminer/MySQL | Remove host port bindings, restrict to internal Docker network, require strong unique credentials. | Nmap from host no longer sees `3306`/`8081`, or firewall blocks them. |
| World-writable directories | Set least-privilege ownership and permissions, e.g. app user owns upload directory with `750`/`755` as appropriate. | SSH user cannot write outside intended upload path. |
| MD5 password hashing | Migrate password storage to bcrypt or Argon2id with unique salts. | Database shows modern password hashes and old MD5 login no longer accepted after migration. |
| Predictable session token | Use Flask signed session or server-side random tokens from `secrets.token_urlsafe`; set `HttpOnly`, `Secure`, and `SameSite=Lax/Strict`. | Session token cannot be predicted and JavaScript cannot read it. |
| Cleartext web-to-API traffic | Use TLS for service communication or terminate TLS at a trusted reverse proxy; rotate static key to scoped short-lived token. | PCAP no longer exposes API key or sensitive payload in cleartext. |
| Weak HTTP headers | Remove debug headers and set security headers: CSP, HSTS where TLS is used, X-Content-Type-Options, Referrer-Policy. | Scanner output confirms improved headers. |

## Network Protection Controls Required by Phase 5

- IDS: deploy Snort or Suricata and create at least 3 custom rules for attacks demonstrated in Phase 4.
- Firewall: restrict database and admin interfaces to trusted networks only.
- Segmentation: separate public web, internal API, and database networks in Docker Compose.
- WAF: add ModSecurity with OWASP CRS or equivalent rules for SQL injection and XSS.

## Crypto Guidance to Cite

- OWASP Password Storage Cheat Sheet.
- OWASP Session Management Cheat Sheet.
- Mozilla SSL Configuration Generator.
- OWASP Transport Layer Protection Cheat Sheet.
