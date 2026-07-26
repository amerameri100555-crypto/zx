import os

# ==================== تنظیمات اصلی ====================
TOKEN = "8532288807:AAGJXJnmHJ68Cyh7eMK9muIcZydKAZLayVQ"
OWNER_ID = 7803165903
DEEPAI_API_KEY = "eb27dd91-b502-49ea-8c59-cf8324bcef59"

# ==================== آدرس‌ها ====================
BASE_URL = f"https://api.telegram.org/bot{TOKEN}"

# ==================== وضعیت‌ها ====================
service_lock_status = {}  # {chat_id: True/False}
welcome_status = {}       # {chat_id: True/False}
porn_lock_status = {}     # {chat_id: True/False}
porn_blocked_users = {}   # {chat_id: {user_id: unblock_time}}