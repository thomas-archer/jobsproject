# Generated by Django 2.2.5 on 2020-07-08 02:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0006_auto_20200707_2339'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='resume_file',
            field=models.FileField(default='/Users/tarcher/Desktop/dummy.pdf', upload_to='resume_files'),
        ),
    ]
