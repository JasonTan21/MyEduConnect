# Phase 2: Reconnaissance and Enumeration Findings

## Scope

Reconnaissance and enumeration were performed against the locally hosted MyEduConnect lab platform.

| Item | Value |
|---|---|
| Target company | MyEduConnect Sdn Bhd |
| Lab domain | `myeduconnect.local` |
| Target IP | `192.168.0.92` |
| Main web portal | `http://192.168.0.92:8080` |
| REST API | `http://192.168.0.92:5001` |
| Adminer console | `http://192.168.0.92:8081` |

Because MyEduConnect Sdn Bhd is fictional, public OSINT was simulated against the controlled lab domain and locally hosted platform. No real third-party organization was targeted.

## 2.1 OSINT and Footprinting

| No. | Intelligence Finding | Tool / Source | Evidence File | Security Relevance |
|---:|---|---|---|---|
| 1 | WHOIS lookup returned no public WHOIS server for `myeduconnect.local`. | `whois` | `evidence/scans/whois/phase2-whois.txt` | Confirms the lab domain is not publicly registered; reconnaissance must continue through local network discovery. |
| 2 | DNS lookup for `myeduconnect.local` returned `NXDOMAIN`. | `nslookup` | `evidence/scans/dns/phase2-nslookup.txt` | The domain is not resolvable through the configured DNS server. |
| 3 | `dig ANY` confirmed no DNS answers for `myeduconnect.local` and warned that `.local` is reserved for mDNS. | `dig` | `evidence/scans/dns/phase2-dig-any.txt` | Indicates a local/private lab naming scheme instead of public DNS. |
| 4 | Reverse DNS lookup for `192.168.0.92` returned no useful PTR host record. | `dig -x` | `evidence/scans/dns/phase2-reverse-dns.txt` | Host identity cannot be confirmed through reverse DNS alone. |
| 5 | theHarvester returned no public hosts for `myeduconnect.local`. | theHarvester | `evidence/scans/theharvester/phase2-theharvester.json` | No public search-engine footprint exists for the fictional lab domain. |
| 6 | Search-engine reconnaissance produced limited/no public results for `myeduconnect.local`. | Browser search | `evidence/scans/search-engine-recon/phase2-myeduconnect.local.png` | Confirms the target is a private lab asset, not an indexed public service. |
| 7 | Search-engine reconnaissance for `MyEduConnect Sdn Bhd` produced controlled/limited public footprint. | Browser search | `evidence/scans/search-engine-recon/phase2-MyEduConnect Sdn Bhd.png` | Supports the fictional-company assumption and limits public OSINT exposure. |
| 8 | Main web portal is reachable on port `8080` and titled `MyEduConnect`. | WhatWeb / curl | `evidence/scans/whatweb/phase2-whatweb-web.txt` | Identifies the primary application entry point. |
| 9 | Web stack fingerprint discloses `Werkzeug/3.1.8`, `Python/3.12.13`, and `MyEduConnect-Legacy/1.0`. | WhatWeb / HTTP headers | `evidence/scans/whatweb/phase2-whatweb-web.txt`, `evidence/scans/http/phase2-web-headers.txt` | Technology disclosure helps attackers select framework-specific tests. |
| 10 | Public web content disclosed demo emails including `admin@myeduconnect.local` and `aina@student.local`. | WhatWeb | `evidence/scans/whatweb/phase2-whatweb-web.txt` | Email/user discovery can support password guessing and social-engineering scenarios. |
| 11 | REST API health endpoint is reachable at `http://192.168.0.92:5001/health`. | curl / WhatWeb | `evidence/scans/http/phase2-api-headers.txt`, `evidence/scans/whatweb/phase2-whatweb-api.txt` | Confirms a separate API attack surface. |
| 12 | Adminer database console is reachable on port `8081` and exposes PHP `8.4.21`. | curl / WhatWeb | `evidence/scans/http/phase2-adminer-headers.txt`, `evidence/scans/whatweb/phase2-whatweb-adminer.txt` | Exposed database administration interface increases risk if credentials are weak. |

## 2.2 Active Scanning

Status: complete. TCP and UDP scans were performed against the target host, and focused service-version scans were performed against the platform ports.

### Services Discovered

| Port | Protocol | Service | Version / Fingerprint | Component | Evidence |
|---:|---|---|---|---|---|
| 2222 | TCP | SSH | OpenSSH `10.0p2 Debian 7+deb13u2` | Web container SSH service | `evidence/scans/nmap/phase2-tcp-service-scan.txt` |
| 3306 | TCP | MySQL | MySQL `8.0.46`, `mysql_native_password` | Database service | `evidence/scans/nmap/phase2-tcp-service-scan.txt` |
| 5001 | TCP | HTTP | Werkzeug `3.1.8`, Python `3.12.13` | REST API | `evidence/scans/nmap/phase2-tcp-service-scan.txt` |
| 8080 | TCP | HTTP | Werkzeug `3.1.8`, Python `3.12.13`; title `MyEduConnect` | Main web portal | `evidence/scans/nmap/phase2-tcp-service-scan.txt` |
| 8081 | TCP | HTTP | PHP `8.4.21`; title `Login - Adminer` | Adminer database console | `evidence/scans/nmap/phase2-tcp-service-scan.txt` |

### Additional Host-Level Ports Observed

The full TCP scan also identified host-level services on ports `22`, `53`, `5000`, `7000`, and `60394`. These were treated as host/VM environment observations and not primary MyEduConnect application components. The MyEduConnect platform assessment focused on the intentionally exposed lab ports: `2222`, `3306`, `5001`, `8080`, and `8081`.

### Scan Commands Used

```bash
nmap 192.168.0.92
nmap -p- --min-rate 3000 192.168.0.92 -oN phase2-full-tcp-scan.txt
sudo nmap -sU 192.168.0.92 -oN phase2-udp-scan.txt
nmap -sV -sC -p 2222,3306,5001,8080,8081 192.168.0.92 -oN phase2-tcp-service-scan.txt
nmap -sV --script http-title,http-headers,http-methods -p 5001,8080,8081 192.168.0.92 -oN phase2-http-enum.txt
nmap -sV --script ssh2-enum-algos,ssh-hostkey -p 2222 192.168.0.92 -oN phase2-ssh-enum.txt
nmap -sV --script mysql-info -p 3306 192.168.0.92 -oN phase2-mysql-enum.txt
```

## 2.3 Service Enumeration

Status: complete. Each discovered MyEduConnect service was enumerated using a combination of Nmap scripts, HTTP header inspection, banner grabbing, default-credential checks, and anonymous-access checks.

| Service | Enumeration Performed | Finding | Evidence |
|---|---|---|---|
| HTTP web portal `8080` | HTTP headers, title, supported methods, WhatWeb fingerprinting, banner grabbing, anonymous access check, weak credential check | Portal title is `MyEduConnect`; server leaks Werkzeug/Python plus custom `MyEduConnect-Legacy/1.0` and `X-Powered-By: Flask-Debug-Lab`. Homepage and course catalogue are anonymously accessible, while dashboard redirects unauthenticated users to `/login`. Demo web credentials were confirmed. | `evidence/scans/http/phase2-web-headers.txt`, `evidence/scans/nmap/phase2-http-enum.txt`, `evidence/scans/enumeration/phase2-web-banner.txt`, `evidence/scans/enumeration/phase2-anonymous-web-home.txt`, `evidence/scans/enumeration/phase2-anonymous-web-courses.txt`, `evidence/scans/enumeration/phase2-anonymous-dashboard.txt`, `evidence/scans/enumeration/phase2-web-weak-credential.png` |
| REST API `5001` | HTTP headers, title, WhatWeb fingerprinting, banner grabbing, anonymous access check | API `/health` endpoint responds without authentication and discloses service name/status. `/internal/stats` rejects anonymous access with `403 invalid api key`. | `evidence/scans/http/phase2-api-headers.txt`, `evidence/scans/whatweb/phase2-whatweb-api.txt`, `evidence/scans/enumeration/phase2-api-banner.txt`, `evidence/scans/enumeration/phase2-anonymous-api-health.txt`, `evidence/scans/enumeration/phase2-anonymous-api-stats.txt` |
| Adminer `8081` | HTTP headers, title, supported methods, WhatWeb fingerprinting, banner grabbing, weak credential check | Adminer login page exposed; PHP `8.4.21` disclosed; `GET`, `HEAD`, `POST`, and `OPTIONS` are supported. Weak database credentials were confirmed through the Adminer interface. | `evidence/scans/http/phase2-adminer-headers.txt`, `evidence/scans/nmap/phase2-http-enum.txt`, `evidence/scans/enumeration/phase2-adminer-banner.txt`, `evidence/scans/enumeration/phase2-adminer-weak-credential.png` |
| SSH `2222` | Version detection, SSH algorithm enumeration, banner grabbing, weak credential check | OpenSSH service exposed on non-standard host port `2222`; OS detected as Linux. Banner confirms `OpenSSH_10.0p2 Debian-7+deb13u2`. Weak SSH credentials were confirmed. | `evidence/scans/nmap/phase2-ssh-enum.txt`, `evidence/scans/enumeration/phase2-ssh-banner.txt`, `evidence/scans/enumeration/phase2-ssh-weak-credential.png` |
| MySQL `3306` | Version detection, MySQL info script, banner grabbing, anonymous access check, weak credential checks | MySQL `8.0.46` exposed; `mysql_native_password` authentication plugin discovered. Anonymous access was denied, but weak known credentials for `root` and `myedu` were confirmed. | `evidence/scans/nmap/phase2-tcp-service-scan.txt`, `evidence/scans/nmap/phase2-mysql-enum.txt`, `evidence/scans/enumeration/phase2-mysql-banner.txt`, `evidence/scans/enumeration/phase2-anonymous-mysql.png`, `evidence/scans/enumeration/phase2-mysql-weak-credential.png`, `evidence/scans/enumeration/phase2-app-db-user-weak-credential.png` |

### Banner Grabbing Commands Used

```bash
nc -nv 192.168.0.92 2222
timeout 5 nc -nv 192.168.0.92 3306
printf "HEAD / HTTP/1.0\r\n\r\n" | nc -nv 192.168.0.92 8080
printf "GET /health HTTP/1.0\r\n\r\n" | nc -nv 192.168.0.92 5001
printf "HEAD / HTTP/1.0\r\n\r\n" | nc -nv 192.168.0.92 8081
```

### Default-Credential Checks

```bash
ssh student@192.168.0.92 -p 2222
mysql --ssl=0 -h 192.168.0.92 -P 3306 -u root -proot -e "SHOW DATABASES;"
mysql --ssl=0 -h 192.168.0.92 -P 3306 -u myedu -pmyedu123 -e "SHOW DATABASES;"
```

Adminer and web application default/weak credential checks were performed through the browser and captured as screenshots.

### Anonymous-Access Checks

```bash
curl -i http://192.168.0.92:8080/
curl -i http://192.168.0.92:8080/courses
curl -i http://192.168.0.92:8080/dashboard
curl -i http://192.168.0.92:5001/health
curl -i http://192.168.0.92:5001/internal/stats
mysql --ssl=0 -h 192.168.0.92 -P 3306 --user='' --skip-password -e "SHOW DATABASES;"
```

## Phase 2 Completion Statement

Phase 2 is complete. The evidence set includes OSINT/footprinting results, TCP and UDP port scans, service-version detection, HTTP method/header enumeration, banner grabbing, default-credential checks, anonymous-access checks, screenshots, and raw text outputs. These files are organized under `evidence/scans/` and can be referenced in the final report appendices.
