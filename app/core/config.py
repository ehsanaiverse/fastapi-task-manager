import os
from dotenv import load_dotenv

load_dotenv()  # load variables from .env file

SMTP_EMAIL = os.getenv("SMTP_EMAIL")       # your Gmail
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD") # your app password
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587 # TLS = modern, secure port
