# Generated by Django 2.2.5 on 2020-07-08 16:43

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0009_auto_20200708_0227'),
    ]

    operations = [
        migrations.RenameField(
            model_name='profile',
            old_name='full_name',
            new_name='name',
        ),
        migrations.RenameField(
            model_name='profile',
            old_name='current_company',
            new_name='org',
        ),
    ]
