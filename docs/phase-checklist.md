# Phase Checklist

## Phase 1: Build the Vulnerable Environment

- Working web learning portal: done.
- Registration/login/profile: done.
- Course browsing/search: done.
- Enrolment and mock payment: done.
- Admin panel: done.
- Backend server and database: Flask + MySQL.
- Additional component beyond website: separate REST API container.
- Deployment setup: Docker Compose.
- Architecture diagram: `docs/architecture.md`.
- Vulnerability matrix: `docs/vulnerability-matrix.md`.
- Redeployment guide: `docs/setup-guide.md`.
- Source code: project folder is ready for a private Git repository.

## Phase 2: Reconnaissance and Enumeration

Status: complete. Detailed findings and evidence references are documented in `docs/phase2-findings.md` and `docs/phase2-checklist.md`.

- OSINT/footprinting completed with WHOIS, DNS, reverse DNS, theHarvester, WhatWeb, and search-engine reconnaissance.
- At least 10 intelligence findings documented.
- TCP and UDP Nmap scans completed against target IP `192.168.0.92`.
- Service enumeration completed for HTTP `8080`, Adminer `8081`, API `5001`, SSH `2222`, and MySQL `3306`.
- Banner grabbing, default-credential checks, and anonymous-access checks completed.
- Raw outputs and screenshots saved under `evidence/scans`.

## Phase 3: Vulnerability Assessment and Sniffing

Recommended evidence to collect:

- Run at least one scanner such as Nikto, Nuclei, WhatWeb, Gobuster, or OpenVAS.
- Manually identify at least 5 issues scanners miss from `docs/vulnerability-matrix.md`.
- Capture web-to-API traffic and show the cleartext API call with static `X-API-Key`.
- Save PCAPs in `evidence/pcaps`.

## Phase 4: Exploitation

Suggested exploit coverage:

- SQL injection: `/login`, `/courses?q=`, or `/internal/student/<id>`.
- Stored XSS: profile bio or admin announcement.
- IDOR: `/invoice/<payment_id>`.
- Server/OS: SSH weak credentials, exposed Adminer/MySQL.
- Privilege escalation: demonstrate access from SSH user to sensitive app files/configuration or exposed DB credentials, then explain impact.
- Network-layer: capture the cleartext API key and replay the API request.
- Post-exploitation: extract redacted sample data from MySQL or create a controlled test persistence account.

## Phase 5: Defense, Hardening, and Re-test

Use `docs/hardening-plan.md` as the remediation map. For the report, apply fixes in a separate branch or copy, then re-run the same attacks and document that they fail.

## Phase 6: Final Report

Use the assignment guideline structure exactly:

- Cover and Declaration.
- Executive Summary.
- Methodology.
- Phase 1 build documentation.
- Phase 2 to 4 findings.
- Phase 5 remediation and re-test evidence.
- PDPA 2010 compliance commentary.
- Conclusion.
- IEEE references.
- Appendices.

## Phase 7: Presentation and Live Demo

Recommended live demo:

1. Show login/course SQL injection or stored XSS on vulnerable version.
2. Switch to remediated version.
3. Re-run the same attack and show it fails.
4. Briefly show the changed code/config.
