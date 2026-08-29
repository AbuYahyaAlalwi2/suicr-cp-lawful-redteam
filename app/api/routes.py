python
from flask import Blueprint, request, jsonify
from app.core.analyzer import analyze_website, scan_ports
from app.core.executor import execute_bank_action, execute_wallet_action, create_wallet
from app.services.db_service import generate_op_id, save_operation
import json

api = Blueprint('api', __name__)

@api.route('/analyze', methods=['POST'])
def api_analyze():
    data = request.json
    url = data.get('url')
    result = analyze_website(url)
    if "error" in result:
        return jsonify({"status": "error", "message": result["error"]})
    op_id = generate_op_id(url)
    save_operation(op_id, url, "تحليل موقع", "N/A", "تحليل موقع", json.dumps(result))
    return jsonify({"status": "success", "op_id": op_id, "data": result})

@api.route('/bank/withdraw', methods=['POST'])
def api_bank_withdraw():
    data = request.json
    result = execute_bank_action(data['account'], data['amount'], data['reason'])
    op_id = generate_op_id(data['account'])
    save_operation(op_id, data['account'], "سحب بنكي", str(data['amount']), data['reason'], json.dumps(result))
    return jsonify({"status": "success", "op_id": op_id, "data": result})
