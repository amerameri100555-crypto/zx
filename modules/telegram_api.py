import requests
import logging
from config.settings import BASE_URL

logger = logging.getLogger(__name__)

def send_message(chat_id, text, keyboard=None, reply_to_message_id=None):
    url = f"{BASE_URL}/sendMessage"
    payload = {"chat_id": chat_id, "text": text, "parse_mode": "HTML", "disable_web_page_preview": True}
    if keyboard:
        payload["reply_markup"] = keyboard
    if reply_to_message_id:
        payload["reply_to_message_id"] = reply_to_message_id
    try:
        response = requests.post(url, json=payload)
        if response.status_code != 200:
            logger.error(f"خطا در ارسال: {response.text}")
        return response
    except Exception as e:
        logger.error(f"خطا: {e}")
        return None

def delete_message(chat_id, message_id):
    url = f"{BASE_URL}/deleteMessage"
    payload = {"chat_id": chat_id, "message_id": message_id}
    try:
        response = requests.post(url, json=payload)
        if response.status_code != 200:
            logger.error(f"خطا در حذف پیام: {response.text}")
        return response
    except Exception as e:
        logger.error(f"خطا در حذف پیام: {e}")
        return None

def edit_message(chat_id, message_id, text, keyboard=None):
    url = f"{BASE_URL}/editMessageText"
    payload = {"chat_id": chat_id, "message_id": message_id, "text": text, "parse_mode": "HTML", "disable_web_page_preview": True}
    if keyboard:
        payload["reply_markup"] = keyboard
    try:
        response = requests.post(url, json=payload)
        if response.status_code != 200:
            logger.error(f"خطا در ویرایش: {response.text}")
        return response
    except Exception as e:
        logger.error(f"خطا: {e}")
        return None

def answer_callback(callback_id):
    url = f"{BASE_URL}/answerCallbackQuery"
    payload = {"callback_query_id": callback_id}
    try:
        requests.post(url, json=payload)
    except Exception as e:
        logger.error(f"خطا در پاسخ کال‌بک: {e}")

def get_chat_member(chat_id, user_id):
    url = f"{BASE_URL}/getChatMember"
    payload = {"chat_id": chat_id, "user_id": user_id}
    try:
        response = requests.post(url, json=payload)
        if response.status_code == 200:
            return response.json().get("result", {})
        return {}
    except Exception as e:
        logger.error(f"خطا در دریافت اطلاعات کاربر: {e}")
        return {}