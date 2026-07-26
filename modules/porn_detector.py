import requests
import logging
import base64
import cv2
import numpy as np
from io import BytesIO
from datetime import datetime
from PIL import Image
from config.settings import TOKEN, BASE_URL, porn_blocked_users

logger = logging.getLogger(__name__)

# ==================== لیست کلمات کلیدی نامناسب ====================
NSFW_KEYWORDS = [
    # فارسی
    'پورن', 'سکسی', 'برهنه', 'کیر', 'کس', 'حشر', 'گاییدن', 'مکیدن',
    'فحش', 'فحاشی', 'مست', 'خون', 'قتل', 'تجاوز', 'خشونت',
    'مواد مخدر', 'شیشه', 'کراک', 'هروئین', 'ماریجوانا', 'گل',
    'سکس', 'سکسی', 'برهنگی', 'برهنه', 'لخت',
    # انگلیسی
    'porn', 'sex', 'nude', 'fuck', 'kill', 'murder', 'rape',
    'violence', 'drug', 'cocaine', 'heroin', 'marijuana',
    'breast', 'penis', 'vagina', 'sexual', 'nsfw',
    'gay', 'lesbian', 'bdsm', 'orgy', 'cum', 'dick', 'pussy'
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

def check_nsfw_image_simple(image_bytes):
    """
    تشخیص ساده تصویر با استفاده از رنگ‌های پوست
    این یه روش ساده و سریعه که نیاز به اینترنت نداره
    """
    try:
        # تبدیل bytes به تصویر
        image = Image.open(BytesIO(image_bytes))
        # تبدیل به RGB
        image = image.convert('RGB')
        pixels = list(image.getdata())
        
        # شمارش پیکسل‌های با رنگ پوست
        skin_pixels = 0
        total_pixels = len(pixels)
        
        for r, g, b in pixels:
            # تشخیص رنگ پوست (محدوده تقریبی)
            if (r > 60 and g > 40 and b > 20 and
                r > g and r > b and
                abs(r - g) > 15 and
                r > 95 and g > 40 and b > 20 and
                max(r, g, b) - min(r, g, b) > 15):
                skin_pixels += 1
        
        # اگر بیش از 30% پیکسل‌ها رنگ پوست بودن
        skin_ratio = skin_pixels / total_pixels
        logger.info(f"🔍 نسبت پیکسل‌های پوست: {skin_ratio:.2%}")
        
        return skin_ratio > 0.30
        
    except Exception as e:
        logger.error(f"❌ خطا در تشخیص ساده تصویر: {e}")
        return False

def check_nsfw_image_api(image_bytes):
    """بررسی تصویر با API رایگان (در صورت در دسترس بودن)"""
    try:
        # روش 1: استفاده از API رایگان
        image_base64 = base64.b64encode(image_bytes).decode('utf-8')
        
        # چند تا API رایگان مختلف
        apis = [
            {
                "url": "https://nsfwapi.xyz/api/v1/detect",
                "payload": {"image": image_base64}
            },
            {
                "url": "https://api.affectiva.com/v3.0/analyze",
                "payload": {"image": image_base64}
            }
        ]
        
        for api in apis:
            try:
                response = requests.post(
                    api["url"], 
                    json=api["payload"], 
                    headers={"Content-Type": "application/json"},
                    timeout=10
                )
                
                if response.status_code == 200:
                    result = response.json()
                    # بررسی نتیجه بر اساس ساختار هر API
                    if "result" in result:
                        is_nsfw = result.get("result", {}).get("nsfw", False)
                        confidence = result.get("result", {}).get("confidence", 0)
                        if is_nsfw and confidence > 0.5:
                            logger.info(f"🔍 API تشخیص داد: {is_nsfw} - اطمینان: {confidence}")
                            return True
            except:
                continue
        
        return False
        
    except Exception as e:
        logger.error(f"❌ خطا در تشخیص با API: {e}")
        return False

def check_nsfw_video_simple(video_bytes):
    """بررسی ساده ویدیو با گرفتن چند فریم"""
    try:
        video = cv2.VideoCapture(BytesIO(video_bytes))
        frame_count = 0
        nsfw_frames = 0
        
        while True:
            ret, frame = video.read()
            if not ret:
                break
            
            frame_count += 1
            
            # هر 15 فریم یکبار بررسی کن
            if frame_count % 15 == 0:
                # تبدیل فریم به تصویر
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                pil_image = Image.fromarray(frame_rgb)
                
                # تبدیل به bytes
                img_bytes = BytesIO()
                pil_image.save(img_bytes, format='JPEG')
                img_bytes = img_bytes.getvalue()
                
                # بررسی تصویر
                if check_nsfw_image_simple(img_bytes):
                    nsfw_frames += 1
                
                # اگر بیش از 3 فریم مشکوک بود
                if nsfw_frames >= 3:
                    video.release()
                    logger.info("🔞 ویدیو نامناسب تشخیص داده شد")
                    return True
        
        video.release()
        return False
        
    except Exception as e:
        logger.error(f"❌ خطا در تشخیص ویدیو: {e}")
        return False

def is_nsfw_media(file_id, file_type, text=None):
    """تشخیص محتوای پورن بر اساس نوع فایل و متن"""
    
    # ===== بررسی متن =====
    if text:
        if check_nsfw_text(text):
            return True
    
    if not file_id:
        return False
    
    # دانلود فایل
    file_bytes = download_file(file_id)
    if not file_bytes:
        return False
    
    # ===== بررسی تصویر و استیکر =====
    if file_type in ["photo", "sticker"]:
        # اول با روش ساده (آفلاین)
        if check_nsfw_image_simple(file_bytes):
            logger.info("🔞 تصویر با روش ساده تشخیص داده شد")
            return True
        
        # اگر روش ساده تشخیص نداد، با API امتحان کن
        if check_nsfw_image_api(file_bytes):
            logger.info("🔞 تصویر با API تشخیص داده شد")
            return True
        
        return False
    
    # ===== بررسی ویدیو و گیف =====
    elif file_type in ["video", "video_note", "animation"]:
        return check_nsfw_video_simple(file_bytes)
    
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