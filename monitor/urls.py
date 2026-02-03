from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views
from . import api  # Import the new API file
from django.contrib.auth.decorators import login_required

# API Router Configuration
router = DefaultRouter()
router.register(r'servers', api.ServerViewSet)
router.register(r'metrics', api.MetricViewSet)

urlpatterns = [
    # ... Standard Views (dashboard, processes, etc.) ...
    path('', views.dashboard, name='dashboard'),
    path('chart-data/', views.chart_data, name='chart_data'),
    path('metrics/', views.system_metrics, name='system_metrics'),
    path('processes/', views.processes, name='processes'),
    path('processes/list/', views.processes_list, name='processes_list'),
    path('processes/kill/<int:pid>/', views.kill_process, name='kill_process'),
    
    # Terminal Routes
    path('terminal/', views.terminal, name='terminal'),
    path('terminal/execute/', views.terminal_execute, name='terminal_execute'),

    # ... API Routes ...
    # All API URLs will start with 'api/'
    path('api/', include(router.urls)), 
    path('network/', views.network_dashboard, name='network_dashboard'),
    path('network/details/', views.network_details, name='network_details'),
    # Server CRUD Routes (Using CBVs)
    path('servers/', login_required(views.ServerListView.as_view()), name='server_list'),
    path('servers/add/', login_required(views.ServerCreateView.as_view()), name='server_create'),
    path('servers/edit/<int:pk>/', login_required(views.ServerUpdateView.as_view()), name='server_edit'),
    path('servers/delete/<int:pk>/', login_required(views.ServerDeleteView.as_view()), name='server_delete'),
    
]