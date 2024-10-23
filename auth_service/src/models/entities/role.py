import uuid

from sqlalchemy import UUID, Column, String, Table, ForeignKey
from sqlalchemy.orm import relationship

from auth_service.src.db.postgres import Base


class Role(Base):
    __tablename__ = 'role'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
    name = Column(String(50), nullable=False, unique=True)
    permissions = relationship('Permission', secondary='auth.role_permission', back_populates='roles',
                               lazy='selectin')
    users = relationship('User', secondary='auth.user_role', back_populates='roles',
                         lazy='selectin')


role_permission = Table(
    'role_permission',
    Base.metadata,
    Column('role_id', UUID(as_uuid=True), ForeignKey('auth.role.id', ondelete='CASCADE'), primary_key=True),
    Column('permission_id', UUID(as_uuid=True), ForeignKey('auth.permission.id', ondelete='CASCADE'), primary_key=True),
    schema='auth'
)
