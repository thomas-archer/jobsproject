from django.contrib.auth.models import User
from .models import Jobquery,Jobpost
from .scripts import fetch_listings
from django.forms.models import model_to_dict
from users.models import Profile

def other_dailies():
    # Remove queries with no owners - tested, works
    unused_queries = Jobquery.objects.filter(jobpost_set_isnull=True)
    for q in unused_queries:
        q.delete()
    # Reset daily query limit for users - tested, works
    Profile.objects.filter(queries_today__gt=0).update(queries_today=0)


#For testing
# def refresh_all_queries():
    #Profile.objects.filter(queries_today__gt=0).update(queries_today=0)


def refresh_all_queries():
    #To start out, refresh weekly not daily
    all_queries = Jobquery.objects.all()
    for query in all_queries:
        update_query(query)
    return




def update_query(query):
    print(query)
    existing_leverids = Jobpost.objects.values_list('lever_id',flat=True)
    all_listings = fetch_listings(query.combined_query,existing_leverids)
    new_listings = all_listings[0]
    existing_listings = all_listings[1]
    for l in new_listings:
        try:
            jp = Jobpost.objects.create(company=l['company'],position=l['text'].lower(),commitment=l['categories']['commitment'],location=l['categories']['location'],team=l['categories']['team'],description=l['descriptionPlain'],url=l['applyUrl'],lever_id=l['id'])
            jp.save()
            jp.jobqueries.add(query)
            jp.save()
        except:
            Jobpost.objects.create(company=l['company'],position=l['text'].lower(),commitment='',location='',team='',description=l['descriptionPlain'],url=l['applyUrl'],lever_id=l['id'])   
            jp.save()
            jp.jobqueries.add(query)
            jp.save()
        print('added new!')

    current_jobpost_leverids = Jobpost.objects.filter(jobqueries=query).values_list('lever_id',flat=True)
    for l in existing_listings:
        if l in current_jobpost_leverids:
            print('continued!')
            continue
        try:
            jp = Jobpost.objects.get(lever_id=l)
            jp.save()
            jp.jobqueries.add(query)
            jp.save()
            print('added existing!')
        except Exception as e:
            print(e)
            pass