import time
import requests  # Add this import for making HTTP requests

class DDoSDetectionService:
    
    def __init__(self, api_url=None):
        self.api_url = "http://192.168.47.133/ddos-model"
        
    def check_for_attacks(self):
        try:
           
            try:
                response = requests.get(
                    self.api_url, 
                    timeout=3)
                
                print(f"API call made to {self.api_url}, status: {response.status_code}")
            except requests.exceptions.RequestException as e:
                print(f"API call failed: {str(e)}")
            
          
            source_ip = "None" 
            
            response_data = {"status": "success","source_ip": source_ip,"result": 0,}
            if response_data['result'] == 1:
                # If an attack is detected, store the alert
                alert = self.store_alert_if_detected(response_data)
                if alert:
                    print(f"Alert stored: {alert}")
            return response_data
            
        except Exception as e:
            print(f"Error in DDoS detection service: {str(e)}")
            return {
                "status": "error",
                "message": str(e),
                "result": 0
            }
        
    def store_alert_if_detected(self, detection_data):
        try:
            # Only create an alert if result is 1 (attack detected)
            if detection_data.get('result') != 1:
                return None
                
            # Import here to avoid circular imports
            from login.models import DDoSAlert
            from django.utils import timezone
            
            # Create new DDoSAlert object
            alert = DDoSAlert.objects.create(
                attack_type='ddos_attack',
                source_ip=detection_data.get('source_ip', '0.0.0.0'),
                target_ip='0.0.0.0',  # Assuming target IP is not provided
                timestamp=timezone.now(),
                severity='critical',
                status='active',
                blocked=False 
            )
            
            return alert
            
        except Exception as e:
            print(f"Error storing DDoS alert: {str(e)}")
            return None