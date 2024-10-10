import uuid
from datetime import datetime

from sqlalchemy import Column, UUID, ForeignKey, String, Date, Boolean, DateTime

from auth_service.src.db.postgres import Base


class Subscription(Base):
    __tablename__ = 'subscription'
    __table_args__ = {'schema': 'auth'}

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey('auth.user.id'), nullable=False)
    subscription_type = Column(String(50), nullable=False)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    is_active = Column(Boolean, nullable=False, default=True)
    auto_renewal = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, nullable=False)
