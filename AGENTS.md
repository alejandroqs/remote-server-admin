# AGENTS.md - System Architecture & Context

## 1. Project Overview
**Project Name:** Remote Server Admin (Django Dashboard)
**Type:** Monolithic Web Application / Server Management Utility.
**Goal:** Lightweight, cross-platform server monitoring and administration interface (Webmin-like).
**Philosophy:** "Batteries Included". Zero external service dependencies (Redis/Postgres optional). Relies on Python standard library and Django ecosystem.
**Repository Status:** Active Development.

## 2. Technical Stack & Constraints

### Backend
* **Core:** Python 3.10+, Django 5.x.
* **System Interface:** `psutil` (Cross-platform system monitoring).
* **API:** Django Rest Framework (DRF) - *ReadOnly Architecture for metrics*.
* **Server:**
    * **Dev/Windows:** `waitress` (via `start_server.py`).
    * **Prod/Linux:** `gunicorn` (auto-detected via `start_server.py`).
* **Static Files:** `whitenoise` (CompressedManifestStaticFilesStorage).

### Frontend (Strict Constraints)
* **Pattern:** Server-Side Rendering (SSR) + Hypermedia (HATEOAS).
* **Framework:** Bootstrap 5.3 (CDN) - *Dark Mode Native Support*.
* **Interactivity:** **HTMX** (v1.9+).
    * *Rule:* Use HTMX for DOM updates. Avoid vanilla JS `fetch` unless handling Canvas/Charts.
* **Visualization:** Chart.js (fed via JSON endpoints).
* **Icons:** FontAwesome 6.

### Data Persistence
* **Database:** SQLite (default).
* **Metrics:** Time-series data stored in relational table `SystemMetric`.
* **Concurrency:** Background Daemon Thread (`threading`) triggered by launcher script.

## 3. Directory Structure & Key Components

```text
server_dashboard/
├── .env                    # Secrets (DEBUG, SECRET_KEY) - GitIgnored
├── start_server.py         # Entry Point (OS Detection + Thread Manager)
├── setup-agent-links.sh    # Agent Context Setup (Bash)
├── Setup-AgentLinks.ps1    # Agent Context Setup (PowerShell)
├── manage.py               # Django CLI
├── locale/                 # Gettext translations (en/es)
├── skills/                 # Specialized Agent Skills (SSOT)
│   ├── django-expert/
│   ├── python-design-patterns/
│   └── python-performance-optimizations/
├── core/
│   ├── settings.py         # Config: i18n, Logging, WhiteNoise, DRF
│   └── urls.py             # Root URLConf + Error Handlers (404/500)
├── monitor/
│   ├── api.py              # DRF ViewSets (ServerViewSet, MetricViewSet)
│   ├── management/
│   │   └── commands/
│   │       └── collect_metrics.py # Background Worker Logic
│   ├── templates/monitor/
│   │   ├── base.html       # Layout: Sidebar, Navbar, Theme Toggles, Scripts
│   │   ├── partials/       # HTMX Fragments (Atomic design)
│   │   └── ...             # Views: dashboard, processes, network, inventory
│   └── views.py            # Logic: FBV for Dashboard, CBV for CRUD
```

## 4. Feature Set & Implementation Status

### Core Modules
1.  **Dashboard:** Real-time metrics (CPU/RAM/Swap/Disk).
    * *Impl:* HTMX polling (2s) + Chart.js (JSON fetch).
    * *Layout:* Cards showing % usage, color-coded (CPU=Blue, RAM=Green, Swap=Yellow, Disk=Red).
2.  **Web Terminal:**
    * *Impl:* Django View executing `subprocess.run(shell=True)`.
    * *Features:* Persistent Current Working Directory (Session-based).
    * *Security:* Superuser only.
3.  **Process Management:**
    * *Impl:* `psutil` listing + `kill()` signal.
    * *Security:* Superuser required for destructive actions.
4.  **Network Monitor:**
    * *Impl:* Interface enumeration + Connection table (Netstat-like).
5.  **Server Inventory:**
    * *Impl:* Full CRUD using Class-Based Views (CBV) & ModelForms.

### Special Features
*   **Demo Mode:**
    *   *Trigger:* `DEMO_MODE=True` in environment.
    *   *Behavior:* Simulates metrics (waves), creates ephemeral admin user, read-only terminal/process modules.
    *   *Purpose:* Safe deployment on PaaS (Render, Railway) for portfolio demonstration.

### Cross-Cutting Concerns
* **Security:**
    * Login Required middleware.
    * CSRF Protection (globally injected into HTMX headers).
    * `DEBUG=False` hardened (Custom 404/500 templates).
* **UX/UI:**
    * **Dark Mode:** Auto-sync with OS + Manual Toggle (LocalStorage).
    * **i18n:** English/Spanish support (Gettext).
* **Deployment:**
    * Multi-OS Launcher (`start_server.py`): Auto-compiles translations, collects statics, launches background thread, and selects web server engine.

## 5. specialized Skills & Guidelines

Refer to these dedicated skill files for in-depth guidance on specific topics.
**IMPORTANT:** Before starting a complex task, check if a relevant skill exists in `skills/`.

*   **Django Backend Expert:** `skills/django-expert/SKILL.md`
    *   *Usage:* Advanced ORM queries, DRF architecture, Authentication, Security, and Production-readiness.
*   **Python Design Patterns:** `skills/python-design-patterns/SKILL.md`
    *   *Usage:* Refactoring strategies, SOLID principles, and deciding when to use abstraction vs. simplicity.
*   **Performance Optimization:** `skills/python-performance-optimizations/SKILL.md`
    *   *Usage:* Profiling (cProfile), Memory leak detection, N+1 query resolution, and algorithm optimization.

## 6. Development Guidelines for AI Agents

When contributing to this codebase, adhere to the following:

1.  **Language Requirement:** All code, variable names, function names, and inline comments must be written in **English**. Spanish is only allowed in translation files (`.po`) or specific user-facing strings marked for translation.
2.  **HTMX First:** Do not introduce React/Vue. If a UI component needs updating, create a partial template and use `hx-get` or `hx-post`.
3.  **Stateless Views:** Keep logic in `views.py` or `api.py`. Avoid session-heavy logic for metrics.
4.  **Cross-Platform Compatibility:** Always check `platform.system()` if using OS-specific commands (e.g., file paths, subprocesses).
5.  **Translation:** All user-facing strings must use `{% trans "String" %}` in templates or `_("String")` in Python.
6.  **Logging:** Use `logging.getLogger('monitor')`. Do not use `print()`.

### Agent Environment Setup
To ensure you have access to the latest context and skills, run the setup script for your OS:
*   **Windows:** `.\Setup-AgentLinks.ps1`
*   **Linux/Mac:** `./setup-agent-links.sh`
This will create symlinks from `AGENTS.md` and `skills/` to your specific agent configuration (e.g., `.cursorrules`, `.clinerules`, `.gemini/`).

## 7. Roadmap

* [x] **Demo Mode:** Simulation for public portfolio display.
* [ ] **Log Viewer:** Web interface to read `server.log` in real-time (WebSockets/HTMX polling).
* [ ] **Authentication:** 2FA implementation.
* [ ] **Alerting:** Email/Telegram hooks when CPU > 90%.
* [ ] **Architecture Upgrade:** Migrate background thread to Celery/Redis (only if scale requires).