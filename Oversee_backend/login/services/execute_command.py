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
        self.csrf_token = "84c8e3322dc3aeab7da597fe2600e8eb27093786"  # Set via set_credentials()
        self.auth_cookie = "Auth=cisco:1748873671:0:15:4294967295:4230a3af00e22d6da475f8704b2761832fb95fecb19c8b698b7c7295b9a589de9a275f8aa60cb9407e66d16aee9a5ac5c030055a5a9c5fa15376e2fa4b16f155e8754a1c3bb728aa605d2f443852fc90dc4f8d1f15946c29cd7afbb906ccef66:16d2157b64280e13257c2f2fe670cdc9c95f7060f06d596c4a717435cb5a7d23"
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