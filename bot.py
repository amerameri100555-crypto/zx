import requests
import time
import logging
import json
import jdatetime
import base64
from io import BytesIO
from datetime import datetime, timedelta
from PIL import Image

TOKEN = "8532288807:AAGJXJnmHJ68Cyh7eMK9muIcZydKAZLayVQ"
BASE_URL = f"https://api.telegram.org/bot{TOKEN}"

OWNER_ID = 7803165903
service_lock_status = {}
welcome_status = {}
porn_lock_status = {}
porn_blocked_users = {}

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

def get_iran_time():
    now = datetime.now()
    jalali = jdatetime.datetime.fromgregorian(datetime=now)
    weekdays = {6: 'شنبه', 0: 'یکشنبه', 1: 'دوشنبه', 2: 'سه‌شنبه', 3: 'چهارشنبه', 4: 'پنج‌شنبه', 5: 'جمعه'}
    weekday_name = weekdays.get(jalali.weekday(), '')
    date_str = f"{weekday_name} {jalali.day} - {jalali.month} - {jalali.year}"
    time_str = f"{jalali.hour:02d}:{jalali.minute:02d}:{jalali.second:02d}"
    return date_str, time_str

def send_message(chat_id, text, keyboard=None, reply_to_message_id=None):
    url = f"{BASE_URL}/sendMessage"
    payload = {"chat_id": chat_id, "text": text, "parse_mode": "HTML", "disable_web_page_preview": True}
    if keyboard:
        payload["reply_markup"] = keyboard
    if reply_to_message_id:
        payload["reply_to_message_id"] = reply_to_message_id
    try:
        response = requests.post(url, json=payload, timeout=15)
        return response
    except Exception as e:
        logger.error(f"خطا: {e}")
        return None

def delete_message(chat_id, message_id):
    url = f"{BASE_URL}/deleteMessage"
    payload = {"chat_id": chat_id, "message_id": message_id}
    try:
        response = requests.post(url, json=payload, timeout=10)
        return response
    except Exception as e:
        logger.error(f"خطا: {e}")
        return None

def edit_message(chat_id, message_id, text, keyboard=None):
    url = f"{BASE_URL}/editMessageText"
    payload = {"chat_id": chat_id, "message_id": message_id, "text": text, "parse_mode": "HTML", "disable_web_page_preview": True}
    if keyboard:
        payload["reply_markup"] = keyboard
    try:
        response = requests.post(url, json=payload, timeout=10)
        return response
    except Exception as e:
        logger.error(f"خطا: {e}")
        return None

def answer_callback(callback_id):
    url = f"{BASE_URL}/answerCallbackQuery"
    payload = {"callback_query_id": callback_id}
    try:
        requests.post(url, json=payload, timeout=5)
    except Exception as e:
        logger.error(f"خطا: {e}")

def get_chat_member(chat_id, user_id):
    url = f"{BASE_URL}/getChatMember"
    payload = {"chat_id": chat_id, "user_id": user_id}
    try:
        response = requests.post(url, json=payload, timeout=10)
        if response.status_code == 200:
            return response.json().get("result", {})
        return {}
    except Exception as e:
        logger.error(f"خطا: {e}")
        return {}

def restrict_user(chat_id, user_id, until_date):
    url = f"{BASE_URL}/restrictChatMember"
    permissions = {
        "can_send_messages": True,
        "can_send_media_messages": False,
        "can_send_polls": True,
        "can_send_other_messages": False,
        "can_add_web_page_previews": True
    }
    payload = {
        "chat_id": chat_id,
        "user_id": user_id,
        "permissions": permissions,
        "until_date": until_date
    }
    try:
        response = requests.post(url, json=payload, timeout=10)
        if response.status_code == 200:
            logger.info(f"✅ کاربر محدود شد")
            return True
        return False
    except Exception as e:
        logger.error(f"خطا: {e}")
        return False

def is_admin(chat_id, user_id):
    member = get_chat_member(chat_id, user_id)
    status = member.get("status", "")
    return status in ["creator", "administrator"]

def get_updates(offset=None):
    url = f"{BASE_URL}/getUpdates"
    params = {"timeout": 30, "offset": offset}
    try:
        response = requests.get(url, params=params, timeout=20)
        if response.status_code == 200:
            return response.json().get("result", [])
        return []
    except Exception as e:
        logger.error(f"خطا: {e}")
        return []

def download_file(file_id):
    url = f"{BASE_URL}/getFile"
    payload = {"file_id": file_id}
    try:
        response = requests.post(url, json=payload, timeout=15)
        if response.status_code == 200:
            file_path = response.json().get("result", {}).get("file_path")
            if file_path:
                file_url = f"https://api.telegram.org/file/bot{TOKEN}/{file_path}"
                file_response = requests.get(file_url, timeout=20)
                if file_response.status_code == 200:
                    return file_response.content
        return None
    except Exception as e:
        logger.error(f"خطا: {e}")
        return None

def check_nsfw_with_api(image_bytes):
    try:
        image_base64 = base64.b64encode(image_bytes).decode('utf-8')
        url = "https://nsfwapi.xyz/api/v1/detect"
        payload = {"image": image_base64}
        headers = {"Content-Type": "application/json"}
        response = requests.post(url, json=payload, headers=headers, timeout=15)
        if response.status_code == 200:
            result = response.json()
            is_nsfw = result.get("result", {}).get("nsfw", False)
            confidence = result.get("result", {}).get("confidence", 0)
            logger.info(f"🔍 API: {is_nsfw}")
            return is_nsfw and confidence > 0.4
        return False
    except Exception as e:
        logger.error(f"خطا: {e}")
        return False

def check_nsfw_simple(image_bytes):
    try:
        image = Image.open(BytesIO(image_bytes))
        image = image.convert('RGB')
        pixels = list(image.getdata())
        skin = 0
        total = len(pixels)
        for r, g, b in pixels:
            if (r > 60 and g > 40 and b > 20 and r > g and r > b and abs(r - g) > 15 and r > 95 and g > 40 and b > 20 and max(r, g, b) - min(r, g, b) > 15):
                skin += 1
        ratio = skin / total
        logger.info(f"🔍 رنگ پوست: {ratio:.2%}")
        return ratio > 0.40
    except Exception as e:
        logger.error(f"خطا: {e}")
        return False

def is_nsfw_media(file_id, file_type):
    if not file_id:
        return False
    if file_type not in ["photo", "sticker"]:
        return False
    file_bytes = download_file(file_id)
    if not file_bytes:
        return False
    if check_nsfw_with_api(file_bytes):
        return True
    if check_nsfw_simple(file_bytes):
        return True
    return False

def is_user_blocked(chat_id, user_id):
    if chat_id not in porn_blocked_users:
        return False
    if user_id not in porn_blocked_users[chat_id]:
        return False
    if datetime.now() < porn_blocked_users[chat_id][user_id]:
        return True
    else:
        del porn_blocked_users[chat_id][user_id]
        return False

def delete_message_after_delay(chat_id, message_id, delay=10):
    def delete_later():
        time.sleep(delay)
        delete_message(chat_id, message_id)
    import threading
    threading.Thread(target=delete_later, daemon=True).start()

def get_start_text(user_id, first_name):
    date_str, time_str = get_iran_time()
    return f"""
🌟 سلام بر تو {first_name} عزیز 🌹
💬 من رباتی هوشمند و قدرتمند برای مدیریت حرفه‌ای گروه‌های تلگرامی هستم!
📆 تاریخ : {date_str}
⏰ ساعت : {time_str}
🔥 برتری‌های انحصاری من
💻 ساخته شده توسط تیم ZX
⚠️ تمامی حقوق محفوظ است
"""

def get_welcome_text(first_name, group_name, user_id):
    date_str, time_str = get_iran_time()
    return f"""
⫸ سلام {first_name} عزیز 🌹
◄ به گروه {group_name} خوش اومدی 💐
◂ تاریخ : {date_str} 📆
◂ ساعت : {time_str} ⏰
"""

def get_block_message(first_name, user_id):
    return f"""
⫸ کاربر گرامی : {first_name}
◄ استفاده از رسانه مستهجن ممنوع است
◂ به مدت ۷ روز از ارسال رسانه محدود شدید
"""

def get_unknown_text():
    return """
❌ متاسفانه متوجه نشدم
🔰 لطفاً /start رو بفرستید
"""

def get_info_text():
    return """
📓 اطلاعات بیشتر
✅ سرور اختصاصی آمستردام
✅ بدون تبلیغات
✅ پشتیبانی ۲۴/۷
✅ آپدیت مادام‌العمر
"""

def get_test_guide_text():
    return """
🗒 راهنمای تست
💎 تست ۳ روزه رایگان
🔰 شرایط استفاده
✅ نصب در ۳ مرحله
⚠️ تذکر مهم
"""

def get_compare_text():
    return """
🦾 تفاوت رایگان با اشتراکی
📘 اطلاعات کامل
💎 ربات اشتراکی ReaperVoid
🔰 انتخاب با شماست
"""

def get_price_text():
    return """
💎 نرخ ربات
💰 پلن‌ها
📌 ماهانه: ۷۰,۰۰۰ تومان
📌 سه ماهه: ۱۹۰,۰۰۰ تومان
📌 شش ماهه: ۳۵۰,۰۰۰ تومان
📌 یکساله: ۶۵۰,۰۰۰ تومان
"""

def get_main_keyboard():
    keyboard = [
        [{"text": "➕ اضافه به گروه", "url": "https://t.me/ReaperVoidbot?startgroup=new"}],
        [{"text": "📓 اطلاعات بیشتر", "callback_data": "info"}, {"text": "🦾 تفاوت", "callback_data": "compare"}],
        [{"text": "🗒 راهنمای تست", "callback_data": "test"}],
        [{"text": "💎 نرخ ربات", "callback_data": "price"}],
        [{"text": "👨‍💻 پشتیبانی", "url": "https://t.me/XMrAmer"}]
    ]
    return json.dumps({"inline_keyboard": keyboard})

def get_back_keyboard():
    keyboard = [[{"text": "🔙 بازگشت", "callback_data": "back"}]]
    return json.dumps({"inline_keyboard": keyboard})

def handle_message(update):
    message = update.get("message", {})
    chat_id = message.get("chat", {}).get("id")
    message_id = message.get("message_id")
    chat_type = message.get("chat", {}).get("type")
    user = message.get("from", {})
    user_id = user.get("id", 0)
    first_name = user.get("first_name", "کاربر")
    text = message.get("text", "").strip().lower()
    
    if not chat_id:
        return
    
    if chat_type in ["group", "supergroup"]:
        
        if porn_lock_status.get(chat_id, False):
            if is_user_blocked(chat_id, user_id):
                delete_message(chat_id, message_id)
                return
            
            is_nsfw = False
            file_id = None
            file_type = None
            
            if "photo" in message:
                file_id = message["photo"][-1]["file_id"]
                file_type = "photo"
                is_nsfw = is_nsfw_media(file_id, file_type)
            elif "sticker" in message:
                file_id = message["sticker"]["file_id"]
                file_type = "sticker"
                is_nsfw = is_nsfw_media(file_id, file_type)
            
            if is_nsfw and file_id:
                delete_message(chat_id, message_id)
                until = int((datetime.now() + timedelta(days=7)).timestamp())
                restrict_user(chat_id, user_id, until)
                if chat_id not in porn_blocked_users:
                    porn_blocked_users[chat_id] = {}
                porn_blocked_users[chat_id][user_id] = datetime.now() + timedelta(days=7)
                block_text = get_block_message(first_name, user_id)
                msg = send_message(chat_id, block_text)
                if msg and msg.status_code == 200:
                    mid = msg.json().get("result", {}).get("message_id")
                    if mid:
                        delete_message_after_delay(chat_id, mid, 10)
                return
        
        if service_lock_status.get(chat_id, False):
            if "new_chat_members" in message:
                for member in message["new_chat_members"]:
                    member_name = member.get("first_name", "کاربر")
                    member_id = member.get("id")
                    delete_message(chat_id, message_id)
                    if welcome_status.get(chat_id, True):
                        group_name = message.get("chat", {}).get("title", "گروه")
                        welcome_text = get_welcome_text(member_name, group_name, member_id)
                        msg = send_message(chat_id, welcome_text)
                        if msg and msg.status_code == 200:
                            mid = msg.json().get("result", {}).get("message_id")
                            if mid:
                                delete_message_after_delay(chat_id, mid, 10)
                return
            if "left_chat_member" in message:
                delete_message(chat_id, message_id)
                return
        
        elif welcome_status.get(chat_id, True):
            if "new_chat_members" in message:
                for member in message["new_chat_members"]:
                    member_name = member.get("first_name", "کاربر")
                    member_id = member.get("id")
                    group_name = message.get("chat", {}).get("title", "گروه")
                    welcome_text = get_welcome_text(member_name, group_name, member_id)
                    msg = send_message(chat_id, welcome_text)
                    if msg and msg.status_code == 200:
                        mid = msg.json().get("result", {}).get("message_id")
                        if mid:
                            delete_message_after_delay(chat_id, mid, 10)
                return
        
        if is_admin(chat_id, user_id):
            if text == "قفل خدمات تلگرام" or text == "/lock_service":
                service_lock_status[chat_id] = True
                send_message(chat_id, "قفل خدمات تلگرام فعال شد", reply_to_message_id=message_id)
                return
            if text == "باز کردن خدمات تلگرام" or text == "/unlock_service":
                service_lock_status[chat_id] = False
                send_message(chat_id, "قفل خدمات تلگرام غیرفعال شد", reply_to_message_id=message_id)
                return
            if text == "خوش آمدگویی فعال" or text == "/enable_welcome":
                welcome_status[chat_id] = True
                send_message(chat_id, "خوش آمدگویی فعال شد", reply_to_message_id=message_id)
                return
            if text == "خوش آمدگویی غیرفعال" or text == "/disable_welcome":
                welcome_status[chat_id] = False
                send_message(chat_id, "خوش آمدگویی غیرفعال شد", reply_to_message_id=message_id)
                return
        
        if user_id == OWNER_ID:
            if text == "قفل پورن" or text == "/lock_porn":
                porn_lock_status[chat_id] = True
                send_message(chat_id, "قفل پورن فعال شد", reply_to_message_id=message_id)
                return
            if text == "باز کردن پورن" or text == "/unlock_porn":
                porn_lock_status[chat_id] = False
                if chat_id in porn_blocked_users:
                    del porn_blocked_users[chat_id]
                send_message(chat_id, "قفل پورن غیرفعال شد", reply_to_message_id=message_id)
                return
        
        if text == "/start":
            return
    
    elif chat_type == "private":
        if text == "/start":
            start_text = get_start_text(user_id, first_name)
            keyboard = get_main_keyboard()
            send_message(chat_id, start_text, keyboard, reply_to_message_id=message_id)
            return
        if text:
            unknown_text = get_unknown_text()
            send_message(chat_id, unknown_text, reply_to_message_id=message_id)
            return

def handle_callback(update):
    callback = update.get("callback_query", {})
    callback_id = callback.get("id")
    chat_id = callback.get("message", {}).get("chat", {}).get("id")
    message_id = callback.get("message", {}).get("message_id")
    data = callback.get("data", "")
    
    if not chat_id or not data:
        return
    
    logger.info(f"کال‌بک: {data}")
    
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

def main():
    logger.info("ربات ReaperVoid راه‌اندازی شد!")
    offset = None
    while True:
        try:
            updates = get_updates(offset)
            for update in updates:
                offset = update["update_id"] + 1
                if "message" in update:
                    handle_message(update)
                if "callback_query" in update:
                    handle_callback(update)
        except Exception as e:
            logger.error(f"خطا: {e}")
            time.sleep(5)
        time.sleep(1)

if __name__ == "__main__":
    main()