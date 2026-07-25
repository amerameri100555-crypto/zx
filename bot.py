import requests
import time
import logging
import json
import jdatetime
from datetime import datetime
import base64
import io

TOKEN = "8532288807:AAGJXJnmHJ68Cyh7eMK9muIcZydKAZLayVQ"
BASE_URL = f"https://api.telegram.org/bot{TOKEN}"

# ==================== تنظیمات ====================
OWNER_ID = 7803165903  # فقط سازنده ربات
service_lock_status = {}  # {chat_id: True/False}
welcome_status = {}       # {chat_id: True/False}
porn_lock_status = {}     # {chat_id: True/False} - قفل پورن

# API تشخیص پورن (از سرویس رایگان استفاده میکنیم)
# برای این مثال از API سرویس DeepAI استفاده میکنیم (نیاز به API Key)
DEEPAI_API_KEY = "your-deepai-api-key"  # باید ثبت نام کنی و کلید بگیری
# یا از سرویس NSFW Detector استفاده کن

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# ==================== توابع تشخیص پورن ====================

def download_file(file_id):
    """دانلود فایل از تلگرام"""
    url = f"{BASE_URL}/getFile"
    payload = {"file_id": file_id}
    try:
        response = requests.post(url, json=payload)
        if response.status_code == 200:
            file_path = response.json().get("result", {}).get("file_path")
            if file_path:
                file_url = f"https://api.telegram.org/file/bot{TOKEN}/{file_path}"
                file_response = requests.get(file_url)
                if file_response.status_code == 200:
                    return file_response.content
        return None
    except Exception as e:
        logger.error(f"خطا در دانلود فایل: {e}")
        return None

def check_nsfw_image(image_bytes):
    """بررسی تصویر با API تشخیص پورن"""
    try:
        # روش 1: استفاده از DeepAI (رایگان - نیاز به ثبت نام)
        # ثبت نام در: https://deepai.org/dashboard/profile
        url = "https://api.deepai.org/api/nsfw-detector"
        files = {'image': ('image.jpg', image_bytes, 'image/jpeg')}
        headers = {'api-key': DEEPAI_API_KEY}
        response = requests.post(url, files=files, headers=headers)
        
        if response.status_code == 200:
            result = response.json()
            nsfw_score = result.get("output", {}).get("nsfw_score", 0)
            # اگر نمره بیشتر از 0.7 باشه، محتوا پورن محسوب میشه
            return nsfw_score > 0.7
        else:
            logger.error(f"خطا در API تشخیص پورن: {response.text}")
            return False
            
    except Exception as e:
        logger.error(f"خطا در تشخیص پورن: {e}")
        return False

def check_nsfw_video(file_bytes):
    """بررسی ویدیو (با نمونه‌گیری از فریم‌ها)"""
    # اینجا میتونیم از کتابخانه‌های OpenCV برای استخراج فریم استفاده کنیم
    # یا از APIهای تشخیص ویدیو
    # فعلاً یک بررسی ساده
    return False  # برای پیاده‌سازی کامل نیاز به کتابخانه‌های بیشتر داریم

def check_nsfw_animation(file_bytes):
    """بررسی گیف/انیمیشن"""
    # مشابه ویدیو
    return False

def is_nsfw_media(file_id, file_type):
    """تشخیص محتوای پورن بر اساس نوع فایل"""
    file_bytes = download_file(file_id)
    if not file_bytes:
        return False
    
    if file_type in ["photo"]:
        return check_nsfw_image(file_bytes)
    elif file_type in ["video", "video_note"]:
        return check_nsfw_video(file_bytes)
    elif file_type in ["animation"]:
        return check_nsfw_animation(file_bytes)
    elif file_type in ["sticker"]:
        # استیکرها رو هم بررسی میکنیم (اگه تصویر باشن)
        return check_nsfw_image(file_bytes)
    return False

# ==================== متن‌ها ====================

def get_start_text(user_id, first_name):
    return f"""
🌟 <b>سلام بر تو <a href="tg://user?id={user_id}">{first_name}</a> عزیز</b> 🌹

💬 من رباتی هوشمند و قدرتمند برای مدیریت حرفه‌ای گروه‌های تلگرامی هستم!

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
    now = datetime.now()
    jalali = jdatetime.datetime.fromgregorian(datetime=now)
    weekdays = {6: 'شنبه', 0: 'یکشنبه', 1: 'دوشنبه', 2: 'سه‌شنبه', 3: 'چهارشنبه', 4: 'پنج‌شنبه', 5: 'جمعه'}
    weekday_name = weekdays.get(jalali.weekday(), '')
    date_str = f"{weekday_name} {jalali.day} - {jalali.month} - {jalali.year}"
    time_str = f"{jalali.hour:02d}:{jalali.minute:02d}:{jalali.second:02d}"
    
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

✅ این ربات بر روی <b>سرورهای اختصاصی و باکیفیت آمستردام هلند</b> مستقر شده است که کمترین پینگ را به سرورهای تلگرام دارند و این امر موجب پردازش فوق‌سریع اطلاعات در گروه‌های بزرگ میشود.

✅ هدف اصلی ما، <b>حفاظت کامل از گروه شما</b> در تمامی ابعاد است. برخلاف بسیاری از ربات‌های دیگر، هرگز تبلیغاتی در گروه شما ارسال نخواهد شد و از این راه درآمدی کسب نمیکنیم، زیرا ارزش گروه شما برای ما بسیار بالاتر از این مسائل است.

✅ هیچگونه دسترسی یا سوءاستفاده‌ای از گروه شما توسط ربات انجام نخواهد شد و شما میتوانید با اطمینان کامل از خدمات ما استفاده کنید.

✅ تمامی قابلیت‌های کاربردی و مورد نیاز برای انواع گروه‌ها در این ربات پیاده‌سازی شده است و همچنین در صورت درخواست ویژگی جدید از سوی مشتریان، در سریعترین زمان ممکن به ربات اضافه میشود.

✅ ربات ReaperVoid همواره در حال <b>به‌روزرسانی و توسعه</b> است و تلاش میکنیم بهترین و ساده‌ترین خدمات را به مشتریان عزیز ارائه دهیم.

✅ سیستم <b>پاکسازی پیام‌ها</b> در این ربات بسیار پیشرفته طراحی شده و قادر است تمامی پیام‌های گروه را از ابتدای تاسیس تا امروز، در کمتر از ۳ ثانیه حذف کند.

✅ سیستم <b>تشخیص ربات‌های مخرب و تبلیغ‌دهنده</b> با دقت بالایی طراحی شده و با کمترین درصد خطا، تمامی ربات‌های مزاحم را شناسایی و از گروه شما محدود یا اخراج میکند.

✅ مشتریان برای ما در اولویت هستند و هرگز شما را در مواجهه با مشکلات و سوالات تنها نمیگذاریم. تیم پشتیبانی ما در تمام ساعات شبانه‌روز در کنار شماست.

✅ تمامی فعالیت‌های گروه تحت نظارت کامل ربات قرار دارد و شما میتوانید در هر زمان، <b>گزارشات دقیق و آماری</b> از عملکرد گروه خود دریافت کنید.

✅ دستورات ربات به دو زبان <b>فارسی و انگلیسی</b> طراحی شده و سعی شده در نهایت سادگی باشد. همچنین یک <b>پنل مدیریتی شیشه‌ای (Inline Panel)</b> در ربات تعبیه شده که تمامی تنظیمات گروه را به راحتی در اختیار شما قرار میدهد.

✅ این ربات توسط <b>تیم حرفه‌ای و با‌سابقه ZX</b> توسعه یافته و هدف ما ایجاد امنیت و سهولت در مدیریت گروه‌های شماست. ربات ReaperVoid همواره چندین قدم از سایر ربات‌های مشابه جلوتر است و از هیچ نظر عقب نخواهد ماند.
"""

def get_test_guide_text():
    return """
🗒 <b>راهنمای تست ربات ReaperVoid</b>

💎 برای آشنایی با قدرت و برتری ربات ReaperVoid نسبت به سایر ربات‌های مدیریت گروه، امکان تست <b>۳ روزه</b> تمامی قابلیت‌ها به صورت <b>کاملاً رایگان</b> فراهم شده است.

🔰 <b>شرایط استفاده از طرح تست :</b>

📌 گروه شما حداقل <b>۳۰ عضو فعال</b> داشته باشد.

📌 تا به حال از هیچ ربات تیم ZX استفاده نکرده باشید (مشتری جدید باشید).

📌 گروه شما شامل موارد زیر نباشد :

⛔️ گروه‌های سیاسی و اعتراضی
⛔️ گروه‌های مستهجن و غیراخلاقی
⛔️ گروه‌های شرط‌بندی و قمار
⛔️ گروه‌های توهین‌آمیز به ادیان
⛔️ گروه‌های کلاهبرداری و فیشینگ
⛔️ گروه‌های فروش کالای قاچاق

✅ <b>نصب ربات در ۳ مرحله ساده :</b>

1️⃣ مرحله اول : اضافه کردن ربات به گروه

2️⃣ مرحله دوم : ادمین کردن ربات با تمام دسترسی‌ها (به جز ادمین مخفی)

3️⃣ مرحله سوم : تنظیم قفل‌ها و حالت‌های مورد نظر

✳️ توجه داشته باشید که برای ارائه بهترین خدمات، این ربات دارای یک <b>ربات مکمل (Cli)</b> است که به صورت خودکار همراه با ربات اصلی نصب و ادمین میشود.

⚠️ <b>تذکر مهم :</b> قبل از نصب ربات ما، مطمئن شوید هیچ ربات دیگری در گروه حضور ندارد، زیرا ربات‌های دیگر ممکن است با ربات ما تداخل داشته باشند. در صورت عدم دریافت پیام پس از نصب، ربات را حذف و مجدداً اضافه کنید.

🧑🏻‍💻 در صورت نیاز به کمک در نصب، کافیست به <b>پشتیبانی</b> مراجعه کنید تا در سریع‌ترین زمان، ربات توسط تیم ما در گروه شما نصب و تنظیم شود ❤️
"""

def get_compare_text():
    return """
🦾 <b>تفاوت ربات رایگان با اشتراکی</b>

📘 اطلاعاتی که هر صاحب گروهی باید درباره انواع ربات‌های مدیریت گروه بداند !

در این مقاله به طور کامل به بررسی تفاوت‌های اساسی بین ربات‌های رایگان و اشتراکی می‌پردازیم :

💫 <b>ربات اشتراکی</b> یعنی رباتی که با پرداخت هزینه، به صورت حرفه‌ای و بدون هیچگونه تبلیغاتی در اختیار شما قرار می‌گیرد.

🔖 <b>بررسی جامع تفاوت‌ها :</b>

┅┅┅┅┅┅┅┅┅┅┅┅┅

✅ <b>ربات‌های رایگان :</b>

این ربات‌ها معمولاً توسط برنامه‌نویسان نیمه‌حرفه‌ای نوشته می‌شوند و هدف اصلی آنها <b>درآمدزایی از طریق تبلیغات</b> در گروه شماست. این ربات‌ها حداقل روزی ۲ بار (هر ۱۲ ساعت یکبار) پیام‌های تبلیغاتی شامل لینک‌های کانال‌های لینک‌دونی، تبلیغ تلگرام‌های غیررسمی، فروش محصولات نامرغوب و ... در گروه شما ارسال می‌کنند.

⚠️ <b>خطرناک‌ترین نوع تبلیغ :</b> تلگرام‌های غیررسمی که با نصب آنها، کاربر توسط مدیران ربات کنترل شده و بدون رضایت خود، وارد گروه‌های مختلف شده یا پیام‌های ناخواسته ارسال می‌کند.

در ربات‌های رایگان، فقط <b>ظاهر سازی</b> شده و باطن قابل قبولی ندارند. هدف اصلی آنها افزایش تعداد گروه‌ها برای بالا بردن بازدید تبلیغات است. به دلیل تمرکز مدیران روی درآمدزایی، این ربات‌ها از نظر <b>کیفیت و قابلیت‌ها در سطح بسیار پایین‌تری</b> نسبت به ربات‌های اشتراکی قرار دارند.

┅┅┅┅┅┅┅┅┅┅┅┅┅

💎 <b>ربات اشتراکی ReaperVoid (تیم ZX) :</b>

در مقابل، ربات <b>اشتراکی ReaperVoid</b> توسط <b>تیم حرفه‌ای و با‌سابقه ZX</b> طراحی و توسعه یافته است. تفاوت‌های اساسی عبارتند از :

◄ <b>بدون تبلیغات :</b> هرگز تبلیغاتی در گروه شما ارسال نمی‌شود و از این راه درآمدی کسب نمی‌کنیم.

◄ <b>سرعت فوق‌العاده :</b> با سرورهای اختصاصی آمستردام، پردازش در کسری از ثانیه انجام می‌شود.

◄ <b>قابلیت‌های پیشرفته :</b> شامل هوش مصنوعی، ضدپورن، ضدربات، ضدخیانت، ضدترک، پاکسازی سریع و ده‌ها قابلیت دیگر.

◄ <b>پشتیبانی ۲۴/۷ :</b> تیم پشتیبانی ما در تمام ساعات شبانه‌روز در کنار شماست.

◄ <b>آپدیت مادام‌العمر :</b> ربات همیشه به‌روز و پیشرفته‌تر از رقبا.

◄ <b>امنیت کامل :</b> هیچگونه سوءاستفاده‌ای از گروه شما انجام نمی‌شود.

◄ <b>پنل مدیریتی شیشه‌ای :</b> تنظیمات گروه به ساده‌ترین شکل ممکن.

┅┅┅┅┅┅┅┅┅┅┅┅┅

📌 با توجه به قدرت خرید مردم، ربات‌های رایگان به سرعت در گروه‌ها پخش می‌شوند اما این به معنای کیفیت بالای آنها نیست. همیشه تعداد ماشین‌های بی‌کیفیت در خیابان بیشتر از ماشین‌های باکیفیت است!

💎 <b>انتخاب با شماست :</b> کیفیت و امنیت یا تبلیغات و مشکلات؟

🔰 <b>با ReaperVoid ، گروه خود را به سطح بعدی ببرید!</b>
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

💳 برای خرید و اطلاع از تخفیف‌های ویژه با پشتیبانی تماس بگیرید.

🆔 @XMrAmer
"""

# ==================== کیبوردها ====================

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

# ==================== توابع تلگرام ====================

def send_message(chat_id, text, keyboard=None, reply_to_message_id=None):
    url = f"{BASE_URL}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "HTML",
        "disable_web_page_preview": True
    }
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
    payload = {
        "chat_id": chat_id,
        "message_id": message_id,
        "text": text,
        "parse_mode": "HTML",
        "disable_web_page_preview": True
    }
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

def is_admin(chat_id, user_id):
    member = get_chat_member(chat_id, user_id)
    status = member.get("status", "")
    return status in ["creator", "administrator"]

def get_updates(offset=None):
    url = f"{BASE_URL}/getUpdates"
    params = {"timeout": 30, "offset": offset}
    try:
        response = requests.get(url, params=params)
        if response.status_code == 200:
            return response.json().get("result", [])
        return []
    except Exception as e:
        logger.error(f"خطا: {e}")
        return []

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
    
    # ===== مدیریت در گروه‌ها =====
    if chat_type in ["group", "supergroup"]:
        
        # ===== قفل پورن - بررسی رسانه‌ها =====
        if porn_lock_status.get(chat_id, False):
            # بررسی عکس
            if "photo" in message:
                photo = message["photo"][-1]  # آخرین (بزرگترین) سایز
                file_id = photo["file_id"]
                if is_nsfw_media(file_id, "photo"):
                    delete_message(chat_id, message_id)
                    send_message(chat_id, f"❌ <b>محتوای نامناسب حذف شد!</b>\n👤 کاربر: {first_name}")
                    logger.info(f"🔞 محتوای پورن حذف شد از {first_name} در گروه {chat_id}")
                    return
            
            # بررسی ویدیو
            if "video" in message:
                file_id = message["video"]["file_id"]
                if is_nsfw_media(file_id, "video"):
                    delete_message(chat_id, message_id)
                    send_message(chat_id, f"❌ <b>ویدیوی نامناسب حذف شد!</b>\n👤 کاربر: {first_name}")
                    logger.info(f"🔞 ویدیوی پورن حذف شد از {first_name} در گروه {chat_id}")
                    return
            
            # بررسی گیف/انیمیشن
            if "animation" in message:
                file_id = message["animation"]["file_id"]
                if is_nsfw_media(file_id, "animation"):
                    delete_message(chat_id, message_id)
                    send_message(chat_id, f"❌ <b>گیف نامناسب حذف شد!</b>\n👤 کاربر: {first_name}")
                    logger.info(f"🔞 گیف پورن حذف شد از {first_name} در گروه {chat_id}")
                    return
            
            # بررسی استیکر
            if "sticker" in message:
                file_id = message["sticker"]["file_id"]
                if is_nsfw_media(file_id, "sticker"):
                    delete_message(chat_id, message_id)
                    send_message(chat_id, f"❌ <b>استیکر نامناسب حذف شد!</b>\n👤 کاربر: {first_name}")
                    logger.info(f"🔞 استیکر پورن حذف شد از {first_name} در گروه {chat_id}")
                    return
            
            # بررسی ویدیو نوت
            if "video_note" in message:
                file_id = message["video_note"]["file_id"]
                if is_nsfw_media(file_id, "video_note"):
                    delete_message(chat_id, message_id)
                    send_message(chat_id, f"❌ <b>ویدیو نوت نامناسب حذف شد!</b>\n👤 کاربر: {first_name}")
                    logger.info(f"🔞 ویدیو نوت پورن حذف شد از {first_name} در گروه {chat_id}")
                    return
        
        # ===== پردازش پیام‌های خدماتی =====
        if service_lock_status.get(chat_id, False):
            if "new_chat_members" in message:
                for member in message["new_chat_members"]:
                    member_name = member.get("first_name", "کاربر")
                    member_id = member.get("id")
                    delete_message(chat_id, message_id)
                    
                    if welcome_status.get(chat_id, True):
                        group_name = message.get("chat", {}).get("title", "گروه")
                        welcome_text = get_welcome_text(member_name, group_name, member_id)
                        send_message(chat_id, welcome_text)
                        logger.info(f"👋 خوش‌آمدگویی به {member_name} در گروه {group_name}")
                return
            
            if "left_chat_member" in message:
                delete_message(chat_id, message_id)
                logger.info(f"🚪 پیام خروج حذف شد")
                return
        
        elif welcome_status.get(chat_id, True):
            if "new_chat_members" in message:
                for member in message["new_chat_members"]:
                    member_name = member.get("first_name", "کاربر")
                    member_id = member.get("id")
                    group_name = message.get("chat", {}).get("title", "گروه")
                    welcome_text = get_welcome_text(member_name, group_name, member_id)
                    send_message(chat_id, welcome_text)
                    logger.info(f"👋 خوش‌آمدگویی به {member_name} در گروه {group_name}")
                return
        
        # ===== دستورات گروه =====
        # دستورات فقط برای ادمین‌ها
        if is_admin(chat_id, user_id):
            
            if text == "قفل خدمات تلگرام" or text == "/lock_service":
                service_lock_status[chat_id] = True
                response_text = "<b>◂ قفل خدمات تلگرام فعال شد !</b>"
                send_message(chat_id, response_text, reply_to_message_id=message_id)
                logger.info(f"🔒 قفل خدمات در گروه {chat_id} توسط {first_name} فعال شد")
                return
            
            if text == "باز کردن خدمات تلگرام" or text == "/unlock_service":
                service_lock_status[chat_id] = False
                response_text = "<b>◂ قفل خدمات تلگرام غیر فعال شد !</b>"
                send_message(chat_id, response_text, reply_to_message_id=message_id)
                logger.info(f"🔓 قفل خدمات در گروه {chat_id} توسط {first_name} غیرفعال شد")
                return
            
            if text == "خوش آمدگویی فعال" or text == "/enable_welcome":
                welcome_status[chat_id] = True
                response_text = "<b>◄ خوش آمدگویی فعال شد !</b>"
                send_message(chat_id, response_text, reply_to_message_id=message_id)
                logger.info(f"✅ خوش‌آمدگویی در گروه {chat_id} توسط {first_name} فعال شد")
                return
            
            if text == "خوش آمدگویی غیرفعال" or text == "/disable_welcome":
                welcome_status[chat_id] = False
                response_text = "<b>◄ خوش آمدگویی غیرفعال شد !</b>"
                send_message(chat_id, response_text, reply_to_message_id=message_id)
                logger.info(f"❌ خوش‌آمدگویی در گروه {chat_id} توسط {first_name} غیرفعال شد")
                return
        
        # ===== دستورات فقط برای سازنده ربات =====
        if user_id == OWNER_ID:
            
            if text == "قفل پورن" or text == "/lock_porn":
                porn_lock_status[chat_id] = True
                response_text = "<b>◂ قفل پورن فعال شد !</b>"
                send_message(chat_id, response_text, reply_to_message_id=message_id)
                logger.info(f"🔞 قفل پورن در گروه {chat_id} توسط سازنده فعال شد")
                return
            
            if text == "باز کردن پورن" or text == "/unlock_porn":
                porn_lock_status[chat_id] = False
                response_text = "<b>◂ قفل پورن غیر فعال شد !</b>"
                send_message(chat_id, response_text, reply_to_message_id=message_id)
                logger.info(f"🔞 قفل پورن در گروه {chat_id} توسط سازنده غیرفعال شد")
                return
        
        # ===== استارت در گروه =====
        if text == "/start":
            return
    
    # ===== مدیریت در پیوی =====
    elif chat_type == "private":
        
        if text == "/start":
            start_text = get_start_text(user_id, first_name)
            keyboard = get_main_keyboard()
            send_message(chat_id, start_text, keyboard, reply_to_message_id=message_id)
            logger.info(f"📨 ارسال استارت به {first_name} در پیوی")
            return
        
        if text:
            unknown_text = get_unknown_text()
            send_message(chat_id, unknown_text, None, reply_to_message_id=message_id)
            logger.info(f"❌ پاسخ به پیام ناشناخته از {first_name} در پیوی: {text}")
            return

def handle_callback(update):
    callback = update.get("callback_query", {})
    callback_id = callback.get("id")
    chat_id = callback.get("message", {}).get("chat", {}).get("id")
    message_id = callback.get("message", {}).get("message_id")
    data = callback.get("data", "")
    
    if not chat_id or not data:
        return
    
    logger.info(f"🔘 کال‌بک دریافت شد: {data} از {chat_id}")
    
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
        answer_callback(c