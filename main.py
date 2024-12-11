import asyncio
import json
import os
import traceback
import firebase_admin
from firebase_admin import credentials, firestore, initialize_app
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, ConversationHandler, MessageHandler, filters, CallbackQueryHandler
from functions.commands.commands import start, start_auto_messaging, stop_notify, end, remove_item, list_item, help_command, handle_remove_item, add_new_item, ASK_URL
from functions.commands.insert_url import cancel, handle_url
from functions.items.send_notifications import scheduled_message_wrapper


####################################################################
bot_token = os.environ['BOT_TOKEN']

app = ApplicationBuilder().token(bot_token).build()

# Initialize Firestore DB
cred = credentials.Certificate('private/jackbotprice-firebase-adminsdk-b225s-a1fd9fc4c8.json')
firebase_admin.initialize_app(cred)

db = firestore.client()

add_item_conv_handler = ConversationHandler(
    entry_points=[CommandHandler("addItem", add_new_item)],
    states={
        ASK_URL: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_url)],
    },
    fallbacks=[CommandHandler("cancel", cancel)],
)
add_item_conv_handler_emote_buttons = ConversationHandler(
    entry_points=[MessageHandler(filters.Text('🆕 Add Item'), add_new_item)],
    states={
        ASK_URL: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_url)],
    },
    fallbacks=[MessageHandler(filters.Text('❌Cancel'), cancel)],
)

# Command Handler 
app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.Text('🚀Start'), start))

app.add_handler(CommandHandler("auto", start_auto_messaging))
app.add_handler(MessageHandler(filters.Text('🔔Enable Notification'), start_auto_messaging))

app.add_handler(CommandHandler("stop", stop_notify))
app.add_handler(MessageHandler(filters.Text('🔕Disable Notification'), stop_notify))

app.add_handler(CommandHandler("end", end))
app.add_handler(MessageHandler(filters.Text('🛑Stop Bot'), end))

app.add_handler(CommandHandler("remove", remove_item))
app.add_handler(MessageHandler(filters.Text('🗑️Remove Item'), remove_item))

app.add_handler(CommandHandler("list", list_item))
app.add_handler(MessageHandler(filters.Text('📋List Items'), list_item))

app.add_handler(CommandHandler("help", help_command))
app.add_handler(MessageHandler(filters.Text('❓Help'), help_command))

app.add_handler(CommandHandler("cancel", cancel))
app.add_handler(MessageHandler(filters.Text('❌Cancel'), cancel))

app.add_handler(add_item_conv_handler)
app.add_handler(add_item_conv_handler_emote_buttons)

app.add_handler(CallbackQueryHandler(handle_remove_item))


async def tg_bot_main(app, event):
    async with app:
        await app.process_update(
            Update.de_json(json.loads(event["body"]), app.bot)
        )

def lambda_handler(event, context):
    print(f"Event: {event}")
    try:
        if "detail-type" in event and event["detail-type"] == "Scheduled Event":
            print("Triggered by Scheduler")

            asyncio.run(scheduled_message_wrapper(context, app))
        else:
            print("Triggered by User Interaction")

            asyncio.run(tg_bot_main(app, event))
    except Exception as e:
        traceback.print_exc()
        print(e)
        return {"statusCode": 500}

    return {"statusCode": 200}