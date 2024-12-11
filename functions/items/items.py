from datetime import datetime
from google.cloud.firestore_v1.base_query import FieldFilter

def add_new_item_db(db, url, item_name, price, date_added, chat_id):
    try:
        item_data = {
            "url": url,
            "item_name": item_name,
            "starting_price": price,
            "date_added": date_added,
            "current_price": price,
            "lowest_price": price,
            "highest_price": price,
            "chat_id": str(chat_id)
        }

        db.collection('items').add(item_data)
        print("Item successfully added!")
    except Exception as e:
        print(f"Error adding item: {e}")
        return None


def get_item_by_url_and_chat_id(db, url, chat_id):
    try:
        items_ref = db.collection('items')
        query = items_ref.where(filter=FieldFilter("url", "==", url)).where(filter=FieldFilter("chat_id", "==", chat_id))
        results = query.stream()

        # Get the first (and only) result, or None if no match
        item = next(results, None)

        if item:
            return item.to_dict()
        else:
            return None
    except Exception as e:
        print(f"Error retrieving item: {e}")
        return None
    

def get_items_by_chat_id(db, chat_id):
    items_ref = db.collection('items')
    items = items_ref.where(filter=FieldFilter("chat_id", "==", str(chat_id))).stream()

    item_list = []
    for doc in items:
        item_data = doc.to_dict()  # Extract document fields
        item_data['id'] = doc.id 
        item_list.append(item_data)

    # Check if items exist
    if item_list:
        item_list.sort(key=lambda x: datetime.strptime(x['date_added'], "%B %d, %Y, %H:%M:%S"))
        return item_list
    else:
        return None
    

def remove_all_items(db, chat_id):
    items_ref = db.collection('items')
    docs = items_ref.where(filter=FieldFilter("chat_id", "==", str(chat_id))).stream()

    for doc in docs:
        print(f'Deleting document {doc.id}')
        doc.reference.delete()

def remove_item_by_id(db, item_id):
    item_ref = db.collection('items').document(item_id)
    item_ref.delete()


def update_item_prices(db, item_id, current_price, lowest_price, highest_price):
    items_ref = db.collection('items').document(item_id)

    try:
        items_ref.update({
            "current_price": current_price,
            "lowest_price": lowest_price,
            "highest_price": highest_price
        })
        print(f"Prices successfully updated in document {item_id}")
    except Exception as e:
        print(f"Error updating document: {e}")

