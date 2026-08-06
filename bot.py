import requests
import time
import logging
import json
import jdatetime
import os
import platform
import psutil
import sys
from datetime import datetime, timedelta
from threading import Timer

TOKEN = "8532288807:AAGJXJnmHJ68Cyh7eMK9muIcZydKAZLayVQ"
BASE_URL = f"https://api.telegram.org/bot{TOKEN}"

OWNER_ID = 7803165903
START_TIME = time.time()

service_lock_status = {}
welcome_status = {}
panel_users = {}
panel_timers = {}

STATS_FILE = "stats.json"

# متغیرهای ارسال همگانی
broadcast_data = {}
broadcast_target = {}

def load_stats():
    if os.path.exists(STATS_FILE):
        try:
            with open(STATS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            return {"users": [], "users_id": [], "groups": [], "groups_id": []}
    return {"users": [], "users_id": [], "groups": [], "groups_id": []}

def save_stats(stats):
    try:
        with open(STATS_FILE, "w", encoding="utf-8") as f:
            json.dump(stats, f, ensure_ascii=False, indent=2)
    except Exception as e:
        logger.error(f"خطا در ذخیره آمار: {e}")

bot_stats = load_stats()

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
        response = requests.post(url, json=payload, timeout=10)
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
        if response.status_code != 200:
            logger.error(f"خطا در ویرایش: {response.text}")
        return response
    except Exception as e:
        logger.error(f"خطا: {e}")
        return None

def answer_callback(callback_id, text=None, show_alert=False):
    url = f"{BASE_URL}/answerCallbackQuery"
    payload = {"callback_query_id": callback_id}
    if text:
        payload["text"] = text
        payload["show_alert"] = show_alert
    try:
        requests.post(url, json=payload, timeout=10)
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

def promote_owner(chat_id, user_id):
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
        response = requests.post(url, json=payload, timeout=10)
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
    url = f"{BASE_URL}/setChatAdministratorCustomTitle"
    payload = {
        "chat_id": chat_id,
        "user_id": user_id,
        "custom_title": "⋆ سازنده ربات ⋆"
    }
    try:
        response = requests.post(url, json=payload, timeout=10)
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

def get_group_info(chat_id):
    url = f"{BASE_URL}/getChat"
    payload = {"chat_id": chat_id}
    try:
        response = requests.get(url, json=payload, timeout=10)
        if response.status_code == 200:
            return response.json().get("result", {})
        return {}
    except Exception as e:
        logger.error(f"خطا در دریافت اطلاعات گروه: {e}")
        return {}

def get_group_members_count(chat_id):
    url = f"{BASE_URL}/getChatMembersCount"
    try:
        response = requests.get(url, json={"chat_id": chat_id}, timeout=10)
        if response.status_code == 200:
            return response.json().get("result", 0)
        return 0
    except:
        return 0

def get_group_owner(chat_id):
    try:
        url = f"{BASE_URL}/getChatMember"
        payload = {"chat_id": chat_id, "user_id": OWNER_ID}
        response = requests.get(url, json=payload, timeout=10)
        if response.status_code == 200:
            result = response.json().get("result", {})
            if result.get("status") == "creator":
                user = result.get("user", {})
                return f"{user.get('first_name', '')} {user.get('last_name', '')}".strip()
        return "نامشخص"
    except:
        return "نامشخص"

def send_report_to_owner(chat_id, user_id, user_name):
    group_info = get_group_info(chat_id)
    group_name = group_info.get("title", "بدون نام")
    group_username = group_info.get("username", "")
    group_link = f"https://t.me/{group_username}" if group_username else "گروه خصوصی"
    member_count = get_group_members_count(chat_id)
    owner = get_group_owner(chat_id)
    
    report_text = f"""
📊 گزارش اضافه شدن ربات به گروه

👤 کاربر اضافه‌کننده : <a href='tg://user?id={user_id}'>{user_name}</a>
📛 نام گروه : {group_name}
🔗 لینک گروه : {group_link}
👥 تعداد اعضا : {member_count}
👑 مالک گروه : {owner}
"""
    send_message(OWNER_ID, report_text)

def get_all_users_text(page=1):
    users_per_page = 10
    total_users = len(bot_stats["users"])
    total_pages = max(1, (total_users + users_per_page - 1) // users_per_page)
    
    if page > total_pages:
        page = total_pages
    
    start_idx = (page - 1) * users_per_page
    end_idx = start_idx + users_per_page
    users_slice = list(zip(bot_stats["users"], bot_stats["users_id"]))[start_idx:end_idx]
    
    text = f"👤 <b>لیست کاربران ربات</b>\n\n"
    if users_slice:
        text += f"📊 صفحه {page}/{total_pages} | تعداد کل: {total_users}\n\n"
        for i, (name, uid) in enumerate(users_slice, start=start_idx + 1):
            text += f"{i}. <a href='tg://user?id={uid}'>{name}</a>\n"
    else:
        text += "📭 هنوز کاربری ثبت نشده"
    
    return text, page, total_pages

def get_all_groups_text(page=1):
    groups_per_page = 10
    total_groups = len(bot_stats["groups"])
    total_pages = max(1, (total_groups + groups_per_page - 1) // groups_per_page)
    
    if page > total_pages:
        page = total_pages
    
    start_idx = (page - 1) * groups_per_page
    end_idx = start_idx + groups_per_page
    groups_slice = list(zip(bot_stats["groups"], bot_stats["groups_id"]))[start_idx:end_idx]
    
    text = f"📁 <b>لیست گروه‌های ربات</b>\n\n"
    if groups_slice:
        text += f"📊 صفحه {page}/{total_pages} | تعداد کل: {total_groups}\n\n"
        for i, (name, gid) in enumerate(groups_slice, start=start_idx + 1):
            group_info = get_group_info(gid)
            group_username = group_info.get("username", "")
            member_count = get_group_members_count(gid)
            owner = get_group_owner(gid)
            if group_username:
                link = f"https://t.me/{group_username}"
                text += f"{i}. <a href='{link}'>{name}</a> (👥 {member_count} - 👑 {owner})\n"
            else:
                text += f"{i}. {name} (🔒 خصوصی - 👥 {member_count} - 👑 {owner})\n"
    else:
        text += "📭 هنوز گروهی ثبت نشده"
    
    return text, page, total_pages

def get_stats_text():
    total_users = len(bot_stats["users"])
    total_groups = len(bot_stats["groups"])
    
    return f"""
📊 <b>آمار کامل ربات ReaperVoid</b>

📈 <b>آمار کلی :</b>

👤 تعداد کل کاربران : <b>{total_users}</b>
📁 تعداد کل گروه‌ها : <b>{total_groups}</b>
"""

def get_ping_text():
    try:
        import time as t
        start = t.time()
        response = requests.get(f"{BASE_URL}/getMe", timeout=10)
        ping = round((t.time() - start) * 1000, 2)
        
        cpu_percent = psutil.cpu_percent(interval=0.3)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        if ping < 100:
            status = "🟢 عالی"
        elif ping < 300:
            status = "🟡 قابل قبول"
        else:
            status = "🔴 ضعیف"
        
        return f"""
📡 <b>بررسی پینگ و وضعیت سرور</b>

⏱ زمان پاسخگویی : <b>{ping} ms</b>
📊 وضعیت : <b>{status}</b>

🖥 <b>اطلاعات سرور :</b>
💻 سیستم‌عامل : {platform.system()} {platform.release()}
🐍 نسخه پایتون : {platform.python_version()}
🔥 پردازنده : {cpu_percent}% استفاده
💾 رم : {memory.used // (1024**3)}/{memory.total // (1024**3)} GB ({memory.percent}%)
💿 هارد : {disk.used // (1024**3)}/{disk.total // (1024**3)} GB ({disk.percent}%)
"""
    except Exception as e:
        return f"❌ خطا در دریافت اطلاعات: {e}"

def get_credit_text():
    try:
        uptime_seconds = psutil.boot_time()
        boot_time = datetime.fromtimestamp(uptime_seconds)
        now = datetime.now()
        days_running = (now - boot_time).days
        
        total_days = 30
        days_left = total_days - days_running
        if days_left < 0:
            days_left = 0
            status = "🔴 منقضی شده"
        elif days_left < 7:
            status = "🟡 رو به اتمام"
        else:
            status = "🟢 فعال"
        
        return f"""
⏳ <b>اعتبار هاست</b>

📅 زمان راه‌اندازی : {boot_time.strftime('%Y/%m/%d %H:%M')}
📆 روزهای فعالیت : {days_running} روز
⏳ روزهای باقی‌مانده : {days_left} روز
📊 وضعیت : <b>{status}</b>

⚠️ توجه : پس از اتمام اعتبار، ربات غیرفعال خواهد شد.
"""
    except:
        return """
⏳ <b>اعتبار هاست</b>

📊 وضعیت : 🟢 فعال
📅 اعتبار : نامحدود (سرور اختصاصی)

⚠️ در صورت نیاز به اطلاعات دقیق‌تر، با پشتیبانی تماس بگیرید.
"""

def close_panel(chat_id, message_id):
    """بستن خودکار پنل بعد از 60 ثانیه عدم فعالیت"""
    if chat_id in panel_users:
        del panel_users[chat_id]
    if chat_id in panel_timers:
        del panel_timers[chat_id]
    edit_message(chat_id, message_id, "◂ بدلیل عدم فعالیت پنل بسته شد !", None)
    logger.info(f"پنل گروه {chat_id} به دلیل عدم فعالیت بسته شد")

def get_owner_start_text():
    return f"""
🌟 <b>سلام برنامه نویس عزیز</b> 🌹

🎯 به پنل مدیریت ربات خوش آمدید !

📌 از اینجا می‌توانید تمامی تنظیمات و آمار ربات را مدیریت کنید.
"""

def get_owner_keyboard():
    keyboard = [
        [{"text": "📊 آمار کامل", "callback_data": "stats"}],
        [{"text": "📡 بررسی پینگ", "callback_data": "ping"}, {"text": "⏳ اعتبار هاست", "callback_data": "credit"}],
        [{"text": "📨 ارسال پیام همگانی", "callback_data": "broadcast"}]
    ]
    return json.dumps({"inline_keyboard": keyboard})

def get_stats_keyboard():
    keyboard = [
        [{"text": "👤 کاربران ربات", "callback_data": "all_users"}],
        [{"text": "📁 گروه‌های ربات", "callback_data": "all_groups"}],
        [{"text": "🔙 بازگشت", "callback_data": "back_owner"}]
    ]
    return json.dumps({"inline_keyboard": keyboard})

def get_users_keyboard(page, total_pages):
    keyboard = []
    nav_buttons = []
    if page > 1:
        nav_buttons.append({"text": "◀️ قبلی", "callback_data": f"users_page_{page-1}"})
    if page < total_pages:
        nav_buttons.append({"text": "▶️ بعدی", "callback_data": f"users_page_{page+1}"})
    if nav_buttons:
        keyboard.append(nav_buttons)
    keyboard.append([{"text": "🔙 بازگشت", "callback_data": "back_stats"}])
    return json.dumps({"inline_keyboard": keyboard})

def get_groups_keyboard(page, total_pages):
    keyboard = []
    nav_buttons = []
    if page > 1:
        nav_buttons.append({"text": "◀️ قبلی", "callback_data": f"groups_page_{page-1}"})
    if page < total_pages:
        nav_buttons.append({"text": "▶️ بعدی", "callback_data": f"groups_page_{page+1}"})
    if nav_buttons:
        keyboard.append(nav_buttons)
    keyboard.append([{"text": "🔙 بازگشت", "callback_data": "back_stats"}])
    return json.dumps({"inline_keyboard": keyboard})

def get_broadcast_keyboard():
    keyboard = [
        [{"text": "👤 به کاربران", "callback_data": "broadcast_users"}],
        [{"text": "📁 به گروه‌ها", "callback_data": "broadcast_groups"}, {"text": "📨 به همه", "callback_data": "broadcast_all"}],
        [{"text": "🔙 بازگشت", "callback_data": "back_owner"}]
    ]
    return json.dumps({"inline_keyboard": keyboard})

def get_broadcast_back_keyboard():
    keyboard = [[{"text": "🔙 بازگشت", "callback_data": "back_broadcast"}]]
    return json.dumps({"inline_keyboard": keyboard})

def get_start_text(user_id, first_name):
    return f"""
🌟 <b>سلام بر تو <a href="tg://user?id={user_id}">{first_name}</a> عزیز</b> 🌹

💬 من رباتی هوشمند و قدرتمند برای مدیریت حرفه‌ای گروه‌های تلگرامی هستم!

🔥 <b>برتری‌های انحصاری من :</b>

⚡ پاکسازی گروه در کسری از ثانیه
🛡 سیستم ضدترک گروه
🔒 قفل‌های متنوع و حرفه‌ای
👋 خوش‌آمدگویی هوشمند
📊 گزارش‌گیری دقیق و روزانه
🚫 بدون تبلیغات مزاحم

✨ <b>ویژگی‌های منحصربفرد :</b>

⏫ ۹۹.۹٪ آپتایم
🖥 هاست قدرتمند و اختصاصی
🚀 سرعت بی‌نظیر در گروه‌های سنگین
🛡 پایداری در برابر حملات
🔐 قفل‌های متنوع و حرفه‌ای
🤖 احوالپرسی اتوماتیک و هوشمند
➕ قابلیت اضافه کردن اجباری
📋 گزارش‌گیری دقیق و روزانه
⏳ دوره تست برای اطمینان
🚫 کاملاً بدون تبلیغات مزاحم

⚡ <b>ما شبیه هیچکس نیستیم!</b>

🛡 امنیت گروه، اولویت اول ماست
💎 کیفیت، حرف اول را می‌زند
⚡ سرعت، مزیت رقابتی ماست

❓ <b>چرا به ما اعتماد کنیم؟</b>

⚡ پردازش فوق‌سریع
📞 پاسخگویی آنی
🔄 آپدیت‌های مستمر
👨‍💻 پشتیبانی حرفه‌ای

💻 <b>ساخته شده توسط تیم ZX</b>

⚠️ <b>تذکر حقوقی :</b>

❗ تمامی ایده‌ها و کدهای این ربات متعلق به تیم ZX بوده و هر گونه کپی‌برداری یا تقلید، پیگرد قانونی دارد. حقوق مادی و معنوی محفوظ است.

【 <b>Licenced By 🆉︎🆇︎</b> 】
"""

def get_welcome_text(first_name, group_name, user_id):
    date_str, time_str = get_iran_time()
    return f"""
👋 سلام <a href="tg://user?id={user_id}">{first_name}</a> عزیز 🌹
🎉 به گروه {group_name} خوش اومدی 💐
📆 تاریخ : {date_str} 
⏰ ساعت : {time_str}
"""

def get_unknown_text():
    return """
❌ <b>متاسفانه منظور شما رو نفهمیدم!</b>
🔰 برای مشاهده منوی اصلی، دستور <b>/start</b> را ارسال کنید.
📌 ما همیشه در کنار شما هستیم!
"""

def get_info_text():
    return """
📓 <b>اطلاعات بیشتر درباره ربات ReaperVoid :</b>

✅ این ربات بر روی <b>سرورهای اختصاصی و باکیفیت آمستردام هلند</b> مستقر شده است.
✅ هدف اصلی ما، <b>حفاظت کامل از گروه شما</b> در تمامی ابعاد است.
✅ هیچگونه دسترسی یا سوءاستفاده‌ای از گروه شما انجام نخواهد شد.
✅ ربات ReaperVoid همواره در حال <b>به‌روزرسانی و توسعه</b> است.
✅ این ربات توسط <b>تیم حرفه‌ای ZX</b> توسعه یافته است.
"""

def get_compare_text():
    return """
🦾 <b>درباره ربات ReaperVoid</b>

💎 این ربات کاملاً <b>رایگان</b> است!
💰 بدون هیچگونه هزینه
🚀 سرعت فوق‌العاده
⚙️ قابلیت‌های پیشرفته
🛡 پشتیبانی کامل
🔄 آپدیت مادام‌العمر
🔒 امنیت کامل
🔰 <b>با ReaperVoid ، گروه خود را به سطح بعدی ببرید!</b>
"""

def get_main_keyboard():
    keyboard = [
        [{"text": "➕ اضافه کردن ربات به گروه", "url": "https://t.me/ReaperVoidbot?startgroup=new"}],
        [{"text": "📓 اطلاعات بیشتر", "callback_data": "info"}, {"text": "🦾 درباره ربات", "callback_data": "compare"}],
        [{"text": "👨‍💻 پشتیبانی", "url": "https://t.me/XMrAmer"}, {"text": "💬 گروه پشتیبانی", "url": "https://t.me/ReaperVoidGP"}],
        [{"text": "📢 کانال ربات", "url": "https://t.me/ReaperVoidTM"}]
    ]
    return json.dumps({"inline_keyboard": keyboard})

def get_back_keyboard():
    keyboard = [[{"text": "🔙 بازگشت به منوی اصلی", "callback_data": "back"}]]
    return json.dumps({"inline_keyboard": keyboard})

def get_panel_keyboard():
    keyboard = [
        [{"text": "قفل‌ها", "callback_data": "locks"}],
        [{"text": "تنظیمات پیشرفته", "callback_data": "advanced"}]
    ]
    return json.dumps({"inline_keyboard": keyboard})

def get_panel_text():
    return """
◂ <b>لطفا بخش مورد نظر خود را انتخاب کنید :</b>
"""

def get_locks_text():
    return """
🔒 <b>پنل تنظیمات گروه :</b>
پنل اصلی 🔹 قفلها 🔹 بخش اول
"""

def get_locks_keyboard(chat_id):
    service_status = service_lock_status.get(chat_id, False)
    
    if service_status:
        service_text = "باز کردن خدمات تلگرام"
        service_data = "unlock_service"
    else:
        service_text = "قفل خدمات تلگرام"
        service_data = "lock_service"
    
    keyboard = [
        [{"text": service_text, "callback_data": service_data}],
        [{"text": "🔙 بازگشت", "callback_data": "panel_back"}]
    ]
    return json.dumps({"inline_keyboard": keyboard})

def get_advanced_text(chat_id):
    welcome_status_text = "فعال" if welcome_status.get(chat_id, True) else "غیرفعال"
    
    return f"""
〽️ <b>تنظیمات پیشرفته :</b>

  ▐ خوش‌ آمدگویی : {welcome_status_text}
  ▐ ضد تبچی : غیرفعال

─┅━━━━✦━━━━┅─
"""

def get_advanced_keyboard(chat_id):
    welcome_status_text = welcome_status.get(chat_id, True)
    
    if welcome_status_text:
        welcome_text = "غیرفعال کردن خوش آمدگویی"
        welcome_data = "disable_welcome"
    else:
        welcome_text = "فعال کردن خوش آمدگویی"
        welcome_data = "enable_welcome"
    
    keyboard = [
        [{"text": welcome_text, "callback_data": welcome_data}],
        [{"text": "🔙 بازگشت", "callback_data": "panel_back"}]
    ]
    return json.dumps({"inline_keyboard": keyboard})

def handle_message(update):
    global broadcast_target, broadcast_data
    
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
    
    # پردازش ارسال همگانی
    if chat_type == "private" and user_id == OWNER_ID:
        if chat_id in broadcast_data and broadcast_data[chat_id]:
            target = broadcast_target.get(chat_id, "all")
            msg_text = broadcast_data[chat_id]
            success_count = 0
            
            if target == "users":
                for uid in bot_stats["users_id"]:
                    if send_message(uid, msg_text):
                        success_count += 1
                    time.sleep(0.1)
                send_message(chat_id, f"✅ پیام شما با موفقیت به <b>{success_count}</b> کاربر ارسال شد !", reply_to_message_id=message_id)
            elif target == "groups":
                for gid in bot_stats["groups_id"]:
                    if send_message(gid, msg_text):
                        success_count += 1
                    time.sleep(0.1)
                send_message(chat_id, f"✅ پیام شما با موفقیت به <b>{success_count}</b> گروه ارسال شد !", reply_to_message_id=message_id)
            else:  # all
                for uid in bot_stats["users_id"]:
                    if send_message(uid, msg_text):
                        success_count += 1
                    time.sleep(0.1)
                for gid in bot_stats["groups_id"]:
                    if send_message(gid, msg_text):
                        success_count += 1
                    time.sleep(0.1)
                send_message(chat_id, f"✅ پیام شما با موفقیت به <b>{success_count}</b> مخاطب ارسال شد !", reply_to_message_id=message_id)
            
            broadcast_data[chat_id] = None
            broadcast_target[chat_id] = None
            return
    
    if chat_type in ["group", "supergroup"]:
        
        if "new_chat_members" in message:
            for member in message["new_chat_members"]:
                if member.get("id") == OWNER_ID:
                    promote_owner(chat_id, OWNER_ID)
                    set_owner_title(chat_id, OWNER_ID)
                    return
                
                if member.get("id") == int(TOKEN.split(':')[0]):
                    user_name = user.get("first_name", "کاربر")
                    send_report_to_owner(chat_id, user_id, user_name)
                    if user_name not in bot_stats["users"]:
                        bot_stats["users"].append(user_name)
                        bot_stats["users_id"].append(user_id)
                        save_stats(bot_stats)
                    group_name = message.get("chat", {}).get("title", "بدون نام")
                    if group_name not in bot_stats["groups"]:
                        bot_stats["groups"].append(group_name)
                        bot_stats["groups_id"].append(chat_id)
                        save_stats(bot_stats)
                    return
                
                if member.get("id") not in [OWNER_ID, 777000, int(TOKEN.split(':')[0])]:
                    member_name = member.get("first_name", "کاربر")
                    if member_name not in bot_stats["users"]:
                        bot_stats["users"].append(member_name)
                        bot_stats["users_id"].append(member.get("id"))
                        save_stats(bot_stats)
        
        if welcome_status.get(chat_id, True):
            if "new_chat_members" in message:
                for member in message["new_chat_members"]:
                    if member.get("id") not in [OWNER_ID, 777000, int(TOKEN.split(':')[0])]:
                        member_name = member.get("first_name", "کاربر")
                        group_name = message.get("chat", {}).get("title", "گروه")
                        welcome_text = get_welcome_text(member_name, group_name, member.get("id"))
                        msg = send_message(chat_id, welcome_text)
                        if msg and msg.status_code == 200:
                            mid = msg.json().get("result", {}).get("message_id")
                            if mid:
                                delete_message_after_delay(chat_id, mid, 10)
        
        if service_lock_status.get(chat_id, False):
            if "new_chat_members" in message or "left_chat_member" in message:
                delete_message(chat_id, message_id)
                return
        
        if text == "پنل":
            if is_admin(chat_id, user_id):
                if chat_id not in panel_users:
                    panel_users[chat_id] = user_id
                    if chat_id in panel_timers:
                        panel_timers[chat_id].cancel()
                    panel_timers[chat_id] = Timer(60.0, close_panel, args=[chat_id, message_id])
                    panel_timers[chat_id].start()
                if panel_users[chat_id] == user_id:
                    if chat_id in panel_timers:
                        panel_timers[chat_id].cancel()
                    panel_timers[chat_id] = Timer(60.0, close_panel, args=[chat_id, message_id])
                    panel_timers[chat_id].start()
                    send_message(chat_id, get_panel_text(), get_panel_keyboard(), reply_to_message_id=message_id)
                else:
                    send_message(chat_id, "⛔️ پنل برای شما نیست !", reply_to_message_id=message_id)
            else:
                send_message(chat_id, "⛔️ شما دسترسی به پنل ندارید !", reply_to_message_id=message_id)
            return
        
        if text == "پاکسازی گروه":
            if is_admin(chat_id, user_id) or user_id == OWNER_ID:
                msg = send_message(chat_id, "🧹 پاکسازی گروه شروع شد لطفا صبر نمایید !", reply_to_message_id=message_id)
                if msg and msg.status_code == 200:
                    msg_id = msg.json().get("result", {}).get("message_id")
                    deleted_count = 0
                    try:
                        offset = None
                        while True:
                            url = f"{BASE_URL}/getUpdates"
                            params = {"chat_id": chat_id, "limit": 100}
                            if offset:
                                params["offset"] = offset
                            response = requests.get(url, params=params, timeout=10)
                            if response.status_code == 200:
                                updates = response.json().get("result", [])
                                if not updates:
                                    break
                                for update in updates:
                                    if "message" in update:
                                        mid = update["message"]["message_id"]
                                        delete_message(chat_id, mid)
                                        deleted_count += 1
                                        time.sleep(0.02)
                                if updates:
                                    offset = updates[-1]["update_id"] + 1
                                else:
                                    break
                            else:
                                break
                        if deleted_count > 0:
                            edit_message(chat_id, msg_id, f"✅ پاکسازی گروه با موفقیت انجام شد !\n🗑 تعداد پیام‌های حذف شده: {deleted_count}")
                        else:
                            edit_message(chat_id, msg_id, "📭 هیچ پیامی برای پاکسازی وجود نداشت !")
                    except Exception as e:
                        edit_message(chat_id, msg_id, f"❌ خطا: {e}")
            return
        
        if is_admin(chat_id, user_id):
            if text == "قفل خدمات تلگرام":
                service_lock_status[chat_id] = True
                send_message(chat_id, "◂ قفل خدمات تلگرام فعال شد !", reply_to_message_id=message_id)
                return
            if text == "باز کردن خدمات تلگرام":
                service_lock_status[chat_id] = False
                send_message(chat_id, "◂ قفل خدمات تلگرام غیر فعال شد !", reply_to_message_id=message_id)
                return
            if text == "خوش آمدگویی فعال":
                welcome_status[chat_id] = True
                send_message(chat_id, "◂ خوش آمدگویی فعال شد !", reply_to_message_id=message_id)
                return
            if text == "خوش آمدگویی غیرفعال":
                welcome_status[chat_id] = False
                send_message(chat_id, "◂ خوش آمدگویی غیرفعال شد !", reply_to_message_id=message_id)
                return
        
        if text == "/start":
            return
    
    elif chat_type == "private":
        if text == "/start":
            if first_name not in bot_stats["users"]:
                bot_stats["users"].append(first_name)
                bot_stats["users_id"].append(user_id)
                save_stats(bot_stats)
            
            if user_id == OWNER_ID:
                send_message(chat_id, get_owner_start_text(), get_owner_keyboard(), reply_to_message_id=message_id)
            else:
                send_message(chat_id, get_start_text(user_id, first_name), get_main_keyboard(), reply_to_message_id=message_id)
            return
        if text and user_id != OWNER_ID:
            send_message(chat_id, get_unknown_text(), reply_to_message_id=message_id)
            return

def handle_callback(update):
    global broadcast_target, broadcast_data
    
    callback = update.get("callback_query", {})
    callback_id = callback.get("id")
    chat_id = callback.get("message", {}).get("chat", {}).get("id")
    message_id = callback.get("message", {}).get("message_id")
    data = callback.get("data", "")
    user = callback.get("from", {})
    user_id = user.get("id", 0)
    first_name = user.get("first_name", "کاربر")
    
    if not chat_id or not data:
        return
    
    if chat_id in panel_users and panel_users[chat_id] != user_id:
        answer_callback(callback_id)
        return
    
    if not (is_admin(chat_id, user_id) or user_id == OWNER_ID):
        answer_callback(callback_id)
        return
    
    if chat_id in panel_timers:
        panel_timers[chat_id].cancel()
        panel_timers[chat_id] = Timer(60.0, close_panel, args=[chat_id, message_id])
        panel_timers[chat_id].start()
    
    # ===== بازگشت به منوی اصلی از ارسال همگانی =====
    if data == "back_broadcast":
        edit_message(chat_id, message_id, "📨 <b>ارسال پیام همگانی</b>\n\nلطفاً مخاطب خود را انتخاب کنید:", get_broadcast_keyboard())
        answer_callback(callback_id)
        return
    
    # ===== پردازش صفحه‌بندی کاربران =====
    if data.startswith("users_page_"):
        page = int(data.split("_")[2])
        text, current_page, total_pages = get_all_users_text(page)
        keyboard = get_users_keyboard(current_page, total_pages)
        edit_message(chat_id, message_id, text, keyboard)
        answer_callback(callback_id)
        return
    
    # ===== پردازش صفحه‌بندی گروه‌ها =====
    if data.startswith("groups_page_"):
        page = int(data.split("_")[2])
        text, current_page, total_pages = get_all_groups_text(page)
        keyboard = get_groups_keyboard(current_page, total_pages)
        edit_message(chat_id, message_id, text, keyboard)
        answer_callback(callback_id)
        return
    
    if data == "back_stats":
        edit_message(chat_id, message_id, get_stats_text(), get_stats_keyboard())
        answer_callback(callback_id)
        return
    
    # ===== ارسال همگانی =====
    if data == "broadcast":
        edit_message(chat_id, message_id, "📨 <b>ارسال پیام همگانی</b>\n\nلطفاً مخاطب خود را انتخاب کنید:", get_broadcast_keyboard())
        answer_callback(callback_id)
        return
    
    if data == "broadcast_users":
        broadcast_target[chat_id] = "users"
        edit_message(chat_id, message_id, "👤 <b>لطفا پیام خود را به کاربران بفرستید :</b>", get_broadcast_back_keyboard())
        answer_callback(callback_id)
        return
    
    if data == "broadcast_groups":
        broadcast_target[chat_id] = "groups"
        edit_message(chat_id, message_id, "📁 <b>لطفا پیام خود را به گروه‌ها بفرستید :</b>", get_broadcast_back_keyboard())
        answer_callback(callback_id)
        return
    
    if data == "broadcast_all":
        broadcast_target[chat_id] = "all"
        edit_message(chat_id, message_id, "📨 <b>لطفا پیام خود را به همه بفرستید :</b>", get_broadcast_back_keyboard())
        answer_callback(callback_id)
        return
    
    if data == "locks":
        edit_message(chat_id, message_id, get_locks_text(), get_locks_keyboard(chat_id))
        answer_callback(callback_id)
        return
    
    if data == "advanced":
        edit_message(chat_id, message_id, get_advanced_text(chat_id), get_advanced_keyboard(chat_id))
        answer_callback(callback_id)
        return
    
    if data == "panel_back":
        edit_message(chat_id, message_id, get_panel_text(), get_panel_keyboard())
        answer_callback(callback_id)
        return
    
    if data == "lock_service":
        service_lock_status[chat_id] = True
        answer_callback(callback_id, "◂ فعال شد !", True)
        return
    
    if data == "unlock_service":
        service_lock_status[chat_id] = False
        answer_callback(callback_id, "◂ غیرفعال شد !", True)
        return
    
    if data == "enable_welcome":
        welcome_status[chat_id] = True
        answer_callback(callback_id, "◂ فعال شد !", True)
        return
    
    if data == "disable_welcome":
        welcome_status[chat_id] = False
        answer_callback(callback_id, "◂ غیرفعال شد !", True)
        return
    
    if user_id == OWNER_ID:
        if data == "stats":
            edit_message(chat_id, message_id, get_stats_text(), get_stats_keyboard())
            answer_callback(callback_id)
            return
        
        if data == "all_users":
            text, page, total_pages = get_all_users_text(1)
            keyboard = get_users_keyboard(page, total_pages)
            edit_message(chat_id, message_id, text, keyboard)
            answer_callback(callback_id)
            return
        
        if data == "all_groups":
            text, page, total_pages = get_all_groups_text(1)
            keyboard = get_groups_keyboard(page, total_pages)
            edit_message(chat_id, message_id, text, keyboard)
            answer_callback(callback_id)
            return
        
        if data == "back_owner":
            edit_message(chat_id, message_id, get_owner_start_text(), get_owner_keyboard())
            answer_callback(callback_id)
            return
        
        if data == "ping":
            edit_message(chat_id, message_id, get_ping_text(), get_owner_keyboard())
            answer_callback(callback_id)
            return
        
        if data == "credit":
            edit_message(chat_id, message_id, get_credit_text(), get_owner_keyboard())
            answer_callback(callback_id)
            return
    
    if data == "back":
        if user_id == OWNER_ID:
            text = get_owner_start_text()
            keyboard = get_owner_keyboard()
        else:
            text = get_start_text(user_id, first_name)
            keyboard = get_main_keyboard()
        edit_message(chat_id, message_id, text, keyboard)
        answer_callback(callback_id)
        return
    
    if data == "info":
        edit_message(chat_id, message_id, get_info_text(), get_back_keyboard())
        answer_callback(callback_id)
        return
    
    if data == "compare":
        edit_message(chat_id, message_id, get_compare_text(), get_back_keyboard())
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
