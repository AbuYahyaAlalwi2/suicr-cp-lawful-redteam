# app/main.py (محدث)
from flask import Flask, render_template
from app.config import Config
from app.api.routes import api
from app.services.telegram_bot import run_bot
from app.core.tor_manager import TorManager
from app.core.stealth_network import StealthNetwork
import threading
import logging

# تفعيل السجلات
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config.from_object(Config)
app.register_blueprint(api, url_prefix='/api')

# ===== بدء تشغيل Tor تلقائياً عند تشغيل النظام =====
def initialize_stealth():
    """تهيئة الشبكة المخفية وتشغيل Tor"""
    logger.info("🛡️ جاري تهيئة الاتصالات المخفية...")
    stealth = StealthNetwork()
    if stealth.tor_manager.start():
        logger.info("✅ تم تشغيل Tor بنجاح مع الجسور المحددة")
    else:
        logger.warning("⚠️ فشل تشغيل Tor، سيتم العمل بوضع المحاكاة (غير آمن)")

# تشغيل التهيئة في خلفية (حتى لا نؤخر بدء التشغيل)
threading.Thread(target=initialize_stealth, daemon=True).start()

@app.route('/')
def index():
    return render_template('dashboard.html')

if __name__ == '__main__':
    # تشغيل بوت التليجرام في خلفية
    threading.Thread(target=run_bot, daemon=True).start()
    
    # تشغيل واجهة الويب
    app.run(host='0.0.0.0', port=5000, debug=Config.DEBUG)def api_wallet_create():
    result = create_wallet()
    op_id = generate_op_id(result["wallet"])
    save_operation(op_id, result["wallet"], "إنشاء محفظة", "0", "إنشاء محفظة جديدة", json.dumps(result))
    return jsonify({"status": "success", "op_id": op_id, "data": result})

@app.route('/api/operation/<op_id>')
def api_get_operation(op_id):
    db = SessionLocal()
    op = db.query(Operation).filter(Operation.op_id == op_id).first()
    db.close()
    if not op:
        return jsonify({"status": "error", "message": "عملية غير موجودة"}), 404
    return jsonify({"status": "success", "data": op.to_dict()})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=Config.DEBUG)
