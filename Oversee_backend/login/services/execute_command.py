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
        self.csrf_token = "88c35ddc11170c014bed6afcde2d880b50464778"  # Set via set_credentials()
        self.auth_cookie = "Auth=cisco:1746713736:0:15:4294967295:abbef3dc9e8911e6dd1c3039946c780eb07375a63dee0efbee1e1d06aad072ac83a365c8360edcaf73b468ee9af01925a8b2253222b69cc10a198dff156310c65a8d56a938b36d9c1342c59dc3fca16476de068f8f0ace40eabdd4f5fce25100:7a193c130dfe7496fc0ef3f38913de1b50d88b8c8134a00b63e4b2bfe8d7ce5a; polaris-username=cisco"

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