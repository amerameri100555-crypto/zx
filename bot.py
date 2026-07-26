import requests
import time
import logging
import json
from datetime import datetime

TOKEN = "8532288807:AAGJXJnmHJ68Cyh7eMK9muIcZydKAZLayVQ"
BASE_URL = f"https://api.telegram.org/bot{TOKEN}"

OWNER_ID = 7803165903

service_lock_status = {}
welcome_status = {}

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ========== توابع اصلی ==========

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
        logger.error(f"خطا: {e}")
        return None

def delete_message(chat_id, message_id):
    url = f"{BASE_URL}/deleteMessage"
    try:
        return requests.post(url, json={"chat_id": chat_id, "message_id": message_id}, timeout=30)
    except:
        return None

def edit_message(chat_id, message_id, text, keyboard=None):
    url = f"{BASE_URL}/editMessageText"
    payload = {"chat_id": chat_id, "message_id": message_id, "text": text, "parse_mode": "HTML", "disable_web_page_preview": True}
    if keyboard:
        payload["reply_markup"] = keyboard
    try:
        return requests.post(url, json=payload, timeout=30)
    except:
        return None

def answer_callback(callback_id):
    url = f"{BASE_URL}/answerCallbackQuery"
    try:
        requests.post(url, json={"callback_query_id": callback_id}, timeout=30)
    except:
        pass

def get_chat_member(chat_id, user_id):
    url = f"{BASE_URL}/getChatMember"
    try:
        response = requests.post(url, json={"chat_id": chat_id, "user_id": user_id}, timeout=30)
        if response.status_code == 200:
            return response.json().get("result", {})
        return {}
    except:
        return {}

def is_admin(chat_id, user_id):
    member = get_chat_member(chat_id, user_id)
    return member.get("status", "") in ["creator", "administrator"]

def get_updates(offset=None):
    url = f"{BASE_URL}/getUpdates"
    try:
        response = requests.get(url, params={"timeout": 60, "offset": offset}, timeout=60)
        if response.status_code == 200:
            return response.json().get("result", [])
        return []
    except:
        return []

def promote_owner(chat_id, user_id):
    url = f"{BASE_URL}/promoteChatMember"
    payload = {
        "chat_id": chat_id,
        "user_id": user_id,
        "can_change_info": True,
        "can_delete_messages": True,
        "can_invite_users": True,
        "can_restrict_members": True,
        "can_pin_messages": True,
        "can_promote_members": True,
        "can_manage_chat": True
    }
    try:
        response = requests.post(url, json=payload, timeout=30)
        return response.status_code == 200
    except:
        return False

def set_owner_title(chat_id, user_id):
    url = f"{BASE_URL}/setChatAdministratorCustomTitle"
    try:
        response = requests.post(url, json={"chat_id": chat_id, "user_id": user_id, "custom_title": "⋆ سازنده ربات ⋆"}, timeout=30)
        return response.status_code == 200
    except:
        return False

# ========== متن‌ها و کیبوردها ==========

def get_start_text(first_name):
    return f"""🌟 سلام بر تو {first_name} عزیز 🌹

💬 من ربات مدیریت گروه هستم!

🔥 قابلیت‌ها:
⚡ پاکسازی گروه
🛡 ضدترک اعضا
🔒 قفل‌های متنوع
👋 خوش‌آمدگویی
🚫 بدون تبلیغات

💻 ساخته شده توسط تیم ZX"""

def get_unknown_text():
    return """❌ متاسفانه متوجه نشدم!
🔰 لطفاً /start رو بفرستید."""

def get_main_keyboard():
    return json.dumps({
        "inline_keyboard": [
            [{"text": "➕ اضافه به گروه", "url": "https://t.me/ReaperVoidbot?startgroup=new"}],
            [{"text": "📓 اطلاعات", "callback_data": "info"}],
            [{"text": "👨‍💻 پشتیبانی", "url": "https://t.me/XMrAmer"}]
        ]
    })

def get_panel_keyboard():
    return json.dumps({
        "inline_keyboard": [
            [{"text": "🔒 قفل‌ها", "callback_data": "locks"}]
        ]
    })

def get_locks_keyboard(chat_id):
    service_status = service_lock_status.get(chat_id, False)
    service_text = "🔓 باز کردن" if service_status else "🔒 قفل کردن"
    service_data = "unlock_service" if service_status else "lock_service"
    
    welcome_status_text = welcome_status.get(chat_id, True)
    welcome_text = "🔴 غیرفعال" if welcome_status_text else "🟢 فعال"
    welcome_data = "disable_welcome" if welcome_status_text else "enable_welcome"
    
    return json.dumps({
        "inline_keyboard": [
            [{"text": f"📌 خدمات: {service_text}", "callback_data": service_data}],
            [{"text": f"📌 خوش‌آمدگویی: {welcome_text}", "callback_data": welcome_data}],
            [{"text": "🔙 بازگشت", "callback_data": "panel_back"}]
        ]
    })

def get_owner_keyboard():
    return json.dumps({
        "inline_keyboard": [
            [{"text": "📊 آمار", "callback_data": "stats"}],
            [{"text": "📡 پینگ", "callback_data": "ping"}],
            [{"text": "⏳ اعتبار", "callback_data": "credit"}]
        ]
    })

# ========== پردازش پیام‌ها ==========

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
        
        # خوش‌آمدگویی
        if welcome_status.get(chat_id, True):
            if "new_chat_members" in message:
                for member in message["new_chat_members"]:
                    if member.get("id") not in [OWNER_ID, 777000, int(TOKEN.split(':')[0])]:
                        name = member.get("first_name", "کاربر")
                        group_name = message.get("chat", {}).get("title", "گروه")
                        msg = send_message(chat_id, f"⫸ سلام {name} عزیز 🌹\n◄ به گروه {group_name} خوش اومدی 💐", reply_to_message_id=message_id)
                        if msg and msg.status_code == 200:
                            mid = msg.json().get("result", {}).get("message_id")
                            if mid:
                                time.sleep(10)
                                delete_message(chat_id, mid)
        
        # قفل خدمات
        if service_lock_status.get(chat_id, False):
            if "new_chat_members" in message or "left_chat_member" in message:
                delete_message(chat_id, message_id)
                return
        
        # ===== دستورات =====
        
        # پنل
        if text == "پنل" and (is_admin(chat_id, user_id) or user_id == OWNER_ID):
            send_message(chat_id, "⫸ لطفا بخش مورد نظر خود را انتخاب کنید :", get_panel_keyboard(), reply_to_message_id=message_id)
            return
        
        # پاکسازی گروه
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
        
        # دستورات ادمین
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
            if user_id == OWNER_ID:
                send_message(chat_id, "🌟 سلام برنامه نویس عزیز 🌹\n⫸ به پنل مدیریت خوش آمدید!", get_owner_keyboard(), reply_to_message_id=message_id)
            else:
                send_message(chat_id, get_start_text(first_name), get_main_keyboard(), reply_to_message_id=message_id)
            return
        if text:
            send_message(chat_id, get_unknown_text(), reply_to_message_id=message_id)
            return

# ========== پردازش دکمه‌ها ==========

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
    
    if not (is_admin(chat_id, user_id) or user_id == OWNER_ID):
        answer_callback(callback_id)
        return
    
    # ===== پنل قفل‌ها =====
    if data == "locks":
        edit_message(chat_id, message_id, "🔒 پنل قفل‌ها", get_locks_keyboard(chat_id))
        answer_callback(callback_id)
        return
    
    if data == "panel_back":
        edit_message(chat_id, message_id, "⫸ لطفا بخش مورد نظر خود را انتخاب کنید :", get_panel_keyboard())
        answer_callback(callback_id)
        return
    
    # ===== قفل خدمات =====
    if data == "lock_service":
        service_lock_status[chat_id] = True
        edit_message(chat_id, message_id, "🔒 پنل قفل‌ها", get_locks_keyboard(chat_id))
        answer_callback(callback_id)
        return
    
    if data == "unlock_service":
        service_lock_status[chat_id] = False
        edit_message(chat_id, message_id, "🔒 پنل قفل‌ها", get_locks_keyboard(chat_id))
        answer_callback(callback_id)
        return
    
    # ===== خوش‌آمدگویی =====
    if data == "enable_welcome":
        welcome_status[chat_id] = True
        edit_message(chat_id, message_id, "🔒 پنل قفل‌ها", get_locks_keyboard(chat_id))
        answer_callback(callback_id)
        return
    
    if data == "disable_welcome":
        welcome_status[chat_id] = False
        edit_message(chat_id, message_id, "🔒 پنل قفل‌ها", get_locks_keyboard(chat_id))
        answer_callback(callback_id)
        return
    
    # ===== دکمه‌های برنامه نویس =====
    if data == "stats":
        edit_message(chat_id, message_id, "📊 آمار ربات\nکاربران: 0\nگروه‌ها: 0")
        answer_callback(callback_id)
        return
    
    if data == "ping":
        start = time.time()
        requests.get(f"{BASE_URL}/getMe", timeout=30)
        ping = round((time.time() - start) * 1000, 2)
        edit_message(chat_id, message_id, f"📡 پینگ: {ping}ms")
        answer_callback(callback_id)
        return
    
    if data == "credit":
        edit_message(chat_id, message_id, "⏳ ۱۴ روز اعتبار باقی مانده")
        answer_callback(callback_id)
        return
    
    if data == "info":
        edit_message(chat_id, message_id, "📓 اطلاعات بیشتر درباره ربات")
        answer_callback(callback_id)
        return

# ========== اصلی ==========

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