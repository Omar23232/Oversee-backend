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
    
    def get_uptime(self):
        """Get the uptime of the switch"""
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
    
    def get_memory_stats(self):
        """Get memory usage statistics from the switch"""
        result = self.execute("show memory statistics")
        
        if result['status'] == 'success':
            try:
                memory_text = result['output']['raw_output']
                
                # Parse memory information using regex
                # Example: "Total: 12345K, Used: 6789K, Free: 5556K"
                total_match = re.search(r'Total:\s+(\d+)K', memory_text)
                used_match = re.search(r'Used:\s+(\d+)K', memory_text)
                free_match = re.search(r'Free:\s+(\d+)K', memory_text)
                
                if total_match and used_match and free_match:
                    total_kb = int(total_match.group(1))
                    used_kb = int(used_match.group(1))
                    free_kb = int(free_match.group(1))
                    
                    # Convert to MB for consistency with router output
                    total_mb = total_kb / 1024
                    used_mb = used_kb / 1024
                    free_mb = free_kb / 1024
                    
                    # Calculate percentage
                    used_percentage = (used_kb / total_kb) * 100
                    
                    return {
                        'status': 'success',
                        'output': {
                            'total': total_mb,
                            'used': used_mb,
                            'free': free_mb,
                            'used_percentage': round(used_percentage, 2)
                        }
                    }
                
                # Return the raw text if parsing fails
                return {
                    'status': 'success',
                    'output': {'raw': memory_text}
                }
                
            except Exception as e:
                return {
                    'status': 'error',
                    'message': f"Error parsing memory stats: {str(e)}"
                }
        
        return result