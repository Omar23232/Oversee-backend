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
        self.csrf_token = "51c0056527b9cd8739460670df886d00362b8032"  # Set via set_credentials()
        self.auth_cookie = "Auth=cisco:1749396158:0:15:4294967295:40e334dabf9b8c2c54739dc9ee0a7391c306e364e1d8a43e79e794c5e8d269c93678a0f8a5962bfd49559b8c362ccff6011fb97ed367fc5124be850cb9598be180a730aec6e39124461f6ed57dc64793864c2ea49eeefee55ba815bbdb40f678:8e482bad38fca341fcc794edf38001eb49f8f429b633b2dcdb0e69993b47100e"
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
            