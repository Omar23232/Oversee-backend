import requests
import json
from urllib3.exceptions import InsecureRequestWarning
from django.utils import timezone
from login.models import DeviceMemory

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

def fetch_and_store_memory_stats(device_ip="192.168.47.131"):
    url = f"https://{device_ip}/restconf/data/Cisco-IOS-XE-memory-oper:memory-statistics/memory-statistic=Processor"
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
        memory_data = data["Cisco-IOS-XE-memory-oper:memory-statistic"]
        DeviceMemory.objects.create(
            device_ip=device_ip,
            name=memory_data["name"],
            total_memory=int(memory_data["total-memory"]),
            used_memory=int(memory_data["used-memory"]),
            free_memory=int(memory_data["free-memory"]),
            lowest_usage=int(memory_data["lowest-usage"]),
            highest_usage=int(memory_data["highest-usage"])
        )
        return True
    except Exception as e:
        print(f"Error fetching from {device_ip}: {str(e)}")
        return False