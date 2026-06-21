# MyEduConnect Security Engagement Lab

MyEduConnect is a Docker-based ethical hacking and penetration testing lab for the CCS6324 final assignment. The platform represents the fictional Malaysian education technology company **MyEduConnect Sdn Bhd** and is intended only for authorized testing in a local lab environment.

The project supports the assignment lifecycle: build, reconnaissance, vulnerability assessment, exploitation, hardening, re-testing, reporting, and live demonstration.

## Safety Notice

Do not deploy this project to the public internet. The exposed services, weak credentials, vulnerable code paths, insecure transport, and privilege-escalation path are intentional for coursework demonstration.

## Current Main Branch Scope

The current `main` branch contains the vulnerable lab platform and submitted evidence collected by the team.

Implemented platform components:

- Flask web learning portal with registration, login, profile, course catalogue/search, enrolment, mock payment, support upload, dashboard, and admin panel.
- Separate Flask REST API consumed by the web portal.
- MySQL 8 database.
- Adminer database console.
- SSH service exposed through the web container.
- Controlled privilege-escalation path through a writable root-run backup script.
- Evidence folders for Phase 1, Phase 2, and Phase 3.

If the secure/vulnerable toggle version is developed separately, keep it on a clearly named branch such as:

```text
feature/secure-vulnerable-toggle
```

Recommended branch meaning:

```text
main                           Vulnerable lab and evidence baseline
feature/secure-vulnerable-toggle  Hardened or toggle-based version for Phase 5 re-test
```

## Quick Start

From this project folder:

```bash
docker compose up --build
```

If the image was recently changed, especially after Dockerfile updates:

```bash
docker compose down
docker compose build --no-cache web
docker compose up
```

Open these services:

| Service | URL / Access | Purpose |
|---|---|---|
| Web portal | `http://localhost:8080` | Main MyEduConnect learning platform |
| REST API | `http://localhost:5001/health` | Separate API component |
| Adminer | `http://localhost:8081` | Database administration console |
| SSH | `ssh student@localhost -p 2222` | Web container shell access |
| MySQL | `localhost:3306` | Exposed database service |

## Demo Credentials

| Component | Username | Password |
|---|---|---|
| Web admin | `admin@myeduconnect.local` | `admin123` |
| Web student | `aina@student.local` | `student123` |
| Web teacher | `teacher@school.local` | `teacher123` |
| SSH | `student` | `student123` |
| MySQL root | `root` | `root` |
| MySQL app user | `myedu` | `myedu123` |

## Docker Services

| Container | Exposed Port | Internal Port | Description |
|---|---:|---:|---|
| `myeduconnect-web` | `8080` | `8080` | Flask web portal |
| `myeduconnect-web` | `2222` | `22` | SSH foothold service |
| `myeduconnect-api` | `5001` | `5001` | Separate REST API |
| `myeduconnect-db` | `3306` | `3306` | MySQL database |
| `myeduconnect-adminer` | `8081` | `8080` | Adminer database console |

## Deliberate Vulnerability Coverage

The lab includes the required vulnerability categories:

- OWASP Top 10 web vulnerabilities, including SQL injection, stored XSS, broken access control, and unsafe upload behavior.
- Server/OS misconfigurations, including weak SSH credentials, exposed Adminer/MySQL, weak permissions, and a writable root-run backup script.
- Cryptographic weaknesses, including unsalted MD5 password hashes and predictable session tokens.
- Network-layer weakness through cleartext HTTP traffic and static internal API key usage.

The full deliberate vulnerability list is documented in:

```text
docs/vulnerability-matrix.md
```

## Privilege Escalation Path

The current vulnerable web container includes a controlled privilege-escalation path for Phase 4.

After SSH access:

```bash
ssh student@localhost -p 2222
```

Check the vulnerable backup script:

```bash
ls -l /usr/local/bin/myedu-backup
sudo -l
```

The intended finding is:

```text
Writable root-run backup script / sudo misconfiguration
```

Evidence and remediation should be documented in the final report. The hardening recommendation is documented in:

```text
docs/hardening-plan.md
```

## Evidence Structure

| Folder | Purpose |
|---|---|
| `evidence/screenshots/` | Phase 1 platform screenshots |
| `evidence/scans/` | Phase 2 OSINT, Nmap, HTTP, WhatWeb, theHarvester, DNS, and enumeration evidence |
| `evidence/screenshots_phase3/` | Phase 3 vulnerability assessment screenshots |
| `evidence/pcaps/` | Wireshark or traffic-capture evidence |
| `exploits/` | Phase 4 payload notes, exploit scripts, or command transcripts |

## Documentation

| File | Description |
|---|---|
| `docs/setup-guide.md` | Redeployment and setup instructions |
| `docs/architecture.md` | Architecture and network layout |
| `docs/vulnerability-matrix.md` | Deliberate vulnerability matrix |
| `docs/phase-checklist.md` | Assignment phase checklist |
| `docs/phase2-checklist.md` | Phase 2 completion checklist |
| `docs/phase2-findings.md` | Phase 2 findings and evidence references |
| `docs/hardening-plan.md` | Phase 5 remediation and re-test guidance |

## Phase Status Summary

| Phase | Status | Notes |
|---|---|---|
| Phase 1 Build | Complete | Platform, Docker setup, architecture, and screenshots are included. |
| Phase 2 Reconnaissance and Enumeration | Complete | OSINT, Nmap, service enumeration, banner grabbing, default-credential checks, and anonymous-access checks are included. |
| Phase 3 Vulnerability Assessment and Sniffing | Complete | Assessment evidence and screenshots are included. |
| Phase 4 Exploitation | Complete | Vulnerabilities and privilege-escalation path are available for demonstration. |
| Phase 5 Defense, Hardening, and Re-test | Complete on separate branch | The hardening mode/toggle implementation is located on branch `feature/secure-toggle`. |
| Phase 6 Final Report | Complete / report-dependent | Use the docs and evidence folders as source material. |

## Resetting Lab Data

Normal stop/start keeps database data:

```bash
docker compose down
docker compose up
```

To fully reset seeded data:

```bash
docker compose down -v
docker compose up --build
```

## Hardening Branch Notice

The `main` branch is kept as the vulnerable platform and evidence baseline for assessment, exploitation, and documentation.

The Phase 5 hardening mode/toggle implementation is available on:

```text
feature/secure-toggle
```

Lecturers should review `main` for the vulnerable version and evidence baseline, then review `feature/secure-toggle` for the hardened version, secure mode/toggle functionality, remediation work, and re-test comparison.
