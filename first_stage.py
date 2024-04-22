from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime
from selenium.common.exceptions import TimeoutException
import time
import pandas as pd
from glob_functions import send_message


def browsing(urls_path):

    def extract_urls_from_string(input_string):
        output_urls = []

        for line in input_string.split('\n'):
            start_index = line.find(f'href="/opportunity/global-{product}/')
            while start_index != -1:
                start_index += len(f'href="/opportunity/global-{product}/')
                end_index = line.find('"', start_index)
                url = line[start_index:end_index]
                output_urls.append(f'https://aiesec.org/opportunity/global-{product}/{url}')
                start_index = line.find(f'href="/opportunity/global-{product}/', end_index + 1)
        return output_urls
    
    def load_more(driver):
        try:
            load_more_button = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, '//button[@class="ant-btn ant-btn-primary"]/span[text()="Load more"]')))
            load_more_button.click()
            time.sleep(5)
        except TimeoutException:
            raise

    chrome_options = webdriver.ChromeOptions()    
    ######

    chrome_options.add_argument('--headless')
    chrome_options.add_argument("start-maximized")
    chrome_options.add_argument("disable-infobars")
    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--no-sandbox")
    
    ######
    driver = webdriver.Chrome(options=chrome_options)
    current_date = datetime.now().strftime('%Y-%m-%d')
    x = 8
    product = "talent"

    url = f"https://aiesec.org/search?earliest_start_date={current_date}&programmes={x}"
    driver.get(url)


    try:
        cookie_accept_button = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '//button[@class="ant-btn ant-btn-primary ant-btn-block mb-[8px]"]/span[text()="Accept all cookies"]')))
        cookie_accept_button.click()
    except Exception as e:
        print(f"Error while accepting cookies: {e}")

    try:
        while True:
            load_more(driver)
    except TimeoutException:
        print("No more 'Load more' button found. Exiting...")


    html_content = driver.page_source
    output_urls = extract_urls_from_string(html_content)

    try:
        df = pd.read_csv(urls_path)
    except FileNotFoundError:
        df = pd.DataFrame(columns=['urls', 'status'])

    output_urls = extract_urls_from_string(html_content)
    new_urls = list(set(output_urls) - set(df['urls']))
    num_new_urls = len(new_urls)
    new_df = pd.DataFrame({'urls': new_urls, 'status': 'not_processed'})
    df = pd.concat([df, new_df], ignore_index=True)
    df.to_csv(urls_path, index=False)
    print("Stage 1 - Completed")
    driver.quit()
    send_message(f"We added {num_new_urls} to the database !")

