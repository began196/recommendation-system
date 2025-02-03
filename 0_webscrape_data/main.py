from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import csv
import datetime
import time
from functions.functions import extract_maker

# Save start time
start = time.time()

# Intialize output
data_output = [['product', 'product_link','price', 'weight', 'maker', 'description', 'img_src']]

# Catach any product that has failed to be scraped 
failed = [['failed_url', 'error_type']]

# Set up path to chromedriver
service = Service('C:\myDocuments\projects\instant-noodles\chromedriver-win64\chromedriver.exe')

# Instant noodle products webpage URL
url = 'https://www.japancentre.com/en/categories/11439-instant-noodles?page='

for i in range(3):

    print('Currently at page: ' + str(i+1))

    # Append page number to URL
    curr_url = url + str(i+1)

    # Start the WebDriver
    driver = webdriver.Chrome(service=service)

    # Load the webpage
    driver.get(curr_url)

    try:  
        # Wait for webpage to load   
        time.sleep(2)

        # Wait until an element with class 'cards' is present if wait time above not sufficient
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.CLASS_NAME, "cards"))
        )
        
        # Get everything in 'cards' class
        data = driver.find_element(By.CLASS_NAME, "cards").get_attribute('innerHTML')

    finally:
        driver.quit()

    # Parse source into beautiful soup
    soup = BeautifulSoup(data, 'html.parser')

    # Finds each product from the store page
    a_tags = soup.find_all("a", {"class" : "card product"})

    # Get hyperlink from each product
    href_products = [a.get('href') for a in a_tags]

    # Loop through each products' link and extract info
    for href_prod in href_products:
        
        # Get product link
        product_link = 'https://www.japancentre.com' + href_prod

        # Start the WebDriver
        driver = webdriver.Chrome(service=service)

        # Load the webpage
        driver.get(product_link)

        try:
            # Wait for webpage to load
            time.sleep(2)

            # Wait until an element with class 'container1' is present if wait time above not sufficient
            WebDriverWait(driver, 5).until(
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

# Get today's date
current_date = datetime.datetime.today().strftime('%Y_%m_%d')

# Save all scraped data
with open('0_webscrape_data/data/instant_noodles_'+ str(current_date) +'.csv', 'w', newline='') as csvfile:
    writer = csv.writer(csvfile)
    writer.writerows(data_output)

print(str(len(data_output) - 1) + ' rows of data scraped and saved.' )

# Save failed urls as csv
if(len(failed) > 1):
    with open('0_webscrape_data/data/failed_urls_'+ str(current_date) + '.csv', 'w', newline='') as csvfile:
        writer_fail = csv.writer(csvfile)
        writer_fail.writerows(failed)
    print(str(len(failed) - 1) + ' rows of data failed to be scraped.' )

# Save end time
end = time.time()

# Get time difference
time_diff = float(end-start)

if time_diff // 60 == 0:
    time_diff_str = str(time_diff) + ' sec'
else:
    time_diff_str = str(time_diff / 60) + ' min'

print('Code took ' + time_diff_str + ' to run.')

