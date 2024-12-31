import csv
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime
import time
import re
def setup_driver():
    options = Options()
    # options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    return webdriver.Chrome(options=options)

def scrape_csis():
    start_url = 'https://www.csis.org/search?keyword=iraq&archive=0&sort_by=date'
    print("Starting scraping for csis.org ...")
    driver = setup_driver()

    links = []
    current_year = datetime.now().year

    # Start pagination
    page_number = 0
    while True:
        current_url = f"{start_url}&page={page_number}"
        print(f"Processing page: {current_url}")
        driver.get(current_url)

        try:
            # Wait for articles to load
            WebDriverWait(driver, 20).until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, "article.article-search-listing"))
            )
            articles = driver.find_elements(By.CSS_SELECTOR, "article.article-search-listing")
            print(f"Found {len(articles)} articles on this page.")

            if not articles:
                print(f"No articles found on page {page_number}. Stopping.")
                break

            for article in articles:
                try:
                    # Extract the link
                    driver.execute_script("arguments[0].scrollIntoView();", article)
                    link_element = article.find_element(By.CSS_SELECTOR, "h3 a")
                    link = link_element.get_attribute("href")
                    # Extract the date
                    date_element = article.find_element(By.CSS_SELECTOR, ".contributors span.inline-block")
                    date_text = date_element.text.strip("— ").strip()
                    # Parse the date
                    article_date = datetime.strptime(date_text, "%B %d, %Y")
                    title = link_element.text

                    # Check if the date is in the current year
                    if article_date.year == current_year:
                        links.append({"link": link, "publication_date": date_text, "title": "title"})
                    else:
                        # Stop scraping if the date condition is not met
                        print(f"Article date {article_date} does not meet the condition. Stopping.")
                        driver.quit()
                        print("Scraping complete.")
                        return links
                except ValueError as ve:
                    print(f"Date parsing error for: {date_text}. Error: {ve}")
                    continue
                except Exception as e:
                    print(f"Error processing an article: {e}")

        except Exception as e:
            print(f"Error processing page {current_url}: {e}")
            break

        # Go to the next page
        page_number += 1
        time.sleep(1)  # Allow time for the next page to load

    driver.quit()
    print("Scraping complete.")
    return links

def extract_article_data(driver, link_data):
    link = link_data["link"]
    publication_date = link_data["publication_date"]
    title = link_data["title"]
    driver.get(link)
    data = {
        "id": None,  # Will be added later when saving to CSV
        "title": title ,
        "link": link,
        "authors": None,
        "publication_date": publication_date,
        "resource": "CSIS",
        "resource_location": "Washington D.C.",
        "type": None,
        "content": None,
    }

    try:

        # Extract authors
        try:
            author_element = driver.find_element(By.CSS_SELECTOR,".contributors .contributor-list")
            data["authors"] = author_element.text.strip()
        except Exception:
            data["authors"] = "Unknown"

        # Extract type
        try:
            type_match = re.search(r"https://www\.csis\.org/([^/]+)", data["link"])
            data["type"] = type_match.group(1) if type_match else "Unknown"
        except Exception:
            data["type"] = "Unknown"

        # Extract content
        try:
            content_elements = driver.find_elements(By.CSS_SELECTOR, ".wysiwyg-wrapper.text-high-contrast")
            content = " ".join([element.text for element in content_elements])
            data["content"] = content if content.strip() else "Content not available"
        except Exception as e:
            data["content"] = "Content extraction error"
    except Exception as e:
        print(f"Error extracting data from {link}: {e}")

    return data

def save_to_csv(data, filename="csis_articles.csv"):
    fieldnames = [
        "id", "title", "link", "authors", "publication_date",
        "resource", "resource_location", "type", "content"
    ]
    with open(filename, mode="w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        for i, row in enumerate(data, 1):
            row["id"] = i
            writer.writerow(row)

if __name__ == "__main__":
    # Step 1: Scrape article links and dates
    links_data = scrape_csis()

    # Step 2: Extract data from each article
    driver = setup_driver()
    articles_data = []
    for link_data in links_data:
        article_data = extract_article_data(driver, link_data)
        articles_data.append(article_data)

    driver.quit()

    # Step 3: Save data to CSV
    save_to_csv(articles_data)
    print("Data saved to articles.csv")
