import uuid

from sqlalchemy import Column, UUID, String
from sqlalchemy.orm import relationship

from auth_service.src.db.postgres import Base


class Permission(Base):
    __tablename__ = 'permission'
    __table_args__ = {'schema': 'auth'}

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
    name = Column(String(50), nullable=False, unique=True)
    http_method = Column(String(50), nullable=False)
    resource = Column(String(50), nullable=False)

    roles = relationship('Role', secondary='auth.role_permission', back_populates='permissions',
                         lazy="selectin")
