# 🛡️ SUICR-CP Telegram Bot - دليل التثبيت

## 📋 المتطلبات

- Python 3.8 أو أحدث
- Token من Telegram Bot
- متصفح الإنترنت

## 🚀 التثبيت والتشغيل

### الخطوة 1: تنسيخ المستودع

```bash
git clone https://github.com/AbuYahyaAlalwi2/suicr-cp-lawful-redteam.git
cd suicr-cp-lawful-redteam
```

### الخطوة 2: إنشاء بيئة افتراضية

```bash
python -m venv venv

# على Windows:
venv\Scripts\activate

# على Linux/Mac:
source venv/bin/activate
```

### الخطوة 3: تثبيت المكتبات

```bash
pip install -r requirements.txt
```

### الخطوة 4: إنشاء ملف .env

انسخ `.env.example` إلى `.env`:

```bash
cp .env.example .env
```

ثم عدّل `.env` وأضف Token البوت:

```env
TELEGRAM_BOT_TOKEN=your_bot_token_here
TELEGRAM_CHAT_ID=your_chat_id_here
```

### الخطوة 5: تشغيل البوت

```bash
python bot.py
```

يجب أن تراى رسالة مثل:
```
╔═══════════════════════════════════════════════════════╗
║   🛡️  SUICR-CP Telegram Bot  🛡️                      ║
║           تم تشغيل البوت بنجاح!                       ║
║                                                       ║
║  ✅ البوت جاهز لاستقبال الرسائل                       ║
║  📲 ابدأ بإرسال /start أو أي أمر                     ║
╚═══════════════════════════════════════════════════════╝
```

## 🤖 كيفية الحصول على Bot Token

1. افتح Telegram وابحث عن **BotFather**
2. أرسل `/start`
3. أرسل `/newbot`
4. أتبع التعليمات لإنشاء بوت جديد
5. انسخ التوكن وأضفه في `.env`

## 📱 اختبار البوت

بعد تشغيل البوت، افتح Telegram وابحث عن البوت الذي أنشأته:

```
/start          - ابدأ البوت
/help           - عرض الأوامر
/status         - حالة النظام
```

## 🔒 تنبيهات الأمان

⚠️ **لا تشارك Token البوت مع أحد!**
⚠️ **لا ترفع ملف `.env` على GitHub!**
⚠️ **استخدم `.gitignore` لحماية الملفات الحساسة**

## 🐛 استكشاف الأخطاء

### البوت لا يستجيب

```bash
# تحقق من التوكن
echo $TELEGRAM_BOT_TOKEN

# تأكد من تثبيت المكتبات
pip install -r requirements.txt

# شغل البوت مع تتبع الأخطاء
python -u bot.py
```

### خطأ: "TELEGRAM_BOT_TOKEN not found"

1. تأكد من وجود ملف `.env`
2. تأكد أن التوكن موجود فيه
3. أعد تشغيل البوت

## 📝 الأوامر المتاحة

- `/start` - بدء البوت
- `/help` - عرض المساعدة
- `/status` - حالة النظام
- `تحليل الموقع [URL]` - تحليل موقع
- `اخترق موقع [URL]` - محاكاة اختراق
- `اعطني مفتاح [Google/AWS]` - الحصول على مفتاح
- `اخترق شبكة [الاسم]` - اختراق شبكة
- `حدث النظام` - تحديث النظام

## 🌐 النشر على Render

1. أنسخ المستودع على GitHub
2. اذهب إلى [Render.com](https://render.com)
3. أنشئ خدمة Web جديدة
4. اربطها بـ GitHub
5. أضف متغيرات البيئة في الإعدادات
6. اضغط "Deploy"

## 📞 الدعم

إذا واجهت مشاكل، تحقق من:
- ملف `.env` موجود وصحيح
- Token صحيح ونشط
- المكتبات مثبتة بشكل صحيح
- الاتصال بالإنترنت يعمل

---

**آخر تحديث:** 2026-08-29
**الإصدار:** 2.0.0
