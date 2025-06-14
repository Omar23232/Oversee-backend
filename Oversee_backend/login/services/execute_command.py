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
        self.csrf_token = "94505b1351207e839ebf25e42274cd9021ded781"  # Set via set_credentials()
        self.auth_cookie = "Auth=cisco:1749586316:0:15:4294967295:6d29169f268c8753fb861ee4bc9b9992b922a0ebcb1e93c32b08ec608a0805bdeca92a1a6347ff0845c4c62dffebd31fea17dab94316d7a87cd29c3d310772ab1c9b0316d212841abf25e98cc8ca84d27da228be947e45208d1f378fb348ab3f:d72fa48fde8c8b2c690156b30c4894012834e50b0e045ffbc141777a8669bab7"
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
            