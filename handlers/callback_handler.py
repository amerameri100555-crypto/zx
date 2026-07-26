import logging
import json
from modules.telegram_api import edit_message, answer_callback
from utils.texts import (
    get_start_text, get_info_text, get_test_guide_text,
    get_compare_text, get_price_text
)

logger = logging.getLogger(__name__)

def get_main_keyboard():
    keyboard = [
        [{"text": "➕ اضافه کردن به گروه", "url": "https://t.me/ReaperVoidbot?startgroup=new"}],
        [{"text": "📓 اطلاعات بیشتر", "callback_data": "info"}, {"text": "🦾 تفاوت رایگان با اشتراکی", "callback_data": "compare"}],
        [{"text": "🗒 راهنمای تست", "callback_data": "test"}],
        [{"text": "💎 نرخ ربات", "callback_data": "price"}],
        [{"text": "👨‍💻 پشتیبانی", "url": "https://t.me/XMrAmer"}, {"text": "💬 گروه پشتیبانی", "url": "https://t.me/ReaperVoidGP"}],
        [{"text": "📢 کانال ربات", "url": "https://t.me/ReaperVoidTM"}]
    ]
    return json.dumps({"inline_keyboard": keyboard})

def get_back_keyboard():
    keyboard = [[{"text": "🔙 بازگشت به منوی اصلی", "callback_data": "back"}]]
    return json.dumps({"inline_keyboard": keyboard})

def handle_callback(update):
    callback = update.get("callback_query", {})
    callback_id = callback.get("id")
    chat_id = callback.get("message", {}).get("chat", {}).get("id")
    message_id = callback.get("message", {}).get("message_id")
    data = callback.get("data", "")
    
    if not chat_id or not data:
        return
    
    logger.info(f"🔘 کال‌بک: {data}")
    
    if data == "back":
        user = callback.get("from", {})
        user_id = user.get("id", 0)
        first_name = user.get("first_name", "کاربر")
        text = get_start_text(user_id, first_name)
        keyboard = get_main_keyboard()
        edit_message(chat_id, message_id, text, keyboard)
        answer_callback(callback_id)
    elif data == "info":
        edit_message(chat_id, message_id, get_info_text(), get_back_keyboard())
        answer_callback(callback_id)
    elif data == "test":
        edit_message(chat_id, message_id, get_test_guide_text(), get_back_keyboard())
        answer_callback(callback_id)
    elif data == "compare":
        edit_message(chat_id, message_id, get_compare_text(), get_back_keyboard())
        answer_callback(callback_id)
    elif data == "price":
        edit_message(chat_id, message_id, get_price_text(), get_back_keyboard())
        answer_callback(callback_id)