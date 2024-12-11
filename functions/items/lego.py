import requests
from bs4 import BeautifulSoup

def retrieve_info_url_lego(url):
    # Define headers to simulate a real browser request
    headers = {
        "accept-language": "en-US,en;q=0.9",
        "accept-encoding": "gzip, deflate, br",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36",
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7"
    }
    
    # Send GET request to the LEGO product URL
    resp = requests.get(url, headers=headers)
    soup = BeautifulSoup(resp.text, 'html.parser')

    # Initialize variables to store the product name and price
    item_name = None
    item_price = None

    item_name_max_length = 35

    try:
        # Extract item name (based on new HTML structure)
        item_name = soup.find('h1', {'data-test': 'product-overview-name'}).find('span', {'class': 'Markup__StyledMarkup-sc-nc8x20-0 dbPAWk'}).text.strip()
        if len(item_name) > item_name_max_length:
            item_name = item_name[:item_name_max_length] + '...'
        print(item_name)
    except:
        item_name = None

    try:
        # Extract item price from the LEGO website's price span element
        item_price = soup.find("span", {"class": "ds-heading-lg ProductPrice_priceText__ndJDK"}).text.strip()
        print(item_price)
    except:
        item_price = None

    return item_name, item_price


def retrieve_price_from_url_lego(url):    
    headers = {
        "accept-language": "en-US,en;q=0.9",
        "accept-encoding": "gzip, deflate, br",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36",
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7"
    }

    # Send GET request to the LEGO product URL
    resp = requests.get(url, headers=headers)
    soup = BeautifulSoup(resp.text, 'html.parser')

    item_price = None

    try:
        # Extract price from the LEGO website using the correct class
        item_price = soup.find("span", {"class": "ds-heading-lg ProductPrice_priceText__ndJDK"}).text.strip()
        print(item_price)
    except:
        item_price = None

    return item_price
