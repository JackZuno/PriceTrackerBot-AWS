from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup

# List of available commands
available_commands = """
Here are the commands you can use:

🚀 *General Commands*:
- /start - Start the bot
- /end - Stop the bot
- /help - Show available commands

🔔 *Notifications*:
- /auto - Enable automatic notifications
- /stop - Stop receiving notifications

📝 *Item Management*:
- /addItem - Add a new item to track
- /remove - Remove an item from the list
- /list - List all the items
"""

def get_persistent_keyboard():
    rows = [
    ['🔔Enable Notification', '🔕Disable Notification'],         # Notifications
    ['🆕 Add Item', '🗑️Remove Item'],  # Item Management
    ['📋List Items', '🛑Stop Bot', '❓Help']           # General Commands
]

    return ReplyKeyboardMarkup(
        rows,
        input_field_placeholder="At your service 🫡",
        one_time_keyboard=False,  # Keep the keyboard visible after the first press
        resize_keyboard=True  # Resize the keyboard to fit the screen
    )

def get_persistent_keyboard_after_end():
    rows = [
        ['🚀Start', '❓Help'],  
    ]
    return ReplyKeyboardMarkup(
        rows,
        input_field_placeholder="Please, start the bot 🥹🙏",
        one_time_keyboard=False, 
        resize_keyboard=True  
    )

def get_add_item_keyboard():
    return ReplyKeyboardMarkup(
        [
            ['❌Cancel']
        ],
        input_field_placeholder="To track or not to track 💸",
        one_time_keyboard=False, 
        resize_keyboard=True 
    )

def get_remove_items_keyboard(items):
    # Create Inline Keyboard for Remove All Items and individual items
    inline_keyboard = [
        [InlineKeyboardButton("🗑️ Remove All Items", callback_data="remove_all_items")]
    ]
    inline_keyboard.extend([
        [InlineKeyboardButton(f"❌ {item['item_name']}", callback_data=f"remove_item_{item['id']}")]
        for item in items
    ])

    # Create a regular keyboard (ReplyKeyboardMarkup) for the cancel button
    cancel_keyboard = ReplyKeyboardMarkup(
        [['❌Cancel']], 
        input_field_placeholder="Are you sure? 🥹",
        one_time_keyboard=False, 
        resize_keyboard=True
    )

    return InlineKeyboardMarkup(inline_keyboard), cancel_keyboard
