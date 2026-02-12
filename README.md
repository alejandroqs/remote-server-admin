# Remote Server Admin 🚀

![Django](https://img.shields.io/badge/Django-5.0-092E20?style=for-the-badge&logo=django&logoColor=white)
![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![HTMX](https://img.shields.io/badge/HTMX-1.9-blue?style=for-the-badge&logo=htmx&logoColor=white)
![Bootstrap](https://img.shields.io/badge/Bootstrap-5.3-7952B3?style=for-the-badge&logo=bootstrap&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)

> **A lightweight "Webmin-like" server monitoring and administration platform, built with Django and HTMX.**

---

## 📖 Description

**Remote Server Admin** is a "Full Stack" solution for managing local or remote servers. Unlike complex traditional SPAs, this project uses **HTMX** to achieve real-time interactivity (partial DOM updates) while maintaining the simplicity and robustness of a monolithic Django architecture.

The system monitors critical resources (CPU, RAM, Disk), manages system processes, and exposes a REST API, all orchestrated by a custom cross-platform launcher.

### ✨ Key Features

* **📊 Real-Time Dashboard:** Metrics visualization via **HTMX** (polling) and historical charts with **Chart.js**.
* **🎭 Demo Mode:** Safe simulation mode for public portfolios (Paas deployments). Simulates traffic/load and blocks internal system commands.
* **💻 Web Terminal:** Fully functional web-based shell (Bash/CMD) for superusers with directory persistence.
* **⚡ Process Management:** Interactive table to inspect and terminate (Kill) processes (protected for superusers).
* **🌐 Network Monitor:** Inspection of active interfaces and connections (similar to `netstat`).
* **📦 Inventory CRUD:** Complete server management system with validations.
* **🔌 RESTful API:** JSON endpoints exposed via **Django Rest Framework**.
* **🎨 Modern UI:** Responsive design with automatic **Dark Mode** (system sync).
* **🚀 Hybrid Deployment:** Smart startup script for Windows (Waitress) and Linux (Gunicorn).

---

## 📸 Screenshots

*(Add your screenshots here, for example: `![Dashboard](docs/screenshot_dashboard.png)`)*

---

## 🛠️ Tech Stack & Architecture

The project follows an **MVT (Model-View-Template)** architecture enhanced with modern patterns:

### Backend
* **Framework:** Django 5.x
* **System Interface:** `psutil` (Cross-platform hardware abstraction).
* **API:** Django Rest Framework (DRF) for data exposure.
* **Concurrency:** Daemon thread (`threading`) for background metric collection without blocking the web server.

### Frontend
* **Style:** Bootstrap 5.3 (Heavy use of Grid System and CSS Variables for Dark Mode).
* **Interactivity:** **HTMX** replaces 90% of traditional JavaScript. Cards and tables update automatically without page reloads.
* **Charts:** Chart.js powered by lightweight JSON endpoints.

### Infrastructure / DevOps
* **Waitress/Gunicorn:** Production WSGI servers depending on the environment.
* **WhiteNoise:** Efficient static file management.
* **Logging:** Rotating log system for auditing.

---

## 🚀 Installation & Usage

### Prerequisites
* Python 3.10 or higher.

### 1. Clone the repository
```bash
git clone https://github.com/your-username/server-admin-pro.git
cd server-admin-pro
```

### 2. Set up the virtual environment
```bash
python -m venv venv
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure environment variables
Create a `.env` file in the root directory:
```ini
DEBUG=True
SECRET_KEY=your_local_secret_key
# Set to True to enable simulation mode (safe for public demos)
# DEMO_MODE=True
```

### 5. Start the System
This single command will run migrations, collect static files, and launch both the metric collector and the web server:
```bash
python start_server.py
```
Access at: `http://127.0.0.1:8000`

---

## 🤖 Contributing with AI Agents

This repository is designed to be **AI-First**. It includes a "Single Source of Truth" (SSOT) for context and specialized skills.

### 1. Setup Agent Context
Run the setup script to link your AI assistant (Cursor, Cline, Windsurf, Copilot, etc.) to the project's central context.

**Windows (PowerShell):**
```powershell
.\Setup-AgentLinks.ps1
```

**Linux/Mac (Bash):**
```bash
chmod +x setup-agent-links.sh
./setup-agent-links.sh
```

### 2. Specialized Skills
The `skills/` directory contains specialized instructions for AI agents:
*   **Django Expert:** Best practices for ORM and DRF.
*   **Design Patterns:** Architectural guidance (SOLID, KISS).
*   **Performance:** Optimization strategies for Python.

Refer to `AGENTS.md` for full development guidelines.

---

## 📂 Project Structure
```text
server_dashboard/
├── AGENTS.md           # SSOT for AI Context
├── skills/             # Specialized AI Skills
├── core/               # Main configuration (Settings, Auth)
├── monitor/            # Main application
│   ├── api.py          # DRF ViewSets
│   ├── management/     # Background Workers
│   ├── templates/      # HTML + HTMX Partials
│   └── views.py        # Business logic
├── locale/             # Translation files (ES/EN)
└── start_server.py     # Multi-threaded Launcher
```

---

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE.md) file for details.

---

Developed with ❤️ by Alejandro Quesada