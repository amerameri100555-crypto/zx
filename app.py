import asyncio

from loader import dp,bot

from app.database.db import db

from app.handlers.start import router as start_router

from app.config.logger import logger

async def startup():

    logger.info("Creating Database...")

    await db.create_tables()

    logger.success("Database Ready")

    dp.include_router(start_router)

async def main():

    await startup()

    logger.success("?? SibShop Bot Started")

    await dp.start_polling(bot)

if __name__=="__main__":

    asyncio.run(main())
