#!/usr/bin/env python
# coding: utf-8

# In[1]:


#print (driver.page_source)
#Selenium
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException
import time
import pandas as pd
import re
from datetime import datetime
# paste url
url = 'https://www.lazada.com.ph/huggies/?q=All-Products&from=wangpu&langFlag=en&pageTypeId=2'

# let us initiate our driver firstly
driver = webdriver.Chrome()
driver.get(url)

# Let us create an empty lists to store the data
data_dict = {
    'Product_Names':[],
    'Product_URLs':[],
    'Current_Price':[],
    'Original_Price':[],
    'Discount_Percentage':[],
    'Units_Sold':[],
    'Reviews':[] 
}
    
# Lets us define a function to retireve the information we need
def get_page_data(driver, data_dict):
    #suppose we want to selenium to wait for it to exist on the page.
    #Explict waits
    try:
        element = WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.CLASS_NAME, 'Bm3ON')))
        search_results = driver.find_elements(By.CLASS_NAME, 'Bm3ON')
        
        for result in search_results:
            product_name = result.find_element(By.CLASS_NAME, 'RfADt').text
            product_url = result.find_element(By.TAG_NAME, 'a').get_attribute('href')
            current_price = result.find_element(By.CLASS_NAME, 'ooOxS').text
            try:
                original_price = result.find_element(By.CSS_SELECTOR, 'div.WNoq3 del.ooOxS').text
            except NoSuchElementException:
                original_price = "N/A"
            try:
                discount_percentage = result.find_element(By.CSS_SELECTOR,'div.WNoq3 span.IcOsH').text
            except NoSuchElementException:
                discount_percentage = "N/A"
            try:
                units_sold = result.find_element(By.CLASS_NAME,'_1cEkb').text
            except NoSuchElementException:
                units_sold = "N/A"
            try:
                reviews = result.find_element(By.CLASS_NAME,'qzqFw').text
            except NoSuchElementException:
                reviews = "N/A"
         
            # Append the empty lists with the data we have
            data_dict['Product_Names'].append(product_name)
            data_dict['Product_URLs'].append(product_url)
            data_dict['Current_Price'].append(current_price)
            data_dict['Original_Price'].append(original_price)
            data_dict['Discount_Percentage'].append(discount_percentage)
            data_dict['Units_Sold'].append(units_sold)
            data_dict['Reviews'].append(reviews)
    except NoSuchElementException:
        print("Some elements not found for this product.")
    except Exception as e:
        print(f"An error occurred: {e}")

# Now let us create a loop that will go through all the pages
current_page = 1
while True:
    # Get data from the current page
    print(f"Processing page {current_page}...")
    try:
        get_page_data(driver, data_dict)
    except StaleElementReferenceException:
        print("StaleElementReferenceException occurred. Waiting for the page to load again...")
        WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.CLASS_NAME, 'Bm3ON')))
        get_page_data(driver, data_dict)

    # Check if there is a next page link
    next_page_link = driver.find_elements(By.CLASS_NAME, 'ant-pagination-next')
    if len(next_page_link) == 0 or 'ant-pagination-disabled' in next_page_link[0].get_attribute('class'): 
        break
    else:
        # Click on the next page link to navigate to the next page
        next_page_link[0].click()
        # Wait for the new page to load
        WebDriverWait(driver, 60).until(EC.presence_of_element_located((By.CLASS_NAME, 'Bm3ON')))
        time.sleep(10)
    current_page += 1

# Create the DataFrame from the collected data
df = pd.DataFrame(data_dict)


# In[2]:


# Now let use manipulate our data
# Let us start by creating a function to extract product ID from the URL
def extract_product_id(url):
    match = re.search(r'i(\d+)\.html', url)
    if match:
        return match.group(1)
    return None

# Apply the function to create the 'Product_ID' column
df['Product_ID'] = df['Product_URLs'].apply(extract_product_id)

df.reset_index(drop=True)


# In[3]:


#Lets convert the file into excel

current_datetime = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
filename = f"Document_1_Scrape{current_datetime}.xlsx"
df.to_excel(filename,index=False)

