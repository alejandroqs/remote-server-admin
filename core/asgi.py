"""
ASGI config for core project.
It exposes the ASGI callable as a module-level variable named ``application``.
Used for asynchronous deployment (e.g., with Uvicorn/Daphne).
"""

import os

from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

application = get_asgi_application()
