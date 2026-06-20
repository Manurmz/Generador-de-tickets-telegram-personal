from collections import defaultdict
from datetime import datetime

STATES = {
    "PROCESSING_RECEIPT": "processing_receipt",
    "WAITING_AMOUNT": "waiting_amount",
    "PROCESSING_DOCUMENT": "processing_document"
}


class UserStateManager:
    def __init__(self):
        self.user_data = defaultdict(dict)

    def set_state(self, chat_id, state, data=None):
        self.user_data[chat_id] = {
            "state": state,
            "data": data or {},
            "timestamp": datetime.now()
        }

    def get_state(self, chat_id):
        return self.user_data.get(chat_id, {})

    def clear_state(self, chat_id):
        if chat_id in self.user_data:
            del self.user_data[chat_id]

    def update_data(self, chat_id, key, value):
        if chat_id in self.user_data:
            self.user_data[chat_id]["data"][key] = value
