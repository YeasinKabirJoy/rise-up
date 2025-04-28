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

def load_config(file_path='config.json'):
    try:
        # Load the JSON file
        with open(file_path, 'r') as file:
            config = json.load(file)
        
        
        required_top_level = ['working_directory', 'paths', 'parameters']
        required_paths = ['images', 'csv']
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
            
            print(f"Successfully found elements with {selector_type.__name__}: {selector} on attempt {attempt}")
            return elements
        
        except TimeoutException:
            print(f"Attempt {attempt} failed: Timeout - Elements with {selector_type.__name__} '{selector}' not visible within {timeout} seconds")
        except NoSuchElementException:
            print(f"Attempt {attempt} failed: No elements found with {selector_type.__name__} '{selector}'")
        except WebDriverException as e:
            print(f"Attempt {attempt} failed: WebDriver error - {str(e)}")
        except Exception as e:
            print(f"Attempt {attempt} failed: Unexpected error - {str(e)}")
        
        # Increment attempt counter
        attempt += 1
        if attempt <= max_retries:
            print(f"Retrying... ({attempt}/{max_retries})")
            time.sleep(1)  # Brief pause before retrying to avoid overwhelming the server
    
    print(f"All {max_retries} attempts failed for {selector_type.__name__}: {selector}")
    return None


    