python
from flask import Flask, render_template
from app.config import Config
from app.api.routes import api
from app.services.telegram_bot import run_bot
import threading

app = Flask(__name__)
app.config.from_object(Config)
app.register_blueprint(api, url_prefix='/api')

@app.route('/')
def index():
    return render_template('dashboard.html')

if __name__ == '__main__':
    # تشغيل البوت في خلفية
    threading.Thread(target=run_bot, daemon=True).start()
    # تشغيل Flask
    app.run(host='0.0.0.0', port=5000, debug=Config.DEBUG)
