# services/command_client.py
import requests
import base64
import json
from urllib3.exceptions import InsecureRequestWarning
from django.utils import timezone
from login.models import ExecutedCommand
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

class CiscoCommandExecutor:
    def __init__(self, device_ip):
        self.device_ip = device_ip
        self.base_url = f"https://{device_ip}/webui/rest/execCliCommand"
        self.csrf_token = "d88e92ebe4644e359f797ae8c5ad64cdb8caac3c" 
        self.auth_cookie = "Auth=cisco:1751311216:0:15:4294967295:67ca36cd7bf1431ba64a70abcae6368b43e4dab1ad06b834691caa7a18d9d471059a998a510e9e3f49493f504396f0581d166446207458f05949e2a6f01e3cec868f957972ff3df85744005ffe10f9d64943ae3863b409d91a0beb45591fb4a4:f543b03afdd11e7226eba87412193abee9f590cca8437eb45cd66e28209f4b97"
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
            
            if user is not None:
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
            