import logging
from datetime import datetime, timedelta
from config.settings import OWNER_ID, service_lock_status, welcome_status, porn_lock_status, porn_blocked_users
from modules.telegram_api import send_message, delete_message, get_chat_member
from modules.porn_detector import is_nsfw_media, is_user_blocked, get_block_message
from modules.welcome import get_welcome_text
from utils.texts import get_start_text, get_unknown_text
from handlers.callback_handler import get_main_keyboard

logger = logging.getLogger(__name__)

def is_admin(chat_id, user_id):
    member = get_chat_member(chat_id, user_id)
    status = member.get("status", "")
    return status in ["creator", "administrator"]

def handle_message(update):
    message = update.get("message", {})
    chat_id = message.get("chat", {}).get("id")
    message_id = message.get("message_id")
    chat_type = message.get("chat", {}).get("type")
    user = message.get("from", {})
    user_id = user.get("id", 0)
    first_name = user.get("first_name", "کاربر")
    text = message.get("text", "").strip()
    
    if not chat_id:
        return
    
    if chat_type in ["group", "supergroup"]:
        
        # ===== قفل پورن =====
        if porn_lock_status.get(chat_id, False):
            
            # اگر کاربر قبلاً محدود شده
            if is_user_blocked(chat_id, user_id):
                delete_message(chat_id, message_id)
                logger.info(f"🔞 کاربر {first_name} محدود شده، پیام حذف شد")
                return
            
            is_nsfw = False
            file_type = None
            file_id = None
            
            # بررسی عکس
            if "photo" in message:
                photo = message["photo"][-1]
                file_id = photo["file_id"]
                file_type = "photo"
                is_nsfw = is_nsfw_media(file_id, file_type, text)
            
            # بررسی استیکر
            elif "sticker" in message:
                file_id = message["sticker"]["file_id"]
                file_type = "sticker"
                is_nsfw = is_nsfw_media(file_id, file_type, text)
            
            # بررسی ویدیو
            elif "video" in message:
                file_id = message["video"]["file_id"]
                file_type = "video"
                is_nsfw = is_nsfw_media(file_id, file_type, text)
            
            # بررسی گیف
            elif "animation" in message:
                file_id = message["animation"]["file_id"]
                file_type = "animation"
                is_nsfw = is_nsfw_media(file_id, file_type, text)
            
            # بررسی ویدیو نوت
            elif "video_note" in message:
                file_id = message["video_note"]["file_id"]
                file_type = "video_note"
                is_nsfw = is_nsfw_media(file_id, file_type, text)
            
            # بررسی متن (بدون رسانه)
            elif text:
                is_nsfw = is_nsfw_media(None, None, text)
            
            # اگر محتوا نامناسب بود
            if is_nsfw:
                delete_message(chat_id, message_id)
                
                # محدود کردن کاربر به مدت 7 روز
                if chat_id not in porn_blocked_users:
                    porn_blocked_users[chat_id] = {}
                porn_blocked_users[chat_id][user_id] = datetime.now() + timedelta(days=7)
                
                block_text = get_block_message(first_name, user_id)
                send_message(chat_id, block_text)
                logger.info(f"🔞 محتوای نامناسب حذف شد از {first_name} و محدود شد")
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
                        send_message(chat_id, welcome_text)
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
                    send_message(chat_id, welcome_text)
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
                logger.info(f"🔞 قفل پورن فعال شد در گروه {chat_id}")
                return
            if text in ["باز کردن پورن", "/unlock_porn"]:
                porn_lock_status[chat_id] = False
                if chat_id in porn_blocked_users:
                    del porn_blocked_users[chat_id]
                send_message(chat_id, "<b>◂ قفل پورن غیر فعال شد !</b>", reply_to_message_id=message_id)
                logger.info(f"🔞 قفل پورن غیرفعال شد در گروه {chat_id}")
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