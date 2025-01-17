import webull
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv() 

# Access environment variables
db_url = os.getenv("DATABASE_URL")
api_key = os.getenv("API_KEY")

print(db_url + api_key)