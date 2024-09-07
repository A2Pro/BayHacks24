import requests
from bs4 import BeautifulSoup

def scrape_data(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36',
        'Accept-Language': 'en-US,en;q=0.9',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive'
    }

    try:
        r = requests.get(url, headers=headers)
        r.raise_for_status()  # Raises an HTTPError for bad responses (4xx and 5xx)
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
        return None, None

    with open("result.txt", "w", errors="ignore") as f:
        f.write(r.text)

    soup = BeautifulSoup(r.text, 'html.parser')
    [s.extract() for s in soup(['[document]'])]
    visible_text = str(soup.getText())

    title_tag = soup.title
    if title_tag:
        title = title_tag.string.strip()
    else:
        title = "N/A"
    
    return visible_text, title
