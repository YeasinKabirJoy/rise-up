import os
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, WebDriverException
from selenium.webdriver import Keys
import pandas as pd
import re
import json
from xpath_inventory import xpath
import pprint

def load_config(file_path='config.json'):
    try:
        # Load the JSON file
        with open(file_path, 'r') as file:
            config = json.load(file)
        
        
        required_top_level = ['working_directory', 'paths', 'parameters']
        required_paths = ['image', 'csv']
        required_parameters = ['timeout', 'target_url']
        
        for key in required_top_level:
            if key not in config:
                print(f"Error: Missing required top-level key '{key}' in {file_path}")
                return None
        
       
        if not isinstance(config['paths'], dict):
            print(f"Error: 'paths' must be a dictionary in {file_path}")
            return None
        for key in required_paths:
            if key not in config['paths']:
                print(f"Error: Missing required key 'paths.{key}' in {file_path}")
                return None
        
        if not isinstance(config['parameters'], dict):
            print(f"Error: 'parameters' must be a dictionary in {file_path}")
            return None
        for key in required_parameters:
            if key not in config['parameters']:
                print(f"Error: Missing required key 'parameters.{key}' in {file_path}")
                return None
        
        if not isinstance(config['working_directory'], str):
            print(f"Error: 'working_directory' must be a string in {file_path}")
            return None
        if not isinstance(config['parameters']['timeout'], (int, float)):
            print(f"Error: 'parameters.timeout' must be a number in {file_path}")
            return None
        if not isinstance(config['parameters']['target_url'], str):
            print(f"Error: 'parameters.target_url' must be a string in {file_path}")
            return None
        
        return config
    
    except FileNotFoundError:
        print(f"Error: File {file_path} not found")
        return None
    except json.JSONDecodeError:
        print(f"Error: Invalid JSON format in {file_path}")
        return None


def find_element(driver,selector_type, selector,timeout):

    max_retries=2
    attempt = 1
    while attempt <= max_retries:
        try:
            # Initialize WebDriverWait with the timeout from config
            wait = WebDriverWait(driver, timeout)
            
            # Wait until all elements are visible
            elements = wait.until(EC.visibility_of_element_located((selector_type, selector)))
            
            print(f"Successfully found elementm on attempt {attempt}")
            return elements
        
        except TimeoutException:
            print(f"Attempt {attempt} failed: Timeout - Elements with not visible within {timeout} seconds")
        except NoSuchElementException:
            print(f"Attempt {attempt} failed: No elements found")
        except WebDriverException as e:
            print(f"Attempt {attempt} failed: WebDriver error - {str(e)}")
        except Exception as e:
            print(f"Attempt {attempt} failed: Unexpected error - {str(e)}")
        
        # Increment attempt counter
        attempt += 1
        if attempt <= max_retries:
            print(f"Retrying... ({attempt}/{max_retries})")
            time.sleep(1)  # Brief pause before retrying to avoid overwhelming the server
    
    print(f"All {max_retries} attempts failed")
    return None

def extract_discount(discount_text):

    pattern = r'^(\d+\.?\d*)\s*(%?).*$'
    match = re.search(pattern, discount_text, re.IGNORECASE)
    
    if match:
        value = match.group(1)  
        percent = match.group(2)  
        return f"{value}{percent}"  
    return None 


class Extraction:
    def __init__(self,driver,config):
        self.config = config
        self.driver = driver
        self.timeout = self.config['parameters']['timeout']

    def load_target(self):

        driver = self.driver
        target = self.config['parameters']['target_url']
        print(f"Loading target: {target}")

        try:
            driver.get(target)
            WebDriverWait(driver, 20).until(
                lambda driver: driver.execute_script("return document.readyState") == "complete"
            )
    
        except TimeoutException:
            print("Error: Page did not fully load within 20 seconds")
        except WebDriverException as e:
            print(f"Error: Failed to load the page - {str(e)}")
        except Exception as e:
            print(f"Unexpected error: {str(e)}")

    def get_product_links(self):
        
        links = []
        print("Finding product links")
        product_row = find_element(self.driver,By.XPATH,xpath["product_row"],self.timeout)
        link_tag = product_row.find_elements(By.CLASS_NAME,'p-img-container')
        for link in link_tag:
            links.append(link.get_attribute('href'))
        

        pagination_ul = find_element(self.driver,By.XPATH,xpath["pagination"],self.timeout)
        pages = pagination_ul.find_elements(By.TAG_NAME,'li')

        for i in range(2,len(pages)-1):
            print(f"Going to page: {i}")
            pages[i].click()
            time.sleep(5)
            product_row = find_element(self.driver,By.XPATH,xpath["product_row"],self.timeout)
            link_tag = product_row.find_elements(By.CLASS_NAME,'p-img-container')
            for link in link_tag:
                links.append(link.get_attribute('href'))

        return links
    
    def get_product_details(self,link):
        print(f"Extracting from: {link}")

        _ = {}
        image_link = []
        self.driver.get(link)
        WebDriverWait(driver, 10).until(
            lambda driver: driver.execute_script("return document.readyState") == "complete"
        )

        print("Finding image links")
        image_div = find_element(self.driver,By.XPATH,xpath["product_image_galary"],self.timeout)
        image_link_tag = image_div.find_elements(By.TAG_NAME,'img')

        for link_tag in image_link_tag:
            image_link.append(link_tag.get_attribute('src'))


        print("Finding shoe name")
        shoe_name_h1 = find_element(self.driver,By.XPATH,xpath["shoe_name"],self.timeout)
        if shoe_name_h1:
            shoe_name = shoe_name_h1.text
        else:
            shoe_name = ''
            print("Shoe name not found")


        print("Finding shoe id")
        shoe_id_p = find_element(self.driver,By.XPATH,xpath["shoe_id"],self.timeout)
        if shoe_id_p:
            shoe_id = shoe_id_p.text
        else:
            shoe_name = ''
            print("Shoe id not found")

        print("Finding price")
        price_div = find_element(self.driver,By.XPATH,xpath["price"],self.timeout)
        if price_div:
            price = price_div.text.strip("BDT ")
        else:
            price = ''
            print("Price not found")
        
        print("Finding Discount")
        discount_span = find_element(self.driver,By.XPATH,xpath["discount"],self.timeout)
        if discount_span:
            discount = extract_discount(discount_span.text)
            if discount is None:
                discount = ''
                print("Invalid discount format")
        else:
            discount = ''
            print("Discount not found")
        

        print("Finding color code")
        color_code_span = find_element(self.driver,By.XPATH,xpath["color_code"],self.timeout)
        if color_code_span:
            color_code = color_code_span.text
        else:
            color_code = ''
            print("Color code not found")
        

        _['shoe_name'] = shoe_name
        _['shoe_id'] = shoe_id
        _['price'] =  price
        _['discount'] = discount
        _['color_code'] = color_code

        for i in range(0,len(image_link)):
            _[f'image{i+1}'] = image_link[i]
            if i==4:
                break

        return _

if __name__ == '__main__':

    data = []
    data_for_excel = []

    config = load_config()
    if config is None:
        exit(1)

    
    driver = webdriver.Chrome()
    try:
        excration = Extraction(driver,config)
        excration.load_target()
        links = excration.get_product_links()
        for link in links:
            data.append(excration.get_product_details(link))
        pprint.pprint(data)
    except Exception as e:
        print(f'Error: {str(e)}')
    finally:
        driver.quit()