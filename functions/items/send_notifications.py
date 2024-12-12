from telegram.error import Forbidden
from telegram.ext import ContextTypes, ConversationHandler
from firebase_admin import firestore
from functions.items.items import get_items_by_chat_id, update_item_prices
from functions.items.extract_info import retrieve_price_from_url
from functions.users.manage_users import get_user_data, get_users_notifications


async def scheduled_message_wrapper(context: ContextTypes.DEFAULT_TYPE, app):
    # Initialize Firestore DB
    db = firestore.client()

    users = get_users_notifications(db)

    if users is None:
        return ConversationHandler.END

    for user in users:
        await scheduled_message(user, context, app)


def convert_price(price):
    price = price.replace("€", "").replace("$", "").replace("£", "").replace(",", ".").strip()
    return float(price)


def compare_prices(current_price, lowest_price, highest_price, current_price_from_url):
    # Remove the currency and the comma
    current_price_num = convert_price(current_price)
    lowest_price_num = convert_price(lowest_price)
    highest_price_num = convert_price(highest_price)
    current_price_from_url_num = convert_price(current_price_from_url)
    
    # Compare prices
    if current_price_num == current_price_from_url_num:
        print("Nothing changed")
        return current_price, lowest_price, highest_price
    elif current_price_from_url_num < lowest_price_num:
        lowest_price = current_price_from_url
    elif current_price_from_url_num > highest_price_num:
        highest_price = current_price_from_url

    return current_price_from_url, lowest_price, highest_price


async def scheduled_message(user, context: ContextTypes.DEFAULT_TYPE, app):
    # chat_id = context.job.chat_id
    chat_id = str(user.get('chat_id', None))

    # Initialize Firestore DB
    db = firestore.client()
    
    # Extract all the items
    items = get_items_by_chat_id(db, chat_id)

    print(f"Items: {items}")

    final_message = ""

    if items:
        full_message = []

        for item in items:
            item_message = generate_message(db, item)

            # Join all parts into a single string and add it to the full_message list
            full_message.append('\n'.join(item_message))

        # Merge all item messages into a single message with each message separated by a newline
        final_message = "\n\n".join(full_message)
    else:
        try:
            message = "No items found.\n The notifications have been disabled, you can enable them with the /auto command!"
            await app.bot.send_message(chat_id=chat_id, text=message, parse_mode='Markdown')
            db.collection('users').document(str(chat_id)).update({'bot_on': True, 'notifications_on': False})
            return ConversationHandler.END
        except Forbidden:
            print(f"User {chat_id} has blocked the bot.")
            db.collection('users').document(str(chat_id)).update({'bot_on': False, 'notifications_on': False})

    try:
        # Send the scheduled message
        await app.bot.send_message(chat_id=chat_id, text=final_message, parse_mode='Markdown', disable_web_page_preview=True)
    except Forbidden:
        print(f"User {chat_id} has blocked the bot.")
        db.collection('users').document(str(chat_id)).update({'bot_on': False, 'notifications_on': False})


def generate_message(db, item):
    # Extract item details
    item_id = item.get('id')
    item_name = item.get('item_name', 'Unknown Item')
    starting_price = item.get('starting_price', 'N/A')
    current_price = item.get('current_price', 'N/A')
    lowest_price = item.get('lowest_price', 'N/A')
    highest_price = item.get('highest_price', 'N/A')
    url = item.get('url', 'https://example.com')  
    date_added = item.get('date_added', 'Unknown')

    current_price_from_url = retrieve_price_from_url(url)

    if current_price_from_url == None:
        current_price_from_url = current_price

    print(f"Item name: {item_name}")
    print(f"Item price: {current_price}")
    print(f"Item price from url: {current_price_from_url}")

    new_current_price, new_lowest_price, new_highest_price = compare_prices(
        current_price, lowest_price, highest_price, current_price_from_url
    )

    current_price_line = f"💸 *Current Price*: {new_current_price}"
    if current_price != new_current_price:
        current_price_line += " 🆕"

    lowest_price_line = f"📉 *Lowest Price*: {new_lowest_price}"
    if lowest_price != new_lowest_price:
        lowest_price_line += " 🆕"

    highest_price_line = f"📈 *Highest Price*: {new_highest_price}"
    if highest_price != new_highest_price:
        highest_price_line += " 🆕"

    # Create the message for each item
    item_message = [
        f"📦 *{item_name}*",
        f"💰 *Starting Price*: {starting_price}",
        f"🗓️ *Date Added*: {date_added}",
        current_price_line,
        lowest_price_line,
        highest_price_line,
        f"🔗 *Link to the item*: [{item_name}]({url})\n"
    ]

    update_item_prices(db, item_id, new_current_price, new_lowest_price, new_highest_price)

    return item_message
