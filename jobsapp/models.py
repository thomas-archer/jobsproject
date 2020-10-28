from django.db import models
from django.utils import timezone
from django.urls import reverse
from django.contrib.auth.models import User
# Create your models here.


class Jobquery(models.Model):
    position = models.CharField(max_length=100)
    location = models.CharField(max_length=50,default="")
    updated_date = models.DateTimeField(default=timezone.now)
    owners = models.ManyToManyField(User,blank=True)
    combined_query = models.CharField(max_length=150)

    is_sample_list = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        self.position = self.position.lower()
        self.location = self.location.lower()
        self.combined_query = self.position.lower() + " " + self.location.lower()
        super(Jobquery, self).save(*args, **kwargs) # Call the "real" save() method

    @property
    def full_query(self):
        #insert back in quotation marks around position for direct results
        return self.position+" "+self.location

    @property
    def formatted_query(self):
        return self.position+" | "+self.location

    def __str__(self):
        return self.full_query

    def get_absolute_url(self):
        return reverse('joblist-detail',kwargs={'pk':self.pk})


class Jobpost(models.Model):
    company = models.CharField(max_length=100,blank=True,default="_")
    position = models.CharField(max_length=100,blank=True,default="_")
    commitment = models.CharField(max_length=100,blank=True,default="_")
    location = models.CharField(max_length=100,blank=True,default="_")
    team = models.CharField(max_length=100,blank=True,default="_")
    description = models.CharField(max_length=2000,blank=True,default="_")
    url = models.CharField(max_length=1000)
    lever_id = models.CharField(max_length=100)

    date_added = models.DateTimeField(default=timezone.now)

    jobqueries = models.ManyToManyField(Jobquery,blank=True)
    
    
    @property
    def info_url(self):
        return self.url.split('/apply')[0]
    
    def __str__(self):
        return self.company+self.position

