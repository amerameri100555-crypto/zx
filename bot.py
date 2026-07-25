import requests
import time
import logging
import json

TOKEN = "8532288807:AAGJXJnmHJ68Cyh7eMK9muIcZydKAZLayVQ"
BASE_URL = f"https://api.telegram.org/bot{TOKEN}"

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# متن استارت
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
"""

# متن اطلاعات تکمیلی
def get_info_text():
    return """
📋 <b>اطلاعات تکمیلی درباره ربات ReaperVoid :</b>

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

─┅━━━━✦━━━━┅─

👨‍💻 جهت مشاوره و نصب :

🆔 @MrNasiB
"""

def get_inline_keyboard():
    """ساخت دکمه‌های شیشه‌ای"""
    keyboard = [
        [
            {"text": "📢 کانال ربات", "url": "https://t.me/ReaperVoidTM"},
            {"text": "👨‍💻 ارتباط با پشتیبانی", "url": "https://t.me/XMrAmer"}
        ],
        [
            {"text": "➕ اضافه کردن به گروه", "url": "https://t.me/ReaperVoidbot?startgroup=new"},
            {"text": "💬 گروه پشتیبانی", "url": "https://t.me/ReaperVoidGP"}
        ],
        [
            {"text": "📋 اطلاعات تکمیلی", "callback_data": "info"}
        ]
    ]
    return json.dumps({"inline_keyboard": keyboard})

def send_message_with_keyboard(chat_id, text, keyboard):
    """ارسال پیام با دکمه‌های شیشه‌ای"""
    url = f"{BASE_URL}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "HTML",
        "disable_web_page_preview": True,
        "reply_markup": keyboard
    }
    try:
        response = requests.post(url, json=payload)
        if response.status_code != 200:
            logger.error(f"خطا در ارسال پیام: {response.text}")
        return response
    except Exception as e:
        logger.error(f"خطا: {e}")
        return None

def edit_message_text(chat_id, message_id, text, keyboard=None):
    """ویرایش پیام (برای دکمه‌های کال‌بک)"""
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
            logger.error(f"خطا در ویرایش پیام: {response.text}")
        return response
    except Exception as e:
        logger.error(f"خطا: {e}")
        return None

def answer_callback_query(callback_id, text=None):
    """پاسخ به کال‌بک کوئری"""
    url = f"{BASE_URL}/answerCallbackQuery"
    payload = {"callback_query_id": callback_id}
    if text:
        payload["text"] = text
        payload["show_alert"] = False
    try:
        requests.post(url, json=payload)
    except Exception as e:
        logger.error(f"خطا در پاسخ به کال‌بک: {e}")

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

def main():
    logger.info("🤖 ربات با موفقیت راه‌اندازی شد!")
    logger.info("📡 در حال گوش دادن به پیام‌ها...")
    
    offset = None
    while True:
        try:
            updates = get_updates(offset)
            for update in updates:
                offset = update["update_id"] + 1
                
                # مدیریت پیام‌ها
                if "message" in update:
                    message = update["message"]
                    chat_id = message["chat"]["id"]
                    user = message.get("from", {})
                    user_id = user.get("id", 0)
                    first_name = user.get("first_name", "کاربر")
                    
                    if "text" in message and message["text"] == "/start":
                        text = get_start_text(user_id, first_name)
                        keyboard = get_inline_keyboard()
                        send_message_with_keyboard(chat_id, text, keyboard)
                        logger.info(f"📨 ارسال استارت به {first_name}")
                
                # مدیریت کال‌بک‌ها (دکمه‌های شیشه‌ای)
                if "callback_query" in update:
                    callback = update["callback_query"]
                    callback_id = callback["id"]
                    chat_id = callback["message"]["chat"]["id"]
                    message_id = callback["message"]["message_id"]
                    data = callback.get("data", "")
                    
                    if data == "info":
                        info_text = get_info_text()
                        # ارسال پیام جدید با اطلاعات تکمیلی
                        keyboard_back = json.dumps({
                            "inline_keyboard": [
                                [{"text": "🔙 بازگشت به منوی اصلی", "callback_data": "back"}]
                            ]
                        })
                        # ویرایش پیام فعلی به اطلاعات تکمیلی
                        edit_message_text(chat_id, message_id, info_text, keyboard_back)
                        answer_callback_query(callback_id)
                        logger.info(f"📨 نمایش اطلاعات تکمیلی به {chat_id}")
                    
                    elif data == "back":
                        # بازگشت به منوی اصلی
                        user = callback.get("from", {})
                        user_id = user.get("id", 0)
                        first_name = user.get("first_name", "کاربر")
                        start_text = get_start_text(user_id, first_name)
                        keyboard = get_inline_keyboard()
                        edit_message_text(chat_id, message_id, start_text, keyboard)
                        answer_callback_query(callback_id)
                        logger.info(f"🔙 بازگشت به منوی اصلی {chat_id}")
                        
        except Exception as e:
            logger.error(f"خطا در حلقه اصلی: {e}")
        time.sleep(1)

if __name__ == "__main__":
    main()