python
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Text, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
from app.config import Config

Base = declarative_base()
engine = create_engine(Config.DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)

class Operation(Base):
    __tablename__ = 'operations'
    id = Column(Integer, primary_key=True, index=True)
    op_id = Column(String(20), unique=True, index=True)
    target = Column(String(255))
    action = Column(String(100))
    amount = Column(String(50))
    reason = Column(Text)
    timestamp = Column(DateTime, default=datetime.utcnow)
    report = Column(Text)

    def to_dict(self):
        return {
            'id': self.id,
            'op_id': self.op_id,
            'target': self.target,
            'action': self.action,
            'amount': self.amount,
            'reason': self.reason,
            'timestamp': self.timestamp.isoformat(),
            'report': self.report
        }

class Key(Base):
    __tablename__ = 'keys'
    id = Column(Integer, primary_key=True)
    platform = Column(String(50))
    key_data = Column(Text)
    is_active = Column(Boolean, default=True)
    expires_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_used = Column(DateTime, nullable=True)
