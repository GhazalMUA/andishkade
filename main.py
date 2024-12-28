from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

def setup_driver():
    options = Options()
    # options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    return webdriver.Chrome(options=options)

def scrape_brookings():
    
    print("Starting scraping for brookings.edu...")
    driver = setup_driver()

    # Open the target website
    driver.get("https://www.brookings.edu/?s=iraq")
    time.sleep(2)
    while True:
        try:
            # Attempt to locate the "Last Year" button
            last_year_filter_button = WebDriverWait(driver, 2).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, 'input[value="%7B%22start%22:1703828932,%22end%22:1735364932%7D"]'))
            )
            last_year_filter_button.click()
            print("Clicked 'Last Year' button successfully!")
            break  # Exit loop after clicking the button
        except Exception:
            # Scroll down if the button is not yet visible
            driver.execute_script("window.scrollBy(0, 500);")  # Scroll by 500px
            time.sleep(1)  # Pause to allow the page to adjust
    
    # # Wait until the page loads and find the desired element (e.g., headlines)
    # last_year_filter_button = WebDriverWait(driver, 10).until(
    #     EC.element_to_be_clickable((By.CSS_SELECTOR, 'input[value="%7B%22start%22:1703828932,%22end%22:1735364932%7D"]'))
    # )
    # last_year_filter_button.click()
    # print("Clicked 'Last Year' button successfully!")
    
    # Wait for the articles
    WebDriverWait(driver, 10).until(
    EC.presence_of_element_located((By.CSS_SELECTOR, ".articles-stream"))
    )
        
    # Scroll, click "Show More", and wait for new results
    while True:
        try:
            # Scroll to the bottom of the page
            driver.execute_script("window.scrollTo(0, 1000;")
            time.sleep(1)  # Wait for the page to adjust
            
            # Check for the "Show More" button
            show_more_button = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.XPATH, '//*[@id="algolia-hits"]/div/button/div'))
            )
            show_more_button.click()  # Click the button
            print('i clicked on show more')
            time.sleep(2)  # Wait for new articles to load
        except Exception:
            # Break the loop if the "Show More" button is no longer available
            print("No more 'Show More' button or all articles loaded.")
            break
        
    # Extracting articles    
    articles = driver.find_elements(By.CSS_SELECTOR, ".articles-stream a.overlay-link")
    article_data = []
    
    #extracting title and url of each article
    for article in articles:
        title_element = article.find_element(By.CSS_SELECTOR, "span.sr-only")
        title = title_element.text  # Get the text of the title
        link = article.get_attribute("href")  # Get the link
        if title and link:
            article_data.append({"title": title, "link": link})

    print(f"Total articles collected: {len(article_data)}")
    driver.quit()

# Run the scraper
scrape_brookings()
