from django.shortcuts import render,redirect,get_object_or_404
from django.contrib.auth.models import User
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import (
    ListView,
    DetailView,
    CreateView,
    UpdateView,
    DeleteView
)
from .models import Jobquery,Jobpost
from django.views.generic import View
from django.core.mail import send_mail
from django.urls import reverse
from .scripts import fetch_listings, autofill_lever
from django.forms.models import model_to_dict
from users.models import Profile

from django.core.mail import send_mail, BadHeaderError
from .forms import ContactForm

# Create your views here.
def home(request):
    if request.method == 'GET' and request.GET.get('sample_btn'):
        sample_title = request.POST.get('title')
        sample_location = request.POST.get('location')
        return render(request, 'jobsapp/sample_list.html',{'sample_title':sample_title,'sample_location':sample_location})
    return render(request, 'jobsapp/home.html',{'title':'Home'})


class sampleListView(ListView):
    model = Jobpost
    template_name = 'jobsapp/sample_list.html' 
    context_object_name = 'jobposts'

    def get_queryset(self):
        sample_title = self.request.GET.get('sample_title')
        sample_location = self.request.GET.get('sample_location')
        temp_jobquery = Jobquery.objects.filter(position=sample_title,location=sample_location)[0]
        print(temp_jobquery)
        print("test")
        #If user is signed in, only show posts not applied to
        if self.request.user.id:
            return super().get_queryset().filter(jobqueries=temp_jobquery).exclude(applied_users=self.request.user).distinct().order_by('-date_added')
        else:
            return super().get_queryset().filter(jobqueries=temp_jobquery).order_by('-date_added')
    
    def get_context_data(self, *args, **kwargs):
        sample_title = self.request.GET.get('sample_title')
        sample_location = self.request.GET.get('sample_location')
        temp_jobquery_id = Jobquery.objects.filter(position=sample_title,location=sample_location)[0].id
        context = super().get_context_data(**kwargs)
        context['title'] = 'Sample Jobquery'
        context['jobquery_display'] = Jobquery.objects.get(pk=temp_jobquery_id).full_query
        context['jobquery_num_listings'] = len(Jobquery.objects.get(pk=temp_jobquery_id).jobpost_set.all())

        return context


def about(request):
    return render(request, 'jobsapp/about.html',{'title':'About'})

# def contact(request):
#     return render(request, 'jobsapp/contact.html',{'title':'Contact'})



class JobpostslistView(LoginRequiredMixin,ListView):
    login_url = '/login/'
    redirect_field_name = 'redirect_to'

    model = Jobpost
    template_name = 'jobsapp/jobpost_list.html' 
    context_object_name = 'jobposts'
    
    def get_queryset(self):
        user = get_object_or_404(User, username=self.request.user)
        return super().get_queryset().filter(jobqueries__owners=user).exclude(applied_users=user).distinct().order_by('-date_added')

    def get_context_data(self, *args, **kwargs):
        user = get_object_or_404(User, username=self.request.user)
        context = super().get_context_data(**kwargs)
        context['title'] = 'My Joblist'
        context['jobqueries'] = Jobquery.objects.filter(owners=user)
        return context



class JobqueryCreateView(LoginRequiredMixin, CreateView):
    model = Jobquery
    fields = ['position','location']
    success_url = '/'

    def form_valid(self,form):
        print(self.request.user.jobquery_set.all().count())
        if self.request.user.jobquery_set.all().count()>=10:
            messages.error(self.request, "Maximum of 10 searches allowed at a time")
            return render(self.request, 'jobsapp/jobquery_form.html', {'form': form})
        #Insert here to check not only exact match, but also close enough match
        try:
            existing_joblist = Jobquery.objects.get(position=self.request.POST['position'],location=self.request.POST['location'])
            existing_joblist.owners.add(self.request.user)
            return HttpResponseRedirect(self.get_success_url())
        except:
            #later on pass in all posts into fetch_listings to check for redundencies and make repetitive lever API calls
            existing_leverids = Jobpost.objects.values_list('lever_id',flat=True)

            all_listings = fetch_listings(form.instance.full_query,existing_leverids)
            new_listings = all_listings[0]
            existing_listings = all_listings[1]

            form.instance.save()
            form.instance.owners.add(self.request.user)
            form.instance.save()
            for l in new_listings:
                try:
                    jp = Jobpost.objects.get(lever_id=l['id'])
                    jp.save()
                    jp.jobqueries.add(form.instance)
                    jp.save()
                    print('exists!')
                except:
                    print('does not exist!')
                    try:
                        jp = Jobpost.objects.create(company=l['company'],position=l['text'],commitment=l['categories']['commitment'],location=l['categories']['location'],team=l['categories']['team'],description=l['descriptionPlain'],url=l['applyUrl'],lever_id=l['id'])
                        jp.save()
                        jp.jobqueries.add(form.instance)
                        jp.save()
                    except:
                        Jobpost.objects.create(company=l['company'],position=l['text'],commitment='',location='',team='',description=l['descriptionPlain'],url=l['applyUrl'],lever_id=l['id'])   
                        jp.save()
                        jp.jobqueries.add(form.instance)
                        jp.save()

            
            return super().form_valid(form)

    def get_success_url(self):
        return reverse('jobposts-list')

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Create New Jobquery'
        return context



def applyAllJobs(request):
    if request.method == 'GET':
        user = request.user
        relevant_posts = Jobpost.objects.filter(jobqueries__owners=user).exclude(applied_users=user).distinct().order_by('-date_added')
        applicant = Profile.objects.get(user__username=user)
        applicant_data = model_to_dict(applicant)
        applicant_data['resume'] = str(applicant.resume.path)
        applicant_data['email']=request.user.email
        applicant_data['urls[LinkedIn]'] = applicant_data.pop('linkedin_URL')
        applicant_data['urls[Twitter]'] = applicant_data.pop('twitter_URL')
        applicant_data['urls[GitHub]'] = applicant_data.pop('github_URL')
        applicant_data['urls[Portfolio]'] = applicant_data.pop('portfolio_URL')
        failed_count=0
        for appliedpost in relevant_posts:
            try:
                result = autofill_lever(applicant_data,appliedpost.url)
                if(result=='404'):
                    appliedpost.delete()
                else:
                    appliedpost.applied_users.add(request.user)
            except:
                failed_count+=1
                pass  
        if failed_count==0:
            return HttpResponse('Success') 
        else:
            return HttpResponse(failed_count)
    else:
        return HttpResponse("Request method is not a GET")


def applyToJob(request):
    if request.method == 'GET':
        jobpost_id = request.GET['jobpost_id']
        appliedpost = Jobpost.objects.get(pk=jobpost_id)
        applicant = Profile.objects.get(user__username=request.user)
        applicant_data = model_to_dict(applicant)
        applicant_data['resume'] = str(applicant.resume.path)
        applicant_data['email']=request.user.email
        applicant_data['urls[LinkedIn]'] = applicant_data.pop('linkedin_URL')
        applicant_data['urls[Twitter]'] = applicant_data.pop('twitter_URL')
        applicant_data['urls[GitHub]'] = applicant_data.pop('github_URL')
        applicant_data['urls[Portfolio]'] = applicant_data.pop('portfolio_URL')
        try:
            result = autofill_lever(applicant_data,appliedpost.url)
            #In case that apply page gives 404, meaning post was taken down
            if(result=='404'):
                appliedpost.delete()
                return HttpResponse("Post no longer exists")
            #Below works for adding to applied list:
            appliedpost.applied_users.add(request.user)
            return HttpResponse("Success")
        #Reaches here if error autofilling an application, should ideally never happen right now
        except:
            return HttpResponse(appliedpost.url)
    else:
        return HttpResponse("Request method is not a GET")



def removeJob(request):
    if request.method == 'GET':
        jobpost_id = request.GET['jobpost_id']
        removed_post = Jobpost.objects.get(pk=jobpost_id)
        #using applied users to hold removed posts because they don't show up on refresh
        removed_post.applied_users.add(request.user)
        #Keep track of how many posts removed for purpose of showing # of applied posts
        # request.user.profile.removed_count+=1
        request.user.profile.save()
        # print(request.user.profile.removed_count)
        return HttpResponse("Removed!")
    else:
        return HttpResponse("Request method is not a GET")




def removeJobQuery(request):
    if request.method == 'GET':
        jobquery_id = request.GET['jobquery_id']
        removed_query = Jobquery.objects.get(pk=jobquery_id)
        removed_query.owners.remove(request.user)
    
        return HttpResponse("Success")

    else:
        return HttpResponse("Request method is not a GET")













#Contact form view
def contactView(request):
    if request.method == 'GET':
        form = ContactForm()
    else:
        form = ContactForm(request.POST)
        if form.is_valid():
            subject = form.cleaned_data['subject']
            from_email = form.cleaned_data['from_email']
            message = form.cleaned_data['message']
            try:
                send_mail(subject, message, from_email, ['thoms.archer@gmail.com'])
            except BadHeaderError:
                return HttpResponse('Invalid header found.')
            return redirect('jobsapp-contact')
    context = {
        'form': form,
        'title':'Contact'
    }
    return render(request, "jobsapp/contact.html", context) 
