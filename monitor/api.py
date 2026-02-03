from rest_framework import viewsets
from .models import Server, SystemMetric
from .serializers import ServerSerializer, MetricSerializer

# ViewSet: Magically creates routes automatically (GET, POST, etc.)
class ServerViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Server.objects.all()
    serializer_class = ServerSerializer

class MetricViewSet(viewsets.ReadOnlyModelViewSet):
    # Default sorting: most recent first
    queryset = SystemMetric.objects.all().order_by('-timestamp')
    serializer_class = MetricSerializer
    
    # Optional: Simple filter to get only 'Localhost' metrics
    def get_queryset(self):
        queryset = super().get_queryset()
        server_name = self.request.query_params.get('server', None)
        if server_name:
            queryset = queryset.filter(server__name=server_name)
        return queryset