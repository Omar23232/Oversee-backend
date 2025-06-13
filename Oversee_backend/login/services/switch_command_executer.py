import requests
import re
import json
from bs4 import BeautifulSoup
from urllib3.exceptions import InsecureRequestWarning
from django.utils import timezone
from login.models import ExecutedCommand

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

class switch_command_executor:
    def __init__(self, device_ip):
        self.device_ip = device_ip
        self.base_url = f"http://{device_ip}/level/15/exec/-"
        self.auth = ('cisco', 'cisco')
        
    # Set the user agent to mimic a web browser
    def _format_command_url(self, command):
        parts = command.replace('|', '%7C').split()
        url_path = '/'.join(parts)
        return f"{self.base_url}/{url_path}/CR"
    
    # Extract the output from the HTML content returned by the switch
    def _extract_output_from_html(self, html_content):
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Find the output section which is in the PRE tag after H5
            output_section = soup.find('h5').find_next('pre')
            
            if output_section:
                # Extract text and clean it up
                output_text = output_section.get_text().strip()
                # Remove the 'command completed' message and other artifacts
                output_text = re.sub(r'<HR>|command completed\.', '', output_text).strip()
                return output_text
            
            return "No output found"
        except Exception as e:
            return f"Error parsing output: {str(e)}"
    
    def execute(self, cli_command, user=None):
        """Execute a command on the switch and return the result"""
        try:
            command_url = self._format_command_url(cli_command)
            
            response = requests.get(
                command_url,
                auth=self.auth,
                timeout=10
            )
            
            if response.status_code == 200:
                output = self._extract_output_from_html(response.text)
                
                # Store the command execution in the database
                ExecutedCommand.objects.create(
                    device_ip=self.device_ip,
                    command=cli_command,
                    output={"raw_output": output},
                    user=user
                )
                
                return {
                    'status': 'success',
                    'output': {"raw_output": output}
                }
            else:
                return {
                    'status': 'error',
                    'message': f"HTTP error: {response.status_code}"
                }
                
        except Exception as e:
            return {
                'status': 'error',
                'message': str(e)
            }
    
    #  Get the uptime of the switch
    def get_uptime(self):
        
        result = self.execute("show version | include uptime")
        
        if result['status'] == 'success':
            try:
                uptime_text = result['output']['raw_output']
                
                # Parse the uptime text using regex
                uptime_match = re.search(r'uptime is (\d+) (years|year|weeks|week|days|day|hours|hour|minutes|minute)(?:, (\d+) (weeks|week|days|day|hours|hour|minutes|minute))?(?:, (\d+) (days|day|hours|hour|minutes|minute))?(?:, (\d+) (hours|hour|minutes|minute))?(?:, (\d+) (minutes|minute|seconds|second))?', uptime_text)
                
                if uptime_match:
                    # Convert to a standardized format
                    uptime_parts = {}
                    
                    # Process each matched group
                    for i in range(1, len(uptime_match.groups()), 2):
                        if uptime_match.group(i) and uptime_match.group(i+1):
                            value = int(uptime_match.group(i))
                            unit = uptime_match.group(i+1).rstrip('s')  # Remove plural 's'
                            uptime_parts[unit] = value
                    
                    # Ensure all parts exist
                    for unit in ['year', 'week', 'day', 'hour', 'minute', 'second']:
                        if unit not in uptime_parts:
                            uptime_parts[unit] = 0
                    
                    return {
                        'status': 'success',
                        'output': uptime_parts
                    }
                
                # Return the raw text if parsing fails
                return {
                    'status': 'success',
                    'output': {'raw': uptime_text}
                }
                
            except Exception as e:
                return {
                    'status': 'error',
                    'message': f"Error parsing uptime: {str(e)}"
                }
        
        return result
    
    # Get memory usage statistics from the switch and store in database
    def get_memory_stats(self):
        result = self.execute("show memory statistics")
        
        if result['status'] == 'success':
            try:
                memory_text = result['output']['raw_output']
                processor_match = re.search(r'Processor\s+\w+\s+(\d+)\s+(\d+)\s+(\d+)', memory_text)
                
                if processor_match:
                    total_memory = int(processor_match.group(1))
                    used_memory = int(processor_match.group(2))
                    free_memory = int(processor_match.group(3))
                    
                    # Calculate percentage
                    used_percentage = (used_memory / total_memory) * 100 if total_memory > 0 else 0
                    
                    # Store in database
                    from login.models import DeviceMemory
                    
                    DeviceMemory.objects.create(
                        device_ip=self.device_ip,
                        total_memory=total_memory,
                        used_memory=used_memory,
                        free_memory=free_memory,
                        lowest_usage=used_memory,  # Using current value as initial lowest
                        highest_usage=used_memory  # Using current value as initial highest
                    )
                    
                    print(f"Successfully stored memory stats: Total={total_memory}, Used={used_memory}, Free={free_memory}")
                    
                    return {
                        'status': 'success',
                        'output': {
                            'total': total_memory / (1024 * 1024),  
                            'used': used_memory / (1024 * 1024),    
                            'free': free_memory / (1024 * 1024),    
                            'used_percentage': round(used_percentage, 2)
                        }
                    }
                
                # If the first pattern didn't match, try an alternative pattern
                header_match = re.search(r'Head\s+Total\(b\)\s+Used\(b\)\s+Free\(b\)', memory_text)
                processor_line_match = re.search(r'Processor\s+\w+\s+(\d+)\s+(\d+)\s+(\d+)', memory_text)
                
                if header_match and processor_line_match:
                    total_memory = int(processor_line_match.group(1))
                    used_memory = int(processor_line_match.group(2))
                    free_memory = int(processor_line_match.group(3))
                    
                    # Store in database
                    from login.models import DeviceMemory
                    
                    DeviceMemory.objects.create(
                        device_ip=self.device_ip,
                        total_memory=total_memory,
                        used_memory=used_memory,
                        free_memory=free_memory,
                        lowest_usage=used_memory,
                        highest_usage=used_memory
                    )
                    
                    print(f"Successfully stored memory stats (alt pattern): Total={total_memory}, Used={used_memory}, Free={free_memory}")
                    
                    return {
                        'status': 'success',
                        'output': {
                            'total': total_memory / (1024 * 1024),
                            'used': used_memory / (1024 * 1024),
                            'free': free_memory / (1024 * 1024),
                            'used_percentage': round((used_memory / total_memory) * 100, 2)
                        }
                    }
                
                # Return the raw text if parsing fails
                print("Failed to parse memory stats, no pattern matched")
                print("Memory text:", memory_text)
                return {
                    'status': 'error',
                    'message': 'Failed to parse memory statistics',
                    'raw_output': memory_text
                }
                    
            except Exception as e:
                print(f"Error in get_memory_stats: {str(e)}")
                return {
                    'status': 'error',
                    'message': f"Error parsing memory stats: {str(e)}"
                }
        
        return result
    
    
    
    # Get CPU usage statistics from the switch and store in database
    def get_cpu_stats(self):
        
        result = self.execute("show processes cpu sorted")
        
        if result['status'] == 'success':
            try:
                cpu_text = result['output']['raw_output']
                
                # Looking for line like: "CPU utilization for five seconds: 12%/5%; one minute: 8%; five minutes: 5%"
                cpu_match = re.search(r'CPU utilization for five seconds: (\d+)%.*?; one minute: (\d+)%.*?; five minutes: (\d+)%', cpu_text)
                
                if cpu_match:
                    five_seconds = float(cpu_match.group(1))
                    one_minute = float(cpu_match.group(2))
                    five_minutes = float(cpu_match.group(3))
                    
                    # Store in database
                    from login.models import DeviceCPU
                    
                    DeviceCPU.objects.create(
                        device_ip=self.device_ip,
                        five_seconds=five_seconds,
                        one_minute=one_minute,
                        five_minutes=five_minutes
                    )
                    
                    return {
                        'status': 'success',
                        'output': {
                            'five_seconds': five_seconds,
                            'one_minute': one_minute,
                            'five_minutes': five_minutes
                        }
                    }
                
                # Return the raw text if parsing fails
                return {
                    'status': 'error',
                    'message': 'Failed to parse CPU data',
                    'raw_output': cpu_text
                }
                
            except Exception as e:
                return {
                    'status': 'error',
                    'message': f"Error parsing CPU stats: {str(e)}"
                }
        
        return result
    
    
    # Get interface statistics from the switch and store in database
    def get_interface_stats(self):
        result = self.execute("show interfaces")
        
        if result['status'] == 'success':
            try:
                interfaces_text = result['output']['raw_output']
                
                # Split the output by interface sections
                interface_pattern = r'((GigabitEthernet\d+/\d+|Vlan\d+)) is ([\w/()-]+).*?(?=(?:(GigabitEthernet\d+/\d+|Vlan\d+) is|\Z))'
                interface_sections = re.findall(interface_pattern, interfaces_text, re.DOTALL)
                
                print(f"Found {len(interface_sections)} valid interface sections")
                
                # Keep track of successful interfaces processed
                processed_interfaces = []
                
                for section in interface_sections:
                    try:
                        interface_name = section[0]  # The interface name is now in index 0
                        status = section[2].lower()  # Status is now in index 2
                        interface_text = interface_name + " is " + status  # Beginning of the text
                        full_section_text = section[3] if len(section) > 3 else ""  # Full section text
                        
                        print(f"Processing interface: {interface_name}, status: {status}")
                        
                        # Extract MAC address
                        mac_match = re.search(r'address is ([0-9a-f.]{14})', interface_text)
                        if not mac_match:
                            # Try searching in the full text for this interface
                            mac_match = re.search(r'address is ([0-9a-f.]{14})', full_section_text)
                        
                        mac_address = mac_match.group(1).replace('.', '') if mac_match else "00:00:00:00:00:00"
                        
                        # Format MAC address with colons
                        mac_formatted = ':'.join(mac_address[i:i+2] for i in range(0, 12, 2))
                        
                        # Extract bandwidth information - Look in full section text
                        in_rate_match = re.search(r'(\d+) minute input rate (\d+) bits/sec', full_section_text)
                        out_rate_match = re.search(r'(\d+) minute output rate (\d+) bits/sec', full_section_text)
                        
                        in_bandwidth = float(in_rate_match.group(2)) / 1000000 if in_rate_match else 0  # Convert to Mbps
                        out_bandwidth = float(out_rate_match.group(2)) / 1000000 if out_rate_match else 0  # Convert to Mbps
                        
                        # Extract packet statistics
                        in_packets_match = re.search(r'(\d+) packets input', full_section_text)
                        out_packets_match = re.search(r'(\d+) packets output', full_section_text)
                        
                        in_packets = int(in_packets_match.group(1)) if in_packets_match else 0
                        out_packets = int(out_packets_match.group(1)) if out_packets_match else 0
                        
                        # Extract error statistics
                        in_errors_match = re.search(r'(\d+) input errors', full_section_text)
                        out_errors_match = re.search(r'(\d+) output errors', full_section_text)
                        
                        in_errors = int(in_errors_match.group(1)) if in_errors_match else 0
                        out_errors = int(out_errors_match.group(1)) if out_errors_match else 0
                        
                        # Calculate error rate - define total_errors first
                        total_errors = in_errors + out_errors
                        total_packets = in_packets + out_packets
                        error_rate = (total_errors / total_packets * 100) if total_packets > 0 else 0
                        
                        # Extract discards if available
                        in_discards_match = re.search(r'Input queue: (\d+)/\d+/\d+/\d+', full_section_text)
                        in_discards = int(in_discards_match.group(1)) if in_discards_match else 0
                        
                        out_discards_match = re.search(r'Total output drops: (\d+)', full_section_text)
                        out_discards = int(out_discards_match.group(1)) if out_discards_match else 0
                        
                        # Calculate packet loss
                        packet_loss = ((in_discards + out_discards) / total_packets * 100) if total_packets > 0 else 0
                        
                        # Use current time as last_change
                        last_change = timezone.now()
                        
                        # Store in the database
                        from login.models import InterfaceStatus
                        
                        InterfaceStatus.objects.create(
                            device_ip=self.device_ip,
                            name=interface_name,
                            oper_status="up" if "up" in status else "down",
                            last_change=last_change,
                            mac_address=mac_formatted,
                            in_bandwidth=in_bandwidth,
                            out_bandwidth=out_bandwidth,
                            in_errors=in_errors,
                            out_errors=out_errors,
                            in_discards=in_discards,
                            out_discards=out_discards,
                            in_packets=in_packets,
                            out_packets=out_packets,
                            error_rate=error_rate,
                            packet_loss=packet_loss
                        )
                        
                        processed_interfaces.append({
                            'name': interface_name,
                            'status': "up" if "up" in status else "down",
                            'mac': mac_formatted,
                            'in_bandwidth': round(in_bandwidth, 2),
                            'out_bandwidth': round(out_bandwidth, 2),
                            'error_rate': round(error_rate, 3),
                            'packet_loss': round(packet_loss, 3)
                        })
                        
                    except Exception as e:
                        print(f"Error processing interface {interface_name}: {str(e)}")
                        continue
                
                print(f"Successfully processed {len(processed_interfaces)} interfaces")
                return {
                    'status': 'success',
                    'interfaces': processed_interfaces,  # Use 'interfaces' key for consistency
                    'output': processed_interfaces  # Keep 'output' for backward compatibility
                }
                    
            except Exception as e:
                print(f"Error in get_interface_stats: {str(e)}")
                return {
                    'status': 'error',
                    'message': f"Error parsing interface stats: {str(e)}"
                }
        
        return result