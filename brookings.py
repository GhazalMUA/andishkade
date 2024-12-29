from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import csv

'''
this site will opens by germany vpn
'''
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
            last_year_filter_button = driver.find_element(By.XPATH, '//*[@id="facet-dates"]/label[3]/input')
            driver.execute_script("arguments[0].scrollIntoView(true);", last_year_filter_button)  # Scroll to the button
            WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="facet-dates"]/label[3]/input')))
            last_year_filter_button.click()
            print("Clicked 'Last Year' button successfully!")
            break
        except Exception:
            # Scroll down if the button is not yet visible
            driver.execute_script("window.scrollBy(0, 500);")  # Scroll by 500px
            time.sleep(1)  # Pause to allow the page to adjust
            
    # Wait for the articles container to load
    WebDriverWait(driver, 10).until(
    EC.presence_of_element_located((By.CSS_SELECTOR, ".articles-stream"))
    )
        
    # Scroll, click "Show More", and wait for new results
    while True:
        try:
            # Scroll to ensure the button is in view
            show_more_button = WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.XPATH, '/html/body/div[2]/main/section/div[2]/div/div[6]/div/div/div[2]/div[2]/div[2]/div/div/button/div/div'))
            )
            driver.execute_script("arguments[0].scrollIntoView(true);", show_more_button)  # Scroll to the button
            WebDriverWait(driver, 2).until(EC.element_to_be_clickable((By.XPATH, '/html/body/div[2]/main/section/div[2]/div/div[6]/div/div/div[2]/div[2]/div[2]/div/div/button/div/div')))
            show_more_button.click()  # Click the button
            print("Clicked 'Show More' button.")
            time.sleep(3)  # Wait for new content to load
        except Exception:
            print("No more 'Show More' button or all articles loaded.")
            break
        
    # Extracting articles    
    articles = driver.find_elements(By.CSS_SELECTOR, ".articles-stream a.overlay-link")
    print('i see all articles')
    article_data = []
    
    #extracting title and url of each article
    for article in articles:
        title_element = article.find_element(By.CSS_SELECTOR, "span.sr-only")
        title = title_element.text  # Get the text of the title
        link = article.get_attribute("href")  # Get the link
        if title and link:
            article_data.append({"title": title, "link": link})

    print(f"Total articles collected: {len(article_data)}")


    # Visit each article link and collect details
    for item in article_data:
        driver.get(item["link"])
        time.sleep(2)  # Adjust based on the page load time
        
    # Check if the current URL contains '/events/' (event articles are not proper for scraping)
        current_url = driver.current_url
        if '/articles/' not in current_url:
            print(f"Skipped non-article link: {current_url}")
            article_data.remove(item)  # Remove skipped links from the list
            continue  # Skip to the next article

        try:
            # Extract Content
            content = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "div.byo-block.-narrow.wysiwyg-block.wysiwyg"))
            ).text
            item["content"] = content
            
            # Publish Date
            publication_date = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "p.text-medium"))
            ).text
            item["publication_date"] = publication_date
            
            # Extract Author/Authors
            author_elements = driver.find_elements(By.CSS_SELECTOR, "a.h5.person-hover")
            authors = [author.text for author in author_elements]  # Get the text of each author
            item["authors"] = ", ".join(authors)  # Join multiple authors with commas

            main_type = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR,"p.label-large"))
            ).text
            
            # Extract additional tags (e.g., Podcast, Testimony)
            additional_tags_elements = driver.find_elements(By.CSS_SELECTOR, ".tm-tag")
            additional_tags = [tag.text for tag in additional_tags_elements]

            # Combine the main type with additional tags
            type_article = main_type
            if additional_tags:
                type_article += " + " + " + ".join(additional_tags)

            item["type"] = type_article
            item["resource"] = 'BROOKINGS'
            item["resource_location"] = "Washington, D.C"

        except Exception as e:
            print(f"Failed to extract details for {current_url}: {e}")
            item["content"] = None
            item["publication_date"] = None
            item["authors"] = None
            item["link"] = item.get("link", None)
            item["type"] = None

    
    # Save to CSV
    save_to_csv(article_data)

    driver.quit()
    
def save_to_csv(data):
    # Define CSV file name
    csv_file = "brookings_articles.csv"
    for i, item in enumerate(data, start=1):
        item["id"] = i
    # Specify the header
    fieldnames = ["id", "title", "link", "authors", "publication_date", "resource", "resource_location", "type", "content",]

    # Write data to CSV
    with open(csv_file, mode="w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()  # Write the header
        writer.writerows(data)  # Write the rows

    print(f"Data successfully saved to {csv_file}")


# Run the scraper
scrape_brookings()
