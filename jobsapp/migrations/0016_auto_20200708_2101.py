# Generated by Django 2.2.5 on 2020-07-08 21:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('jobsapp', '0015_jobpost_already_applied'),
    ]

    operations = [
        migrations.AlterField(
            model_name='jobpost',
            name='commitment',
            field=models.CharField(blank=True, max_length=100),
        ),
        migrations.AlterField(
            model_name='jobpost',
            name='location',
            field=models.CharField(blank=True, max_length=100),
        ),
        migrations.AlterField(
            model_name='jobpost',
            name='team',
            field=models.CharField(blank=True, max_length=100),
        ),
    ]