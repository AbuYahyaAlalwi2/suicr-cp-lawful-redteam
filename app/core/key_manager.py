python
from sqlalchemy.orm import Session
from app.models import Key, SessionLocal
from datetime import datetime
import json

class KeyManager:
    @staticmethod
    def get_active_key(platform):
        db = SessionLocal()
        key = db.query(Key).filter(
            Key.platform == platform,
            Key.is_active == True,
            (Key.expires_at > datetime.utcnow()) | (Key.expires_at == None)
        ).first()
        db.close()
        if key:
            return json.loads(key.key_data)
        return None
    
    @staticmethod
    def get_best_cloud_for_task(task_type):
        available = []
        for platform in ['google', 'aws', 'oracle']:
            key = KeyManager.get_active_key(platform)
            if key:
                available.append(platform)
        if not available:
            return None
        return available[0]
