# Generated by Django 2.2.5 on 2020-07-08 21:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0010_auto_20200708_1643'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='comments',
            field=models.TextField(blank=True, max_length=50000),
        ),
    ]
