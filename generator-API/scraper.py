import requests
from bs4 import BeautifulSoup
from db_setup import ScrapedContent, session
from urllib.parse import urljoin, urlparse

# Define a set to keep track of visited URLs to avoid duplicate scraping
visited_urls = set()

def scrape_website(url, bot_id, depth=3, current_depth=0):
    """
    Recursively scrapes a website, follows internal links, and stores content in the database with bot_id.

    Parameters:
    url (str): The URL to scrape.
    bot_id (str): The identifier for the bot.
    depth (int): The maximum depth of recursion.
    current_depth (int): The current depth level.
    """
    if current_depth > depth:
        return  # Stop recursion if the maximum depth is reached

    if url in visited_urls:
        return  # Avoid revisiting URLs

    visited_urls.add(url)  # Mark the current URL as visited

    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')

        # Extract text content from the page
        text = ' '.join(soup.stripped_strings)

        # Store content to the database if not empty
        if text.strip():
            scraped_entry = ScrapedContent(url=url, content=text, bot_id=bot_id)
            session.add(scraped_entry)
            session.commit()
            print(f"Content from {url} stored successfully for bot_id {bot_id}.")

        # Recursively follow and scrape links within the page
        if current_depth < depth:
            for link in soup.find_all('a', href=True):
                absolute_url = urljoin(url, link['href'])
                if urlparse(absolute_url).netloc == urlparse(url).netloc:
                    scrape_website(absolute_url, bot_id, depth, current_depth + 1)

    except requests.exceptions.RequestException as e:
        print(f"Error scraping {url}: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")

# Example usage
if __name__ == "__main__":
    test_url = "https://docs.solace.com/Cloud/Event-Portal/event-portal-lp.htm"
    scrape_website(test_url, depth=3)
