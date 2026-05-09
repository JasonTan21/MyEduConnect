# MyEduConnect Vulnerable Lab

This project is a deliberately vulnerable local training platform for the CCS6324 final assignment case study. It represents the fictional MyEduConnect Sdn Bhd learning portal and is designed for authorized testing only inside a local Docker lab.

## What This Covers

- Working web platform: registration, login, profile, course browsing/search, enrolment, mock payment, support uploads, dashboard, admin panel.
- Backend server: Flask web application with MySQL.
- Additional component: separate Flask REST API consumed by the web portal.
- Deployment: Docker Compose with web, API, MySQL, Adminer, and exposed SSH.
- Deliberate vulnerabilities: OWASP Top 10 web issues, server/OS misconfigurations, crypto weaknesses, and a network-layer cleartext issue.
- Phase 1 deliverables: architecture diagram, vulnerability matrix, redeployment guide, and source code.

## Quick Start

```bash
docker compose up --build
```

Open these local services:

- Web portal: http://localhost:8080
- Adminer database console: http://localhost:8081
- REST API health: http://localhost:5001/health
- SSH into web container: `ssh student@localhost -p 2222`

Demo accounts:

- Admin: `admin@myeduconnect.local` / `admin123`
- Student: `aina@student.local` / `student123`
- Teacher: `teacher@school.local` / `teacher123`
- SSH: `student` / `student123`
- MySQL root: `root` / `root`
- MySQL app user: `myedu` / `myedu123`

## Important Safety Note

Do not deploy this to the public internet. The weak credentials, unsafe SQL, weak sessions, exposed services, and insecure upload handling are intentional so the group can demonstrate exploitation and remediation.

## Suggested Evidence Folders

Use the included folders to organize your assignment evidence:

- `evidence/scans`
- `evidence/pcaps`
- `evidence/screenshots`
- `exploits`

## Main Documentation

- [Setup Guide](docs/setup-guide.md)
- [Architecture](docs/architecture.md)
- [Vulnerability Matrix](docs/vulnerability-matrix.md)
- [Phase Checklist](docs/phase-checklist.md)
- [Hardening Plan](docs/hardening-plan.md)
