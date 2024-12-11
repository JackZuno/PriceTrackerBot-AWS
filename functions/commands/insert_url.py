from datetime import datetime
from telegram import Update
from telegram.ext import ContextTypes, CallbackContext, ConversationHandler
from firebase_admin import firestore
from functions.items.extract_info import retrieve_info_url
from functions.items.items import add_new_item_db, get_item_by_url_and_chat_id
from functions.keyboard.keyboard import get_add_item_keyboard, get_persistent_keyboard
from functions.users.manage_users import get_user_data

# Define states
ASK_URL = 1

async def handle_url(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text

    # Validate URL format
    if url.startswith("http://") or url.startswith("https://"):
        chat_id = update.message.chat_id

        # Add the URL to Firestore (implement your logic here)
        db = firestore.client()
        user_data = get_user_data(db, chat_id)

        if user_data and user_data.get('bot_on') == True:
            # Check if the url has already been added
            item_data = get_item_by_url_and_chat_id(db, url, chat_id)

            if item_data:
                await update.message.reply_text(
                    f"The item has already been added. Check the full list with the /list command.", 
                    reply_markup=get_persistent_keyboard()
                )
                return ConversationHandler.END

        # Add the new item
        date_added = datetime.now().strftime("%B %d, %Y, %H:%M:%S")
        item_name, item_price = retrieve_info_url(url)

        if item_name == None or item_price == None:
            await update.message.reply_text(
                f"❗ Error: Unable to extract the item name or price. Please ensure the provided data is from *Amazon* or *Ebay* and try again.", 
                reply_markup=get_persistent_keyboard(),
                parse_mode='Markdown'
            )
            return ConversationHandler.END

        add_new_item_db(db, url, item_name, item_price, date_added, chat_id)

        # Use await with reply_text
        message = f"The *{item_name}* has been successfully added and it costs *{item_price}*!"
        await update.message.reply_text(message, reply_markup=get_persistent_keyboard(), parse_mode='Markdown')
        return ConversationHandler.END
    else:
        # Use await with reply_text
        await update.message.reply_text("That doesn't seem like a valid URL. Please try again:", reply_markup=get_add_item_keyboard())
        return ASK_URL


# Cancel command handler
async def cancel(update: Update, context: CallbackContext):
    await update.message.reply_text("Operation canceled. ❌", reply_markup=get_persistent_keyboard())
    return ConversationHandler.END
