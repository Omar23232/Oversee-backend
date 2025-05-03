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
