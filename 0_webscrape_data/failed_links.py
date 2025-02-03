from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import csv
import time
import datetime
import pandas as pd
from functions.functions import extract_maker

# Save start time
start = time.time()

# Intialize output
data_output = []

# Catach any product that has failed to be scraped 
failed = [['failed_url', 'error_type']]

# Set up path to chromedriver
service = Service('C:\myDocuments\projects\instant-noodles\chromedriver-win64\chromedriver.exe')

# Get today's date
current_date = datetime.datetime.today().strftime('%Y_%m_%d')

try:
    failed_product_links = pd.read_csv('0_webscrape_data/data/failed_urls_'+ current_date +'.csv').failed_url
except:
    print('No failed products found!')
    exit() 

# Loop through each products' link and extract info
for product_link in failed_product_links:

    # Start the WebDriver
    driver = webdriver.Chrome(service=service)

    # Load the webpage
    driver.get(product_link)

    try:
        # Wait for webpage to load
        time.sleep(2)

        # Wait until an element with class 'container1' is present if wait time above not sufficient
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.CLASS_NAME, "Gallery"))
        )
        
        # Get everything in 'cards' class
        item_details = driver.find_element(By.CLASS_NAME, "product-page").get_attribute('innerHTML')

        # Parse source into beautiful soup
        item_soup = BeautifulSoup(item_details, 'html.parser')

        # Product name
        try:
            name = item_soup.find("h1", {'class' : 'Title'}).get_text(strip=True)
        except:
            name = 'NA'

        # Weight
        try:
            weight = item_soup.find("p", {'class' : 'Qty'}).get_text(strip=True)
        except:
            weight = None

        # Price
        try:
            price = item_soup.find("p", {'class' : 'price'}).get_text(strip=True) 
        except AttributeError:
            try:
                price = item_soup.find("span", {'class' : 'price'}).get_text(strip=True)
            except:
                price = None
    
        # Image
        try:
            img_tag = item_soup.find("li", {'class' : 'splide__slide is-active is-visible'}).find('img')
            img_src = img_tag['src'] if img_tag else None
        except Exception as e:
            img_src = None

        # Description
        all_desc = item_soup.find_all("div", {'class' : 'product-description'})
        try:
            description = all_desc[0].find('p').get_text(strip = True)
        except:
            description = None

        # Get Maker Tag
        try:
            maker = extract_maker(item_soup.find("div", {'class' : 'categories'}))
        except:
            maker = None

        data_output.append([name, product_link, price, weight, maker, description, img_src])
    
    except Exception as e:
        # Raise an error if we failed to scrape
        print('Data failed to be scraped: ' + product_link)
        failed.append([product_link, e])

    finally:
        driver.quit()

file_name = '0_webscrape_data/data/instant_noodles_'+ str(current_date) +'.csv'

# Open the CSV file in append mode
with open(file_name, mode='a', newline='') as file:
    writer = csv.writer(file)
    # Write new rows
    writer.writerows(data_output)

print(str(len(data_output)) + ' rows of data added to original dataset: ' + file_name)

# Save end time
end = time.time()

# Get time difference
time_diff = float(end-start)

if time_diff // 60 == 0:
    time_diff_str = str(time_diff) + ' sec'
else:
    time_diff_str = str(time_diff / 60) + ' min'

print('Code took ' + time_diff_str + ' to run.')

