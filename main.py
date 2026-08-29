from flask import Flask, render_template, request, jsonify
from app.config import Config
from app.models import Operation, SessionLocal
from app.core.analyzer import analyze_website, scan_ports
from app.core.executor import execute_bank_action, execute_wallet_action, create_wallet, execute_purchase
from app.services.db_service import save_operation, generate_op_id
import json

app = Flask(__name__)
app.config.from_object(Config)

# ===== صفحات الويب =====
@app.route('/')
def index():
    return render_template('dashboard.html')

@app.route('/api/analyze', methods=['POST'])
def api_analyze():
    data = request.json
    url = data.get('url')
    result = analyze_website(url)
    if "error" in result:
        return jsonify({"status": "error", "message": result["error"]})
    op_id = generate_op_id(url)
    save_operation(op_id, url, "تحليل موقع", "N/A", "تحليل موقع", json.dumps(result))
    return jsonify({"status": "success", "op_id": op_id, "data": result})

@app.route('/api/bank/withdraw', methods=['POST'])
def api_bank_withdraw():
    data = request.json
    result = execute_bank_action(data['account'], data['amount'], data['reason'])
    op_id = generate_op_id(data['account'])
    save_operation(op_id, data['account'], "سحب بنكي", str(data['amount']), data['reason'], json.dumps(result))
    return jsonify({"status": "success", "op_id": op_id, "data": result})

@app.route('/api/wallet/create', methods=['POST'])
def api_wallet_create():
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
