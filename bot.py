import requests
import time
import logging
import json

TOKEN = "8532288807:AAGJXJnmHJ68Cyh7eMK9muIcZydKAZLayVQ"
BASE_URL = f"https://api.telegram.org/bot{TOKEN}"

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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

def get_unknown_text():
    return """
❌ <b>متاسفانه قادر به درخواست شما نیستم!</b>

🔰 لطفاً برای مشاهده منوی اصلی و دریافت اطلاعات کامل ربات، 
دستور <b>/start</b> را ارسال کنید.

📌 ما همیشه در کنار شما هستیم!
"""

# ==================== کیبورد ====================

def get_main_keyboard():
    """دکمه‌های منوی اصلی با چیدمان جدید"""
    keyboard = [
        # ردیف 1: یک دکمه (اضافه کردن به گروه)
        [
            {"text": "➕ اضافه کردن به گروه", "url": "https://t.me/ReaperVoidbot?startgroup=new"}
        ],
        # ردیف 2: دو دکمه (اطلاعات بیشتر، تفاوت رایگان با اشتراکی)
        [
            {"text": "📓 اطلاعات بیشتر", "callback_data": "info"},
            {"text": "🦾 تفاوت رایگان با اشتراکی", "callback_data": "compare"}
        ],
        # ردیف 3: یک دکمه (راهنمای تست)
        [
            {"text": "🗒 راهنمای تست", "callback_data": "test"}
        ],
        # ردیف 4: یک دکمه (نرخ ربات)
        [
            {"text": "💎 نرخ ربات", "callback_data": "price"}
        ],
        # ردیف 5: دو دکمه (پشتیبانی و گروه پشتیبانی)
        [
            {"text": "👨‍💻 پشتیبانی", "url": "https://t.me/XMrAmer"},
            {"text": "💬 گروه پشتیبانی", "url": "https://t.me/ReaperVoidGP"}
        ],
        # ردیف 6: یک دکمه (کانال ربات)
        [
            {"text": "📢 کانال ربات", "url": "https://t.me/ReaperVoidTM"}
        ]
    ]
    return json.dumps({"inline_keyboard": keyboard})

def get_back_keyboard():
    """دکمه بازگشت به منوی اصلی"""
    keyboard = [
        [{"text": "🔙 بازگشت به منوی اصلی", "callback_data": "back"}]
    ]
    return json.dumps({"inline_keyboard": keyboard})

# ==================== توابع تلگرام ====================

def send_message_with_keyboard(chat_id, text, keyboard, reply_to_message_id=None):
    """ارسال پیام با ریپلای به پیام مشخص"""
    url = f"{BASE_URL}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "HTML",
        "disable_web_page_preview": True,
        "reply_markup": keyboard
    }
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

def edit_message_text(chat_id, message_id, text, keyboard=None):
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

def answer_callback_query(callback_id, text=None):
    url = f"{BASE_URL}/answerCallbackQuery"
    payload = {"callback_query_id": callback_id}
    if text:
        payload["text"] = text
        payload["show_alert"] = False
    try:
        requests.post(url, json=payload)
    except Exception as e:
        logger.error(f"خطا در پاسخ کال‌بک: {e}")

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

# ==================== اصلی ====================

def main():
    logger.info("🤖 ربات با موفقیت راه‌اندازی شد!")
    logger.info("📡 در حال گوش دادن به پیام‌ها...")
    
    offset = None
    while True:
        try:
            updates = get_updates(offset)
            for update in updates:
                offset = update["update_id"] + 1
                
                if "message" in update:
                    message = update["message"]
                    chat_id = message["chat"]["id"]
                    message_id = message["message_id"]
                    user = message.get("from", {})
                    user_id = user.get("id", 0)
                    first_name = user.get("first_name", "کاربر")
                    
                    if "text" in message:
                        text = message.get("text", "")
                        
                        if text == "/start":
                            start_text = get_start_text(user_id, first_name)
                            keyboard = get_main_keyboard()
                            send_message_with_keyboard(chat_id, start_text, keyboard, reply_to_message_id=message_id)
                            logger.info(f"📨 ارسال استارت با ریپلای به {first_name}")
                        else:
                            # پاسخ به پیام‌های ناشناخته
                            unknown_text = get_unknown_text()
                            send_message_with_keyboard(chat_id, unknown_text, None, reply_to_message_id=message_id)
                            logger.info(f"❌ پاسخ به پیام ناشناخته از {first_name}")
                
                if "callback_query" in update:
                    callback = update["callback_query"]
                    callback_id = callback["id"]
                    chat_id = callback["message"]["chat"]["id"]
                    message_id = callback["message"]["message_id"]
                    data = callback.get("data", "")
                    
                    if data == "back":
                        user = callback.get("from", {})
                        user_id = user.get("id", 0)
                        first_name = user.get("first_name", "کاربر")
                        text = get_start_text(user_id, first_name)
                        keyboard = get_main_keyboard()
                        edit_message_text(chat_id, message_id, text, keyboard)
                        answer_callback_query(callback_id)
                    
                    elif data == "info":
                        edit_message_text(chat_id, message_id, get_info_text(), get_back_keyboard())
                        answer_callback_query(callback_id)
                    
                    elif data == "test":
                        edit_message_text(chat_id, message_id, get_test_guide_text(), get_back_keyboard())
                        answer_callback_query(callback_id)
                    
                    elif data == "compare":
                        edit_message_text(chat_id, message_id, get_compare_text(), get_back_keyboard())
                        answer_callback_query(callback_id)
                    
                    elif data == "price":
                        edit_message_text(chat_id, message_id, get_price_text(), get_back_keyboard())
                        answer_callback_query(callback_id)
                        
        except Exception as e:
            logger.error(f"خطا در حلقه اصلی: {e}")
        time.sleep(1)

if __name__ == "__main__":
    main()