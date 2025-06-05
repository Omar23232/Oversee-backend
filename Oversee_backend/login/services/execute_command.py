# services/command_client.py
import requests
import base64
import json
from urllib3.exceptions import InsecureRequestWarning
from django.utils import timezone
from login.models import ExecutedCommand
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

class CiscoCommandExecutor:
    def __init__(self, device_ip="192.168.47.131"):
        self.device_ip = device_ip
        self.base_url = f"https://{device_ip}/webui/rest/execCliCommand"
        self.csrf_token = "921ec2eba25c19f505a7b9bb001bcbce5052b6c6"  # Set via set_credentials()
        self.auth_cookie = "Auth=cisco:1749099011:0:15:4294967295:4461e9129c3dc83807652c4be4f11b99f26aca0a6ac01f06685794b1b09fb2585ba451c41ff1ea437cfab007343e331e78fef611c92c0e541f553db65941a52de8c7a96eb79c44183dc0bbad59076f61342f77c82c0a837b70e22777ca3a129d:161bdb7e6d5fd93d70d5d91846808bf7dd5d4c8dec3a34c343b2781a7f099a73"
    def execute(self, cli_command, user=None):
        try:
            # Encode command
            encoded_cmd = base64.b64encode(cli_command.encode()).decode()
            
            headers = {
                "Content-Type": "application/json",
                "X-Csrf-Token": self.csrf_token,
                "Cookie": self.auth_cookie
            }
            
            payload = {"cliKeyIn": encoded_cmd}
            
            response = requests.post(
                self.base_url,
                headers=headers,
                json=payload,
                verify=False,
                timeout=10
            )
            print(response.status_code)
            print(response.json())
            
            ExecutedCommand.objects.create(
                device_ip=self.device_ip,
                command=cli_command,
                output=response.json(),
                user=user
            )
            
            return {
                'status': 'success',
                'output': response.json()
            }
            
        except Exception as e:
            return {
                'status': 'error',
                'message': str(e)
            }
        
# if __name__ == "__main__":
    
#     executor = CiscoCommandExecutor()
    
#     # Execute a command (using default or specify one)
#     result = executor.execute()  # uses default "show version" command
#     # OR specify a command:
#     # result = executor.execute("show interfaces")