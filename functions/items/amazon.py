import requests
from bs4 import BeautifulSoup

def retrieve_info_url_amazon(url):
    # With this one it finds the right price
    headers={
        "accept-language": "en-US,en;q=0.9",
        "accept-encoding": "gzip, deflate, br",
        "User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36",
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7"
    }
    
    resp = requests.get(url, headers=headers)
    # resp = requests.get(get_scrapeops_url(url)) # with this one it finds the right price
    soup=BeautifulSoup(resp.text,'html.parser')

    item_name = None
    item_price = None

    item_name_max_length = 35

    try:
        item_name = soup.find('h1',{'id':'title'}).text.lstrip().rstrip()

        if len(item_name) > item_name_max_length:
            item_name = item_name[:item_name_max_length] + '...'
        print(item_name)
    except:
        item_name = None

    try:
        item_price = soup.find("span",{"class":"a-price"}).find("span").text
        print(item_price)
    except:
        item_price = None

    return item_name, item_price


def retrieve_price_from_url_amazon(url):    
    headers={
        "accept-language": "en-US,en;q=0.9",
        "accept-encoding": "gzip, deflate, br",
        "User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36",
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7"
    }

    resp = requests.get(url, headers=headers)
    soup=BeautifulSoup(resp.text,'html.parser')

    item_price = None

    try:
        item_price = soup.find("span",{"class":"a-price"}).find("span").text
        print(item_price)
    except:
        item_price = None

    return item_price