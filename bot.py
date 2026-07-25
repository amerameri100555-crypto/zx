import logging
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext

TOKEN = "8532288807:AAGJXJnmHJ68Cyh7eMK9muIcZydKAZLayVQ"

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

START_TEXT = """
🌟 <b>سلام بر تو XMrAmer عزیز</b> 🌹

💬 من رباتی هوشمند و قدرتمند برای مدیریت حرفه‌ای گروه‌های تلگرامی هستم!

⫸ <b>برتری‌های انحصاری من :</b>

◄ مجهز به پیشرفته‌ترین هوش مصنوعی روز دنیا
◄ فیلتر قوی تشخیص محتوای نامناسب
◄ سیستم امنیتی در برابر ربات‌های مخرب
◄ پاکسازی گروه در کسری از ثانیه
◄ محافظت از گروه در برابر مدیران نفوذی
◄ سیستم ضدترک گروه
◄ درآمدزایی هوشمند از گروه
◄ شناسایی کاربران مشکوک

⫸ <b>ویژگی‌های منحصربفرد :</b>

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

⫸ <b>ما شبیه هیچکس نیستیم!</b>

◄ امنیت گروه، اولویت اول ماست
◄ کیفیت، حرف اول را می‌زند
◄ سرعت، مزیت رقابتی ماست

⫸ <b>چرا به ما اعتماد کنیم؟</b>

◂ پردازش فوق‌سریع
◂ پاسخگویی آنی
◂ آپدیت‌های مستمر
◂ پشتیبانی حرفه‌ای

⫸ <b>همین حالا سفارش بده!</b>
 
🖥️ ساخته شده توسط <b>تیم ZX</b>

⫸ <b>تذکر حقوقی :</b>

◄ تمامی ایده‌ها و کدهای این ربات متعلق به تیم ZX بوده و هر گونه کپی‌برداری یا تقلید، پیگرد قانونی دارد. حقوق مادی و معنوی محفوظ است.

✨ <b>با ما، گروهتو به اوج برسون!</b> ✨
"""

def start(update: Update, context: CallbackContext):
    update.message.reply_text(START_TEXT, parse_mode='HTML', disable_web_page_preview=True)

def help_command(update: Update, context: CallbackContext):
    help_text = """
<b>🤖 راهنمای ربات مدیریت گروه</b>

◄ برای مشاهده اطلاعات ربات از دستور /start استفاده کنید
◄ برای مشاهده راهنما از دستور /help استفاده کنید

<b>⚠️ توجه:</b>
این ربات توسط تیم ZX ساخته شده و تمام حقوق آن محفوظ است.
"""
    update.message.reply_text(help_text, parse_mode='HTML')

def unknown(update: Update, context: CallbackContext):
    update.message.reply_text(
        "❌ دستور نامعتبر!\nبرای مشاهده راهنما از /help استفاده کنید.",
        parse_mode='HTML'
    )

def main():
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher
    
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", help_command))
    dp.add_handler(MessageHandler(Filters.command, unknown))
    
    logger.info("🤖 ربات با موفقیت راه‌اندازی شد!")
    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()