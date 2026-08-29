from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.models import Operation, SessionLocal
from app.core.analyzer import analyze_website, scan_ports
from app.core.executor import execute_bank_action, execute_wallet_action, create_wallet
from app.services.db_service import save_operation, generate_op_id

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/analyze")
def analyze(url: str):
    result = analyze_website(url)
    if "error" in result:
        return {"status": "error", "message": result["error"]}
    op_id = generate_op_id(url)
    save_operation(op_id, url, "تحليل موقع", "N/A", "تحليل موقع", json.dumps(result))
    return {"status": "success", "op_id": op_id, "data": result}

@router.post("/bank/withdraw")
def bank_withdraw(account: str, amount: float, reason: str):
    result = execute_bank_action(account, amount, reason)
    op_id = generate_op_id(account)
    save_operation(op_id, account, "سحب بنكي", str(amount), reason, json.dumps(result))
    return {"status": "success", "op_id": op_id, "data": result}

@router.post("/wallet/create")
def wallet_create():
    result = create_wallet()
    op_id = generate_op_id(result["wallet"])
    save_operation(op_id, result["wallet"], "إنشاء محفظة", "0", "إنشاء محفظة جديدة", json.dumps(result))
    return {"status": "success", "op_id": op_id, "data": result}

@router.get("/operation/{op_id}")
def get_operation(op_id: str, db: Session = Depends(get_db)):
    op = db.query(Operation).filter(Operation.op_id == op_id).first()
    if not op:
        raise HTTPException(status_code=404, detail="عملية غير موجودة")
    return {"status": "success", "data": op.to_dict()}
