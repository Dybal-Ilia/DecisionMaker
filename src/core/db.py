import psycopg
from dotenv import load_dotenv
from src.core.schemas import User
from uuid import uuid4
import os

load_dotenv()
DB_NAME = os.getenv("DB_NAME")
DB_PASSWORD = os.getenv("DB_PASSWORD")

class PGManager:
    def __init__(self, dbname, user, host, password):
        try:
            self.conn = psycopg.connect(
                dbname=dbname,
                user=user,
                host=host,
                password=password
            )
            self.cursor = self.conn.cursor()
        except:
            raise psycopg.DatabaseError()

    def create_user(self, user:User):
        user_id = user.user_id
        user_name = user.user_name
        user_lastname = user.user_lastname
        user_nickname = user.user_nickname
        user_password = user.user_password
        query = f"""INSERT INTO public.users VALUES(
            '{user_id}',
            '{user_name}',
            '{user_lastname}',
            '{user_nickname}',
            '{user_password}'
        )"""
        try:
            self.cursor.execute(query)
            self.conn.commit()
            return True
        except:
            return False

        