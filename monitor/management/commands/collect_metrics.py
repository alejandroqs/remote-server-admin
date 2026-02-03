import time
import psutil
import logging # <--- Import logging
from django.core.management.base import BaseCommand
from django.utils import timezone
from monitor.models import Server, SystemMetric

# Configure the logger
logger = logging.getLogger('monitor')

class Command(BaseCommand):
    help = 'Collects system metrics and saves them to the Database'

    def handle(self, *args, **kwargs):
        # We use logger.info instead of print
        logger.info("Starting metrics collection service...")

        server, created = Server.objects.get_or_create(
            name='Localhost',
            defaults={'ip_address': '127.0.0.1', 'is_active': True}
        )

        while True:
            if not server.is_active:
                logger.warning(f"Server {server.name} is inactive. Skipping cycle.")
                time.sleep(5)
                continue

            try:
                cpu = psutil.cpu_percent(interval=1)
                ram = psutil.virtual_memory().percent
                disk = psutil.disk_usage('/').percent

                SystemMetric.objects.create(
                    server=server,
                    cpu_usage=cpu,
                    ram_usage=ram,
                    disk_usage=disk,
                    timestamp=timezone.now()
                )
                
                # Debug message (optional, only shows if level=DEBUG)
                # logger.debug(f"Metrics saved: CPU {cpu}%") 

            except Exception as e:
                # logger.error automatically saves the error traceback
                logger.error(f"Error collecting metrics: {e}")

            time.sleep(5)