import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-key-12345')
    DATABASE_URL = os.environ.get('DATABASE_URL', 'sqlite:///operations.db')
    TELEGRAM_TOKEN = os.environ.get('TELEGRAM_TOKEN', '8703097627:AAF6-XdA4mp-hn3Y-tE2D8uME1eIztwFTNY')
    OPENROUTER_API_KEY = os.environ.get('OPENROUTER_API_KEY', 'your-openrouter-key')
    DEBUG = os.environ.get('DEBUG', True)
