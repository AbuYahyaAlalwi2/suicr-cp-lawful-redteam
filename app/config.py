import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-key-12345')
    DATABASE_URL = os.environ.get('DATABASE_URL', 'sqlite:///operations.db')
    TELEGRAM_TOKEN = os.environ.get('TELEGRAM_TOKEN', '8703097627:AAF6-XdA4mp-hn3Y-tE2D8uME1eIztwFTNY')
    OPENROUTER_API_KEY = os.environ.get('OPENROUTER_API_KEY', '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')
    BILLING_ACCOUNT_ID = os.environ.get('BILLING_ACCOUNT_ID', '')
    DEBUG = os.environ.get('DEBUG', True)
