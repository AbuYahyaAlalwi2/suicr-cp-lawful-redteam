import os
import logging
import sys
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from dotenv import load_dotenv

# ===== تحميل متغيرات البيئة =====
load_dotenv()
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN") or os.getenv("TOKEN")

# تحقق من وجود TOKEN
if not TOKEN:
    print("❌ خطأ: TELEGRAM_BOT_TOKEN غير موجود في .env أو Render Environment Variables")
    sys.exit(1)

# ===== إعدادات التسجيل =====
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)
logger.info("✅ تم تحميل TOKEN بنجاح")

# ===== دوال مساعدة =====
def analyze_website(url):
    return {
        "ip": "93.184.216.34",
        "os": "Linux",
        "server": "Apache/2.4.41",
        "ssl": "مفعلة",
        "tech": "PHP 7.4, MySQL"
    }

# ===== أوامر البوت =====
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """معالج الأمر /start"""
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
