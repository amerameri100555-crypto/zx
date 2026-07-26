import requests
import logging
import base64
from io import BytesIO
from datetime import datetime
from PIL import Image
from config.settings import TOKEN, BASE_URL, porn_blocked_users

logger = logging.getLogger(__name__)

# ==================== لیست کلمات کلیدی نامناسب ====================
NSFW_KEYWORDS = [
    'پورن', 'سکسی', 'برهنه', 'کیر', 'کس', 'حشر', 'گاییدن', 'مکیدن',
    'فحش', 'فحاشی', 'مست', 'خون', 'قتل', 'تجاوز', 'خشونت',
    'مواد مخدر', 'شیشه', 'کراک', 'هروئین', 'ماریجوانا', 'گل',
    'سکس', 'برهنگی', 'لخت',
    'porn', 'sex', 'nude', 'fuck', 'kill', 'murder', 'rape',
    'violence', 'drug', 'cocaine', 'heroin', 'marijuana',
    'breast', 'penis', 'vagina', 'sexual', 'nsfw'
]

# ==================== توابع تشخیص ====================

def download_file(file_id):
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
    if not text:
        return False
    text_lower = text.lower()
    for keyword in NSFW_KEYWORDS:
        if keyword.lower() in text_lower:
            logger.info(f"🔞 کلمه نامناسب در متن: {keyword}")
            return True
    return False

def check_nsfw_image_simple(image_bytes):
    """تشخیص ساده تصویر با رنگ پوست (بدون نیاز به اینترنت)"""
    try:
        image = Image.open(BytesIO(image_bytes))
        image = image.convert('RGB')
        pixels = list(image.getdata())
        
        skin_pixels = 0
        total_pixels = len(pixels)
        
        for r, g, b in pixels:
            if (r > 60 and g > 40 and b > 20 and
                r > g and r > b and
                abs(r - g) > 15 and
                r > 95 and g > 40 and b > 20 and
                max(r, g, b) - min(r, g, b) > 15):
                skin_pixels += 1
        
        skin_ratio = skin_pixels / total_pixels
        logger.info(f"🔍 نسبت پیکسل‌های پوست: {skin_ratio:.2%}")
        return skin_ratio > 0.35
        
    except Exception as e:
        logger.error(f"❌ خطا در تشخیص تصویر: {e}")
        return False

def check_nsfw_image_api(image_bytes):
    """بررسی تصویر با API رایگان"""
    try:
        image_base64 = base64.b64encode(image_bytes).decode('utf-8')
        
        # API رایگان
        url = "https://nsfwapi.xyz/api/v1/detect"
        payload = {"image": image_base64}
        headers = {"Content-Type": "application/json"}
        
        response = requests.post(url, json=payload, headers=headers, timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            is_nsfw = result.get("result", {}).get("nsfw", False)
            confidence = result.get("result", {}).get("confidence", 0)
            logger.info(f"🔍 API: {is_nsfw} - اطمینان: {confidence}")
            return is_nsfw and confidence > 0.5
        return False
        
    except Exception as e:
        logger.error(f"❌ خطا در API: {e}")
        return False

def is_nsfw_media(file_id, file_type, text=None):
    # بررسی متن
    if text and check_nsfw_text(text):
        return True
    
    if not file_id:
        return False
    
    file_bytes = download_file(file_id)
    if not file_bytes:
        return False
    
    # بررسی تصویر و استیکر
    if file_type in ["photo", "sticker"]:
        if check_nsfw_image_simple(file_bytes):
            return True
        if check_nsfw_image_api(file_bytes):
            return True
        return False
    
    # ویدیو و گیف (فعلاً غیرفعال)
    return False

def is_user_blocked(chat_id, user_id):
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