python
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, CallbackQueryHandler, filters
from app.core.analyzer import analyze_website, scan_ports
from app.core.executor import execute_bank_action, execute_wallet_action, create_wallet
from app.services.db_service import save_operation, generate_op_id
from app.config import Config
import json

async def start(update, context):
    from app.web.buttons import get_main_menu
    await update.message.reply_text("🛡️ النظام السيبراني", reply_markup=get_main_menu())

# باقي الدوال مشابهة لما سبق، مع استدعاء دوال core

def run_bot():
    app = ApplicationBuilder().token(Config.TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    # باقي المعالجات
    app.run_polling()
