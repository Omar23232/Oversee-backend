# Generated by Django 5.2.3 on 2025-06-21 05:16

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('login', '0012_ddosalert'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='ddosalert',
            name='blocked_at',
        ),
        migrations.RemoveField(
            model_name='ddosalert',
            name='mitigation_notes',
        ),
        migrations.RemoveField(
            model_name='ddosalert',
            name='resolved_at',
        ),
    ]
