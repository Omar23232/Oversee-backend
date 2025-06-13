import requests
from urllib3.exceptions import InsecureRequestWarning
from django.utils import timezone
from login.models import InterfaceStatus
import json
import time

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

class InterfaceMonitor:
    def __init__(self, device_ip):
        self.device_ip = device_ip
        self.url = f"https://{device_ip}/restconf/data/ietf-interfaces:interfaces-state"
        # Store previous readings to calculate bandwidth
        self.prev_stats = {}

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
            current_time = time.time()
            
            # Process and save each interface
            for interface in data['ietf-interfaces:interfaces-state']['interface']:
                name = interface['name']
                stats = interface.get('statistics', {})
                
                # Extract octet and packet data
                in_octets = int(stats.get('in-octets', 0))
                out_octets = int(stats.get('out-octets', 0))
                in_packets = int(stats.get('in-unicast-pkts', 0)) + int(stats.get('in-broadcast-pkts', 0)) + int(stats.get('in-multicast-pkts', 0))
                out_packets = int(stats.get('out-unicast-pkts', 0)) + int(stats.get('out-broadcast-pkts', 0)) + int(stats.get('out-multicast-pkts', 0))
                
                # Extract error and discard data
                in_errors = int(stats.get('in-errors', 0))
                out_errors = int(stats.get('out-errors', 0))
                in_discards = int(stats.get('in-discards', 0))
                out_discards = int(stats.get('out-discards', 0))
                
                # Calculate bandwidth if previous readings exist
                in_bandwidth = 0
                out_bandwidth = 0
                
                if name in self.prev_stats:
                    prev_stats = self.prev_stats[name]
                    time_diff = current_time - prev_stats.get('time', 0)
                    
                    if time_diff > 0:
                        # Convert to Mbps (megabits per second)
                        in_bandwidth = ((in_octets - prev_stats.get('in_octets', 0)) * 8) / (time_diff * 1000000)
                        out_bandwidth = ((out_octets - prev_stats.get('out_octets', 0)) * 8) / (time_diff * 1000000)
                
                # Store current readings for next calculation
                self.prev_stats[name] = {
                    'time': current_time,
                    'in_octets': in_octets,
                    'out_octets': out_octets
                }
                
                # Calculate error rate and packet loss as percentages
                total_packets = in_packets + out_packets
                total_errors = in_errors + out_errors
                
                error_rate = 0
                packet_loss = 0
                
                if total_packets > 0:
                    error_rate = (total_errors / total_packets) * 100
                    packet_loss = ((in_discards + out_discards) / total_packets) * 100
                
                # Create database record with all metrics
                InterfaceStatus.objects.create(
                    device_ip=self.device_ip,
                    name=name,
                    oper_status=interface['oper-status'],
                    last_change=interface['last-change'],
                    mac_address=interface['phys-address'],
                    # Add the new metrics
                    in_octets=in_octets,
                    out_octets=out_octets,
                    in_bandwidth=round(in_bandwidth, 2),
                    out_bandwidth=round(out_bandwidth, 2),
                    in_errors=in_errors,
                    out_errors=out_errors,
                    in_discards=in_discards,
                    out_discards=out_discards,
                    in_packets=in_packets,
                    out_packets=out_packets,
                    error_rate=round(error_rate, 3),
                    packet_loss=round(packet_loss, 3)
                )
            
            return {'status': 'success', 'data': data}
            
        except Exception as e:
            return {'status': 'error', 'message': str(e)}