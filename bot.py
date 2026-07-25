import requests
import time

TOKEN = "8532288807:AAGJXJnmHJ68Cyh7eMK9muIcZydKAZLayVQ"
BASE_URL = f"https://api.telegram.org/bot{TOKEN}"

START_TEXT = """
🌟 سلام بر تو XMrAmer عزیز 🌹

💬 من رباتی هوشمند و قدرتمند برای مدیریت حرفه‌ای گروه‌های تلگرامی هستم!

⫸ برتری‌های انحصاری من :

◄ مجهز به پیشرفته‌ترین هوش مصنوعی روز دنیا
◄ فیلتر قوی تشخیص محتوای نامناسب
◄ سیستم امنیتی در برابر ربات‌های مخرب
◄ پاکسازی گروه در کسری از ثانیه
◄ محافظت از گروه در برابر مدیران نفوذی
◄ سیستم ضدترک گروه
◄ درآمدزایی هوشمند از گروه
◄ شناسایی کاربران مشکوک

⫸ ویژگی‌های منحصربفرد :

◂ ۹۹.۹٪ آپتایم
◂ هاست قدرتمند و اختصاصی
◂ سرعت بی‌نظیر در گروه‌های سنگین
◂ پایداری در برابر حملات
◂ قفل‌های متنوع و حرفه‌ای
◂ احوالپرسی اتوماتیک و هوشمند
◂ قابلیت اضافه کردن اجباری
◂ گزارش‌گیری دقیق و روزانه
◂ دوره تست برای اطمینان
◂ کاملاً بدون تبلیغات مزاحم

⫸ ما شبیه هیچکس نیستیم!

◄ امنیت گروه، اولویت اول ماست
◄ کیفیت، حرف اول را می‌زند
◄ سرعت، مزیت رقابتی ماست

⫸ چرا به ما اعتماد کنیم؟

◂ پردازش فوق‌سریع
◂ پاسخگویی آنی
◂ آپدیت‌های مستمر
◂ پشتیبانی حرفه‌ای

⫸ همین حالا سفارش بده!
 
🖥️ ساخته شده توسط تیم ZX

⫸ تذکر حقوقی :

◄ تمامی ایده‌ها و کدهای این ربات متعلق به تیم ZX بوده و هر گونه کپی‌برداری یا تقلید، پیگرد قانونی دارد. حقوق مادی و معنوی محفوظ است.

✨ با ما، گروهتو به اوج برسون! ✨
"""

def send_message(chat_id, text):
    url = f"{BASE_URL}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "HTML"
    }
    requests.post(url, json=payload)

def get_updates(offset=None):
    url = f"{BASE_URL}/getUpdates"
    params = {"timeout": 30, "offset": offset}
    response = requests.get(url, params=params)
    return response.json().get("result", [])

def main():
    print("🤖 ربات با موفقیت راه‌اندازی شد!")
    offset = None
    while True:
        try:
            updates = get_updates(offset)
            for update in updates:
                offset = update["update_id"] + 1
                if "message" in update:
                    message = update["message"]
                    chat_id = message["chat"]["id"]
                    if "text" in message and message["text"] == "/start":
                        send_message(chat_id, START_TEXT)
        except Exception as e:
            print(f"Error: {e}")
        time.sleep(1)

if __name__ == "__main__":
    main()