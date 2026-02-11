from django.shortcuts import render
import psutil
import platform
import subprocess
import os
import subprocess
import os
import math
import time
from django.conf import settings
from .models import SystemMetric
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required, user_passes_test
from django.views.decorators.http import require_POST
import os
import socket
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from .forms import ServerForm
from .models import Server
from django.http import JsonResponse

# View 1: Loads the full page (skeleton)
@login_required
def dashboard(request):
    # 1. Get the last 20 records for 'Localhost'
    # Sort by timestamp descending (newest first) to get the latest ones
    metrics = SystemMetric.objects.filter(server__name='Localhost').order_by('-timestamp')[:20]
    
    # 2. Since we fetched them newest to oldest, the chart would look backwards.
    # We reverse them so time flows from left to right.
    metrics = reversed(list(metrics))
    
    # 3. Prepare lists for Chart.js
    labels = []  # X Axis (Hours)
    data_cpu = [] # Y Axis (CPU Value)
    data_ram = [] # Y Axis (RAM Value - Optional)

    for m in metrics:
        # Save formatted time (e.g., "14:30:05")
        labels.append(m.timestamp.strftime("%H:%M:%S"))
        data_cpu.append(m.cpu_usage)
        data_ram.append(m.ram_usage)

    context = {
        'page_title': 'General Dashboard',
        'chart_labels': labels,   # Pass lists to template
        'chart_data_cpu': data_cpu,
        'chart_data_ram': data_ram,
    }
    
    return render(request, 'monitor/dashboard.html', context)

# View 2: Returns ONLY the HTML for metrics (for HTMX)
@login_required
def system_metrics(request):
    if settings.DEMO_MODE:
        # Simulate organic behavior with sine waves
        t = time.time()
        # CPU: 40% base + 20% oscillation (Range: 20-60%)
        cpu = 40 + 20 * math.sin(t * 0.5)
        # RAM: 50% base + 5% oscillation
        ram = 50 + 5 * math.cos(t * 0.2)
        # Swap: Low usage
        swap = 10 + 2 * math.sin(t * 0.1)
        # Disk: Slow filling effect
        disk = 45 + (t % 100) / 20  # Slowly increases then resets
        
        cpu = round(cpu, 1)
        ram = round(ram, 1)
        swap = round(swap, 1)
        disk = round(disk, 1)
    else:
        cpu = psutil.cpu_percent(interval=None) # interval=None is vital to avoid blocking the response
        ram = psutil.virtual_memory().percent
        
        # Path logic
        path = 'C:\\' if platform.system() == 'Windows' else '/'
        disk_info = psutil.disk_usage(path)
        disk = disk_info.percent
        
        swap = psutil.swap_memory().percent
    
    context = {
        'cpu_metric': cpu,
        'ram_metric': ram,
        'swap_metric': swap,
        'disk_metric': disk,
    }
    # NOTE: We render a different partial template here
    return render(request, 'monitor/partials/metrics.html', context)

@login_required
def processes(request):
    # Main view that loads the skeleton
    return render(request, 'monitor/processes.html', {'page_title': 'Process Manager'})

@login_required
def processes_list(request):
    # Partial view that returns table rows (HTMX)
    data = []
    
    # Iterate over running processes
    # 'attrs' defines which data we want to extract
    for proc in psutil.process_iter(['pid', 'name', 'username', 'status', 'cpu_percent', 'memory_percent']):
        try:
            # Sometimes psutil fails if the process dies while we are reading it
            info = proc.info
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            continue
            
        data.append(info)

    # Sort by CPU usage (descending) and take TOP 10
    # key=lambda x: x['cpu_percent'] or 0  <-- Handles cases where it might be None
    data_sorted = sorted(data, key=lambda x: x['cpu_percent'] or 0, reverse=True)[:10]

    return render(request, 'monitor/partials/process_table.html', {
        'processes': data_sorted,
        'demo_mode': settings.DEMO_MODE
    })

# Decorator: Only superusers can enter here
@user_passes_test(lambda u: u.is_superuser)
@require_POST # We only accept POST requests (security)
def kill_process(request, pid):
    try:
        if settings.DEMO_MODE:
            response = HttpResponse(status=204) # 204 No Content means "do nothing to the DOM"
            response['HX-Trigger'] = '{"showAlert": "🔒 Action Blocked: This feature is disabled in Demo Mode."}'
            return response

        # 1. Suicide protection: Don't kill Django itself
        if pid == os.getpid():
            return HttpResponse('<span class="text-danger fw-bold">Cannot kill the server!</span>')

        # 2. Find and terminate the process
        proc = psutil.Process(pid)
        proc.terminate() # Or proc.kill() to be more aggressive
        
        # 3. Visual response for the table
        return HttpResponse('<span class="text-success fw-bold">Terminated.</span>')

    except psutil.NoSuchProcess:
        return HttpResponse('<span class="text-muted">Already gone.</span>')
    except psutil.AccessDenied:
        return HttpResponse('<span class="text-danger">Access Denied.</span>')
    except Exception as e:
        return HttpResponse(f'<span class="text-danger">Error: {str(e)}</span>')

@user_passes_test(lambda u: u.is_superuser)
def terminal(request):
    # Initialize Current Working Directory if not present
    if 'term_cwd' not in request.session:
        # Default to home directory or valid starting point
        request.session['term_cwd'] = os.path.expanduser('~')
    
    return render(request, 'monitor/terminal.html', {
        'page_title': 'Terminal',
        'cwd': request.session['term_cwd']
    })

@user_passes_test(lambda u: u.is_superuser)
@require_POST
def terminal_execute(request):
    command = request.POST.get('command', '').strip()
    cwd = request.session.get('term_cwd', os.path.expanduser('~'))
    

    if not command:
        return HttpResponse('')
        
    if settings.DEMO_MODE:
        context = {
           'command': command,
           'output': "Simulation Mode Active.\nReal command execution is disabled for security reasons.\nTry 'help' for simulated help (not really, just kidding).",
           'cwd': cwd,
           'new_cwd': cwd
        }
        return render(request, 'monitor/partials/terminal_line.html', context)

    output = ""
    new_cwd = cwd
    
    # Handle 'cd' manually because subprocess runs in a subshell
    if command.startswith('cd '):
        try:
            target_dir = command[3:].strip()
            # Resolve relative paths
            potential_path = os.path.abspath(os.path.join(cwd, target_dir))
            
            if os.path.isdir(potential_path):
                new_cwd = potential_path
                request.session['term_cwd'] = new_cwd
                # We don't print output for success cd, just update prompt
            else:
                output = f"cd: the directory '{target_dir}' does not exist"
        except Exception as e:
            output = str(e)
    else:
        # Execute other commands
        try:
            # shell=True is dangerous but necessary for a terminal emulator. 
            # We rely on superuser protection.
            result = subprocess.run(
                command, 
                shell=True, 
                cwd=cwd, 
                stdout=subprocess.PIPE, 
                stderr=subprocess.PIPE, 
                text=True
            )
            output = result.stdout + result.stderr
        except Exception as e:
            output = str(e)

    context = {
        'command': command,
        'output': output,
        'cwd': cwd,      # Directory WHERE the command ran
        'new_cwd': new_cwd # New directory FOR the next prompt
    }
    return render(request, 'monitor/partials/terminal_line.html', context)

@login_required
def network_dashboard(request):
    return render(request, 'monitor/network.html', {'page_title': 'Monitor de Red'})

@login_required
def network_details(request):
    if settings.DEMO_MODE:
        # Mock Data for Demo Mode (Linux-style)
        interfaces = {
            'lo': [{'ip': '127.0.0.1', 'netmask': '255.0.0.0', 'type': 'IPv4'}],
            'eth0': [{'ip': '192.168.1.15', 'netmask': '255.255.255.0', 'type': 'IPv4'}],
            'docker0': [{'ip': '172.17.0.1', 'netmask': '255.255.0.0', 'type': 'IPv4'}],
        }
        
        connections = [
            {'fd': 10, 'family': 'IPv4', 'type': 'TCP', 'laddr': '0.0.0.0:80', 'raddr': '-', 'status': 'LISTEN', 'status_color': 'success', 'pid': 850},  # Nginx
            {'fd': 11, 'family': 'IPv4', 'type': 'TCP', 'laddr': '0.0.0.0:443', 'raddr': '-', 'status': 'LISTEN', 'status_color': 'success', 'pid': 850}, # Nginx
            {'fd': 25, 'family': 'IPv4', 'type': 'TCP', 'laddr': '127.0.0.1:5432', 'raddr': '-', 'status': 'LISTEN', 'status_color': 'success', 'pid': 1205}, # Postgres
            {'fd': 30, 'family': 'IPv4', 'type': 'TCP', 'laddr': '127.0.0.1:6379', 'raddr': '-', 'status': 'LISTEN', 'status_color': 'success', 'pid': 1100}, # Redis
            {'fd': 45, 'family': 'IPv4', 'type': 'TCP', 'laddr': '0.0.0.0:22', 'raddr': '-', 'status': 'LISTEN', 'status_color': 'success', 'pid': 500}, # SSHd
            {'fd': 88, 'family': 'IPv4', 'type': 'TCP', 'laddr': '192.168.1.15:22', 'raddr': '10.0.0.5:54321', 'status': 'ESTABLISHED', 'status_color': 'primary', 'pid': 502}, # Incoming SSH
            {'fd': 92, 'family': 'IPv4', 'type': 'TCP', 'laddr': '192.168.1.15:443', 'raddr': '172.217.17.14:58000', 'status': 'ESTABLISHED', 'status_color': 'primary', 'pid': 851}, # Active Web User (You!)
            {'fd': 99, 'family': 'IPv4', 'type': 'TCP', 'laddr': '127.0.0.1:5432', 'raddr': '127.0.0.1:48200', 'status': 'ESTABLISHED', 'status_color': 'primary', 'pid': 1205}, # DB Connection
        ]
    else:
        # 1. Real Network Interfaces (IPs, Mac Address)
        interfaces = {}
        for interface_name, addrs in psutil.net_if_addrs().items():
            interfaces[interface_name] = []
            for addr in addrs:
                # Filter to show only IPv4
                if addr.family == socket.AF_INET:
                    interfaces[interface_name].append({
                        'ip': addr.address,
                        'netmask': addr.netmask,
                        'type': 'IPv4'
                    })

        # 2. Real Active Connections (Netstat style)
        connections = []
        # kind='inet' to only see IP connections (excludes unix file sockets)
        for conn in psutil.net_connections(kind='inet'):
            # Translate status (LISTEN, ESTABLISHED, etc.)
            if conn.status == psutil.CONN_LISTEN:
                status_color = 'success' # Green
            elif conn.status == psutil.CONN_ESTABLISHED:
                status_color = 'primary' # Blue
            elif conn.status == psutil.CONN_TIME_WAIT:
                status_color = 'warning' # Yellow
            else:
                status_color = 'secondary'

            connections.append({
                'fd': conn.fd,
                'family': 'IPv4' if conn.family == socket.AF_INET else 'IPv6',
                'type': 'TCP' if conn.type == socket.SOCK_STREAM else 'UDP',
                'laddr': f"{conn.laddr.ip}:{conn.laddr.port}",
                'raddr': f"{conn.raddr.ip}:{conn.raddr.port}" if conn.raddr else "-",
                'status': conn.status,
                'status_color': status_color,
                'pid': conn.pid
            })
        
        # Sort: First those listening (LISTEN), then established
        connections.sort(key=lambda x: x['status'])

    context = {
        'interfaces': interfaces,
        'connections': connections[:50] # Limit to 50 to avoid cluttering the view
    }
    
    return render(request, 'monitor/partials/network_table.html', context)

@login_required
def chart_data(request):
    labels = []
    data_cpu = []
    data_ram = []

    if settings.DEMO_MODE:
        # Generate 20 fake points
        now = time.time()
        for i in range(20):
            t = now - (20 - i) * 5 # 5 seconds intervals
            # Simulate historical wave
            cpu = 40 + 20 * math.sin(t * 0.5)
            ram = 50 + 5 * math.cos(t * 0.2)
            
            # Format time HH:MM:SS
            time_str = time.strftime('%H:%M:%S', time.localtime(t))
            
            labels.append(time_str)
            data_cpu.append(round(cpu, 1))
            data_ram.append(round(ram, 1))
            
    else:
        # Fetch latest data
        metrics = SystemMetric.objects.filter(server__name='Localhost').order_by('-timestamp')[:20]
        # Reverse so the chart goes from left (old) to right (new)
        metrics = reversed(list(metrics))
        
        for m in metrics:
            labels.append(m.timestamp.strftime("%H:%M:%S"))
            data_cpu.append(m.cpu_usage)
            data_ram.append(m.ram_usage)

    return JsonResponse({
        'labels': labels,
        'cpu': data_cpu,
        'ram': data_ram
    })

def custom_page_not_found(request, exception):
    return render(request, 'monitor/404.html', status=404)

def custom_server_error(request):
    return render(request, 'monitor/500.html', status=500)

    # 1. LIST (Read)
class ServerListView(ListView):
    model = Server
    template_name = 'monitor/servers/list.html'
    context_object_name = 'servers'
    
    # We can protect CBVs with a Mixin (equivalent to @login_required)
    # But for simplicity, we do it in urls.py or by adding LoginRequiredMixin
    # from django.contrib.auth.mixins import LoginRequiredMixin

# 2. CREATE (Create)
class ServerCreateView(CreateView):
    model = Server
    form_class = ServerForm
    template_name = 'monitor/servers/form.html'
    success_url = reverse_lazy('server_list') # When done, return to list
    
    def form_valid(self, form):
        # Here you could add extra logic before saving
        return super().form_valid(form)

# 3. EDIT (Update)
class ServerUpdateView(UpdateView):
    model = Server
    form_class = ServerForm
    template_name = 'monitor/servers/form.html' # Reuse template
    success_url = reverse_lazy('server_list')

# 4. DELETE (Delete)
class ServerDeleteView(DeleteView):
    model = Server
    template_name = 'monitor/servers/confirm_delete.html'
    success_url = reverse_lazy('server_list')