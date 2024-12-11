from datetime import time
from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler
from firebase_admin import firestore
from functions.commands.insert_url import ASK_URL
from functions.items.items import get_items_by_chat_id, remove_all_items, remove_item_by_id
from functions.users.manage_users import get_user_data, save_or_update_user_data
from functions.keyboard.keyboard import get_persistent_keyboard, get_persistent_keyboard_after_end, available_commands, get_add_item_keyboard, get_remove_items_keyboard
from functions.items.send_notifications import scheduled_message

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    username = update.effective_user.username
    first_name = update.effective_user.first_name
    chat_id = update.effective_chat.id

    # Initialize Firestore DB
    db = firestore.client()

    # Check if the user has the bot already on
    user_data = get_user_data(db, chat_id)

    # Check if the user exists and the bot is already running
    # with .get('bot_on', True) it return something only if the field is true
    if user_data and user_data.get('bot_on') == True:
        await update.message.reply_text(
            "You have already started the bot 🤖. You can use other commands now.",
            reply_markup=get_persistent_keyboard()
        )
        return ConversationHandler.END

    # Save or update user data in Firebase
    save_or_update_user_data(db, chat_id, username, first_name)

    if username is None:
        username = first_name

    msg = [
        f"Hi {username},\n\n",
        f"Welcome to *JackBotPrice*.\n\n",
        f"Here, you'll be able to receive notifications about price changes for specific items listed, at the moment, on Amazon, Ebay and Lego.\n\n",
        f"To learn more aboute the commands use /help.\n\n",
        f"Enjoy your stay!\n\n",
        f"*Byeee!*"
    ]

    # Join all parts into a single string
    msg = ''.join(msg)

    # Send a message
    await update.message.reply_text(msg, reply_markup=get_persistent_keyboard(), parse_mode='Markdown')


async def end(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.message.chat_id

    # Initialize Firestore DB
    db = firestore.client()

    # Retrieve the user
    user_data = get_user_data(db, chat_id)

    if not user_data or (user_data and user_data.get('bot_on') == False):
        await update.message.reply_text(
            "You need to use the /start command to interact with the bot.", 
            reply_markup=get_persistent_keyboard_after_end()
        )
        return ConversationHandler.END

    # Set the bot_on and notifications_on variables to false (notifications_on is set to False by default)
    user_data["bot_on"] = False
    user_data["notifications_on"] = False
    save_or_update_user_data(db, chat_id, user_data['username'], user_data['first_name'], user_data['bot_on'], user_data['notifications_on'])
    
    # Send a confirmation message to the user
    await context.bot.send_message(
        chat_id=chat_id, 
        text="Your interaction with the bot has been ended. You will no longer receive messages.",
        reply_markup=get_persistent_keyboard_after_end()
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE): 
    chat_id = update.message.chat_id

    # Initialize Firestore DB
    db = firestore.client()

    # Retrieve the user
    user_data = get_user_data(db, chat_id)

    # Show the right commands
    if user_data and user_data.get('bot_on') == True:
        await update.message.reply_text(available_commands, reply_markup=get_persistent_keyboard(), parse_mode='Markdown')
    else:
        await update.message.reply_text(available_commands, reply_markup=get_persistent_keyboard_after_end(), parse_mode='Markdown')


async def start_auto_messaging(update, context):
    chat_id = update.message.chat_id

    # Initialize Firestore DB
    db = firestore.client()

    # Retrieve the user
    user_data = get_user_data(db, chat_id)

    # Check if the bot is running
    if not user_data or (user_data and user_data.get('bot_on') == False):
        await update.message.reply_text("You need to use the /start command to interact with the bot.")
        return ConversationHandler.END
    
    # Check if the notifications are already activated
    if user_data and user_data.get('notifications_on') == True:
        await update.message.reply_text("The notifications are already on. 🔔")
        return ConversationHandler.END
    
    user_data["notifications_on"] = True

    save_or_update_user_data(db, chat_id, user_data['username'], user_data['first_name'], user_data['bot_on'], user_data['notifications_on'])

    # Notify the user that auto messaging has been enabled
    await update.message.reply_text(
        text="Price changing notifications enabled ✔️",
        reply_markup=get_persistent_keyboard()
    )


async def stop_notify(update, context):
    chat_id = update.message.chat_id

    # Initialize Firestore DB
    db = firestore.client()

    # Retrieve the user
    user_data = get_user_data(db, chat_id)

    # Check if the bot is running
    if not user_data or (user_data and user_data.get('bot_on') == False):
        await update.message.reply_text("You need to use the /start command to interact with the bot.")
        return ConversationHandler.END
    
    # Check if the notifications are already activated
    if user_data and user_data.get('notifications_on') == False:
        await update.message.reply_text("The notifications are already off. 🔕")
        return ConversationHandler.END
    
    user_data["notifications_on"] = False

    save_or_update_user_data(db, chat_id, user_data['username'], user_data['first_name'], user_data['bot_on'], user_data['notifications_on'])

    await context.bot.send_message(
        chat_id=chat_id, 
        text='Price changing notifications disabled ❌', 
        reply_markup=get_persistent_keyboard()
    )


async def add_new_item(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.message.chat_id

    # Initialize Firestore DB
    db = firestore.client()

    # Retrieve the user
    user_data = get_user_data(db, chat_id)

    # Check if the bot is running
    if not user_data or (user_data and user_data.get('bot_on') == False):
        await update.message.reply_text("You need to use the /start command to interact with the bot.")
        return ConversationHandler.END

    await update.message.reply_text("Please enter the URL of the item you want to add:", reply_markup=get_add_item_keyboard())
    return ASK_URL


async def list_item(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.message.chat_id

    # Initialize Firestore DB
    db = firestore.client()

    # Retrieve the user
    user_data = get_user_data(db, chat_id)

    # Check if the bot is running
    if not user_data or (user_data and user_data.get('bot_on') == False):
        await update.message.reply_text("You need to use the /start command to interact with the bot.")
        return ConversationHandler.END
    
    items = get_items_by_chat_id(db, chat_id)

    # If items exist, create the message for each item
    if items:
        full_message = []  # List to store all individual item messages

        for item in items:
            # Extract item details
            item_name = item.get('item_name', 'Unknown Item')
            starting_price = item.get('starting_price', 'N/A')
            current_price = item.get('current_price', 'N/A')
            lowest_price = item.get('lowest_price', 'N/A')
            highest_price = item.get('highest_price', 'N/A')
            url = item.get('url', 'https://example.com')  # Use the actual URL to the item
            date_added = item.get('date_added', 'Unknown')
            
            # Create the message for each item
            item_message = [
                f"📦 *{item_name}*",
                f"💰 *Starting Price*: {starting_price}",
                f"🗓️ *Date Added*: {date_added}",
                f"💸 *Current Price*: {current_price}",
                f"📉 *Lowest Price*: {lowest_price}",
                f"📈 *Highest Price*: {highest_price}",
                f"🔗 *Link to the item*: [{item_name}]({url})\n"
            ]

            # Join all parts into a single string and add it to the full_message list
            full_message.append('\n'.join(item_message))

        # Merge all item messages into a single message with each message separated by a newline
        final_message = "\n\n".join(full_message)

        # Send the final merged message
        await update.message.reply_text(final_message, parse_mode='Markdown', disable_web_page_preview=True)

    else:
        await update.message.reply_text("No items found for this chat_id.")


async def remove_item(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.message.chat_id

    # Initialize Firestore DB
    db = firestore.client()

    # Fetch items for the user
    items = get_items_by_chat_id(db, chat_id)

    if not items:
        await update.message.reply_text("No items found to remove.", reply_markup=get_persistent_keyboard())
        return ConversationHandler.END
    
    # Get both inline and cancel keyboards
    inline_keyboard, cancel_keyboard = get_remove_items_keyboard(items)

    # Send the message with both inline and cancel keyboards
    inline_message = await update.message.reply_text(
        "Select an item to remove:", 
        reply_markup=inline_keyboard
    )
    inline_message_id = inline_message.message_id
    
    # Send the cancel keyboard separately (in a follow-up message or as part of the conversation)
    cancel_message = await update.message.reply_text(
        "To cancel, use the button below:", 
        reply_markup=cancel_keyboard
    )
    cancel_message_id = cancel_message.message_id

    # Store message IDs in context for later deletion
    context.user_data['messages_to_delete'] = [inline_message_id, cancel_message_id]


async def handle_remove_item(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query

    # Acknowledge the callback
    await query.answer()

    callback_data = query.data
    chat_id = query.message.chat_id

    # Initialize Firestore DB
    db = firestore.client()

    if callback_data == "remove_all_items":
        # Remove all items for this chat_id
        remove_all_items(db, chat_id)
        await query.edit_message_text("All items have been removed. 🗑️")

        # Delete previous messages
        messages_to_delete = context.user_data.get('messages_to_delete', [])
        for message_id in messages_to_delete:
            try:
                await context.bot.delete_message(chat_id=chat_id, message_id=message_id)
            except Exception as e:
                print(f"Failed to delete message {message_id}: {e}")

        # Optionally, remove the stored message IDs after deletion
        context.user_data.pop('messages_to_delete', None)

        await context.bot.send_message(
            chat_id=chat_id,
            text="All items have been removed. 🗑️",
            reply_markup=get_persistent_keyboard()
        )

    elif callback_data.startswith("remove_item_"):
        # Remove a specific item
        item_id = callback_data.replace("remove_item_", "")

        remove_item_by_id(db, item_id)

        await query.edit_message_text(f"The item has been removed. ❌")

        # Delete previous messages
        messages_to_delete = context.user_data.get('messages_to_delete', [])
        for message_id in messages_to_delete:
            try:
                await context.bot.delete_message(chat_id=chat_id, message_id=message_id)
            except Exception as e:
                print(f"Failed to delete message {message_id}: {e}")

        # Optionally, remove the stored message IDs after deletion
        context.user_data.pop('messages_to_delete', None)

        await context.bot.send_message(
            chat_id=chat_id,
            text="The item has been removed. 🗑️",
            reply_markup=get_persistent_keyboard()
        )

