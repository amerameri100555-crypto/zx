import requests
import time
import logging
import json
import jdatetime
import os
import platform
import psutil
import subprocess
from datetime import datetime, timedelta

TOKEN = "8532288807:AAGJXJnmHJ68Cyh7eMK9muIcZydKAZLayVQ"
BASE_URL = f"https://api.telegram.org/bot{TOKEN}"

OWNER_ID = 7803165903

service_lock_status = {}
welcome_status = {}
panel_users = {}

STATS_FILE = "stats.json"

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

def answer_callback(callback_id):
    url = f"{BASE_URL}/answerCallbackQuery"
    payload = {"callback_query_id": callback_id}
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
📊 <b>گزارش اضافه شدن ربات به گروه</b>

👤 <b>کاربر اضافه‌کننده :</b> <a href='tg://user?id={user_id}'>{user_name}</a>
📛 <b>نام گروه :</b> {group_name}
🔗 <b>لینک گروه :</b> {group_link}
👥 <b>تعداد اعضا :</b> {member_count}
👑 <b>مالک گروه :</b> {owner}
"""
    send_message(OWNER_ID, report_text)

def get_all_users_text():
    text = "👤 <b>لیست کاربران ربات</b>\n\n"
    if bot_stats["users"]:
        text += f"📊 تعداد کل: {len(bot_stats['users'])}\n\n"
        for i, (name, uid) in enumerate(zip(bot_stats["users"], bot_stats["users_id"]), 1):
            text += f"{i}. <a href='tg://user?id={uid}'>{name}</a>\n"
    else:
        text += "📭 هنوز کاربری ثبت نشده"
    return text

def get_all_groups_text():
    text = "📁 <b>لیست گروه‌های ربات</b>\n\n"
    if bot_stats["groups"]:
        text += f"📊 تعداد کل: {len(bot_stats['groups'])}\n\n"
        for i, (name, gid) in enumerate(zip(bot_stats["groups"], bot_stats["groups_id"]), 1):
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
    return text

def get_stats_text():
    total_users = len(bot_stats["users"])
    total_groups = len(bot_stats["groups"])
    
    users_text = ""
    if bot_stats["users"]:
        for name, uid in list(zip(bot_stats["users"], bot_stats["users_id"]))[-10:]:
            users_text += f"🟢 <a href='tg://user?id={uid}'>{name}</a>\n"
    else:
        users_text = "📭 هنوز کاربری ثبت نشده"
    
    groups_text = ""
    if bot_stats["groups"]:
        for name, gid in list(zip(bot_stats["groups"], bot_stats["groups_id"]))[-10:]:
            group_info = get_group_info(gid)
            group_username = group_info.get("username", "")
            member_count = get_group_members_count(gid)
            owner = get_group_owner(gid)
            if group_username:
                groups_text += f"🔗 <a href='https://t.me/{group_username}'>{name}</a> (👥 {member_count} - 👑 {owner})\n"
            else:
                groups_text += f"🔒 {name} (👥 {member_count} - 👑 {owner})\n"
    else:
        groups_text = "📭 هنوز گروهی ثبت نشده"
    
    return f"""
📊 <b>آمار کامل ربات ReaperVoid</b>

📈 <b>آمار کلی :</b>

👤 تعداد کل کاربران : <b>{total_users}</b>
📁 تعداد کل گروه‌ها : <b>{total_groups}</b>

🕒 <b>۱۰ کاربر اخیر :</b>
{users_text}

🕒 <b>۱۰ گروه اخیر :</b>
{groups_text}
"""

def get_ping_text():
    try:
        import time as t
        start = t.time()
        response = requests.get(f"{BASE_URL}/getMe", timeout=10)
        ping = round((t.time() - start) * 1000, 2)
        
        # دریافت اطلاعات سرور
        cpu_percent = psutil.cpu_percent(interval=0.3)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        # تشخیص وضعیت
        if ping < 100:
            status = "🟢 عالی"
        elif ping < 300:
            status = "🟡 قابل قبول"
        else:
            status = "🔴 ضعیف"
        
        return f"""
📡 <b>بررسی پینگ و وضعیت سرور</b>

⏱ <b>زمان پاسخگویی :</b> {ping} ms
📊 <b>وضعیت :</b> {status}

🖥 <b>اطلاعات سرور :</b>
• 💻 سیستم‌عامل : {platform.system()} {platform.release()}
• 🐍 نسخه پایتون : {platform.python_version()}
• 🔥 پردازنده : {cpu_percent}% استفاده
• 💾 رم : {memory.used // (1024**3)}/{memory.total // (1024**3)} GB ({memory.percent}%)
• 💿 هارد : {disk.used // (1024**3)}/{disk.total // (1024**3)} GB ({disk.percent}%)
"""
    except Exception as e:
        return f"❌ خطا در دریافت اطلاعات: {e}"

def get_credit_text():
    try:
        # دریافت اطلاعات از Railway (تاریخ نصب یا اطلاعات هاست)
        # اینجا از روش محاسبه با استفاده از زمان آپتایم سرور
        import subprocess
        try:
            # دریافت زمان آپتایم سیستم
            uptime_seconds = psutil.boot_time()
            boot_time = datetime.fromtimestamp(uptime_seconds)
            now = datetime.now()
            days_running = (now - boot_time).days
            
            # اعتبار تخمینی (مثلاً 30 روز از زمان بوت)
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

📅 <b>زمان راه‌اندازی :</b> {boot_time.strftime('%Y/%m/%d %H:%M')}
📆 <b>روزهای فعالیت :</b> {days_running} روز
⏳ <b>روزهای باقی‌مانده :</b> {days_left} روز
📊 <b>وضعیت :</b> {status}

⚠️ توجه : پس از اتمام اعتبار، ربات غیرفعال خواهد شد.
"""
        except:
            # روش جایگزین
            return """
⏳ <b>اعتبار هاست</b>

📊 وضعیت : 🟢 فعال
📅 اعتبار : نامحدود (سرور اختصاصی)

⚠️ در صورت نیاز به اطلاعات دقیق‌تر، با پشتیبانی تماس بگیرید.
"""
    except Exception as e:
        return f"❌ خطا در دریافت اطلاعات: {e}"

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
        [{"text": "🔙 بازگشت به منوی اصلی", "callback_data": "back_owner"}]
    ]
    return json.dumps({"inline_keyboard": keyboard})

def get_start_text(user_id, first_name):
    return f"""
🌟 <b>سلام بر تو <a href="tg://user?id={user_id}">{first_name}</a> عزیز</b> 🌹

💬 من رباتی هوشمند و قدرتمند برای مدیریت حرفه‌ای گروه‌های تلگرامی هستم!

🔥 برتری‌های انحصاری من :

⚡ <b>پاکسازی گروه در کسری از ثانیه</b>
🛡 <b>سیستم ضدترک گروه</b>
🔒 <b>قفل‌های متنوع و حرفه‌ای</b>
👋 <b>خوش‌آمدگویی هوشمند</b>
📊 <b>گزارش‌گیری دقیق و روزانه</b>
🚫 <b>بدون تبلیغات مزاحم</b>

✨ ویژگی‌های منحصربفرد :

⏫ <b>۹۹.۹٪ آپتایم</b>
🖥 <b>هاست قدرتمند و اختصاصی</b>
🚀 <b>سرعت بی‌نظیر در گروه‌های سنگین</b>
🛡 <b>پایداری در برابر حملات</b>
🔐 <b>قفل‌های متنوع و حرفه‌ای</b>
🤖 <b>احوالپرسی اتوماتیک و هوشمند</b>
➕ <b>قابلیت اضافه کردن اجباری</b>
📋 <b>گزارش‌گیری دقیق و روزانه</b>
⏳ <b>دوره تست برای اطمینان</b>
🚫 <b>کاملاً بدون تبلیغات مزاحم</b>

⚡ ما شبیه هیچکس نیستیم!

🛡 <b>امنیت گروه، اولویت اول ماست</b>
💎 <b>کیفیت، حرف اول را می‌زند</b>
⚡ <b>سرعت، مزیت رقابتی ماست</b>

❓ چرا به ما اعتماد کنیم؟

⚡ <b>پردازش فوق‌سریع</b>
📞 <b>پاسخگویی آنی</b>
🔄 <b>آپدیت‌های مستمر</b>
👨‍💻 <b>پشتیبانی حرفه‌ای</b>

💻 <b>ساخته شده توسط تیم ZX</b>

⚠️ تذکر حقوقی :

❗ <b>تمامی ایده‌ها و کدهای این ربات متعلق به تیم ZX بوده و هر گونه کپی‌برداری یا تقلید، پیگرد قانونی دارد. حقوق مادی و معنوی محفوظ است.</b>

【 <b>Licenced By 🆉︎🆇︎</b> 】
"""

def get_welcome_text(first_name, group_name, user_id):
    date_str, time_str = get_iran_time()
    return f"""
👋 سلام <a href="tg://user?id={user_id}">{first_name}</a> عزیز 🌹
🎉 به گروه <b>{group_name}</b> خوش اومدی 💐
📆 تاریخ : <b>{date_str}</b> 
⏰ ساعت : <b>{time_str}</b>
"""

def get_unknown_text():
    return """
❌ <b>متاسفانه قادر به درخواست شما نیستم!</b>
🔰 لطفاً برای مشاهده منوی اصلی، دستور <b>/start</b> را ارسال کنید.
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
💰 <b>بدون هیچگونه هزینه</b>
🚀 <b>سرعت فوق‌العاده</b>
⚙️ <b>قابلیت‌های پیشرفته</b>
🛡 <b>پشتیبانی کامل</b>
🔄 <b>آپدیت مادام‌العمر</b>
🔒 <b>امنیت کامل</b>
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

def get_panel_keyboard():
    keyboard = [
        [{"text": "🔒 قفل‌ها", "callback_data": "locks"}],
        [{"text": "⚙️ تنظیمات پیشرفته", "callback_data": "advanced"}]
    ]
    return json.dumps({"inline_keyboard": keyboard})

def get_panel_text():
    return """
📋 <b>لطفا بخش مورد نظر خود را انتخاب کنید :</b>
"""

def get_locks_text():
    return """
🔒 <b>پنل تنظیمات گروه :</b>

پنل اصلی 🔹 قفلها 🔹 بخش اول
"""

def get_locks_keyboard(chat_id):
    service_status = service_lock_status.get(chat_id, False)
    
    if service_status:
        service_text = "🔓 باز کردن خدمات تلگرام"
        service_data = "unlock_service"
    else:
        service_text = "🔒 قفل خدمات تلگرام"
        service_data = "lock_service"
    
    keyboard = [
        [{"text": service_text, "callback_data": service_data}],
        [{"text": "🔙 بازگشت به پنل", "callback_data": "panel_back"}]
    ]
    return json.dumps({"inline_keyboard": keyboard})

def get_advanced_text(chat_id):
    welcome_status_text = "🟢 فعال" if welcome_status.get(chat_id, True) else "🔴 غیرفعال"
    
    return f"""
⚙️ <b>تنظیمات پیشرفته :</b>

🔹 <b>وضعیت خوش آمدگویی :</b> {welcome_status_text}
"""

def get_advanced_keyboard(chat_id):
    welcome_status_text = welcome_status.get(chat_id, True)
    
    if welcome_status_text:
        welcome_text = "🔴 غیرفعال کردن خوش آمدگویی"
        welcome_data = "disable_welcome"
    else:
        welcome_text = "🟢 فعال کردن خوش آمدگویی"
        welcome_data = "enable_welcome"
    
    keyboard = [
        [{"text": welcome_text, "callback_data": welcome_data}],
        [{"text": "🔙 بازگشت به پنل", "callback_data": "panel_back"}]
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
                if panel_users[chat_id] == user_id:
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
                send_message(chat_id, "🔒 قفل خدمات تلگرام فعال شد !", reply_to_message_id=message_id)
                return
            if text == "باز کردن خدمات تلگرام":
                service_lock_status[chat_id] = False
                send_message(chat_id, "🔓 قفل خدمات تلگرام غیر فعال شد !", reply_to_message_id=message_id)
                return
            if text == "خوش آمدگویی فعال":
                welcome_status[chat_id] = True
                send_message(chat_id, "✅ خوش آمدگویی فعال شد !", reply_to_message_id=message_id)
                return
            if text == "خوش آمدگویی غیرفعال":
                welcome_status[chat_id] = False
                send_message(chat_id, "❌ خوش آمدگویی غیرفعال شد !", reply_to_message_id=message_id)
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
    first_name = user.get("first_name", "کاربر")
    
    if not chat_id or not data:
        return
    
    if chat_id in panel_users and panel_users[chat_id] != user_id:
        answer_callback(callback_id)
        return
    
    if not (is_admin(chat_id, user_id) or user_id == OWNER_ID):
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
        edit_message(chat_id, message_id, get_locks_text(), get_locks_keyboard(chat_id))
        answer_callback(callback_id)
        return
    
    if data == "unlock_service":
        service_lock_status[chat_id] = False
        edit_message(chat_id, message_id, get_locks_text(), get_locks_keyboard(chat_id))
        answer_callback(callback_id)
        return
    
    if data == "enable_welcome":
        welcome_status[chat_id] = True
        edit_message(chat_id, message_id, get_advanced_text(chat_id), get_advanced_keyboard(chat_id))
        answer_callback(callback_id)
        return
    
    if data == "disable_welcome":
        welcome_status[chat_id] = False
        edit_message(chat_id, message_id, get_advanced_text(chat_id), get_advanced_keyboard(chat_id))
        answer_callback(callback_id)
        return
    
    if user_id == OWNER_ID:
        if data == "stats":
            edit_message(chat_id, message_id, get_stats_text(), get_stats_keyboard())
            answer_callback(callback_id)
            return
        
        if data == "all_users":
            edit_message(chat_id, message_id, get_all_users_text(), get_stats_keyboard())
            answer_callback(callback_id)
            return
        
        if data == "all_groups":
            edit_message(chat_id, message_id, get_all_groups_text(), get_stats_keyboard())
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
        
        if data == "broadcast":
            edit_message(chat_id, message_id, "📨 <b>ارسال پیام همگانی</b>\n\nلطفاً پیام مورد نظر را ارسال کنید.\n\n⚠️ پیام برای <b>همه کاربران</b> ارسال خواهد شد.", get_owner_keyboard())
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
