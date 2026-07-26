import time
import logging
import requests
from config.settings import TOKEN, BASE_URL
from handlers.message_handler import handle_message
from handlers.callback_handler import handle_callback

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

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
    logger.info("🤖 ربات ReaperVoid با موفقیت راه‌اندازی شد!")
    logger.info("📡 در حال گوش دادن به پیام‌ها...")
    
    offset = None
    while True:
        try:
            updates = get_updates(offset)
            for update in updates:
                offset = update["update_id"] + 1
                if "message" in update:
                    handle_message(update)
                if "callback_query" in update:
                    handle_callback(update)
        except Exception as e:
            logger.error(f"خطا در حلقه اصلی: {e}")
            time.sleep(5)
        time.sleep(1)

if __name__ == "__main__":
    main()