# MyEduConnect Security Engagement Lab — Secure Toggle Branch

This branch (`feature/secure-toggle`) extends the vulnerable lab with an **in-app Secure Mode toggle** for Phase 5 demonstration. The same Docker Compose stack can switch between fully-exploitable (Phase 4) and remediated (Phase 5) behaviour without rebuilding the image. For full infrastructure hardening (SSH removed, Adminer removed, MySQL unexposed), a separate hardened stack `docker-compose.secure.yml` is also provided.

> **Safety Notice** — Do not deploy this project to the public internet. Weak credentials, intentional vulnerabilities, and cleartext transport are present by design for coursework demonstration only.

---

## Branch Purpose

| Branch | Purpose |
|---|---|
| `main` | Vulnerable baseline — Phase 1–4 evidence and exploitation |
| `feature/secure-toggle` | This branch — adds Secure Mode toggle and hardened stack for Phase 5 re-test |

Lecturers should review `main` for the exploitable platform and evidence, then switch to this branch to see the hardened version and re-test comparison.

---

## Two Stacks at a Glance

| Stack | Command | What it does |
|---|---|---|
| **Vulnerable** (default) | `docker compose up --build` | All vulnerabilities active; app starts in vulnerable mode |
| **App-layer secure** | `SECURE_MODE=1 docker compose up --build` | Same infra, app code paths hardened (E1–E6, E11, E12) |
| **Fully hardened** | `docker compose -f docker-compose.secure.yml up -d --build` | App hardened + infra hardened (E7–E12 all fixed) |

Run **only one stack at a time** — both publish the web portal on port `8080` so re-test URLs match Phase 4 exactly.

---

## Quick Start — Vulnerable Stack

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

## Enabling Remediated (Secure) Mode — App Layer

There are three ways to enable Secure Mode on the default stack depending on the demo scenario.

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

### Option 3 — Locked Secure Mode (No UI Revert)

To demonstrate a production-style hardened deployment where the UI toggle is disabled and the mode cannot be switched back to vulnerable:

```bash
SECURE_MODE=1 LOCK_MODE=1 docker compose up --build
```

In this mode, `POST /mode` returns `403 Forbidden` and the toggle button is hidden in the admin panel.

---

## Enabling Infrastructure Hardening — Hardened Stack

To see the infrastructure findings (E7–E11) remediated, use the separate hardened compose file. This uses `web/Dockerfile.secure` which removes SSH, and the compose file removes Adminer, unexposes MySQL and the API port, rotates all credentials, and locks the app into Secure Mode.

**Step 1 — Stop the vulnerable stack first:**

```bash
docker compose down
```

**Step 2 — Start the hardened stack:**

```bash
docker compose -f docker-compose.secure.yml up -d --build
```

**Step 3 — Verify it is running:**

```bash
docker ps
```

You should see `myeduconnect-web-secure`, `myeduconnect-api-secure`, and `myeduconnect-db-secure`. No Adminer container will be listed.

**Step 4 — Re-test infrastructure findings:**

| Finding | ID | How to verify it is fixed |
|---|---|---|
| SSH removed | E7 | `ssh student@localhost -p 2222` — connection refused |
| Adminer removed | E8 | `http://localhost:8081` — connection refused |
| MySQL unexposed | E8 | `mysql -h 127.0.0.1 -P 3306 -u root -p` from host — connection refused |
| API port unexposed | E11 | `http://localhost:5001/health` from host — connection refused |
| App locked in Secure Mode | E1–E6, E12 | Toggle button hidden in admin panel; `POST /mode` returns 403 |

**Step 5 — To stop the hardened stack:**

```bash
docker compose -f docker-compose.secure.yml down
```

To also wipe the hardened stack's database volume:

```bash
docker compose -f docker-compose.secure.yml down -v
```

> **Note:** The hardened stack uses its own named volume (`db_data_secure`) so it does not share or overwrite the vulnerable stack's database data.

---

## What Each Stack Fixes

### Application-Layer Findings (controlled by `SECURE_MODE` env var / in-app toggle)

| Finding | ID | Vulnerable Behaviour | Secure Mode Behaviour |
|---|---|---|---|
| SQL Injection — Login | E1 | String-concatenated SQL, MD5 password | Parameterised query, bcrypt `check_password_hash` |
| SQL Injection — Course Search | E2 | Search term injected into `LIKE` clause | Parameterised `LIKE %s` |
| Stored XSS — Announcements | E3 | `\| safe` filter renders raw HTML | Output escaped; `Content-Security-Policy` header added |
| IDOR — Invoice Access | E4 | No ownership check on `/invoice/<id>` | Ownership enforced; admins may view any invoice |
| Weak Session Token | E5 | Predictable `user_id-minute` cookie | Random 32-byte token, server-side session table, `HttpOnly` + `SameSite=Lax` |
| Unrestricted File Upload | E6 | Any extension accepted, original filename kept, public inline serve | Extension allow-list, randomised stored filename, auth-gated download, `X-Content-Type-Options: nosniff` |
| Static API Key | E11 | Hardcoded `demo-api-key` in all requests | Rotated key via `API_SECURE_KEY` env var |
| Weak Password Hashing | E12 | Unsalted MD5 | Salted bcrypt via `werkzeug.security.generate_password_hash` |
| Info-Leaking Headers | — | `Server: MyEduConnect-Legacy/1.0`, `X-Powered-By` | Headers stripped; `X-Frame-Options: DENY`, `Content-Security-Policy` added |

### Infrastructure Findings (fixed by `docker-compose.secure.yml` + `web/Dockerfile.secure`)

| Finding | ID | Remediation in hardened stack |
|---|---|---|
| Weak SSH / exposed shell | E7 | SSH server not installed in `Dockerfile.secure`; port 2222 not published |
| Exposed Adminer & MySQL port | E8 | Adminer service removed; MySQL port 3306 not published to host; strong unique DB credentials |
| World-writable upload dir / non-root | E9 | App runs as non-root user; upload dir permissions corrected in `Dockerfile.secure` |
| Writable root backup script / sudo | E10 | `myedu-backup` script and `NOPASSWD` sudo rule removed in `Dockerfile.secure` |
| API port exposed to host | E11 | Port 5001 not published; API only reachable on internal Docker network |

---

## Phase 5 Re-Test Workflow

### Application-layer re-test (in-app toggle)

1. Start vulnerable stack: `docker compose up --build`
2. Run Phase 4 exploits — capture **before** screenshots confirming findings reproduce.
3. Enable Secure Mode via Admin Panel toggle (Option 1 above).
4. Re-run the same exploits — capture **after** screenshots confirming each finding is blocked.

Recommended order:

```
E1  → Try SQL injection login bypass         → parameterised query blocks it
E2  → Try SQLi in course search              → parameterised LIKE blocks it
E3  → Try stored XSS payload in announcement → CSP + escaping blocks execution
E4  → Try accessing another user's invoice   → 404 returned (ownership enforced)
E5  → Try forging/predicting a session token → random token cannot be guessed
E6  → Try uploading a .php web shell         → 400 returned (extension blocked)
E11 → Inspect API request header key         → rotated key visible in traffic
E12 → Dump hashes from DB, try to crack      → bcrypt hashes resist offline cracking
```

### Infrastructure re-test (hardened stack)

1. Stop vulnerable stack: `docker compose down`
2. Start hardened stack: `docker compose -f docker-compose.secure.yml up -d --build`
3. Re-test each infra finding using the verification steps in the table above.
4. Capture screenshots of each refused connection / removed service.

---

## Resetting Lab Data

Normal stop/start keeps database data:

```bash
docker compose down
docker compose up
```

Full reset of vulnerable stack (wipes all volumes):

```bash
docker compose down -v
docker compose up --build
```

Full reset of hardened stack (wipes hardened volumes):

```bash
docker compose -f docker-compose.secure.yml down -v
docker compose -f docker-compose.secure.yml up -d --build
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
