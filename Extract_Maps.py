from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, WebDriverException
import undetected_chromedriver as uc
import time
import csv
import pandas as pd
import re

def extract_phone_number(driver, wait):
    phone_xpaths = [
        # Try different potential phone number locations
        "//div[contains(@class, 'fontBodyMedium') and contains(text(), '0')]",
        "//div[contains(@class, 'Io6YTe') and contains(text(), '0')]",
        "//div[contains(@class, 'fontBodyMedium kR99db')]",
        "//div[contains(@class, 'rogA2c')]//div[contains(@class, 'Io6YTe')]"
    ]
    
    for xpath in phone_xpaths:
        try:
            # Try to find the element
            phone_elements = driver.find_elements(By.XPATH, xpath)
            
            for element in phone_elements:
                # Extract text
                phone_text = element.text.strip()
                
                # Use regex to extract phone number
                phone_match = re.findall(r'\d{3,}[-\s]?\d{3,}[-\s]?\d{3,}', phone_text)
                
                if phone_match:
                    # Return the first matched phone number
                    return phone_match[0].replace(' ', '').replace('-', '')
        
        except Exception as e:
            print(f"Error searching for phone number: {str(e)}")
    
    return "Phone Number Not Found"

def scrape_data(url, driver, wait):
    try:
        # Navigate to the URL
        driver.get(url)
        time.sleep(3)  # Give some time for the page to load
        
        # Initialize variables with default values
        address = website = phone = "Not Found"
        
        try:
            # Address extraction
            address_element = wait.until(EC.presence_of_element_located(
                (By.XPATH, "//div[contains(@class,'rogA2c')]/div[contains(@class,'Io6YTe')]")
            ))
            address = address_element.text
        except (TimeoutException, NoSuchElementException):
            pass

        try:
            # Website extraction
            website_element = wait.until(EC.presence_of_element_located(
                (By.XPATH, "//a[contains(@aria-label, 'Website')]")
            ))
            website = website_element.get_attribute("href")
        except (TimeoutException, NoSuchElementException):
            pass

        # Phone number extraction
        phone = extract_phone_number(driver, wait)

        return {
            'URL': url,
            'Address': address,
            'Website': website,
            'Phone': phone
        }
    except WebDriverException as e:
        print(f"Error processing URL {url}: {str(e)}")
        return {
            'URL': url,
            'Address': 'Error',
            'Website': 'Error',
            'Phone': 'Error'
        }

def main():
    # Read URLs from CSV file
    try:
        df = pd.read_csv('google_maps_data_alt.csv')  # Replace 'input.csv' with your CSV file name
        urls = df['URL'].tolist()  # Assuming 'URL' is the column name
    except Exception as e:
        print(f"Error reading CSV file: {str(e)}")
        return

    # Initialize the driver
    driver = uc.Chrome()
    wait = WebDriverWait(driver, 10)
    
    # List to store results
    results = []

    try:
        # Process each URL
        for url in urls:
            print(f"Processing URL: {url}")
            result = scrape_data(url, driver, wait)
            results.append(result)
            time.sleep(2)  # Add delay between requests
    
    except Exception as e:
        print(f"An error occurred: {str(e)}")
    
    finally:
        # Close the driver
        driver.quit()
        
        # Save results to CSV
        try:
            df_results = pd.DataFrame(results)
            df_results.to_csv('output.csv', index=False)
            print("Results saved to output.csv")
        except Exception as e:
            print(f"Error saving results: {str(e)}")

if __name__ == "__main__":
    main()