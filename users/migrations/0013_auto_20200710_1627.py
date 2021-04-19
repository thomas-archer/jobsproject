# Generated by Django 2.2.5 on 2020-07-10 16:27

from django.db import migrations, models
import users.validators


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0012_auto_20200708_2113'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='resume',
            field=models.FileField(blank=True, null=True, upload_to='resume_files', validators=[users.validators.validate_file_size]),
        ),
    ]
