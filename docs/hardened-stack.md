# Hardened Stack — Phase 5 Re-test

A second, hardened deployment that remediates the findings the runtime toggle can't reach
(infrastructure E7–E11) **and** runs the app locked in secure mode (E1–E6, E12). Use it to
produce the Phase 5 "after" evidence without disturbing the vulnerable Phase 4 environment.

Files: [`docker-compose.secure.yml`](../docker-compose.secure.yml), [`web/Dockerfile.secure`](../web/Dockerfile.secure).

## Run it (one stack at a time — both use host port 8080)
```bash
docker compose down                                    # stop the vulnerable stack
docker compose -f docker-compose.secure.yml up -d --build
# ... re-test (below) ...
docker compose -f docker-compose.secure.yml down       # stop hardened
docker compose up -d                                   # bring the vulnerable lab back
```
The hardened stack uses its own project name (`myeduconnect-secure`), container names
(`*-secure`) and a separate DB volume (`db_data_secure`), so it never touches the vulnerable
lab's data.

## What it remediates
| # | Finding | How it's fixed in the hardened stack |
|---|---|---|
| E1–E6, E12 | App-layer (SQLi/XSS/IDOR/session/upload/hashing) | `SECURE_MODE=1` + `LOCK_MODE=1` (toggle cannot be flipped back) |
| E7 | SSH weak creds / root login | No SSH server installed, port 2222 not published, no shell creds |
| E8 | Exposed MySQL + Adminer + weak creds | 3306 not published, Adminer removed, strong unique DB passwords |
| E9 | World-writable dirs | `/app/uploads` is `750`, app runs as non-root `appuser` |
| E10 | Sudo privesc script | Script not present; no sudoers NOPASSWD entry |
| E11 | Cleartext API + static key + exposure | 5001 not published, strong rotated `API_SECURE_KEY`, `demo-api-key` rejected |
| — | Debug + info-leak headers | `FLASK_DEBUG=0`; security headers (CSP, nosniff, X-Frame-Options) |

## Re-test (expected results — capture as Phase 5 "after")
```bash
B=http://localhost:8080
# App layer — exploits now fail:
curl -s -o /dev/null -w "%{http_code}\n" -X POST $B/login \
  --data-urlencode "email=admin@myeduconnect.local' -- -" --data-urlencode "password=x"   # 200 (Invalid login)
curl -s "$B/courses?q=%25%27%20UNION%20SELECT%20id,email,password_hash,role,bio%20FROM%20users%20--%20-" | grep -c -E "[a-f0-9]{32}"   # 0
curl -s -o /dev/null -w "%{http_code}\n" --cookie "session_id=1-0" $B/admin   # 302 -> /login
curl -s -o /dev/null -w "%{http_code}\n" -X POST $B/mode -d secure=0          # 403 (mode locked)

# Infra — services no longer reachable from the host:
for p in 2222 3306 5001 8081; do (exec 3<>/dev/tcp/127.0.0.1/$p) 2>/dev/null \
  && { echo "$p OPEN"; exec 3<&-; } || echo "$p REFUSED"; done                # all REFUSED

# Container hardening:
docker exec myeduconnect-web-secure id                     # uid=10001(appuser) — non-root
docker exec myeduconnect-web-secure sh -c "command -v sshd || echo NONE"      # NONE
docker exec myeduconnect-web-secure stat -c '%a %U' /app/uploads             # 750 appuser
```

Normal use still works (admin login with the real password, course search, internal API via
`/api-summary`) — only the abuse paths are closed.

## Notes
- Strong secrets are set in `docker-compose.secure.yml` (DB passwords, `API_SECURE_KEY`). They are
  demo values committed for the lab — in a real deployment load them from a secrets manager / `.env`.
- Transport is still plain HTTP inside the compose network. Full E11 closure (TLS/mTLS between web
  and api) is the one item left for a production setup; the lab closes the exposure + static-key
  parts, which is what the assignment demonstrates.
- This complements [`phase5-remediation-handoff.md`](../phase5-remediation-handoff.md): that doc is the
  per-finding source-fix spec; this stack is a ready-to-run reference implementation of it.
