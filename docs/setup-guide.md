# Setup Guide

## Prerequisites

- Docker Desktop or Docker Engine with Compose.
- At least 2 GB free RAM for the lab.
- Browser for the web portal and Adminer.
- Optional tools for later assignment phases: Nmap, Gobuster, Nikto/Nuclei, Wireshark, Hydra, John/Hashcat, curl.

## Deploy

From the `myeduconnect-lab` directory:

```bash
docker compose up --build
```

Wait until the web service says it is running on port `8080`.

## Access URLs

| Component | URL / Access | Purpose |
|---|---|---|
| Web portal | `http://localhost:8080` | Main MyEduConnect vulnerable learning platform |
| REST API | `http://localhost:5001/health` | Separate API component consumed by the web portal |
| Adminer | `http://localhost:8081` | Exposed database administration service |
| SSH | `ssh student@localhost -p 2222` | Exposed SSH on web container |
| MySQL | `localhost:3306` | Exposed database service |

## Seeded Credentials

| Account | Username | Password |
|---|---|---|
| Admin portal user | `admin@myeduconnect.local` | `admin123` |
| Student portal user | `aina@student.local` | `student123` |
| Teacher portal user | `teacher@school.local` | `teacher123` |
| SSH user | `student` | `student123` |
| MySQL root | `root` | `root` |
| MySQL app | `myedu` | `myedu123` |

## Reset Lab State

```bash
docker compose down -v
docker compose up --build
```

The `-v` removes the MySQL volume so the application reseeds the database.

## Instructor Redeployment Notes

The app initializes its own database tables and sample records on first boot. The source code, Dockerfiles, Compose file, and documentation are all inside this project folder, so the lab can be redeployed from a clean Docker host.
