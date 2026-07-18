import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")

ADMINS = [
    int(x)
    for x in os.getenv("ADMINS","").split(",")
    if x
]

CHANNEL_ID = os.getenv("CHANNEL_ID")

TIMEZONE = os.getenv("TIMEZONE")

DATABASE_NAME = os.getenv("DATABASE_NAME")
