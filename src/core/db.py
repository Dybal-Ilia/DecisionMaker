import psycopg
from src.core.schemas import User
import streamlit as st
import os
import asyncio
from dotenv import load_dotenv

load_dotenv()

DB_URI = os.getenv("DB_URI")


class PGManager:
    def __init__(self, conn: psycopg.AsyncConnection, loop: asyncio.AbstractEventLoop):
        self.conn = conn
        self.loop = loop

    async def create_user(self, user: User) -> bool:
        query = """
            INSERT INTO public.users (user_id, user_name, user_lastname, user_nickname, user_password)
            VALUES (%s, %s, %s, %s, %s)
        """
        try:
            async with self.conn.cursor() as cursor:
                await cursor.execute(
                    query,
                    (
                        user.user_id,
                        user.user_name,
                        user.user_lastname,
                        user.user_nickname,
                        user.user_password,
                    ),
                )
            await self.conn.commit()
            return True
        except Exception as e:
            st.error(f"Unable to create a user: {e}")
            await self.conn.rollback()
            return False

    async def get_user_by_nickname(self, nickname: str):
        query = """
            SELECT user_name, user_lastname, user_nickname
            FROM public.users WHERE user_nickname = %s
        """
        try:
            async with self.conn.cursor() as cursor:
                await cursor.execute(query, (nickname,))
                res = await cursor.fetchone()
                return res
        except Exception as e:
            st.error(f"Unable to fetch user {nickname}: {e}")
            await self.conn.rollback()
            return None

    async def get_nicknames_list(self):
        sql = """
                SELECT 
                    user_nickname
                FROM public.users
                """
        try:
            async with self.conn.cursor() as cursor:
                await cursor.execute(sql)
                res = await cursor.fetchall()
            nickname_list = [r[0] for r in res]
            return nickname_list
        except Exception as e:
            st.error(f"Unable to fetch nicknams list: {e}")
            await self.conn.rollback()
            return None

    async def fetch_password_by_nickname(self, user_nickname):
        sql = """SELECT 
                    user_password
                FROM public.users WHERE user_nickname = %s
                    """
        try:
            async with self.conn.cursor() as cursor:
                await cursor.execute(sql, (user_nickname,))
                res = await cursor.fetchone()
            return res[0]
        except Exception as e:
            st.error(f"Unable to fetch user password: {e}")
            await self.conn.rollback()
            return None


@st.cache_resource
def get_db(_db_uri):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    async def init_conn():
        return await psycopg.AsyncConnection.connect(_db_uri)

    conn = loop.run_until_complete(init_conn())
    manager = PGManager(conn, loop)
    return manager
