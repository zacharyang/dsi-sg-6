from bs4 import BeautifulSoup
import time 
import json 
import re
import numpy as np
import datetime
import unicodedata
import pandas as pd
import settings
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def get_listings():
    '''Does a keyword search using the word "data" on the job search portal and returns all 
    the links on the searh results page'''    
    job_listings_urls=[]

    # URL is imported from setings ## 
    url_prefix=setttings.URL_PREFIX
    driver=webdriver.Chrome()
    
    for i in range(221):
        url=settings.URL_STR.format(i)
        driver.get(url)
        # Wait until the main resulst load # 
        WebDriverWait(driver,10).until(lambda x: x.find_element_by_class_name('card-list'))
        html=driver.page_source
        soup=BeautifulSoup(html,'lxml')
        # Find all links on page in the "card-list" div #
        try:
            job_links=[i.get('href') for i in soup.find('div',class_='card-list').find_all('a') if i.get('href').split('/')[1]=='job']
            print('Got {} jobs for page {}'.format(len(job_links),i))
        except:
            print('Error collecting page {}'.format(i))

        job_listings_urls+=[url_prefix+i for i in job_links]

    driver.close()
    return job_listings_urls


if __name__ == '__main__':

    urls=get_listings()

    with open('./data/job_urls.json','w') as outfile:
        json.dump(urls,outfile)