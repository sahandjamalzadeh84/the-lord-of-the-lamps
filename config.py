from dotenv import load_dotenv
import os


load_dotenv()

API_KEY = os.getenv('API_KEY')

PASSWORD = os.getenv('PASSWORD')

BOT_TOKEN = os.getenv('BOT_TOKEN')

FLASK_APP_URL = os.getenv('FLASK_APP_URL')
