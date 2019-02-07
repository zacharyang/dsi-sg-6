import requests as rq
from bs4 import BeautifulSoup
import time 
import json 
import re
import numpy as np
import datetime
import unicodedata
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def get_jobs(urls):
    '''Takes the job url and extracts and parses the information into a pandas Dataframe'''

    # Initialise the data as a list, and each record to be a dictionary to be stored in the list #
    jobs=[]
    
    # Numerical features # 
    num_features=['salary_lower','salary_upper','num_apps']
    # Title or short form text features # 
    title_features=['company_name','company_location','salary_type','job_title','employment_type','seniority']
    # Long form text features # 
    text_features=['job_description','job_requirements']
    # Date features # 
    date_features=['date_posted','date_expiry']
    # All possible columns in the df # 
    job_features=num_features+title_features+text_features+date_features

    # Date expression for parsing# 
    date_expression='(\d{2} (|Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec|) \d{4})'

    # Initialise the webdriver # 
    driver=webdriver.Chrome()
    for i,url in enumerate(urls):

        driver.get(url)
        # Wait till job info loads, if timeout, close the driver and try again #
        try:
            WebDriverWait(driver,10).until(lambda x: x.find_element_by_id('job_info'))
        except:
            driver.close()
            driver=webdriver.Chrome()
            driver.get(url)
            WebDriverWait(driver,20).until(lambda x: x.find_element_by_id('job_info'))

        html=driver.page_source
        # Parse the data using Beautiful Soup # 
        soup=BeautifulSoup(html,'lxml')

        # Progress marker on successful parsing # 
        print('{:2.2f}% complete'.format(i*100/len(urls)))

        ## Salary information ##
        salary=soup.find('section',class_='salary')
        try:
            salary_range=salary.find('span',class_='salary_range').text.split('to')
            salary_lower=float(re.sub(r'[^0-9]','',salary_range[0]))
            salary_upper=float(re.sub(r'[^0-9]','',salary_range[1]))
            salary_type=salary.find('span',class_='salary_type')
        except:
            salary_lower=None
            salary_upper=None
            salary_type=None

        job_info=soup.find('section',attrs={'id':'job_info'})
        
        ## Company information ## 
        company_name=soup.find('p',attrs={'name':'company'})
        company_location=job_info.find('p',attrs={'id':'address'})

        ## Job Information ## 
        employment_type=job_info.find('p',attrs={'id':'employment_type'})
        seniority=job_info.find('p',attrs={'id':'seniority'})
        job_title=soup.find('h1',attrs={'id':'job_title'})
        num_apps=soup.find('span',attrs={'id':'num_of_applications'})
        date_posted=soup.find('span',attrs={'id':'last_posted_date'})
        date_expiry=soup.find('span',attrs={'id':'expiry_date'})
        job_description=soup.find('div',attrs={'id':'job_description'})
        job_requirements=soup.find('div',attrs={'id':'requirements'})

        ### Parser ### 

        ## Numerical features ## 
        try:
            num_apps=float(re.sub(r'[^0-9]','',num_apps.text))
        except AttributeError:
            pass
        num_vals=[salary_lower,salary_upper,num_apps]

        ## Title Features ## 

        titles=[company_name,company_location,salary_type,job_title,employment_type,seniority]
        titles_vals=[i.text.title() if i is not None else i for i in titles]

        ## Text Features ## 

        texts=[job_description,job_requirements]
        text_vals=[i.text if i is not None else i for i in texts]

        ## Date Features ## 

        dates=[date_posted,date_expiry]
        date_vals=[re.search(date_expression,i.text).group() if i is not None else i for i in dates]


        job_vals= num_vals+titles_vals+text_vals+date_vals

        jobs.append(dict(zip(job_features,job_vals)))


    driver.close()
    return jobs

if __name__ == '__main__':

    with open('./data/job_urls.json','r') as file:
        job_urls=json.load(file)
        file.close()

    jobs_dat=get_jobs(job_urls)
    
    jobs_df=pd.DataFrame(jobs_dat)
    
    jobs_df.to_csv('./data/jobs.csv',index=False)
