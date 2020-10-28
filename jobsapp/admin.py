from django.contrib import admin
from .models import Jobquery, Jobpost

# Register your models here. Adding to this will make it accessible in admin page
admin.site.register(Jobquery)
admin.site.register(Jobpost)