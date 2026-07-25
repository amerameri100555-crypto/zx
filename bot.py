import requests
import time
import logging

TOKEN = "8532288807:AAGJXJnmHJ68Cyh7eMK9muIcZydKAZLayVQ"
BASE_URL = f"https://api.telegram.org/bot{TOKEN}"

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_start_text(user_id, first_name):
    return f"""
🌟 <b>سلام بر تو <a href="tg://user?id={user_id}">{first_name} عزیز</a></b> 🌹

💬 من رباتی هوشمند و قدرتمند برای مدیریت حرفه‌ای گروه‌های تلگرامی هستم!

⫸ برتری‌های انحصاری من :

◄ مجهز به <b>پیشرفته‌ترین هوش مصنوعی</b> روز دنیا
◄ <b>فیلتر قوی</b> تشخیص محتوای نامناسب
◄ <b>سیستم امنیتی</b> در برابر ربات‌های مخرب
◄ <b>پاکسازی گروه</b> در کسری از ثانیه
◄ محافظت از گروه در برابر <b>مدیران نفوذی</b>
◄ <b>سیستم ضدترک</b> گروه
◄ <b>درآمدزایی هوشمند</b> از گروه
◄ شناسایی <b>کاربران مشکوک</b>

⫸ ویژگی‌های منحصربفرد :

◂ <b>۹۹.۹٪ آپتایم</b>
◂ <b>هاست قدرتمند</b> و اختصاصی
◂ <b>سرعت بی‌نظیر</b> در گروه‌های سنگین
◂ <b>پایداری</b> در برابر حملات
◂ <b>قفل‌های متنوع</b> و حرفه‌ای
◂ احوالپرسی <b>اتوماتیک و هوشمند</b>
◂ قابلیت <b>اضافه کردن اجباری</b>
◂ <b>گزارش‌گیری دقیق</b> و روزانه
◂ <b>دوره تست</b> برای اطمینان
◂ کاملاً <b>بدون تبلیغات</b> مزاحم

⫸ ما شبیه هیچکس نیستیم!

◄ <b>امنیت گروه</b>، اولویت اول ماست
◄ <b>کیفیت</b>، حرف اول را می‌زند
◄ <b>سرعت</b>، مزیت رقابتی ماست

⫸ چرا به ما اعتماد کنیم؟

◂ <b>پردازش فوق‌سریع</b>
◂ <b>پاسخگویی آنی</b>
◂ <b>آپدیت‌های مستمر</b>
◂ <b>پشتیبانی حرفه‌ای</b>

⫸ همین حالا سفارش بده!
 
🖥️ ساخته شده توسط <b>تیم ZX</b>

⫸ تذکر حقوقی :

◄ تمامی ایده‌ها و کدهای این ربات متعلق به <b>تیم ZX</b> بوده و هر گونه کپی‌برداری یا تقلید، <b>پیگرد قانونی</b> دارد. حقوق مادی و معنوی محفوظ است.

✨ <b>با ما، گروهتو به اوج برسون!</b> ✨
"""

def send_message(chat_id, text):
    url = f"{BASE_URL}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "HTML",
        "disable_web_page_preview": True
    }
    try:
        response = requests.post(url, json=payload)
        if response.status_code != 200:
            logger.error(f"خطا: {response.text}")
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
                        send_message(chat_id, text)
                        logger.info(f"📨 ارسال استارت به {first_name}")
        except Exception as e:
            logger.error(f"خطا: {e}")
        time.sleep(1)

if __name__ == "__main__":
    main()