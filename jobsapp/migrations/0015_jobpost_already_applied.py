# Generated by Django 2.2.5 on 2020-07-08 17:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('jobsapp', '0014_auto_20200708_1746'),
    ]

    operations = [
        migrations.AddField(
            model_name='jobpost',
            name='already_applied',
            field=models.BooleanField(default=False),
        ),
    ]