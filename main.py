import os
import pandas as pd 
import time
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.action_chains import ActionChains


try:
    # Attempt to initialize driver without specifying a path
    options = Options()
    driver = webdriver.Chrome(options=options)
    print("Driver initialized successfully without specifying a path.")

except Exception as e:
    # Manually passing the driver path to detect the chrome driver.
    print(f"Failed to initialize driver without path: {str(e)}")

    load_dotenv()
    driver_path = os.getenv('driver_path')

    service = Service(executable_path = driver_path)
    driver = webdriver.Chrome(service = service)
    print("Driver initialized successfully with specifying the path.")

# Define output file path
output_file_path = f'./projects.csv'        

# list of the details to be scraped.
fetch_details = ['RERA Regd. No.','Project Name', 'Company Name', 'Registered Office Address', 'GST No.', 'Propietory Name', 'Current Residence Address'] 

# Read URL from file
file = open("./urls.txt", encoding= 'utf-8')
url = file.readline()

driver.get(url)

# list to store all project details
project_details = []
scrap_projects = 6

#Process 6 projects 
for i in range(scrap_projects):
    # dict to store project details
    details = {}

    try:
        #Wait for the intial page to load.
        time.sleep(2)

        project_cards = driver.find_elements(By.CSS_SELECTOR, '[class="card project-card mb-3"]')

        if i >= len(project_cards):
            print(f"Project card {i} not found. Skipping.")
            continue

        button = project_cards[i].find_element(By.CSS_SELECTOR, '[class="btn btn-primary"]')

        # Scroll to get the "View Details" button to the viewport and than click
        actions = ActionChains(driver)
        actions.move_to_element(button).click().perform()

        # Wait for the view details page to load
        time.sleep(4)
        temp = driver.find_element(By.CSS_SELECTOR, '[class="card-body"]')

        # Extract project details.
        project_divs = temp.find_elements(By.CSS_SELECTOR, '[class="details-project ms-3"]')
        
        for project_div in project_divs:

            label = project_div.find_element(By.CSS_SELECTOR, '[class = "label-control"]')

            if label.text in fetch_details:
                strong = project_div.find_element(By.TAG_NAME, "strong")
                details[label.text] = strong.text

        # Navigate to Promoter tab
        li = driver.find_element(By.ID, 'mainContent').find_element(By.TAG_NAME, 'ul').find_elements(By.TAG_NAME, 'li')
        promoter_tab = li[1].find_element(By.TAG_NAME, "a")
        promoter_tab.click()

        # Wait for promoter details to load
        time.sleep(2)
        temp = driver.find_element(By.CSS_SELECTOR, '[class="card-body"]')

        # Extract promoter details
        promoter_divs = temp.find_elements(By.CSS_SELECTOR, '[class="ms-3"]')
        
        for promoter_div in promoter_divs:

            label = promoter_div.find_element(By.CSS_SELECTOR, '[class = "label-control"]')

            if label.text in fetch_details:
                label_text = label.text
                strong = promoter_div.find_element(By.TAG_NAME, "strong")

                if label_text == 'Company Name' or label_text == 'Propietory Name':
                    label_text = 'Promoter Name'

                if label_text == 'Registered Office Address' or label_text == 'Current Residence Address':
                    label_text = 'Address of the Promoter'

                details[label_text] = strong.text
        
        project_details.append(details)
        print(f"Processed project {i+1}/{scrap_projects}")

        # Navigate back to the base URL
        driver.back()

    except Exception as e:
        print(f"Error processing project {i+1}: {str(e)}")
        driver.back()
        continue

# Close the driver
driver.close()


# Saving the project details to a csv file.
if project_details:
    output_df = pd.DataFrame(project_details)

    if os.path.exists(output_file_path):
        # Append to existing file without headers
        output_df.to_csv(output_file_path, mode='a', index=False, header=False)
    else:
        # Create new file with headers
        output_df.to_csv(output_file_path, mode='w', index=False, header=True)
    print(f"Data saved to {output_file_path}")
else:
    print("No data to save.")