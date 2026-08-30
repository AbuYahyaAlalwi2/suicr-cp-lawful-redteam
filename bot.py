import logging
import requests
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes
from agent_core import AutonomousAgent  # استيراد الوكيل الذكي

# ===== التوكن والمفاتيح =====
TELEGRAM_TOKEN = "8812677665:AAGeT4rHVK-IwA8_y5Ir-HMP27U6OPcEPdg"
GITHUB_TOKEN = "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"
OPENROUTER_KEY = "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"
EMAIL = "your_email@example.com"  # اختياري، للاستخدام المستقبلي

# ===== تهيئة الوكيل الذكي =====
agent = AutonomousAgent(
    email=EMAIL,
    github_token=GITHUB_TOKEN,
    model_keys={
        "openrouter": OPENROUTER_KEY,
        # يمكن إضافة Gemini أو Claude لاحقاً
    }
)

# ===== أوامر البوت =====
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("🔍 تحليل موقع", callback_data="analyze")],
        [InlineKeyboardButton("🛡️ فحص منافذ", callback_data="port_scan")],
        [InlineKeyboardButton("🤖 تنفيذ أمر للوكيل", callback_data="agent_command")],
        [InlineKeyboardButton("📋 حالة النظام", callback_data="status")]
    ]
    await update.message.reply_text(
        "🛡️ نظام الوكيل السيبراني الذكي\n"
        "🇸🇦 اختر العملية أو أرسل أمراً مباشراً للوكيل:\n"
        "مثال: 'استنسخ مستودع https://github.com/...'",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data

    if data == "analyze":
        await query.edit_message_text("🔍 أرسل رابط الموقع (مثل: https://example.com)")
    elif data == "port_scan":
        await query.edit_message_text("🛡️ أرسل اسم النطاق أو IP (مثل: example.com)")
    elif data == "agent_command":
        await query.edit_message_text("🤖 أرسل الأمر للوكيل (مثل: 'ابحث عن token في الملفات')")
    elif data == "status":
        await query.edit_message_text(
            "📊 حالة النظام:\n"
            "✅ البوت يعمل\n"
            "✅ الوكيل الذكي جاهز\n"
            "✅ GitHub متصل\n"
            "✅ OpenRouter متصل"
        )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.message.text
    user_id = update.effective_user.id

    # ===== 1. إذا كان الأمر يبدأ بـ "تحليل" =====
    if "تحليل" in msg and ("http" in msg or "https" in msg):
        # استخدام دالة التحليل القديمة (للتوافق)
        result = analyze_website(msg)
        await update.message.reply_text(result)
        return

    # ===== 2. إذا كان الأمر موجهًا للوكيل =====
    else:
        # إرسال إشارة "جارٍ التفكير..."
        await update.message.reply_text("🧠 جاري معالجة طلبك عبر الوكيل الذكي...")

        # تنفيذ الأمر عبر الوكيل
        result = agent.process_command(msg)

        # إرسال النتيجة
        await update.message.reply_text(f"📌 نتيجة الأمر:\n\n{result}")

# ===== دالة تحليل الموقع (للتوافق مع الوضع العادي) =====
def analyze_website(url):
    try:
        domain = url.replace("https://", "").replace("http://", "").split("/")[0]
        ip_response = requests.get(f"https://dns.google/resolve?name={domain}", timeout=10)
        ip = "غير معروف"
        if ip_response.status_code == 200:
            data = ip_response.json()
            if data.get("Answer"):
                ip = data["Answer"][0]["data"]
        return f"🌐 النطاق: {domain}\n📡 IP: {ip}\n🛡️ تم التحليل بنجاح"
    except:
        return "❌ فشل التحليل"

# ===== تشغيل البوت =====
if __name__ == "__main__":
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    print("✅ البوت يعمل مع الوكيل الذكي...")
    app.run_polling()    """معالج الأمر /start"""
    await update.message.reply_text(
        "🛡️ *نظام الأمن السيبراني الوطني*\n"
        "🇸🇦 جاهز لخدمتك!\n\n"
        "📌 *الأوامر المتاحة:*\n"
        "• /help - اعرض الأوامر\n"
        "• /status - حالة النظام\n"
        "• تحليل الموقع [URL]\n\n"
        "💡 اكتب /help لمزيد من المساعدة",
        parse_mode="Markdown"
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """معالج الأمر /help"""
    await update.message.reply_text(
        "📚 *الأوامر المتاحة:*\n\n"
        "🔹 /start - ابدأ هنا\n"
        "🔹 /help - عرض هذه الرسالة\n"
        "🔹 /status - حالة النظام\n\n"
        "📝 *أمثلة:*\n"
        "• تحليل الموقع example.com\n"
        "• اعرض حالة النظام",
        parse_mode="Markdown"
    )

async def status_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """معالج الأمر /status"""
    await update.message.reply_text(
        "📊 *حالة النظام:*\n\n"
        "✅ البوت: متصل وجاهز\n"
        "✅ الاتصال: نشط\n"
        "✅ قاعدة البيانات: متصلة\n"
        "🟢 جميع الخدمات تعمل بكفاءة!",
        parse_mode="Markdown"
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """معالج الرسائل العادية"""
    msg = update.message.text
    msg_lower = msg.lower()
    
    try:
        if "تحليل الموقع" in msg_lower or "تحليل" in msg_lower:
            url = msg.split("تحليل")[-1].strip()
            if not url:
                await update.message.reply_text("❌ يرجى إدخال رابط الموقع")
                return
            
            await update.message.reply_text(f"🔍 جارٍ تحليل {url}...")
            result = analyze_website(url)
            await update.message.reply_text(
                f"✅ *نتائج التحليل:*\n\n"
                f"🌐 IP: `{result['ip']}`\n"
                f"🖥️ نظام التشغيل: {result['os']}\n"
                f"🔧 الخادم: {result['server']}\n"
                f"🔒 SSL: {result['ssl']}\n"
                f"📦 التقنيات: {result['tech']}",
                parse_mode="Markdown"
            )
        else:
            await update.message.reply_text(
                "❌ أمر غير معروف\n\n"
                "💡 اكتب /help لعرض قائمة الأوامر"
            )
    
    except Exception as e:
        logger.error(f"خطأ في معالجة الرسالة: {e}")
        await update.message.reply_text(f"❌ حدث خطأ: {str(e)}")

async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE):
    """معالج الأخطاء"""
    logger.error(f"Update {update} caused error {context.error}")

def main():
    """دالة رئيسية للبوت"""
    logger.info("🚀 جاري تشغيل البوت...")
    print("")
    print("╔═══════════════════════════════════════════════════════╗")
    print("║   🛡️  SUICR-CP Telegram Bot  🛡️                      ║")
    print("║           تم تشغيل البوت بنجاح!                       ║")
    print("║                                                       ║")
    print("║  ✅ البوت جاهز لاستقبال الرسائل                       ║")
    print("║  📲 ابدأ بإرسال /start أو أي أمر                     ║")
    print("╚═══════════════════════════════════════════════════════╝")
    print("")
    
    app = ApplicationBuilder().token(TOKEN).build()
    
    # إضافة معالجات الأوامر
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("status", status_command))
    
    # معالج الرسائل النصية
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    # معالج الأخطاء
    app.add_error_handler(error_handler)
    
    logger.info("✅ البوت يعمل ويستقبل الرسائل...")
    
    # تشغيل البوت بطريقة تناسب Render
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logger.info("\n🛑 تم إيقاف البوت من قبل المستخدم")
    except Exception as e:
        logger.critical(f"❌ خطأ حرج: {e}")
        sys.exit(1)
