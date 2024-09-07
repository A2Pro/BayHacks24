import requests
from bs4 import BeautifulSoup
import json
def geturls(main):
    link = f'https://www.mayoclinic.org/diseases-conditions/search-results?q={main}'
    r = requests.get(link)
    soup = BeautifulSoup(r.text, 'html.parser')

    # Extract JSON data from the script tag
    json_data = soup.find('script', type='application/json')
    if json_data:
        data = json.loads(json_data.string)
    else:
        return []

    urls = []

    def extract_urls_from_dict(d):
        if isinstance(d, dict):
            for key, value in d.items():
                if isinstance(value, str) and value.startswith('http'):
                    urls.append(value)
                elif isinstance(value, (dict, list)):
                    extract_urls_from_dict(value)
        elif isinstance(d, list):
            for item in d:
                extract_urls_from_dict(item)

    extract_urls_from_dict(data)

    # Filter and deduplicate URLs
    realurls = {url for url in urls if "diseases-conditions" in url and "symptoms-causes" in url}

    return list(realurls)