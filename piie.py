# from selenium import webdriver
# from selenium.webdriver.chrome.options import Options
# from selenium.webdriver.common.by import By
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC
# import time
# import csv
# import re
# import random
'''
 bedone vpn
'''

# def setup_driver():
#     options = Options()
#     # options.add_argument("--headless")
#     options.add_argument("--disable-gpu")
#     options.add_argument("--no-sandbox")
#     options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36")
#     options.add_argument("accept-language=en-US,en;q=0.9")

#     return webdriver.Chrome(options=options)

# def scrape_piie():
#     base_url = "https://www.piie.com"  # Replace with the actual base URL of the website
#     start_url = "https://www.piie.com/search?search_api_fulltext=iraq&f%5B0%5D=date%3A2024"  # Replace with the actual search URL


#     print("Starting scraping from piie.com ...")
#     driver = setup_driver()
#     driver.get(start_url)
#     time.sleep(random.uniform(11, 15))
#     # Locate the list of articles
    
#     print('i scrolled.')
#     article_list = driver.find_elements(By.CSS_SELECTOR, "div.content-list-results__list div.view__row")
#     # driver.execute_script("arguments[0].scrollIntoView(true);", article_list)
#     print('I found article list')
#     article_data = []

#     # Extract links from each article
#     for article in article_list:
#         try:
#             link_element = article.find_element(By.CSS_SELECTOR, "h2.image-teaser__title div.field__item a")
#             link = link_element.get_attribute("href")
#             full_link = base_url + link if link.startswith("/") else link
#             title = link_element.text
#             article_data.append({"title": title, "link": full_link})
#         except Exception as e:
#             print(f"Error extracting article link: {e}")

#     print(f"Total articles collected: {len(article_data)}")

#     # Visit each article link and collect details
#     for item in article_data:
#         driver.get(item["link"])
#         time.sleep(random.uniform(11, 16))        
#         print(item["link"])

#         try:
            
#             # Extract content
#             content_element = WebDriverWait(driver, 20).until(
#                 EC.presence_of_element_located((By.CSS_SELECTOR, ".field.field--name-body.field--type-text-with-summary.field--label-visually_hidden"))
#             ).text
#             content = content_element.strip()
#             item["content"] = content

#             # Extract publication date
#             time_element = WebDriverWait(driver, 20).until(
#                 EC.presence_of_element_located((By.CSS_SELECTOR, ".hero-banner-publication__date .field__item time"))
#             )
#             publication_date = time_element.get_attribute("datetime")  
#             item["publication_date"] = publication_date

    
#             #Extract author
#             author_elements = driver.find_elements(By.CSS_SELECTOR, ".author-list .author-list__author")
#             authors = [author.text.strip() for author in author_elements]
#             item["authors"] = ", ".join(authors) if authors else "Unknown"
            

#             # Extract type of the article using regex
#             type_match = re.search(r"https://www\.piie\.com/([^/]+)", item["link"])
#             item["type"] = type_match.group(1) if type_match else "Unknown"


#             # Add additional metadata
#             item["resource"] = "PIIE"
#             item["resource_location"] = "Washington, D.C"
#             item["link"] = full_link
            
#         except Exception as e:
#             print(f"Failed to extract details for {item['link']}: {e}")
#             with open("failed_page.html", "w", encoding="utf-8") as file:
#                 file.write(driver.page_source)
#             item["content"] = None
#             item["publication_date"] = None
#             item["authors"] = None
#             item["link"] = None
#             item["type"] = None

#     # Save to CSV
#     save_to_csv(article_data)
#     driver.quit()

# def save_to_csv(data):
#     csv_file = "piie_articles.csv"
#     fieldnames = ["title", "type", "link", "authors", "publication_date", "resource", "resource_location", "content"]

#     with open(csv_file, mode="w", newline="", encoding="utf-8") as file:
#         writer = csv.DictWriter(file, fieldnames=fieldnames)
#         writer.writeheader()
#         writer.writerows(data)

#     print(f"Data successfully saved to {csv_file}")

# # Run the scraper
# scrape_piie()
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import csv

def setup_driver():
    options = Options()
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36")
    options.add_argument("accept-language=en-US,en;q=0.9")
    return webdriver.Chrome(options=options)

def scrape_piie():
    base_url = "https://www.piie.com"
    start_url = "https://www.piie.com/search?search_api_fulltext=iraq&f%5B0%5D=date%3A2024"

    print("Starting scraping from piie.com ...")
    driver = setup_driver()
    driver.get(start_url)
    time.sleep(10)  # Wait for the page to load

    # Locate all article links
    article_links = driver.find_elements(By.CSS_SELECTOR, "div.content-list-results__list div.view__row h2.image-teaser__title div.field__item a")
    total_links = len(article_links)
    print(f"Total articles found: {total_links}")

    article_data = []

    for i in range(total_links):
        try:
            print(f"Processing article {i + 1} of {total_links}...")

            # Refresh the link list on each loop iteration
            article_links = driver.find_elements(By.CSS_SELECTOR, "div.content-list-results__list div.view__row h2.image-teaser__title div.field__item a")
            article_links[i].click()

            # Debug: Check current URL
            print(f"Navigated to: {driver.current_url}")

            # Wait for the article title to appear
            WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "h1.hero-banner-publication__title"))
            )

            # Scrape article details
            title = driver.find_element(By.CSS_SELECTOR, "h1.hero-banner-publication__title").text.strip()
            content_element = driver.find_element(By.CSS_SELECTOR, "div.field.field--name-body.field--type-text-with-summary.field--label-visually_hidden")
            content = content_element.text.strip()
            publication_date_element = driver.find_element(By.CSS_SELECTOR, "div.hero-banner-publication__date .field__item time")
            publication_date = publication_date_element.get_attribute("datetime")
            author_elements = driver.find_elements(By.CSS_SELECTOR, "div.hero-banner-publication__authors .author-list__author")
            authors = ", ".join([author.text.strip() for author in author_elements]) if author_elements else "Unknown"
            blog_section = driver.find_element(By.CSS_SELECTOR, "div.hero-banner-publication__type .field__item a").text.strip()

            article_data.append({
                "title": title,
                "content": content,
                "publication_date": publication_date,
                "authors": authors,
                "blog_section": blog_section,
                "resource": "PIIE",
                "resource_location": "Washington, D.C",
                "link": driver.current_url,
            })
            print(f"Article '{title}' scraped successfully.")

        except Exception as e:
            print(f"Error processing article {i + 1}: {e}")
            # Debug: Save page source for troubleshooting
            with open(f"debug_page_{i + 1}.html", "w", encoding="utf-8") as f:
                f.write(driver.page_source)
        finally:
            driver.back()  # Go back to the original search page
            time.sleep(10)  # Wait for the page to load again

    # Save results to a CSV file
    save_to_csv(article_data)
    driver.quit()

def save_to_csv(data):
    csv_file = "piie_articles_updated.csv"
    fieldnames = ["title", "content", "publication_date", "authors", "blog_section", "resource", "resource_location", "link"]

    with open(csv_file, mode="w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(data)

    print(f"Data successfully saved to {csv_file}")

# Run the scraper
scrape_piie()
