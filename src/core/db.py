import psycopg
from dotenv import load_dotenv
import os

load_dotenv()
DB_NAME = os.getenv("DB_NAME")
DB_PASSWORD = os.getenv("DB_PASSWORD")

class PGManager:
    def __init__(self):
        self.connection = psycopg.connect(
            dbname =DB_NAME,
            user="postgres",
            host="localhost",
            password=DB_PASSWORD
        )
