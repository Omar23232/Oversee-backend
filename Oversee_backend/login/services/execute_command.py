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
        self.csrf_token = "ed8661689075c87f0bc483a63f6b99026f98b650"  # Set via set_credentials()
        self.auth_cookie = "Auth=cisco:1748841606:0:15:4294967295:0206e4d2b4959318c1319700ec6205b470f7ef84e8be0e5ebe7ac693610ff4c2b9550a407bcadd1f1b44009840d8d0d89ee47ffb702271bae170fdbbdd1b211e5211c946d7e7240a0f6e9a9e55b752bff15e01e090f6c1b8445e760fb1aa83af:9948d21c50ef4d09b7775b5953bb7f686a3db5e6402fc4a41dbf1175c058a407"

    def execute(self, cli_command):
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
            
            # Save to database
            ExecutedCommand.objects.create(
                device_ip=self.device_ip,
                command=cli_command,
                output=response.json()
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