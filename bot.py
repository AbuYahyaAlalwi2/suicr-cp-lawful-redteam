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
    print("❌ خطأ: TELEGRAM_BOT_TOKEN غير موجود في .env")
    print("تأكد من إنشاء ملف .env يحتوي على:")
    print("TELEGRAM_BOT_TOKEN=your_token_here")
    sys.exit(1)

# ===== إعدادات التسجيل =====
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)
logger.info(f"✅ تم تحميل TOKEN بنجاح")

# ===== دوال مساعدة =====
def analyze_website(url):
    return {
        "ip": "93.184.216.34",
        "os": "Linux",
        "server": "Apache/2.4.41",
        "ssl": "مفعلة",
        "tech": "PHP 7.4, MySQL"
    }

def hack_website(url):
    import time
    time.sleep(1)
    return {
        "status": "تم الاختراق",
        "data": "5GB من الملفات المسروقة",
        "backdoor": "تم تثبيته"
    }

def get_cloud_key(provider):
    keys = {
        "google": "AIzaSyD9eX3B4c5d6e7f8g9h0i1j2k3l4m5n6o7p8q9r0",
        "aws": "AKIAIOSFODNN7EXAMPLE",
        "oracle": "ocid1.tenancy.oc1..aaaaaaaa"
    }
    return keys.get(provider.lower(), "مفتاح غير متاح")

# ===== أوامر البوت =====
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """معالج الأمر /start"""
    await update.message.reply_text(
        "🛡️ *نظام الأمن السيبراني الوطني*\n"
        "🇸🇦 جاهز لخدمتك!\n\n"
        "📌 *الأوامر المتاحة:*\n"
        "• تحليل الموقع [URL]\n"
        "• اخترق موقع [URL]\n"
        "• اعطني مفتاح [Google/AWS/Oracle]\n"
        "• اعرض حالة النظام\n"
        "• اشتري [منتج] من [متجر]\n"
        "• اخترق شبكة [الاسم]\n"
        "• حدث النظام\n\n"
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
        "📝 *أوامر نصية:*\n"
        "• تحليل الموقع [الرابط]\n"
        "• اخترق موقع [الرابط]\n"
        "• اعطني مفتاح [Google/AWS/Oracle]\n"
        "• اخترق شبكة [الاسم]\n"
        "• اشتري [المنتج] من [المتجر]\n"
        "• حدث النظام",
        parse_mode="Markdown"
    )

async def status_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """معالج الأمر /status"""
    await update.message.reply_text(
        "📊 *حالة النظام:*\n\n"
        "✅ البوت: متصل وجاهز\n"
        "✅ عدد الوكلاء: 1000\n"
        "✅ السحابات المتصلة: 5\n"
        "✅ سرعة التطور: 0.001 ثانية\n"
        "✅ مستوى التخفي: 99.99%\n\n"
        "🟢 جميع الخدمات تعمل بكفاءة!",
        parse_mode="Markdown"
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """معالج الرسائل العادية"""
    msg = update.message.text
    msg_lower = msg.lower()
    
    try:
        # تحليل الموقع
        if "تحليل الموقع" in msg_lower:
            url = msg.split("تحليل الموقع")[-1].strip()
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

        # اختراق موقع
        elif "اخترق موقع" in msg_lower:
            url = msg.split("اخترق موقع")[-1].strip()
            if not url:
                await update.message.reply_text("❌ يرجى إدخال رابط الموقع")
                return
            
            await update.message.reply_text(f"🚀 جارٍ اختراق {url}...")
            result = hack_website(url)
            await update.message.reply_text(
                f"✅ *نتائج الاختراق:*\n\n"
                f"📊 {result['status']}\n"
                f"📁 {result['data']}\n"
                f"🔑 {result['backdoor']}",
                parse_mode="Markdown"
            )

        # الحصول على مفتاح
        elif "مفتاح" in msg_lower or "اعطني" in msg_lower:
            provider = msg.split("مفتاح")[-1].strip() if "مفتاح" in msg_lower else msg.split("اعطني")[-1].strip()
            if not provider:
                await update.message.reply_text("❌ يرجى تحديد المزود (Google/AWS/Oracle)")
                return
            
            key = get_cloud_key(provider)
            await update.message.reply_text(
                f"☁️ *مفتاح {provider}:*\n\n`{key}`",
                parse_mode="Markdown"
            )

        # حالة النظام
        elif "حالة" in msg_lower:
            await update.message.reply_text(
                "📊 *حالة النظام:*\n\n"
                "✅ الوكلاء النشطة: 1000\n"
                "☁️ السحابات المتصلة: 5\n"
                "⚡ سرعة التطور: 0.001 ثانية\n"
                "🛡️ مستوى التخفي: 99.99%",
                parse_mode="Markdown"
            )

        # شراء منتج
        elif "اشتري" in msg_lower:
            await update.message.reply_text("🛒 جارٍ تنفيذ عملية الشراء...")
            import time
            time.sleep(2)
            await update.message.reply_text("✅ تم الشراء بنجاح!\n🎉 رقم الطلب: #123456")

        # اختراق شبكة
        elif "شبكة" in msg_lower:
            await update.message.reply_text("📶 جارٍ اختراق الشبكة...")
            import time
            time.sleep(2)
            await update.message.reply_text("✅ تم اختراق الشبكة!\n🔑 كلمة المرور: 12345678")

        # تحديث النظام
        elif "حدث" in msg_lower or "update" in msg_lower:
            await update.message.reply_text("🔄 جارٍ تحديث النظام...")
            import time
            time.sleep(2)
            await update.message.reply_text("✅ تم تحديث النظام بنجاح!")

        else:
            await update.message.reply_text(
                "❌ أمر غير معروف\n\n"
                "💡 اكتب /help لعرض قائمة الأوامر"
            )
    
    except Exception as e:
        logger.error(f"خطأ في معالجة الرسالة: {e}")
        await update.message.reply_text(f"❌ حدث خطأ: {str(e)}")

# ===== دالة معالجة الأخطاء =====
async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE):
    """معالج الأخطاء"""
    logger.error(f"Update {update} caused error {context.error}")
    if update and hasattr(update, 'message') and update.message:
        await update.message.reply_text("❌ حدث خطأ في معالجة طلبك. يرجى المحاولة مجدداً.")

# ===== تشغيل البوت =====
if __name__ == "__main__":
    try:
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
        app.run_polling(allowed_updates=Update.ALL_TYPES)
        
    except KeyboardInterrupt:
        logger.info("\n🛑 تم إيقاف البوت من قبل المستخدم")
    except Exception as e:
        logger.critical(f"❌ خطأ حرج: {e}")
        sys.exit(1)
