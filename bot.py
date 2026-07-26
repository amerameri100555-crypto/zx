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

# ==================== تنظیمات ====================
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

# ==================== توابع تاریخ و زمان ایران ====================

def get_iran_time():
    now = datetime.now()
    jalali = jdatetime.datetime.fromgregorian(datetime=now)
    weekdays = {6: 'شنبه', 0: 'یکشنبه', 1: 'دوشنبه', 2: 'سه‌شنبه', 3: 'چهارشنبه', 4: 'پنج‌شنبه', 5: 'جمعه'}
    weekday_name = weekdays.get(jalali.weekday(), '')
    date_str = f"{weekday_name} {jalali.day} - {jalali.month} - {jalali.year}"
    time_str = f"{jalali.hour:02d}:{jalali.minute:02d}:{jalali.second:02d}"
    return date_str, time_str

# ==================== توابع تلگرام ====================

def send_message(chat_id, text, keyboard=None, reply_to_message_id=None):
    url = f"{BASE_URL}/sendMessage"
    payload = {"chat_id": chat_id, "text": text, "parse_mode": "HTML", "disable_web_page_preview": True}
    if keyboard:
        payload["reply_markup"] = keyboard
    if reply_to_message_id:
        payload["reply_to_message_id"] = reply_to_message_id
    try:
        response = requests.post(url, json=payload, timeout=15)
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
        response = requests.post(url, json=payload, timeout=10)
        if response.status_code != 200:
            logger.error(f"خطا در حذف: {response.text}")
        return response
    except Exception as e:
        logger.error(f"خطا در حذف: {e}")
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
    """محدود کردن کاربر از ارسال رسانه (فقط ادمین‌ها میتونن)"""
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
            logger.info(f"✅ کاربر {user_id} محدود شد تا {until_date}")
            return True
        else:
            logger.error(f"❌ خطا در محدود کردن: {response.text}")
            return False
    except Exception as e:
        logger.error(f"❌ خطا: {e}")
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

# ==================== توابع تشخیص پورن (ساده و عملی) ====================

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
        logger.error(f"خطا در دانلود: {e}")
        return None

def check_nsfw_with_api(image_bytes):
    """بررسی با API رایگان NSFW API"""
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
            logger.info(f"🔍 API: {is_nsfw} (اطمینان: {confidence})")
            return is_nsfw and confidence > 0.4
        return False
    except Exception as e:
        logger.error(f"خطا در API: {e}")
        return False

def check_nsfw_simple(image_bytes):
    """بررسی ساده با رنگ پوست (آخرین راه)"""
    try:
        image = Image.open(BytesIO(image_bytes))
        image = image.convert('RGB')
        pixels = list(image.getdata())
        skin = 0
        total = len(pixels)
        for r, g, b in pixels:
            if (r > 60 and g > 40 and b > 20 and
                r > g and r > b and
                abs(r - g) > 15 and
                r > 95 and g > 40 and b > 20 and
                max(r, g, b) - min(r, g, b) > 15):
                skin += 1
        ratio = skin / total
        logger.info(f"🔍 رنگ پوست: {ratio:.2%}")
        return ratio > 0.40
    except Exception as e:
        logger.error(f"خطا: {e}")
        return False

def is_nsfw_media(file_id, file_type):
    """تشخیص پورن - فقط عکس و استیکر"""
    if not file_id:
        return False
    
    # فقط عکس و استیکر رو بررسی کن
    if file_type not in ["photo", "sticker"]:
        logger.info(f"⚠️ نوع {file_type} پشتیبانی نمیشه")
        return False
    
    file_bytes = download_file(file_id)
    if not file_bytes:
        return False
    
    # اول با API
    if check_nsfw_with_api(file_bytes):
        return True
    
    # اگه API جواب نداد، با روش ساده
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

# ==================== متن‌ها و کیبوردها ====================

def get_start_text(user_id, first_name):
    date_str, time_str = get_iran_time()
    return f"""
🌟 <b>سلام بر تو <a href="tg://user?id={user_id}">{first_name}</a> عزیز</b> 🌹

💬 من رباتی هوشمند و قدرتمند برای مدیریت حرفه‌ای گروه‌های تلگرامی هستم!

📆 تاریخ : <b>{date_str}</b>
⏰ ساعت : <b>{time_str}</b>

🔥 برتری‌های من :

◄ <b>پاکسازی گروه در کسری از ثانیه</b>
◄ <b>سیستم ضدترک گروه</b>
◄ <b>قفل‌های متنوع و حرفه‌ای</b>
◄ <b>خوش‌آمدگویی هوشمند</b>
◄ <b>گزارش‌گیری دقیق و روزانه</b>
◄ <b>بدون تبلیغات مزاحم</b>

⚡ ما شبیه هیچکس نیستیم!

💻 <b>ساخته شده توسط تیم ZX</b>

⚠️ تمامی حقوق این ربات متعلق به تیم ZX بوده و هر گونه کپی‌برداری پیگرد قانونی دارد.

【 <b>Licenced By 🆉︎🆇︎</b> 】
"""

def get_welcome_text(first_name, group_name, user_id):
    date_str, time_str = get_iran_time()
    return f"""
⫸ سلام <a href="tg://user?id={user_id}">{first_name}</a> عزیز 🌹

◄ به گروه <b>{group_name}</b> خوش اومدی 💐

◂ تاریخ : <b>{date_str}</b> 📆
◂ ساعت : <b>{time_str}</b> ⏰
"""

def get_block_message(first_name, user_id):
    return f"""
⫸ کاربر گرامی : <a href="tg://user?id={user_id}">{first_name}</a> 

◄ استفاده از رسانه مستهجن ممنوع است!

◂ پیام شما حذف شد و به مدت <b>۷ روز</b> از ارسال رسانه محدود می‌شوید.
"""

def get_info_text():
    return """
📓 <b>اطلاعات بیشتر</b>

✅ ربات بر روی سرورهای اختصاصی آمستردام مستقر است
✅ بدون تبلیغات
✅ پشتیبانی ۲۴/۷
✅ آپدیت مادام‌العمر
✅ امنیت کامل

🔰 <b>تیم ZX</b>
"""

def get_price_text():
    return """
💎 <b>نرخ ربات</b>

💰 <b>پلن‌ها:</b>

📌 ماهانه: ۷۰,۰۰۰ تومان
📌 سه ماهه: ۱۹۰,۰۰۰ تومان
📌 شش ماهه: ۳۵۰,۰۰۰ تومان
📌 یکساله: ۶۵۰,۰۰۰ تومان

┈┅┅━━━━━✦━━━━━┅┅┈

💳 برای خرید با پشتیبانی تماس بگیرید.
🆔 @XMrAmer
"""

def get_unknown_text():
    return """
❌ <b>متاسفانه متوجه نشدم!</b>

🔰 لطفاً برای منوی اصلی /start رو بفرستید.
"""

def get_main_keyboard():
    keyboard = [
        [{"text": "➕ اضافه به گروه", "url": "https://t.me/ReaperVoidbot?startgroup=new"}],
        [{"text": "📓 اطلاعات بیشتر", "callback_data": "info"}, {"text": "💎 نرخ ربات", "callback_data": "price"}],
        [{"text": "👨‍💻 پشتیبانی", "url": "https://t.me/XMrAmer"}, {"text": "💬 گروه", "url": "https://t.me/ReaperVoidGP"}],
        [{"text": "📢 کانال", "url": "https://t.me/ReaperVoidTM"}]
    ]
    return json.dumps({"inline_keyboard": keyboard})

def get_back_keyboard():
    keyboard = [[{"text": "🔙 بازگشت", "callback_data": "back"}]]
    return json.dumps({"inline_keyboard": keyboard})

# ==================== پردازش ====================

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
        
        # ===== خوش‌آمدگویی =====
        if "new_chat_members" in message and welcome_status.get(chat_id, True):
            for member in message["new_chat_members"]:
                name = member.get("first_name", "کاربر")
                mid = member.get("id")
                g_name = message.get("chat", {}).get("title", "گروه")
                welcome = get_welcome_text(name, g_name, mid)
                msg = send_message(chat_id, welcome)
                # حذف بعد 10 ثانیه
                if msg and msg.status_code == 200:
                    mid_msg = msg.json().get("result", {}).get("message_id")
                    if mid_msg:
                        time.sleep(10)
                        delete_message(chat_id, mid_msg)
            # حذف پیام خدماتی تلگرام
            if service_lock_status.get(chat_id, False):
                delete_message(chat_id, message_id)
            return
        
        if "left_chat_member" in message and service_lock_status.get(chat_id, False):
            delete_message(chat_id, message_id)
            return
        
        # ===== قفل پورن (فقط عکس و استیکر) =====
        if porn_lock_status.get(chat_id, False):
            
            # کاربر قبلاً محدود شده؟
            if is_user_blocked(chat_id, user_id):
                delete_message(chat_id, message_id)
                return
            
            is_nsfw = False
            file_id = None
            file_type = None
            
            # عکس
            if "photo" in message:
                file_id = message["photo"][-1]["file_id"]
                file_type = "photo"
                is_nsfw = is_nsfw_media(file_id, file_type)
            
            # استیکر
            elif "sticker" in message:
                file_id = message["sticker"]["file_id"]
                file_type = "sticker"
                is_nsfw = is_nsfw_media(file_id, file_type)
            
            # ویدیو و گیف - فقط اخطار میدیم که پشتیبانی نمیشه
            elif "video" in message or "animation" in message or "video_note" in message:
                msg = send_message(chat_id, f"⚠️ {first_name} عزیز، تشخیص ویدیو و گیف فعلاً پشتیبانی نمیشه!")
                if msg and msg.status_code == 200:
                    mid_msg = msg.json().get("result", {}).get("message_id")
                    if mid_msg:
                        time.sleep(5)
                        delete_message(chat_id, mid_msg)
                return
            
            if is_nsfw and file_id:
                # حذف پیام
                delete_message(chat_id, message_id)
                
                # محدود کردن کاربر (تا 7 روز دیگه)
                until = int((datetime.now() + timedelta(days=7)).timestamp())
                restrict_user(chat_id, user_id, until)
                
                # ذخیره در لیست
                if chat_id not in porn_blocked_users:
                    porn_blocked_users[chat_id] = {}
                porn_blocked_users[chat_id][user_id] = datetime.now() + timedelta(days=7)
                
                # اخطار
                block_text = get_block_message(first_name, user_id)
                msg = send_message(chat_id, block_text)
                if msg and msg.status_code == 200:
                    mid_msg = msg.json().get("result", {}).get("message_id")
                    if mid_msg:
                        time.sleep(10)
                        delete_message(chat_id, mid_msg)
                
                logger.info(f"🔞 {first_name} محدود شد برای ۷ روز")
                return
        
        # ===== دستورات =====
        
        # ادمین‌ها
        if is_admin(chat_id, user_id):
            
            if text in ["قفل خدمات تلگرام", "/lock_service"]:
                service_lock_status[chat_id] = True
                send_message(chat_id, "<b>◂ قفل خدمات تلگرام فعال شد!</b>", reply_to_message_id=message_id)
                return
            
            if text in ["باز کردن خدمات تلگرام", "/unlock_service"]:
                service_lock_status[chat_id] = False
                send_message(chat_id, "<b>◂ قفل خدمات تلگرام غیرفعال شد!</b>", reply_to_message_id=message_id)
                return
            
            if text in ["خوش آمدگویی فعال", "/enable_welcome"]:
                welcome_status[chat_id] = True
                send_message(chat_id, "<b>◄ خوش آمدگویی فعال شد!</b>", reply_to_message_id=message_id)
                return
            
            if text in ["خوش آمدگویی غیرفعال", "/disable_welcome"]:
                welcome_status[chat_id] = False
                send_message(chat_id, "<b>◄ خوش آمدگویی غیرفعال شد!</b>", reply_to_message_id=message_id)
                return
        
        # فقط سازنده
        if user_id == OWNER_ID:
            
            if text in ["قفل پورن", "/lock_porn"]:
                porn_lock_status[chat_id] = True
                send_message(chat_id, "<b>◂ قفل پورن فعال شد!</b>", reply_to_message_id=message_id)
                logger.info(f"🔞 قفل پورن در گروه {chat_id} فعال شد")
                return
            
            if text in ["باز کردن پورن", "/unlock_porn"]:
                porn_lock_status[chat_id] = False
                if chat_id in porn_blocked_users:
                    del porn_blocked_users[chat_id]
                send_message(chat_id, "<b>◂ قفل پورن غیرفعال شد!</b>", reply_to_message_id=message_id)
                logger.info(f"🔞 قفل پورن در گروه {chat_id} غیرفعال شد")
                return
        
        if text == "/start":
            return
    
    # ===== پیوی =====
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
    elif data == "price":
        edit_message(chat_id, message_id, get_price_text(), get_back_keyboard())
        answer_callback(callback_id)

# ==================== اصلی ====================

def main():
    logger.info("🤖 ربات ReaperVoid راه‌اندازی شد!")
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