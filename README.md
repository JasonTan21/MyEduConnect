# MyEduConnect Security Engagement Lab — Secure Toggle Branch

This branch (`feature/secure-toggle`) extends the vulnerable lab with an **in-app Secure Mode toggle** for Phase 5 demonstration. The same Docker Compose stack can switch between fully-exploitable (Phase 4) and remediated (Phase 5) behaviour without rebuilding the image.

> **Safety Notice** — Do not deploy this project to the public internet. Weak credentials, intentional vulnerabilities, and cleartext transport are present by design for coursework demonstration only.

---

## Branch Purpose

| Branch | Purpose |
|---|---|
| `main` | Vulnerable baseline — Phase 1–4 evidence and exploitation |
| `feature/secure-toggle` | This branch — adds Secure Mode toggle for Phase 5 re-test |

Lecturers should review `main` for the exploitable platform and evidence, then switch to this branch to see the hardened version and re-test comparison.

---

## Quick Start

```bash
git checkout feature/secure-toggle
docker compose up --build
```

Open these local services:

| Service | URL / Access | Purpose |
|---|---|---|
| Web portal | `http://localhost:8080` | Main MyEduConnect learning platform |
| REST API | `http://localhost:5001/health` | Separate API component |
| Adminer | `http://localhost:8081` | Database administration console |
| SSH | `ssh student@localhost -p 2222` | Web container shell access |
| MySQL | `localhost:3306` | Exposed database service |

Demo accounts:

| Role | Username | Password |
|---|---|---|
| Admin | `admin@myeduconnect.local` | `admin123` |
| Student | `aina@student.local` | `student123` |
| Teacher | `teacher@school.local` | `teacher123` |
| SSH | `student` | `student123` |
| MySQL root | `root` | `root` |
| MySQL app user | `myedu` | `myedu123` |

---

## Enabling Remediated (Secure) Mode

There are three ways to enable Secure Mode depending on the demo scenario.

### Option 1 — In-App Toggle (Recommended for Live Demo)

1. Log in as admin: `admin@myeduconnect.local` / `admin123`
2. Go to the **Admin Panel**: `http://localhost:8080/admin`
3. Find the **Security Mode** panel at the top of the page.
4. Click **Enable Secure Mode** to switch the application to the remediated code paths.
5. The banner at the top of every page will change from **VULNERABLE MODE** (red) to **SECURE MODE** (green) to confirm the switch.
6. To revert, click **Switch to Vulnerable Mode** from the same panel.

The toggle takes effect immediately — no restart required. All subsequent requests use the secure code paths until toggled back.

### Option 2 — Environment Variable at Startup (Persistent Secure Boot)

To start the lab already in Secure Mode (useful for re-test evidence where you want the app hardened from first boot):

```bash
SECURE_MODE=1 docker compose up --build
```

Or add to `docker-compose.yml` under the `web` service environment section:

```yaml
environment:
  SECURE_MODE: "1"
```

Then rebuild:

```bash
docker compose down
docker compose up --build
```

The app will boot in Secure Mode. The in-app toggle will still allow switching unless `LOCK_MODE` is also set.

### Option 3 — Locked Secure Mode (Hardened Deployment, No UI Revert)

To demonstrate a production-style hardened deployment where the UI toggle is disabled and the mode cannot be switched back to vulnerable:

```bash
SECURE_MODE=1 LOCK_MODE=1 docker compose up --build
```

In this mode, `POST /mode` returns `403 Forbidden` and the toggle button is hidden in the admin panel. This simulates a locked-down production build.

---

## What Secure Mode Fixes

The toggle controls application-layer remediations only. Infrastructure findings (E7–E10) are addressed at the build/deployment level via `web/Dockerfile.secure` and network configuration.

| Finding | ID | Vulnerable Behaviour | Secure Mode Behaviour |
|---|---|---|---|
| SQL Injection — Login | E1 | String-concatenated SQL, MD5 password | Parameterised query, bcrypt/werkzeug `check_password_hash` |
| SQL Injection — Course Search | E2 | Search term injected into `LIKE` clause | Parameterised `LIKE %s` |
| Stored XSS — Announcements | E3 | `\| safe` filter renders raw HTML | Output escaped; `Content-Security-Policy` header added |
| IDOR — Invoice Access | E4 | No ownership check on `/invoice/<id>` | Ownership enforced; admins may view any invoice |
| Weak Session Token | E5 | Predictable `user_id-minute` cookie | Random 32-byte `secrets.token_urlsafe` token, server-side session table, `HttpOnly` + `SameSite=Lax` |
| Unrestricted File Upload | E6 | Any extension accepted, original filename kept, public inline serve | Extension allow-list (`.png .jpg .jpeg .gif .pdf .txt`), randomised stored filename, auth-gated download, `X-Content-Type-Options: nosniff` |
| Static API Key | E11 | Hardcoded `demo-api-key` in all requests | Rotated key (`API_SECURE_KEY` env var) used when secure mode is on |
| Weak Password Hashing | E12 | Unsalted MD5 | Salted bcrypt via `werkzeug.security.generate_password_hash` |
| Info-Leaking Headers | — | `Server: MyEduConnect-Legacy/1.0`, `X-Powered-By` | Headers stripped; `X-Frame-Options: DENY`, `Content-Security-Policy` added |

Infrastructure findings fixed at build/deploy level (not toggled in-app):

| Finding | ID | Remediation |
|---|---|---|
| Weak SSH credentials | E7 | `web/Dockerfile.secure` removes SSH or changes credentials |
| Exposed Adminer | E8 | Remove or restrict Adminer port in `docker-compose.yml` |
| Exposed MySQL port | E9 | Remove `3306` from host port bindings |
| Writable root backup script | E10 | `web/Dockerfile.secure` fixes file permissions and sudo rule |

---

## Phase 5 Re-Test Workflow

1. Start in vulnerable mode (default on this branch without env vars).
2. Run Phase 4 exploits and capture **before** screenshots — confirm findings reproduce.
3. Enable Secure Mode via the admin panel toggle (Option 1 above).
4. Re-run the same exploits and capture **after** screenshots — confirm each finding is blocked.
5. Document the before/after comparison in the Phase 5 section of the final report.

Recommended re-test order:

```
E1  → Try SQL injection login bypass        → parameterised query blocks it
E2  → Try SQLi in course search             → parameterised LIKE blocks it
E3  → Try stored XSS payload in announcement → CSP + escaping blocks execution
E4  → Try accessing another user's invoice  → 404 returned (ownership enforced)
E5  → Try forging/predicting a session token → random token cannot be guessed
E6  → Try uploading a .php web shell         → 400 returned (extension blocked)
E11 → Inspect API request header key        → rotated key visible in traffic
E12 → Dump hashes from DB, try to crack     → bcrypt hashes resist offline cracking
```

---

## Resetting Lab Data

Normal stop/start keeps database data:

```bash
docker compose down
docker compose up
```

Full reset (wipes all volumes including DB):

```bash
docker compose down -v
docker compose up --build
```

---

## Documentation

| File | Description |
|---|---|
| `docs/setup-guide.md` | Redeployment and setup instructions |
| `docs/architecture.md` | Architecture and network layout |
| `docs/vulnerability-matrix.md` | Deliberate vulnerability matrix |
| `docs/phase-checklist.md` | Assignment phase checklist |
| `docs/hardening-plan.md` | Phase 5 remediation and re-test guidance |

---

## Evidence Structure

| Folder | Purpose |
|---|---|
| `evidence/screenshots/` | Phase 1 platform screenshots |
| `evidence/scans/` | Phase 2 OSINT, Nmap, enumeration evidence |
| `evidence/screenshots_phase3/` | Phase 3 vulnerability assessment screenshots |
| `evidence/pcaps/` | Wireshark / traffic-capture evidence |
| `exploits/` | Phase 4 payload notes and exploit scripts |
