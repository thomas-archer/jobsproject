import requests
import json
from apiclient.discovery import build
# import urllib
# from bs4 import BeautifulSoup

#Retrieves lever data from serp/lever
def fetch_listings(input_query,existing_leverids):
    with open('/Users/tarcher/Projects/testdata.json') as f:
        json_data = json.load(f)

    query_results = json_data['organic']
    base_url = 'https://api.lever.co/v0/postings/'
    class Jobresult:
        def __init__(self, company, title, url):
            self.company = company
            self.title = title
            self.url = url
            self.id = url.split('/')[-1]
            self.api_info_url = base_url + url.split('/')[-2]+'/'+url.split('/')[-1]

    query_results

    #Keeps track of jobposts already in database, so don't need to make call to Lever API for data
    overlapping_leverids = []
    job_postings = []
    for item in query_results:
        url=item['url']
        if url.count('-')>=2:
            if 'apply' in url:
                url = url.split('/apply')[0]
            elif '/?' in url:
                url = url.split('/?')[0]
            temp_info = item['title']
            if len(temp_info.split('-'))>1:
                temp_company = temp_info.split('-')[0]
                temp_title = temp_info.split('-')[1]
                job_postings.append(Jobresult(temp_company,temp_title,url))
            else:
                temp_company = ' '
                temp_title = temp_info
                job_postings.append(Jobresult(temp_company,temp_title,url))


    new_jobs=[]
    overlapping_leverids = []
    for j in job_postings[:20]:
        if j.id in existing_leverids:
            overlapping_leverids.append(j.id)
        else:   
            print("api called!")
            response = requests.get(j.api_info_url)
            if response.status_code==200:
                jdata = json.loads(response.content)
                jdata.update(company = j.company)
                new_jobs.append(jdata)
                print("new_job appended!")
            else:
                print("bad url!")
            #Store invalid resposne code lever-id's here, will need database object
            # else:
            #     bad_leverids.append(j.id)


    return [new_jobs,overlapping_leverids]


    




import mechanicalsoup
from bs4 import BeautifulSoup
import re

#Automatically files in and submits a lever form
def autofill_lever(applicant_data,application_url):
    # my_data = {
    #     'name':'person nerson',
    #     'email':'personnerson@yahoo.com',
    #     'phone':'123456789',
    #     'org':'abc.org',
    #     'my_resume':'/Users/tarcher/Desktop/dummy.pdf',
    # }

    browser = mechanicalsoup.StatefulBrowser()
    #application_url = 'https://jobs.lever.co/leverdemo-8/7766e857-f406-48ab-8a04-dbe09bed2d43/apply'
    r = browser.open(application_url)
    if r.status_code!=200:
        return '404'
    page = browser.get_current_page()
    form = browser.select_form('form[method="POST"]')

    raw_inputs = page.find('form').find_all(['input','textarea','select'])
    # custom_questions = page.find_all('li',{'class':'application-question custom-question'})
    #Setting attributes to make things easier
    def cleaning(raw):
        current_marked='...../'
        for i in raw:
            #Setting type attribute
            if 'type' not in i.attrs.keys():
                i['type']='unknown'

            if i.name == 'textarea':
                i['type'] = 'text'

            elif i.name == 'select':
                i['type'] = 'select'

            if 'baseTemplate' in i['name']:
                card_unique=i['name'].split(']')[0]
                if 'required":true' in i['value']:
                    current_marked=card_unique


            if 'required' in i.attrs.keys() or current_marked in i['name'] or i['name']=='resume':
                i['required'] = 'yes'
            else:
                i['required']='no'

    cleaned_inputs = raw_inputs
    cleaning(cleaned_inputs)

    check_options=[]
    radio_options=[]
    for i in cleaned_inputs:
        if i['name'] in applicant_data:
            form.set(i['name'],applicant_data[i['name']])
        elif i['required']=='yes':
            if i['type']=='radio' and 'value' in i.attrs.keys():
                if i['value'].lower()=='yes':
                    form.set(i['name'],i['value'])
                else:
                    if i['name'] not in radio_options:
                        all_radios=page.find_all('input',{'name':i['name']})
                        #options[0] is the first checkbox option input
                        form.set(i['name'],all_radios[0]['value'])
                        radio_options.append(i['name'])
            elif i['type']=='checkbox' and 'value' in i.attrs.keys():
                if i['value'].lower()=='yes':
                    form.set(i['name'],i['value'])
                else:
                    if i['name'] not in check_options:
                        options=page.find_all('input',{'name':i['name']})
                        form.set(i['name'],options[0]['value'])
                        check_options.append(i['name'])
            elif i['type']=='select':
                select_options = page.find('select',{'name':i['name']}).find_all('option')
                for op in select_options:
                    if op.text.lower()=='a':
                        form.set(i['name'],op.text)
                        break
                else:
                    form.set(i['name'],select_options[1].text)
            elif i['type']=='text':
                form.set(i['name'],'.')
            elif i['type']=='file':
                form.set(i['name'],applicant_data['resume'])
            else:
                form.set(i['name'],'.')

    labels = page.find_all('label')
    for l in labels:
        try:
            label_text = l.find('div',{'class':'text'}).text
            label_input_name = l.find_all(['input','textarea','select'])[0]['name']
            if "authorized" in label_text or "legally" in label_text or 'authorization' in label_text:
                form.set(label_input_name,'Yes')
            if 'sponsorship' in label_text or ('require' in label_text and 'visa' in label_text.lower()):
                form.set(label_input_name,'No')
        except:
            pass


    browser.launch_browser()
    form.choose_submit(None)
    #response = browser.submit_selected()
    # print(response)
    # print(response.text)
    browser.close()
    return 'Success'



