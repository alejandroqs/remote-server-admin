from rest_framework import serializers
from .models import Server, SystemMetric

# Translate SystemMetric model to JSON
class MetricSerializer(serializers.ModelSerializer):
    # We can add computed or formatted fields if we want
    server_name = serializers.ReadOnlyField(source='server.name')
    timestamp_formatted = serializers.SerializerMethodField()

    class Meta:
        model = SystemMetric
        # Define which fields we want to expose
        fields = ['id', 'server_name', 'cpu_usage', 'ram_usage', 'disk_usage', 'timestamp', 'timestamp_formatted']

    def get_timestamp_formatted(self, obj):
        return obj.timestamp.strftime('%d/%m/%Y %H:%M:%S')

# Translate Server model
class ServerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Server
        fields = '__all__'