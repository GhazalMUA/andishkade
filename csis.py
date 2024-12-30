from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime
import time

def setup_driver():
    options = Options()
    options.add_argument("--headless")
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

                    # Check if the date is in the current year
                    if article_date.year == current_year:
                        links.append(link)
                    else:
                        # Stop scraping if the date condition is not met
                        print(f"Article date {article_date} does not meet the condition. Stopping.")
                        driver.quit()
                        print("Scraping complete.")
                        return list(links)
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
        time.sleep(5)  # Allow time for the next page to load

    driver.quit()
    print("Scraping complete.")
    return list(links)

# Run the script
if __name__ == "__main__":
    links = scrape_csis()
    print(f"Scraped {len(links)} unique links published this year:")
    for link in links:
        print(link)

