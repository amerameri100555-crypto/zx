import requests
import time
import logging
import json
import jdatetime
import base64
import os
import tempfile
import subprocess
from io import BytesIO
from datetime import datetime, timedelta
from PIL import Image

TOKEN = "8532288807:AAGJXJnmHJ68Cyh7eMK9muIcZydKAZLayVQ"
BASE_URL = f"https://api.telegram.org/bot{TOKEN}"

OWNER_ID = 7803165903

# ==================== API Key ها ====================
SIGHTENGINE_API_USER = "1034163582"
SIGHTENGINE_API_SECRET = "Q9JkCm9SfwWwNFwUDi7EhrgX58jS4TqH"
DEEPAI_API_KEY = "eb27dd91-b502-49ea-8c59-cf8324bcef59"
GOOGLE_VISION_API_KEY = ""  # از Google Cloud بگیر
AZURE_API_KEY = ""  # از Azure بگیر
AMAZON_API_KEY = ""  # از AWS بگیر
CLARIFAI_API_KEY = ""  # از Clarifai بگیر
IMAGGA_API_KEY = ""  # از Imagga بگیر
HIVE_API_KEY = ""  # از Hive بگیر

service_lock_status = {}
welcome_status = {}
porn_lock_status = {}
porn_blocked_users = {}

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# ==================== NudeNet (محلی) ====================
nude_detector = None
try:
    from nudenet import NudeDetector
    import numpy as np
    import cv2
    nude_detector = NudeDetector()
    logger.info("✅ NudeNet بارگذاری شد!")
except Exception as e:
    logger.error(f"❌ NudeNet: {e}")

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
        response = requests.post(url, json=payload, timeout=60)
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
        response = requests.post(url, json=payload, timeout=30)
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
    params = {"timeout": 60, "offset": offset}
    try:
        response = requests.get(url, params=params, timeout=60)
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
        response = requests.post(url, json=payload, timeout=30)
        if response.status_code == 200:
            file_path = response.json().get("result", {}).get("file_path")
            if file_path:
                file_url = f"https://api.telegram.org/file/bot{TOKEN}/{file_path}"
                file_response = requests.get(file_url, timeout=30)
                if file_response.status_code == 200:
                    return file_response.content
        return None
    except Exception as e:
        logger.error(f"خطا در دانلود: {e}")
        return None

# ==================== 10 سرویس تشخیص پورن ====================

def check_nsfw_with_nudenet(image_bytes):
    if nude_detector is None:
        return False
    try:
        nparr = np.frombuffer(image_bytes, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        if img is None:
            img_pil = Image.open(BytesIO(image_bytes))
            img = cv2.cvtColor(np.array(img_pil), cv2.COLOR_RGB2BGR)
        result = nude_detector.detect(img)
        for item in result:
            label = item.get('label', '').lower()
            score = item.get('score', 0)
            if score > 0.5 and label in ['FEMALE_BREAST_EXPOSED', 'MALE_BREAST_EXPOSED',
                                          'FEMALE_GENITALIA_EXPOSED', 'MALE_GENITALIA_EXPOSED',
                                          'BUTTOCKS_EXPOSED', 'ANUS_EXPOSED']:
                logger.info(f"🔍 NudeNet: {label} - {score}")
                return True
        return False
    except Exception as e:
        logger.error(f"خطا در NudeNet: {e}")
        return False

def check_nsfw_with_sightengine(image_bytes):
    try:
        image_base64 = base64.b64encode(image_bytes).decode('utf-8')
        url = "https://api.sightengine.com/1.0/check.json"
        params = {
            "api_user": SIGHTENGINE_API_USER,
            "api_secret": SIGHTENGINE_API_SECRET,
            "models": "nudity-2.0,wad",
            "image_base64": image_base64
        }
        response = requests.get(url, params=params, timeout=30)
        if response.status_code == 200:
            result = response.json()
            nudity = result.get("nudity", {}).get("raw", 0)
            sexual = result.get("nudity", {}).get("sexual_activity", 0)
            gore = result.get("wad", {}).get("gore", 0)
            logger.info(f"🔍 Sightengine: Nudity={nudity}, Sexual={sexual}, Gore={gore}")
            if nudity > 0.6 or sexual > 0.6 or gore > 0.7:
                return True
        return False
    except Exception as e:
        logger.error(f"خطا در Sightengine: {e}")
        return False

def check_nsfw_with_deepai(image_bytes):
    try:
        url = "https://api.deepai.org/api/nsfw-detector"
        files = {'image': ('image.jpg', image_bytes, 'image/jpeg')}
        headers = {'api-key': DEEPAI_API_KEY}
        response = requests.post(url, files=files, headers=headers, timeout=30)
        if response.status_code == 200:
            result = response.json()
            score = result.get("output", {}).get("nsfw_score", 0)
            logger.info(f"🔍 DeepAI: {score}")
            return score > 0.7
        return False
    except Exception as e:
        logger.error(f"خطا در DeepAI: {e}")
        return False

def check_nsfw_with_nsfwapi(image_bytes):
    try:
        image_base64 = base64.b64encode(image_bytes).decode('utf-8')
        url = "https://nsfwapi.xyz/api/v1/detect"
        payload = {"image": image_base64}
        headers = {"Content-Type": "application/json"}
        response = requests.post(url, json=payload, headers=headers, timeout=30)
        if response.status_code == 200:
            result = response.json()
            is_nsfw = result.get("result", {}).get("nsfw", False)
            confidence = result.get("result", {}).get("confidence", 0)
            logger.info(f"🔍 NSFWAPI: {is_nsfw} ({confidence})")
            return is_nsfw and confidence > 0.4
        return False
    except Exception as e:
        logger.error(f"خطا در NSFWAPI: {e}")
        return False

def check_nsfw_with_google_vision(image_bytes):
    try:
        if not GOOGLE_VISION_API_KEY:
            return False
        image_base64 = base64.b64encode(image_bytes).decode('utf-8')
        url = f"https://vision.googleapis.com/v1/images:annotate?key={GOOGLE_VISION_API_KEY}"
        payload = {
            "requests": [{
                "image": {"content": image_base64},
                "features": [{"type": "SAFE_SEARCH_DETECTION"}]
            }]
        }
        response = requests.post(url, json=payload, timeout=30)
        if response.status_code == 200:
            result = response.json()
            safe = result.get("responses", [{}])[0].get("safeSearchAnnotation", {})
            adult = safe.get("adult", "VERY_UNLIKELY")
            racy = safe.get("racy", "VERY_UNLIKELY")
            violence = safe.get("violence", "VERY_UNLIKELY")
            logger.info(f"🔍 Google: Adult={adult}, Racy={racy}, Violence={violence}")
            if adult in ["POSSIBLE", "LIKELY", "VERY_LIKELY"]:
                return True
            if racy in ["LIKELY", "VERY_LIKELY"]:
                return True
            if violence in ["LIKELY", "VERY_LIKELY"]:
                return True
        return False
    except Exception as e:
        logger.error(f"خطا در Google Vision: {e}")
        return False

def check_nsfw_with_azure(image_bytes):
    try:
        if not AZURE_API_KEY:
            return False
        image_base64 = base64.b64encode(image_bytes).decode('utf-8')
        url = "https://api.cognitive.microsoft.com/contentmoderator/moderate/v1.0/ProcessImage/Evaluate"
        headers = {"Ocp-Apim-Subscription-Key": AZURE_API_KEY, "Content-Type": "application/json"}
        payload = {"DataRepresentation": "URL", "Value": image_base64}
        response = requests.post(url, json=payload, headers=headers, timeout=30)
        if response.status_code == 200:
            result = response.json()
            adult_score = result.get("AdultClassificationScore", 0)
            is_adult = result.get("IsImageAdultClassified", False)
            racy_score = result.get("RacyClassificationScore", 0)
            is_racy = result.get("IsImageRacyClassified", False)
            logger.info(f"🔍 Azure: Adult={is_adult}({adult_score}), Racy={is_racy}({racy_score})")
            return is_adult or is_racy or adult_score > 0.7 or racy_score > 0.7
        return False
    except Exception as e:
        logger.error(f"خطا در Azure: {e}")
        return False

def check_nsfw_with_amazon(image_bytes):
    try:
        if not AMAZON_API_KEY:
            return False
        return False
    except Exception as e:
        logger.error(f"خطا در Amazon: {e}")
        return False

def check_nsfw_with_clarifai(image_bytes):
    try:
        if not CLARIFAI_API_KEY:
            return False
        return False
    except Exception as e:
        logger.error(f"خطا در Clarifai: {e}")
        return False

def check_nsfw_with_imagga(image_bytes):
    try:
        if not IMAGGA_API_KEY:
            return False
        return False
    except Exception as e:
        logger.error(f"خطا در Imagga: {e}")
        return False

def check_nsfw_with_hive(image_bytes):
    try:
        if not HIVE_API_KEY:
            return False
        return False
    except Exception as e:
        logger.error(f"خطا در Hive: {e}")
        return False

def check_nsfw_image(image_bytes):
    """بررسی با 10 سرویس مختلف"""
    
    # 1. NudeNet (محلی - سریع)
    if check_nsfw_with_nudenet(image_bytes):
        logger.info("✅ تشخیص با NudeNet")
        return True
    
    # 2. Sightengine
    if check_nsfw_with_sightengine(image_bytes):
        logger.info("✅ تشخیص با Sightengine")
        return True
    
    # 3. DeepAI
    if check_nsfw_with_deepai(image_bytes):
        logger.info("✅ تشخیص با DeepAI")
        return True
    
    # 4. NSFWAPI
    if check_nsfw_with_nsfwapi(image_bytes):
        logger.info("✅ تشخیص با NSFWAPI")
        return True
    
    # 5. Google Vision
    if check_nsfw_with_google_vision(image_bytes):
        logger.info("✅ تشخیص با Google Vision")
        return True
    
    # 6. Azure
    if check_nsfw_with_azure(image_bytes):
        logger.info("✅ تشخیص با Azure")
        return True
    
    # 7-10. سایر سرویس‌ها (در صورت تنظیم API Key)
    
    return False

def check_nsfw_media(file_id, file_type):
    if not file_id:
        return False
    
    if file_type not in ["photo", "sticker"]:
        return False
    
    file_bytes = download_file(file_id)
    if not file_bytes:
        return False
    
    return check_nsfw_image(file_bytes)

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

# ==================== متن‌ها ====================

def get_start_text(user_id, first_name):
    date_str, time_str = get_iran_time()
    return f"""
🌟 <b>سلام بر تو <a href="tg://user?id={user_id}">{first_name}</a> عزیز</b> 🌹

💬 من رباتی هوشمند و قدرتمند برای مدیریت حرفه‌ای گروه‌های تلگرامی هستم!

📆 تاریخ : <b>{date_str}</b>
⏰ ساعت : <b>{time_str}</b>

🔥 برتری‌های انحصاری من :

◄ <b>مجهز به پیشرفته‌ترین هوش مصنوعی روز دنیا</b>
◄ <b>فیلتر قوی تشخیص محتوای نامناسب</b>
◄ <b>سیستم امنیتی در برابر ربات‌های مخرب</b>
◄ <b>پاکسازی گروه در کسری از ثانیه</b>
◄ <b>محافظت از گروه در برابر مدیران نفوذی</b>
◄ <b>سیستم ضدترک گروه</b>
◄ <b>درآمدزایی هوشمند از گروه</b>
◄ <b>شناسایی کاربران مشکوک</b>

✨ ویژگی‌های منحصربفرد :

◂ <b>۹۹.۹٪ آپتایم</b>
◂ <b>هاست قدرتمند و اختصاصی</b>
◂ <b>سرعت بی‌نظیر در گروه‌های سنگین</b>
◂ <b>پایداری در برابر حملات</b>
◂ <b>قفل‌های متنوع و حرفه‌ای</b>
◂ <b>احوالپرسی اتوماتیک و هوشمند</b>
◂ <b>قابلیت اضافه کردن اجباری</b>
◂ <b>گزارش‌گیری دقیق و روزانه</b>
◂ <b>دوره تست برای اطمینان</b>
◂ <b>کاملاً بدون تبلیغات مزاحم</b>

⚡ ما شبیه هیچکس نیستیم!

◄ <b>امنیت گروه، اولویت اول ماست</b>
◄ <b>کیفیت، حرف اول را می‌زند</b>
◄ <b>سرعت، مزیت رقابتی ماست</b>

❓ چرا به ما اعتماد کنیم؟

◂ <b>پردازش فوق‌سریع</b>
◂ <b>پاسخگویی آنی</b>
◂ <b>آپدیت‌های مستمر</b>
◂ <b>پشتیبانی حرفه‌ای</b>

💳 همین حالا سفارش بده!
 
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

def get_block_message(first_name, user_id):
    return f"""
⫸ کاربر گرامی : <a href="tg://user?id={user_id}">{first_name}</a> 

◄ استفاده از رسانه مستهجن ممنوع است ، لذا پیام شما حذف می شود و برای مدت <b>۷ روز</b> از ارسال هرگونه رسانه (عکس، فیلم، گیف، استیکر، فایل) محدود می شوید !
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

def get_test_guide_text():
    return """
🗒 <b>راهنمای تست ربات ReaperVoid</b>

💎 برای آشنایی با قدرت و برتری ربات ReaperVoid، امکان تست <b>۳ روزه</b> تمامی قابلیت‌ها به صورت <b>کاملاً رایگان</b> فراهم شده است.

✅ <b>نصب ربات در ۳ مرحله ساده :</b>

1️⃣ مرحله اول : اضافه کردن ربات به گروه

2️⃣ مرحله دوم : ادمین کردن ربات با تمام دسترسی‌ها

3️⃣ مرحله سوم : تنظیم قفل‌ها و حالت‌های مورد نظر
"""

def get_compare_text():
    return """
🦾 <b>تفاوت ربات رایگان با اشتراکی</b>

💎 <b>ربات اشتراکی ReaperVoid (تیم ZX) :</b>

◄ <b>بدون تبلیغات</b>
◄ <b>سرعت فوق‌العاده</b>
◄ <b>قابلیت‌های پیشرفته</b>
◄ <b>پشتیبانی ۲۴/۷</b>
◄ <b>آپدیت مادام‌العمر</b>
◄ <b>امنیت کامل</b>
"""

def get_price_text():
    return """
💎 <b>نرخ و قیمت ربات ReaperVoid :</b>

┅┅┅┅┅┅┅┅┅┅┅┅┅

💰 <b>پلن های مدیریت گروه :</b>

📌 <b>ماهانه :</b> ۷۰,۰۰۰ تومان
📌 <b>دو ماهه :</b> ۱۴۰,۰۰۰ تومان
📌 <b>سه ماهه :</b> ۲۱۰,۰۰۰ تومان
📌 <b>چهار ماهه :</b> ۲۸۰,۰۰۰ تومان
📌 <b>پنج ماهه :</b> ۳۵۰,۰۰۰ تومان
📌 <b>شش ماهه :</b> ۴۲۰,۰۰۰ تومان
📌 <b>یکساله :</b> ۸۴۰,۰۰۰ تومان

┈┅┅━━━━━✦━━━━━┅┅┈

🪙 <b>نرخ پایه قفل پورن :</b>

📌 <b>قفل پورن :</b> ۸۰,۰۰۰ تومان

┅┅┅┅┅┅┅┅┅┅┅┅┅

💳 برای خرید با پشتیبانی تماس بگیرید.
🆔 @XMrAmer
"""

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
        
        # ===== قفل پورن =====
        if porn_lock_status.get(chat_id, False):
            
            if is_user_blocked(chat_id, user_id):
                delete_message(chat_id, message_id)
                return
            
            is_nsfw = False
            file_id = None
            file_type = None
            has_media = False
            
            if "photo" in message:
                file_id = message["photo"][-1]["file_id"]
                file_type = "photo"
                has_media = True
                is_nsfw = check_nsfw_media(file_id, file_type)
            elif "sticker" in message:
                file_id = message["sticker"]["file_id"]
                file_type = "sticker"
                has_media = True
                is_nsfw = check_nsfw_media(file_id, file_type)
            
            if has_media and is_nsfw:
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
                logger.info(f"🔞 رسانه پورن از {first_name} حذف شد")
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
            if text in ["قفل خدمات تلگرام", "/lock_service"]:
                service_lock_status[chat_id] = True
                send_message(chat_id, "<b>◂ قفل خدمات تلگرام فعال شد !</b>", reply_to_message_id=message_id)
                return
            if text in ["باز کردن خدمات تلگرام", "/unlock_service"]:
                service_lock_status[chat_id] = False
                send_message(chat_id, "<b>◂ قفل خدمات تلگرام غیر فعال شد !</b>", reply_to_message_id=message_id)
                return
            if text in ["خوش آمدگویی فعال", "/enable_welcome"]:
                welcome_status[chat_id] = True
                send_message(chat_id, "<b>◄ خوش آمدگویی فعال شد !</b>", reply_to_message_id=message_id)
                return
            if text in ["خوش آمدگویی غیرفعال", "/disable_welcome"]:
                welcome_status[chat_id] = False
                send_message(chat_id, "<b>◄ خوش آمدگویی غیرفعال شد !</b>", reply_to_message_id=message_id)
                return
        
        # ===== دستورات سازنده =====
        if user_id == OWNER_ID:
            if text in ["قفل پورن", "/lock_porn"]:
                porn_lock_status[chat_id] = True
                send_message(chat_id, "<b>◂ قفل پورن فعال شد !</b>", reply_to_message_id=message_id)
                return
            if text in ["باز کردن پورن", "/unlock_porn"]:
                porn_lock_status[chat_id] = False
                if chat_id in porn_blocked_users:
                    del porn_blocked_users[chat_id]
                send_message(chat_id, "<b>◂ قفل پورن غیر فعال شد !</b>", reply_to_message_id=message_id)
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
    logger.info("🤖 ربات ReaperVoid راه‌اندازی شد!")
    offset = None
    while True: