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


# models.py
from django.db import models

class ExecutedCommand(models.Model):
    device_ip = models.GenericIPAddressField()
    command = models.TextField()
    output = models.JSONField()
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.device_ip} - {self.command[:50]}..."