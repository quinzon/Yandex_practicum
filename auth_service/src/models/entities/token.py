import uuid

from sqlalchemy import Column, UUID, ForeignKey, Text, DateTime

from auth_service.src.db.postgres import Base


class RefreshToken(Base):
    __tablename__ = 'refresh_token'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey('user.id'), nullable=False)
    token_value = Column(Text, nullable=False)
    expires_at = Column(DateTime, nullable=False)
    created_at = Column(DateTime, nullable=False)
