import aiosqlite

from config import DATABASE_NAME


class Database:

    def __init__(self):

        self.db_name = DATABASE_NAME


    async def connect(self):

        db = await aiosqlite.connect(self.db_name)

        db.row_factory = aiosqlite.Row

        return db


    async def create_tables(self):

        db = await self.connect()

        await db.execute(
        '''
        CREATE TABLE IF NOT EXISTS schedules(

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            user_id INTEGER NOT NULL,

            channel_id TEXT NOT NULL,

            message_type TEXT NOT NULL,

            file_id TEXT,

            text TEXT,

            send_datetime TEXT NOT NULL,

            status INTEGER DEFAULT 0

        )
        '''
        )

        await db.commit()

        await db.close()


db = Database()
