import sys
import os

# اضافه کردن مسیر پروژه به PATH
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# اجرای ربات
from core.bot import main

if __name__ == "__main__":
    main()