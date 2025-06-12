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
        
    def _format_command_url(self, command):
        """Convert a command like 'show version | include uptime' to URL format"""
        parts = command.replace('|', '%7C').split()
        url_path = '/'.join(parts)
        return f"{self.base_url}/{url_path}/CR"
    
    def _extract_output_from_html(self, html_content):
        """Extract the command output from the HTML response"""
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
                
                # First, print the raw output for debugging
                print(f"Memory raw output: {memory_text}")
                
                # Parse the table format based on your actual output
                # Looking for the "Processor" row which contains memory values
                # Format: "Processor   13A05020   742622176    63279176   679343000   631335180   628445500"
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
                            'total': total_memory / (1024 * 1024),  # Convert to MB
                            'used': used_memory / (1024 * 1024),    # Convert to MB
                            'free': free_memory / (1024 * 1024),    # Convert to MB
                            'used_percentage': round(used_percentage, 2)
                        }
                    }
                
                # If the first pattern doesn't match, try another pattern based on the format
                # "Head    Total(b)     Used(b)     Free(b)"
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
                
                # Parse CPU information using regex
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