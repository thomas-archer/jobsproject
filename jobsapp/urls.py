from django.urls import path
from .views import (
    JobpostslistView,
    JobqueryCreateView,
    sampleListView,
    AppliedpostsListView
)
from . import views
from django.conf.urls import url



urlpatterns = [

    path('mylist/', JobqueryCreateView.as_view(), name='jobposts-list'),
    path('applied-posts/', AppliedpostsListView.as_view(), name='applied-list'),
    
    url(r'^applyalljobs/$', views.applyAllJobs, name='applyalljobs'),
    url(r'^applytojob/$', views.applyToJob, name='applytojob'),
    url(r'^removejob/$', views.removeJob, name='removejob'),
    url(r'^removejobquery/$', views.removeJobQuery, name='removejobquery'),
    url(r'^testfunc/$', views.testFunction, name='testfunc'),

    path('jobquery/new/', JobqueryCreateView.as_view(), name='jobquery-create'),

    path('sample-list/', sampleListView.as_view(), name='sample-list'),

    path('', views.home, name='jobsapp-home'), #Keep at bottom


    #path('mylists/', UserJoblistView.as_view(), name='user-mylists'),
    #path('jobpost/<int:pk>/', JobpostDetailView.as_view(), name='jobpost-detail')
]
