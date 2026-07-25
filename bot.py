import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackContext, MessageHandler, filters

# توکن ربات
TOKEN = "8532288807:AAGJXJnmHJ68Cyh7eMK9muIcZydKAZLayVQ"

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

async def start(update: Update, context: CallbackContext):
    """ارسال متن استارت با ریپلای به کاربر"""
    user = update.effective_user
    # ریپلای به پیام استارت کاربر
    await update.message.reply_text(
        START_TEXT,
        parse_mode='HTML',  # استفاده از HTML برای بولد و برجسته کردن
        disable_web_page_preview=True
    )

async def help_command(update: Update, context: CallbackContext):
    """دستور راهنما"""
    help_text = """
<b>🤖 راهنمای ربات مدیریت گروه</b>

◄ برای مشاهده اطلاعات ربات از دستور /start استفاده کنید
◄ برای مشاهده راهنما از دستور /help استفاده کنید

<b>⚠️ توجه:</b>
این ربات توسط تیم ZX ساخته شده و تمام حقوق آن محفوظ است.
"""
    await update.message.reply_text(help_text, parse_mode='HTML')

async def unknown(update: Update, context: CallbackContext):
    """پاسخ به پیام‌های ناشناخته"""
    await update.message.reply_text(
        "❌ دستور نامعتبر!\nبرای مشاهده راهنما از /help استفاده کنید.",
        parse_mode='HTML'
    )

def main():
    """تابع اصلی اجرای ربات"""
    # ساخت اپلیکیشن
    application = Application.builder().token(TOKEN).build()

    # افزودن هندلرها
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    
    # هندلر برای پیام‌های ناشناخته (به جز دستورات)
    application.add_handler(MessageHandler(filters.COMMAND, unknown))
    
    # هندلر برای پیام‌های غیر از دستورات (اختیاری)
    # اگر میخواهید به همه پیام‌ها پاسخ دهد، این خط را فعال کنید
    # application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, unknown))

    # شروع ربات
    print("🤖 ربات با موفقیت راه‌اندازی شد!")
    print("📡 در حال گوش دادن به پیام‌ها...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()