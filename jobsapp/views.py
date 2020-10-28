from django.shortcuts import render,redirect,get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import (
    View,
    ListView,
    DetailView,
    CreateView,
    UpdateView,
    DeleteView
)
from django.contrib.auth.models import User
from users.models import Profile
from .models import Jobquery,Jobpost
from .scripts import fetch_listings, autofill_lever
from .forms import ContactForm
from django.forms.models import model_to_dict
from django.core.mail import send_mail, BadHeaderError
# import Levenshtein
# from dal import autocomplete



def home(request):
    if request.method == 'GET':
        form = ContactForm()
    #Sample list "generation"
    elif request.method == 'GET' and request.GET.get('sample_btn'):
        sample_title = request.POST.get('title')
        sample_location = request.POST.get('location')
        print('bad')
        return render(request, 'jobsapp/sample_list.html',{'sample_title':sample_title,'sample_location':sample_location})
    #Contact form
    else:
        form = ContactForm(request.POST)
        if form.is_valid():
            sender = form.cleaned_data['sender']
            subject = form.cleaned_data['subject']
            message = form.cleaned_data['message']
            try:
                send_mail(subject, message, sender, ['thoms.archer@gmail.com'])
                messages.success(request, "Your message has been sent!")
            except BadHeaderError:
                return HttpResponse('Invalid header found.')
            return redirect('jobsapp-home')
    context = {
        'form': form,
        'title':'Home'
    }
    return render(request, "jobsapp/home.html", context) 


class sampleListView(ListView):
    model = Jobpost
    template_name = 'jobsapp/sample_list.html' 
    context_object_name = 'jobposts'

    def get_queryset(self):
        sample_title = self.request.GET.get('sample_title').lower()
        sample_location = self.request.GET.get('sample_location').lower()
        temp_jobquery = Jobquery.objects.get(position=sample_title,location=sample_location,is_sample_list=True)
        print(temp_jobquery)
        print("test")
        #If user is signed in, only show posts not applied to
        if self.request.user.id:
            return super().get_queryset().filter(jobqueries=temp_jobquery).exclude(profile_applied=self.request.user.profile).exclude(profile_removed=self.request.user.profile).distinct().order_by('-date_added')
        else:
            return super().get_queryset().filter(jobqueries=temp_jobquery).order_by('-date_added')
    
    def get_context_data(self, *args, **kwargs):
        sample_title = self.request.GET.get('sample_title').lower()
        sample_location = self.request.GET.get('sample_location').lower()
        temp_jobquery_id = Jobquery.objects.get(position=sample_title,location=sample_location).id
        context = super().get_context_data(**kwargs)
        context['title'] = 'Sample Jobquery'
        context['jobquery_display'] = Jobquery.objects.get(pk=temp_jobquery_id).full_query
        context['jobquery_num_listings'] = len(Jobquery.objects.get(pk=temp_jobquery_id).jobpost_set.all())

        return context


class AppliedpostsListView(LoginRequiredMixin,ListView):
    login_url = '/login/'
    redirect_field_name = 'redirect_to'

    model = Jobpost
    template_name = 'jobsapp/applied-posts.html' 
    context_object_name = 'jobposts'

    def get_queryset(self):
        user = get_object_or_404(User, username=self.request.user)
        return super().get_queryset().filter(jobqueries__owners=user,profile_applied=user.profile).distinct().order_by('-date_added')

    def get_context_data(self, *args, **kwargs):
        user = get_object_or_404(User, username=self.request.user)
        context = super().get_context_data(**kwargs)
        context['title'] = 'Applied Jobs'
        context['jobqueries'] = Jobquery.objects.filter(owners=user)
        return context


class JobpostslistView(LoginRequiredMixin,ListView):
    login_url = '/login/'
    redirect_field_name = 'redirect_to'

    model = Jobpost
    template_name = 'jobsapp/jobpost_list.html' 
    context_object_name = 'jobposts'
    
    def get_queryset(self):
        user = get_object_or_404(User, username=self.request.user)
        return super().get_queryset().filter(jobqueries__owners=user).exclude(profile_applied=user.profile).exclude(profile_removed=user.profile).distinct().order_by('-date_added')

    def get_context_data(self, *args, **kwargs):
        user = get_object_or_404(User, username=self.request.user)
        context = super().get_context_data(**kwargs)
        context['title'] = 'My Joblist'
        context['jobqueries'] = Jobquery.objects.filter(owners=user)
        return context



class JobqueryCreateView(LoginRequiredMixin, CreateView):
    login_url = '/login/'
    redirect_field_name = 'redirect_to'
    
    model = Jobquery
    fields = ['position','location']
    success_url = '/'

    template_name = 'jobsapp/jobpost_list.html' 

    def form_valid(self,form):
        if self.request.user.jobquery_set.all().count()>=self.request.user.profile.query_limit:
            messages.error(self.request, "Maximum of 10 searches allowed at a time")
            return HttpResponseRedirect(self.request.path_info)
        elif self.request.user.profile.queries_today>=10:
            messages.error(self.request, "Only 10 new queries allowed per day")
            return HttpResponseRedirect(self.request.path_info)
        
        self.request.user.profile.queries_today = self.request.user.profile.queries_today + 1
        self.request.user.profile.save()
        try:
            existing_joblist = Jobquery.objects.get(position=self.request.POST['position'].lower(),location=self.request.POST['location'].lower())
            existing_joblist.owners.add(self.request.user)
            messages.success(self.request, "New search created!")
            return HttpResponseRedirect(self.get_success_url())
        except:
            existing_leverids = Jobpost.objects.values_list('lever_id',flat=True)
            all_listings = fetch_listings(form.instance.full_query,existing_leverids)
            new_listings = all_listings[0]
            existing_listings = all_listings[1]

            form.instance.save()
            form.instance.owners.add(self.request.user)
            form.instance.save()
            for l in new_listings:
                print("new post incoming!")
                try:
                    jp = Jobpost.objects.create(company=l['company'],position=l['text'].lower(),commitment=l['categories']['commitment'],location=l['categories']['location'],team=l['categories']['team'],description=l['descriptionPlain'],url=l['applyUrl'],lever_id=l['id'])
                    jp.save()
                    jp.jobqueries.add(form.instance)
                    jp.save()
                except:
                    Jobpost.objects.create(company=l['company'],position=l['text'].lower(),commitment='',location='',team='',description=l['descriptionPlain'],url=l['applyUrl'],lever_id=l['id'])   
                    jp.save()
                    jp.jobqueries.add(form.instance)
                    jp.save()
            for l in existing_listings:
                try:
                    jp = Jobpost.objects.get(lever_id=l)
                    jp.save()
                    jp.jobqueries.add(form.instance)
                    jp.save()
                except Exception as e:
                    print(e)
                    pass
            messages.success(self.request, "New search created!")

        return super().form_valid(form)

    def get_success_url(self):
        return reverse('jobposts-list')

    def get_queryset(self):
        user = get_object_or_404(User, username=self.request.user)
        return super().get_queryset().filter(jobqueries__owners=user).exclude(profile_applied=user.profile).exclude(profile_removed=user.profile).distinct().order_by('-date_added')

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(**kwargs)
        user = get_object_or_404(User, username=self.request.user)
        context['title'] = 'My Joblist'
        context['jobqueries'] = Jobquery.objects.filter(owners=user)
        context['jobposts'] = Jobpost.objects.filter(jobqueries__owners=user).exclude(profile_applied=user.profile).exclude(profile_removed=user.profile).distinct().order_by('-date_added')

        return context



def applyAllJobs(request):
    if request.method == 'GET':
        user = request.user
        relevant_posts = Jobpost.objects.filter(jobqueries__owners=user).exclude(profile_applied=user.profile).exclude(profile_removed=user.profile).distinct().order_by('-date_added')

        #equest.user.jobpost_set.all().count()
        
        applicant = Profile.objects.get(user__username=user)
        applicant_data = model_to_dict(applicant)
        try:
            applicant_data['resume'] = str(applicant.resume.path)
            applicant_data['email']=request.user.email
            applicant_data['urls[LinkedIn]'] = applicant_data.pop('linkedin_URL')
        except:
            return HttpResponse('missing_profile_info')
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
                    request.user.profile.applied_posts.add(appliedpost)
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
        try:
            #Checks to see if post has alread been applied to (Can happen when multiple tabs are open)
            existing = Jobpost.objects.get(profile_applied=request.user.profile,pk=jobpost_id)
            return HttpResponse('post_aleady_applied_to')
        except:
            pass
    

        applicant = Profile.objects.get(user__username=request.user)
        applicant_data = model_to_dict(applicant)
        try:
            applicant_data['resume'] = str(applicant.resume.path)
            applicant_data['email']=request.user.email
            applicant_data['urls[LinkedIn]'] = applicant_data.pop('linkedin_URL')
        except:
            return HttpResponse('missing_profile_info')
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
            request.user.profile.applied_posts.add(appliedpost)
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
        request.user.profile.removed_posts.add(removed_post)
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








from .refresh import refresh_all_queries, update_query
#Used to test functions/scripts
def testFunction(request):
    if request.method == 'GET':
        #refresh_all_queries()
        return HttpResponse("Success")

    else:
        return HttpResponse("Request method is not a GET")
