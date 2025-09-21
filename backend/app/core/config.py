import os
from dotenv import load_dotenv

load_dotenv()

SCIBOX_API_KEY = os.getenv("SCIBOX_API_KEY")
ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", "admin")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "admin")