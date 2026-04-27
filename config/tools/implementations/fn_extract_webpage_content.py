import requests
from bs4 import BeautifulSoup

def fn_extract_webpage_content(url: str) -> str:
    """
    Downloads and extracts the main text body from a provided URL, 
    stripping away HTML tags, scripts, and navigation elements.
    """
    try:
        # Provide a User-Agent header to prevent basic anti-bot blocks
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }

        # Fetch the webpage content
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status() # Raise an exception for bad status codes (e.g., 404, 500)

        # Parse the HTML using BeautifulSoup
        soup = BeautifulSoup(response.text, "html.parser")

        # Remove noisy elements like scripts, styles, navigation, headers, and footers
        for noisy_element in soup(["script", "style", "nav", "header", "footer", "aside"]):
            noisy_element.decompose()

        # Extract the remaining text, using spaces to separate elements
        text = soup.get_text(separator=" ")

        # Clean up excessive whitespace and blank lines
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        cleaned_text = "\n".join(chunk for chunk in chunks if chunk)

        return cleaned_text

    except requests.exceptions.RequestException as e:
        return f"Network error occurred while fetching the URL: {e}"
    except Exception as e:
        return f"An unexpected error occurred during extraction: {e}"
