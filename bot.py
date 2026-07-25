import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext

# توکن ربات
TOKEN = "8532288807:AAGJXJnmHJ68Cyh7eMK9muIcZydKAZLayVQ"

# فعال کردن لاگ
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# متن استارت با فرمت بولد و برجسته (از HTML استفاده میکنیم)
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
    """ارسال متن استارت با ریپلای به کاربر"""
    user = update.effective_user
    # ریپلای به پیام استارت کاربر
    update.message.reply_text(
        START_TEXT,
        parse_mode='HTML',  # استفاده از HTML برای بولد و برجسته کردن
        disable_web_page_preview=True
    )

def help_command(update: Update, context: CallbackContext):
    """دستور راهنما"""
    help_text = """
<b>🤖 راهنمای ربات مدیریت گروه</b>

◄ برای مشاهده اطلاعات ربات از دستور /start استفاده کنید
◄ برای مشاهده راهنما از دستور /help استفاده کنید

<b>⚠️ توجه:</b>
این ربات توسط تیم ZX ساخته شده و تمام حقوق آن محفوظ است.
"""
    update.message.reply_text(help_text, parse_mode='HTML')

def unknown(update: Update, context: CallbackContext):
    """پاسخ به پیام‌های ناشناخته"""
    update.message.reply_text(
        "❌ دستور نامعتبر!\nبرای مشاهده راهنما از /help استفاده کنید.",
        parse_mode='HTML'
    )

def error_handler(update, context):
    """مدیریت خطاها"""
    logger.warning('Update "%s" caused error "%s"', update, context.error)

def main():
    """تابع اصلی اجرای ربات"""
    # ساخت آپدیت‌ر با نسخه قدیمی
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher

    # افزودن هندلرها
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", help_command))
    
    # هندلر برای پیام‌های ناشناخته (به جز دستورات)
    dp.add_handler(MessageHandler(Filters.command, unknown))
    
    # هندلر خطا
    dp.add_error_handler(error_handler)

    # شروع ربات
    logger.info("🤖 ربات با موفقیت راه‌اندازی شد!")
    logger.info("📡 در حال گوش دادن به پیام‌ها...")
    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()