# Generated by Django 2.2.5 on 2020-07-07 23:39

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0005_profile_image'),
    ]

    operations = [
        migrations.RenameField(
            model_name='profile',
            old_name='image',
            new_name='resume_file',
        ),
    ]
