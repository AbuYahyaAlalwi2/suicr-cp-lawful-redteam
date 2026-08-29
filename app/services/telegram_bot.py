python
import json
import re
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes
from app.config import Config
from app.core.analyzer import analyze_website, scan_ports
from app.core.executor import execute_bank_action, execute_wallet_action, create_wallet, execute_purchase
from app.core.key_manager import KeyManager
from app.services.ai_chat import ask_ai
from app.services.db_service import generate_op_id, save_operation
from datetime import datetime

# ===== الأزرار الرئيسية =====
def get_main_menu():
    keyboard = [
        [InlineKeyboardButton("🔍 تحليل موقع", callback_data="analyze")],
        [InlineKeyboardButton("🛡️ فحص منافذ", callback_data="port_scan")],
        [InlineKeyboardButton("🏦 سحب بنكي", callback_data="bank")],
        [InlineKeyboardButton("💰 سحب من محفظة", callback_data="wallet")],
        [InlineKeyboardButton("📱 اختراق هاتف", callback_data="phone_hack")],
        [InlineKeyboardButton("📶 اختراق شبكة", callback_data="wifi_hack")],
        [InlineKeyboardButton("🛒 شراء منتج", callback_data="purchase")],
        [InlineKeyboardButton("💰 إنشاء محفظة", callback_data="create_wallet")],
        [InlineKeyboardButton("📋 استرجاع تقرير", callback_data="get_report")],
        [InlineKeyboardButton("💬 محادثة ذكية (AI)", callback_data="ai_chat")]
    ]
    return InlineKeyboardMarkup(keyboard)

# ===== أوامر البوت =====
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🛡️ نظام الردع السيبراني التنفيذي\n"
        "🇸🇦 اختر العملية من الأزرار أدناه:",
        reply_markup=get_main_menu()
    )

async def handle_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data

    instructions = {
        "analyze": "🔍 أرسل رابط الموقع (مثال: https://example.com)",
        "port_scan": "🛡️ أرسل اسم النطاق أو IP (مثال: example.com)",
        "bank": "🏦 أرسل: رقم الحساب | المبلغ | السبب",
        "wallet": "💰 أرسل: عنوان المحفظة | المبلغ | السبب",
        "phone_hack": "📱 أرسل: رقم الهاتف | السبب",
        "wifi_hack": "📶 أرسل: اسم الشبكة | السبب",
        "purchase": "🛒 أرسل: اسم المنتج | المتجر | سبب الشراء",
        "create_wallet": "💰 جارٍ إنشاء محفظة جديدة...",
        "get_report": "📋 أرسل رقم العملية (OP-XXXXXX)",
        "ai_chat": "💬 أرسل سؤالك أو طلبك للذكاء الاصطناعي"
    }

    if data in instructions:
        if data == "create_wallet":
            wallet = create_wallet()
            op_id = generate_op_id(wallet["wallet"])
            save_operation(op_id, wallet["wallet"], "إنشاء محفظة", "0", "إنشاء محفظة جديدة", json.dumps(wallet))
            await query.edit_message_text(f"✅ تم إنشاء المحفظة\n🆔 {op_id}\n💰 {wallet['wallet']}")
        else:
            await query.edit_message_text(instructions[data])

# ===== معالجة الرسائل النصية =====
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.message.text
    msg_lower = msg.lower()

    # تحليل موقع
    if re.search(r"(تحليل|analyze|حلل)\s*(موقع)?\s*(https?://)?\S+", msg_lower):
        url_match = re.search(r"(https?://)?\S+", msg)
        url = url_match.group(0) if url_match else msg
        if not url.startswith("http"):
            url = "https://" + url
        result = analyze_website(url)
        if "error" in result:
            await update.message.reply_text(f"❌ {result['error']}")
        else:
            op_id = generate_op_id(url)
            save_operation(op_id, url, "تحليل موقع", "N/A", "تحليل موقع", json.dumps(result))
            await update.message.reply_text(
                f"🔍 تحليل الموقع\n🆔 {op_id}\n🌐 {result['domain']}\n📡 IP: {result['ip']}\n🖥️ {result['server']}"
            )

    # فحص منافذ
    elif re.search(r"(فحص|scan|افحص)\s*(منافذ)?\s*\S+", msg_lower):
        domain_match = re.search(r"\S+", msg)
        domain = domain_match.group(0) if domain_match else msg
        if "http" in domain:
            domain = domain.replace("https://", "").replace("http://", "").split("/")[0]
        result = scan_ports(domain)
        op_id = generate_op_id(domain)
        save_operation(op_id, domain, "فحص منافذ", "N/A", "فحص منافذ", str(result))
        await update.message.reply_text(f"🛡️ فحص المنافذ\n🆔 {op_id}\n📊 {result}")

    # عمليات بالـ |
    elif "|" in msg:
        parts = msg.split("|")
        if len(parts) == 3:
            target, action, reason = parts[0].strip(), parts[1].strip(), parts[2].strip()
            if "http" in target:
                op_id = generate_op_id(target)
                save_operation(op_id, target, "اختراق موقع", "N/A", reason, json.dumps({"url": target}))
                await update.message.reply_text(f"✅ اختراق الموقع\n🆔 {op_id}\n🌐 {target}\n📝 {reason}")
            elif target.startswith("0x"):
                result = execute_wallet_action(target, action, reason)
                op_id = generate_op_id(target)
                save_operation(op_id, target, "سحب من محفظة", action, reason, json.dumps(result))
                await update.message.reply_text(f"✅ السحب من المحفظة\n🆔 {op_id}\n💰 {target}")
            else:
                result = execute_bank_action(target, action, reason)
                op_id = generate_op_id(target)
                save_operation(op_id, target, "سحب بنكي", action, reason, json.dumps(result))
                await update.message.reply_text(f"✅ السحب من البنك\n🆔 {op_id}\n🏦 {target}")
    
    # استرجاع تقرير
    elif msg.startswith("OP-"):
        # محاكاة الاسترجاع
        await update.message.reply_text(f"📋 تقرير العملية {msg}:\n🔍 هذه عملية تجريبية")

    # محادثة ذكية
    else:
        ai_reply = ask_ai(msg)
        await update.message.reply_text(f"💬 {ai_reply}")

# ===== تشغيل البوت =====
def run_bot():
    app = ApplicationBuilder().token(Config.TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(handle_button))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    print("✅ بوت التليجرام يعمل...")
    app.run_polling()
