import requests
import time
import logging
import json

TOKEN = "8532288807:AAGJXJnmHJ68Cyh7eMK9muIcZydKAZLayVQ"
BASE_URL = f"https://api.telegram.org/bot{TOKEN}"

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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
                        
        except Exception as e:
            logger.error(f"خطا در حلقه اصلی: {e}")
        time.sleep(1)

if __name__ == "__main__":
    main()