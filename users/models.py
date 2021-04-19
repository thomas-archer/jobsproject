from django.db import models
from django.contrib.auth.models import User
from .validators import validate_file_size
from jobsapp.models import Jobpost

# Create your models here.
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100,blank=True)
    phone = models.CharField(max_length=20,blank=True)
    org = models.CharField(max_length=100,blank=True)
    linkedin_URL = models.CharField(max_length=300,blank=True)
    github_URL = models.CharField(max_length=300,blank=True)
    twitter_URL = models.CharField(max_length=300,blank=True)
    portfolio_URL = models.CharField(max_length=300,blank=True)
    comments = models.TextField(max_length=50000,blank=True)

    resume = models.FileField(null=True,blank=True,upload_to='resume_files',validators=[validate_file_size])

    query_limit=models.IntegerField(default=10)
    queries_today=models.IntegerField(default=0)

    applied_posts = models.ManyToManyField(Jobpost,related_name='%(class)s_applied',blank=True)
    removed_posts = models.ManyToManyField(Jobpost,related_name='%(class)s_removed',blank=True)

    def __str__(self):
        return f'{self.user.username} Profile'
