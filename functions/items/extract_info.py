from functions.items.amazon import retrieve_info_url_amazon, retrieve_price_from_url_amazon
from functions.items.ebay import retrieve_info_url_ebay, retrieve_price_from_url_ebay
from functions.items.lego import retrieve_info_url_lego, retrieve_price_from_url_lego

def retrieve_info_url(url):
    if "amazon" in url.lower() or "amzn" in url.lower():
        print("\nAmazon")

        item_name, item_price = retrieve_info_url_amazon(url)
        
        return item_name, item_price
    elif "ebay" in url.lower():
        print("\nEbay")

        return retrieve_info_url_ebay(url)
    elif "lego" in url.lower():
        print("\nLego")

        return retrieve_info_url_lego(url)
    else:
        print("\nInsert a supported url")

        return None, None


def retrieve_price_from_url(url):
    if "amazon" in url.lower() or "amzn" in url.lower():
        print("\nAmazon")

        item_price = retrieve_price_from_url_amazon(url)
        return item_price
    elif "ebay" in url.lower():
        print("\nEbay")

        return retrieve_price_from_url_ebay(url)
    elif "lego" in url.lower():
        print("\nLego")

        return retrieve_price_from_url_lego(url)
    else:
        print("\nInsert a supported url")
        
        return None


# url_nba = "https://www.nbastore.eu/it/los-angeles-lakers/los-angeles-lakers-nike-city-edition-swingman-jersey-2024-custom-unisex/t-47038580+p-806678031227339+z-9-928504216?_ref=p-TLP:m-GRID:i-r0c1:po-1"
# url_amazon = "https://www.amazon.it/Apple-Auricolari-Bluetooth-personalizzato-Resistenza/dp/B0DGHWD7CT"
# url_lego = "https://www.lego.com/en-it/product/ferrari-sf-24-f1-car-42207"
# url_ebay = "https://www.ebay.com/itm/335696340574?_trksid=p4375194.c102175.m166538"

# retrieve_info_url(url_nba)
# retrieve_info_url(url_amazon)
# retrieve_info_url(url_lego)
# retrieve_info_url(url_ebay)
