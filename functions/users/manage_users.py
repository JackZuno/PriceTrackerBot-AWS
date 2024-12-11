from firebase_admin import firestore
from google.cloud.firestore_v1.base_query import FieldFilter


def save_or_update_user_data(db, chat_id, username, first_name, bot_on=True, notifications_on=False):
    user_ref = db.collection('users').document(str(chat_id))
    
    user_data = {
        "chat_id": str(chat_id),
        "username": username,
        "first_name": first_name,
        "bot_on": bot_on,
        "notifications_on": notifications_on
    }

    # Save or update user data
    user_ref.set(user_data, merge=True)


def get_user_data(db, chat_id):
    user_ref = db.collection('users').document(str(chat_id))
    doc = user_ref.get()
    
    if doc.exists:
        return doc.to_dict()
    else:
        return None


def get_users_notifications(db):
    users_ref = db.collection('users')
    users = users_ref.where(filter=FieldFilter("bot_on", "==", True)).where(filter=FieldFilter("notifications_on", "==", True)).stream()

    user_list = []
    for doc in users:
        user_data = doc.to_dict()  # Extract document fields
        user_list.append(user_data)

    # Check if users exist
    if user_list:
        return user_list
    else:
        return None
    

# Notify users on restart
async def notify_restart(application):
    bot = application.bot
    db = firestore.client()

    users_ref = db.collection('users')  # Assuming your users are stored in this collection
    users = users_ref.where(filter=FieldFilter("notifications_on", "==", True)).stream()

    for user in users:
        chat_id = user.get("chat_id")
        username = user.get("username")

        try:
            await bot.send_message(
                chat_id=chat_id,
                text=(
                    f"Hi @{username}\n\n"
                    "🚨 The bot has been restarted!\n\n"
                    "To continue receiving notifications, please disable (/stop) and then re-enable (/auto) notifications."
                ),
                parse_mode='Markdown'
            )
        except Exception as e:
            print(f"Failed to notify user {chat_id}: {e}")

async def post_init(application):
    # Perform actions you want to do before starting polling
    await notify_restart(application)
    print("Users have been notified of the bot restart.")
