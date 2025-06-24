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
        self.csrf_token = "1381a81f9b146261af250c29f1f8a5f4093de1ad" 
        self.auth_cookie = "Auth=cisco:1750694188:0:15:4294967295:815e2f9b5a1953982ba7d8826da35146071d53b7676378c0990065872dda23ede0932c979a811b94e9009901b3cd3538dd97e2c80db07d8cb09bb1aff3c6fe2ae48d8e3501df746f4cace63a6cde10595b25ece58c1c50d35b30c14beef122e8:cd0120db88002e3c8fa22001b07ffe476bace9160ae0c3417fb1202ad13ceaba"
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
            