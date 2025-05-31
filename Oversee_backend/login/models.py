from django.db import models


class DeviceMemory(models.Model):
    device_ip = models.GenericIPAddressField()
    name = models.CharField(max_length=100)
    total_memory = models.BigIntegerField()
    used_memory = models.BigIntegerField()
    free_memory = models.BigIntegerField()
    lowest_usage = models.BigIntegerField()
    highest_usage = models.BigIntegerField()
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-timestamp']  # Newest first

    def __str__(self):
        return f"{self.device_ip} - {self.name} at {self.timestamp}"
    
    
class DeviceCPU(models.Model):
    device_ip = models.GenericIPAddressField()
    five_seconds = models.FloatField()
    one_minute = models.FloatField()
    five_minutes = models.FloatField()
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-timestamp']
        verbose_name = 'CPU Usage'

    def __str__(self):
        return f"{self.device_ip} - {self.five_seconds}% at {self.timestamp}"



class ExecutedCommand(models.Model):
    device_ip = models.GenericIPAddressField()
    command = models.TextField()
    output = models.JSONField()
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.device_ip} - {self.command[:50]}..."
    

class InterfaceStatus(models.Model):
    device_ip = models.GenericIPAddressField()
    name = models.CharField(max_length=100)
    oper_status = models.CharField(max_length=20)  # up/down
    last_change = models.DateTimeField()
    mac_address = models.CharField(max_length=17)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['name', '-timestamp']),
        ]

    def __str__(self):
        return f"{self.name} - {self.oper_status}"
    
# This model is used to store device information
class DeviceInfo(models.Model):
    hostname = models.CharField(max_length=100)
    uptime = models.CharField(max_length=100)
    system_description = models.TextField()
    location = models.CharField(max_length=200)
    status = models.CharField(max_length=50)
    device_ip = models.GenericIPAddressField()  # Added this instead of contact
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.hostname} - {self.device_ip}"
    
    
# this model is used to store network thresholds for alerts
class NetworkThreshold(models.Model):
    METRIC_CHOICES = [
        ('memory', 'Memory Usage'),
        ('cpu_5s', 'CPU 5 Seconds'),
        ('cpu_1m', 'CPU 1 Minute'),
        ('cpu_5m', 'CPU 5 Minutes')
    ]
    
    SEVERITY_CHOICES = [
        ('warning', 'Warning'),
        ('critical', 'Critical'),
        ('emergency', 'Emergency')
    ]
    
    metric = models.CharField(max_length=20, choices=METRIC_CHOICES)
    threshold_value = models.FloatField()
    severity = models.CharField(max_length=10, choices=SEVERITY_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)

# this model is used to store network alerts
class NetworkAlert(models.Model):
    device_ip = models.CharField(max_length=15)
    metric_name = models.CharField(max_length=50)
    metric_value = models.FloatField()
    threshold_value = models.FloatField()
    severity = models.CharField(max_length=10)
    created_at = models.DateTimeField(auto_now_add=True)
    is_acknowledged = models.BooleanField(default=False)