python
import hashlib
import random
import json
from datetime import datetime
from app.models import Operation, SessionLocal
from app.core.analyzer import analyze_website

def generate_op_id(target):
    raw = f"{target}_{datetime.now().isoformat()}_{random.randint(1000, 9999)}"
    return hashlib.sha256(raw.encode()).hexdigest()[:12].upper()

def save_operation(op_id, target, action, amount, reason, report):
    db = SessionLocal()
    op = Operation(
        op_id=op_id,
        target=target,
        action=action,
        amount=amount,
        reason=reason,
        report=report
    )
    db.add(op)
    db.commit()
    db.close()
