# Generated by Django 5.1.6 on 2025-06-08 17:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('login', '0009_executedcommand_user'),
    ]

    operations = [
        migrations.AddField(
            model_name='interfacestatus',
            name='error_rate',
            field=models.FloatField(default=0),
        ),
        migrations.AddField(
            model_name='interfacestatus',
            name='in_bandwidth',
            field=models.FloatField(default=0),
        ),
        migrations.AddField(
            model_name='interfacestatus',
            name='in_discards',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='interfacestatus',
            name='in_errors',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='interfacestatus',
            name='in_octets',
            field=models.BigIntegerField(default=0),
        ),
        migrations.AddField(
            model_name='interfacestatus',
            name='in_packets',
            field=models.BigIntegerField(default=0),
        ),
        migrations.AddField(
            model_name='interfacestatus',
            name='out_bandwidth',
            field=models.FloatField(default=0),
        ),
        migrations.AddField(
            model_name='interfacestatus',
            name='out_discards',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='interfacestatus',
            name='out_errors',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='interfacestatus',
            name='out_octets',
            field=models.BigIntegerField(default=0),
        ),
        migrations.AddField(
            model_name='interfacestatus',
            name='out_packets',
            field=models.BigIntegerField(default=0),
        ),
        migrations.AddField(
            model_name='interfacestatus',
            name='packet_loss',
            field=models.FloatField(default=0),
        ),
    ]
