import os
import re
# from dotenv import load_dotenv
from urllib.parse import urlencode
import requests
from bs4 import BeautifulSoup

def get_scrapeops_url(url):
    # load_dotenv()
    # API_KEY = os.getenv("API_KEY")
    API_KEY = os.environ['API_KEY']

    payload = {'api_key': API_KEY, 'url': url}
    proxy_url = 'https://proxy.scrapeops.io/v1/?' + urlencode(payload)
    return proxy_url


def retrieve_info_url_ebay(url):
    item_name_max_length = 35

    item_name = None
    item_price_formatted = None

    try:
        # response = requests.get(url, headers=headers)
        response = requests.get(get_scrapeops_url(url))
        response.raise_for_status()

        # Parse the HTML content
        soup = BeautifulSoup(response.text, 'html.parser')

        # Fine the name of the item
        title_tag = soup.find('h1', class_='x-item-title__mainTitle')
        if title_tag:
            title_span = title_tag.find('span', class_='ux-textspans ux-textspans--BOLD')
            if title_span:
                item_name = title_span.text.strip()

                if len(item_name) > item_name_max_length:
                    item_name = item_name[:item_name_max_length] + '...'

        # Find the price element
        price_div = soup.find('div', class_='x-price-primary')  # Find the parent div
        if price_div:
            price_span = price_div.find('span', class_='ux-textspans')  # Find the span with the price text
            if price_span:
                item_price = price_span.text.strip()

                item_price_formatted = format_price(item_price)

        return item_name, item_price_formatted

    except requests.exceptions.RequestException as e:
        print(f"Error fetching the eBay page: {e}")
        return None
    

def format_price(price_text):
    if "US" in price_text:
        price_text = re.sub(r'\bUS\s*\$', '$', price_text)  # Replace 'US $' with '$'
    elif "EUR" in price_text:
        price_text = re.sub(r'\bEUR\s*', '', price_text)  # Remove 'EUR' from the text
        price_text = price_text.strip() + '€'
    
    return price_text


def retrieve_price_from_url_ebay(url):
    item_price_formatted = None
    
    try:
        # response = requests.get(url, headers=headers)
        response = requests.get(get_scrapeops_url(url))
        response.raise_for_status()

        # Parse the HTML content
        soup = BeautifulSoup(response.text, 'html.parser')

        # Find the price element
        price_div = soup.find('div', class_='x-price-primary')  # Find the parent div
        if price_div:
            price_span = price_div.find('span', class_='ux-textspans')  # Find the span with the price text
            if price_span:
                item_price = price_span.text.strip()

                item_price_formatted = format_price(item_price)

        return  item_price_formatted

    except requests.exceptions.RequestException as e:
        print(f"Error fetching the eBay page: {e}")
        return None