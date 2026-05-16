# Phase 2 Checklist

Status: complete.

## 2.1 OSINT and Footprinting

- WHOIS check completed: `evidence/scans/whois/phase2-whois.txt`
- DNS lookup completed: `evidence/scans/dns/phase2-nslookup.txt`
- DNS ANY lookup completed: `evidence/scans/dns/phase2-dig-any.txt`
- Reverse DNS lookup completed: `evidence/scans/dns/phase2-reverse-dns.txt`
- theHarvester completed: `evidence/scans/theharvester/`
- Search-engine reconnaissance screenshots completed: `evidence/scans/search-engine-recon/`
- WhatWeb fingerprinting completed: `evidence/scans/whatweb/`
- At least 10 intelligence findings documented: `docs/phase2-findings.md`

## 2.2 Active Scanning

- Ping proof captured: `evidence/scans/nmap/phase2-ping-proof.png`
- Basic Nmap scan captured: `evidence/scans/nmap/phase2-basic-nmap.png`
- TCP service/version scan completed: `evidence/scans/nmap/phase2-tcp-service-scan.txt`
- Full TCP scan completed: `evidence/scans/nmap/phase2-full-tcp-scan.txt`
- UDP scan completed: `evidence/scans/nmap/phase2-udp-scan.txt`
- HTTP Nmap enumeration completed: `evidence/scans/nmap/phase2-http-enum.txt`
- SSH Nmap enumeration completed: `evidence/scans/nmap/phase2-ssh-enum.txt`
- MySQL Nmap enumeration completed: `evidence/scans/nmap/phase2-mysql-enum.txt`
- Services-discovered table documented: `docs/phase2-findings.md`

## 2.3 Service Enumeration

- Web portal `8080` enumerated with headers, methods, WhatWeb, banner grabbing, anonymous access checks, and weak credential checks.
- REST API `5001` enumerated with headers, WhatWeb, banner grabbing, and anonymous access checks.
- Adminer `8081` enumerated with headers, methods, WhatWeb, banner grabbing, and weak credential checks.
- SSH `2222` enumerated with Nmap scripts, banner grabbing, and weak credential checks.
- MySQL `3306` enumerated with Nmap scripts, banner grabbing, anonymous access checks, and weak credential checks.
- Enumeration evidence stored in `evidence/scans/enumeration/`.

## Final Phase 2 Evidence Locations

- OSINT and DNS: `evidence/scans/whois/`, `evidence/scans/dns/`, `evidence/scans/theharvester/`, `evidence/scans/search-engine-recon/`
- Active scanning: `evidence/scans/nmap/`
- HTTP and technology fingerprinting: `evidence/scans/http/`, `evidence/scans/whatweb/`
- Service enumeration: `evidence/scans/enumeration/`
- Written findings: `docs/phase2-findings.md`
