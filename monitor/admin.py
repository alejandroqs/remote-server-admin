from django.contrib import admin
from .models import Server, SystemMetric

@admin.register(Server)
class ServerAdmin(admin.ModelAdmin):
    list_display = ('name', 'ip_address', 'os_info', 'is_active')

@admin.register(SystemMetric)
class MetricAdmin(admin.ModelAdmin):
    list_display = ('server', 'cpu_usage', 'ram_usage', 'timestamp')
    list_filter = ('server', 'timestamp')