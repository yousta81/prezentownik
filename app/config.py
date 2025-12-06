import os
from dotenv import load_dotenv

load_dotenv()

ENV = os.getenv("ENV", "local")
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))

if ENV == "local":
    DATABASE_URL = os.getenv("SQLITE_URL")
else:
    DATABASE_URL = os.getenv("POSTGRES_URL")

SQLITE_URL = os.getenv("SQLITE_URL")
POSTGRES_URL = os.getenv("POSTGRES_URL")
DATABASE_URL = POSTGRES_URL
