import uuid
from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID

from auth_service.src.db.postgres import Base


class LoginHistory(Base):
    __tablename__ = 'login_history'
    __table_args__ = (
        UniqueConstraint('id', 'timestamp'),
        {
            'postgresql_partition_by': 'RANGE (timestamp)',
        },
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey('auth.user.id'), nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    ip_address = Column(String(45), nullable=False)
    user_agent = Column(String(255), nullable=False)
