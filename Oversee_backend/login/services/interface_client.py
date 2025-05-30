import requests
from urllib3.exceptions import InsecureRequestWarning
from django.utils import timezone
from login.models import InterfaceStatus
import json

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

class InterfaceMonitor:
    def __init__(self, device_ip="192.168.47.131"):
        self.device_ip = device_ip
        self.url = f"https://{device_ip}/restconf/data/ietf-interfaces:interfaces-state?fields=interface(name;oper-status;last-change;phys-address)"

    def fetch_interfaces(self):
        try:
            response = requests.get(
                self.url,
                auth=('cisco', 'cisco'),
                headers={'Accept': 'application/yang-data+json'},
                verify=False,
                timeout=5
            )
            data = response.json()
            
            # Process and save each interface
            for interface in data['ietf-interfaces:interfaces-state']['interface']:
                InterfaceStatus.objects.create(
                    device_ip=self.device_ip,
                    name=interface['name'],
                    oper_status=interface['oper-status'],
                    last_change=interface['last-change'],
                    mac_address=interface['phys-address']
                )
            
            return {'status': 'success', 'data': data}
            
        except Exception as e:
            return {'status': 'error', 'message': str(e)}