import uuid
from datetime import datetime

from sqlalchemy import Column, DateTime, String, Table, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
import bcrypt
from sqlalchemy.orm import relationship

from auth_service.src.db.postgres import Base
from auth_service.src.models.dto.user import UserCreate


class User(Base):
    __tablename__ = 'user'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    first_name = Column(String(50), nullable=True)
    last_name = Column(String(50), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    roles = relationship('Role', secondary='auth.user_role', back_populates='users',
                         lazy='selectin')

    def set_password(self, password: str) -> None:
        salt = bcrypt.gensalt()
        self.password_hash = bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

    def check_password(self, password: str) -> bool:
        return bcrypt.checkpw(password.encode('utf-8'), self.password_hash.encode('utf-8'))

    @classmethod
    def create(cls, user_create: UserCreate) -> 'User':
        user = cls(
            email=user_create.email,
            first_name=user_create.first_name,
            last_name=user_create.last_name
        )
        user.set_password(user_create.password.get_secret_value())
        return user

    def __repr__(self) -> str:
        return f'<User {self.email}>'


user_role = Table(
    'user_role',
    Base.metadata,
    Column('user_id', UUID(as_uuid=True), ForeignKey('auth.user.id', ondelete='CASCADE'), primary_key=True),
    Column('role_id', UUID(as_uuid=True), ForeignKey('auth.role.id', ondelete='CASCADE'), primary_key=True),
    schema='auth'
)
