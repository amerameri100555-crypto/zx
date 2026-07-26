import requests
import logging
import cv2
import numpy as np
from io import BytesIO
from datetime import datetime
from PIL import Image
from nudenet import NudeDetector
from config.settings import TOKEN, BASE_URL, porn_blocked_users

logger = logging.getLogger(__name__)

# ==================== بارگذاری مدل تشخیص برهنگی ====================
# این کار فقط یک بار انجام میشه
try:
    nuke_detector = NudeDetector()
    logger.info("✅ مدل NudeNet با موفقیت بارگذاری شد!")
except Exception as e:
    logger.error(f"❌ خطا در بارگذاری مدل NudeNet: {e}")
    nuke_detector = None

# ==================== لیست کلمات کلیدی نامناسب ====================
NSFW_KEYWORDS = [
    # فارسی
    'پورن', 'سکسی', 'برهنه', 'کیر', 'کس', 'حشر', 'گاییدن', 'مکیدن',
    'فحش', 'فحاشی', 'مست', 'خون', 'قتل', 'تجاوز', 'خشونت',
    'مواد مخدر', 'شیشه', 'کراک', 'هروئین', 'ماریجوانا', 'گل',
    # انگلیسی
    'porn', 'sex', 'nude', 'fuck', 'kill', 'murder', 'rape',
    'violence', 'drug', 'cocaine', 'heroin', 'marijuana',
    'breast', 'penis', 'vagina', 'sexual'
]

# ==================== توابع تشخیص ====================

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
        logger.error(f"❌ خطا در دانلود فایل: {e}")
        return None

def check_nsfw_image(image_bytes):
    """بررسی تصویر با NudeNet"""
    if nuke_detector is None:
        logger.warning("⚠️ مدل NudeNet بارگذاری نشده است!")
        return False
    
    try:
        # تبدیل bytes به تصویر
        image = Image.open(BytesIO(image_bytes))
        
        # تشخیص با NudeNet
        result = nuke_detector.detect(image)
        
        # بررسی نتایج
        for item in result:
            label = item.get('label', '').lower()
            score = item.get('score', 0)
            
            # اگر نمره بالا بود و محتوای نامناسب تشخیص داده شد
            if score > 0.5 and label in ['FEMALE_BREAST_EXPOSED', 'MALE_BREAST_EXPOSED', 
                                          'FEMALE_GENITALIA_EXPOSED', 'MALE_GENITALIA_EXPOSED',
                                          'BUTTOCKS_EXPOSED', 'ANUS_EXPOSED']:
                logger.info(f"🔞 محتوای نامناسب تشخیص داده شد: {label} - نمره: {score}")
                return True
        
        return False
        
    except Exception as e:
        logger.error(f"❌ خطا در تشخیص تصویر: {e}")
        return False

def check_nsfw_video(video_bytes):
    """بررسی ویدیو با گرفتن فریم‌ها و بررسی با NudeNet"""
    try:
        # تبدیل bytes به numpy array برای OpenCV
        nparr = np.frombuffer(video_bytes, np.uint8)
        video = cv2.VideoCapture(BytesIO(video_bytes))
        
        frame_count = 0
        checked_frames = 0
        
        while True:
            ret, frame = video.read()
            if not ret:
                break
            
            frame_count += 1
            
            # هر 10 فریم یکبار بررسی کن (برای کاهش حجم پردازش)
            if frame_count % 10 == 0:
                checked_frames += 1
                # تبدیل فریم به تصویر
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                pil_image = Image.fromarray(frame_rgb)
                
                # تشخیص با NudeNet
                if nuke_detector:
                    result = nuke_detector.detect(pil_image)
                    for item in result:
                        label = item.get('label', '').lower()
                        score = item.get('score', 0)
                        if score > 0.5 and label in ['FEMALE_BREAST_EXPOSED', 'MALE_BREAST_EXPOSED', 
                                                      'FEMALE_GENITALIA_EXPOSED', 'MALE_GENITALIA_EXPOSED',
                                                      'BUTTOCKS_EXPOSED', 'ANUS_EXPOSED']:
                            logger.info(f"🔞 محتوای نامناسب در ویدیو تشخیص داده شد: {label}")
                            video.release()
                            return True
                
                # اگر تعداد فریم‌های بررسی شده به 10 رسید، کافیه
                if checked_frames >= 10:
                    break
        
        video.release()
        return False
        
    except Exception as e:
        logger.error(f"❌ خطا در تشخیص ویدیو: {e}")
        return False

def check_nsfw_text(text):
    """بررسی متن با لیست کلمات کلیدی"""
    if not text:
        return False
    
    text_lower = text.lower()
    for keyword in NSFW_KEYWORDS:
        if keyword.lower() in text_lower:
            logger.info(f"🔞 کلمه نامناسب در متن تشخیص داده شد: {keyword}")
            return True
    
    return False

def is_nsfw_media(file_id, file_type, text=None):
    """تشخیص محتوای پورن بر اساس نوع فایل و متن"""
    
    # ===== بررسی متن =====
    if text:
        if check_nsfw_text(text):
            return True
    
    # ===== بررسی تصویر =====
    if file_type in ["photo", "sticker"]:
        file_bytes = download_file(file_id)
        if file_bytes:
            return check_nsfw_image(file_bytes)
    
    # ===== بررسی ویدیو و گیف =====
    elif file_type in ["video", "video_note", "animation"]:
        file_bytes = download_file(file_id)
        if file_bytes:
            return check_nsfw_video(file_bytes)
    
    return False

def is_user_blocked(chat_id, user_id):
    """بررسی اینکه کاربر محدود شده یا نه"""
    if chat_id not in porn_blocked_users:
        return False
    if user_id not in porn_blocked_users[chat_id]:
        return False
    unblock_time = porn_blocked_users[chat_id][user_id]
    if datetime.now() < unblock_time:
        return True
    else:
        del porn_blocked_users[chat_id][user_id]
        return False

def get_block_message(first_name, user_id):
    return f"""
⫸ کاربر گرامی : <a href="tg://user?id={user_id}">{first_name}</a> 

◄ استفاده از رسانه مستهجن و محتوای نامناسب ممنوع است ، لذا پیام شما حذف می شود و برای مدتی از ارسال رسانه محدود می شوید !

◂ مدت زمان محدود شده از ارسال رسانه : <b>۷ روز</b>
"""