from django.contrib import admin
from .models import (
    DeviceMemory, 
    DeviceCPU, 
    ExecutedCommand, 
    InterfaceStatus, 
    DeviceInfo, 
    NetworkThreshold, 
    NetworkAlert,
    DDoSAlert,
    UserRole
)

# Register models
admin.site.register(DeviceMemory)
admin.site.register(DeviceCPU)
admin.site.register(ExecutedCommand)
admin.site.register(InterfaceStatus)
admin.site.register(DeviceInfo)
admin.site.register(NetworkThreshold)
admin.site.register(NetworkAlert)
admin.site.register(UserRole)

@admin.register(DDoSAlert)
class DDoSAlertAdmin(admin.ModelAdmin):
    list_display = ('attack_type', 'source_ip', 'target_ip', 'severity', 'status', 'detection_time')
    list_filter = ('attack_type', 'status', 'severity', 'detection_time')
    search_fields = ('source_ip', 'target_ip', 'target_service')
    readonly_fields = ('detection_time',)
    fieldsets = (
        ('Attack Information', {
            'fields': ('attack_type', 'source_ip', 'target_ip', 'target_port', 'target_service', 'severity', 'ai_confidence')
        }),
        ('Status & Metrics', {
            'fields': ('status', 'detection_time', 'duration', 'packet_rate', 'bandwidth', 'connection_count')
        }),
        ('Response', {
            'fields': ('blocked', 'blocked_at', 'resolved_at', 'mitigation_notes')
        }),
    )
