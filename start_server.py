# start_server.py
"""
Custom launcher script for ServerAdmin Pro.
This script handles:
1. OS Detection (Windows vs Linux).
2. Database Migrations and Static Files collection.
3. Background Worker Thread for metrics collection.
4. Launching the appropriate production WSGI server (Waitress/Gunicorn).
"""
import subprocess
import time
import sys
import os
import platform  # To detect the Operating System
from threading import Thread
from dotenv import load_dotenv

def run_metric_collector():
    """Runs the metric collection command in a background thread."""
    print("📊 Starting metrics collector...")
    subprocess.run([sys.executable, "manage.py", "collect_metrics"])

def create_demo_user():
    """Creates a default admin user for Demo Mode (Ephemeral Filesystems)."""
    print("👤 Checking for admin user...")
    
    # Python script to run inside Django Shell
    create_user_script = """
import os
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@example.com', 'admin')
    print('OK: Admin user created (admin/admin)')
else:
    print('INFO: Admin user already exists')
"""
    # Execute via manage.py shell
    subprocess.run(
        [sys.executable, "manage.py", "shell", "-c", create_user_script],
        stdout=subprocess.PIPE
    )

def run_web_server():
    """Executes the web server depending on the OS."""
    system_os = platform.system()
    
    if system_os == "Windows":
        print("🪟 Windows detected. Starting Waitress...")
        print("🌍 Dashboard available at: http://127.0.0.1:8000")
        # Waitress is a pure-Python WSGI server compatible with Windows
        subprocess.run([
            sys.executable, "-m", "waitress", 
            "--listen=*:8000", 
            "core.wsgi:application"
        ])
    else:
        # We are on Linux/Mac
        print(f"🐧 {system_os} detected. Starting Gunicorn...")
        print("🌍 Dashboard available at: http://0.0.0.0:8000")
        
        # Gunicorn is a robust WSGI server for UNIX systems
        # It requires separate installation: pip install gunicorn
        try:
            subprocess.run([
                "gunicorn", 
                "--bind", "0.0.0.0:8000", 
                "--workers", "3",  # Real Multi-threading/Multi-processing
                "core.wsgi:application"
            ])
        except FileNotFoundError:
            print("❌ Error: Gunicorn is not installed or not in PATH.")
            print("   Run: pip install gunicorn")

if __name__ == "__main__":
    print("--- STARTING SERVER DASHBOARD SYSTEM ---")
    
    # Load environment variables from .env file
    load_dotenv()
    
    # 1. Run Migrations (Database check)
    print("🛠️  Checking database...")
    subprocess.run([sys.executable, "manage.py", "migrate"], stdout=subprocess.DEVNULL)
    
    # 2. Compile Translations (i18n)
    # Only attempt to compile if the locale folder exists
    if os.path.exists('locale'):
        print("🌐 Compiling translations...")
        # Ignore errors in case gettext is not installed on the system
        subprocess.run([sys.executable, "manage.py", "compilemessages"], stderr=subprocess.DEVNULL)
    
    # 3. Collect Static Files
    # Essential for loading CSS/JS when DEBUG=False
    if os.environ.get('DEBUG') == 'False':
        print("🎨 Collecting static files...")
        subprocess.run([sys.executable, "manage.py", "collectstatic", "--noinput"], stdout=subprocess.DEVNULL)

    # 4. Metrics Background Thread (REAL MODE)
    # In Demo Mode, we don't need real metrics filling the DB
    if os.environ.get('DEMO_MODE') != 'True':
         metrics_thread = Thread(target=run_metric_collector, daemon=True)
         metrics_thread.start()
    else:
        print("🎭 DEMO MODE ACTIVED: Skipping background metric collector.")
        # 4.1 Ensure Admin User exists for Demo
        create_demo_user()

    time.sleep(2)

    # 5. Start Web Server
    try:
        run_web_server()
    except KeyboardInterrupt:
        print("\n🛑 Shutting down server...")
