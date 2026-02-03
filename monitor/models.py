# monitor/models.py
from django.db import models

class Server(models.Model):
    name = models.CharField(max_length=100, help_text="Nombre del servidor (ej: Localhost)")
    ip_address = models.GenericIPAddressField(protocol='both', blank=True, null=True)
    os_info = models.CharField(max_length=255, blank=True, null=True, help_text="SO y Versión")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.ip_address})"

class SystemMetric(models.Model):
    server = models.ForeignKey(Server, on_delete=models.CASCADE, related_name='metrics')
    
    # Core Metrics (We store percentages from 0 to 100)
    # CPU usage in %
    cpu_usage = models.FloatField(help_text="Uso de CPU en %")
    # RAM usage in %
    ram_usage = models.FloatField(help_text="Uso de RAM en %")
    # Main disk usage in %
    disk_usage = models.FloatField(help_text="Uso de Disco principal en %")
    
    # GPU is optional as not all servers have one
    # GPU usage in %
    gpu_usage = models.FloatField(null=True, blank=True, help_text="Uso de GPU en %")
    
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        # Default ordering: most recent first
        ordering = ['-timestamp']

    def __str__(self):
        return f"Metric {self.server.name} - {self.timestamp.strftime('%H:%M:%S')}"