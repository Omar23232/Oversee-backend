import requests
import json
from urllib3.exceptions import InsecureRequestWarning
from django.utils import timezone
from login.models import DeviceCPU

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

def fetch_and_store_cpu_stats(device_ip="192.168.47.131"):
    url = f"https://{device_ip}/restconf/data/Cisco-IOS-XE-process-cpu-oper:cpu-usage/cpu-utilization"
    try:
        response = requests.get(
            url,
            auth=('cisco', 'cisco'),
            headers={'Accept': 'application/yang-data+json'},
            verify=False,
            timeout=5
        )
        data = response.json()
        
         # Save to database
        cpu_data = data["Cisco-IOS-XE-process-cpu-oper:cpu-utilization"]
        DeviceCPU.objects.create(
            device_ip=device_ip,
            five_seconds=float(cpu_data["five-seconds"]),
            one_minute=float(cpu_data["one-minute"]),
            five_minutes=float(cpu_data["five-minutes"]))
        return True
    except Exception as e:
        print(f"CPU Fetch Error: {str(e)}")
        return False