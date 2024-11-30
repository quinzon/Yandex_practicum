from functools import lru_cache
from typing import Type

from fastapi import Depends
from sqlalchemy import select, insert
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from auth_service.src.db.postgres import get_session
from auth_service.src.models.entities.user import User, SocialAccount, user_role
from auth_service.src.repository.base import BaseRepository


class UserRepository(BaseRepository[User]):
    def get_model(self) -> Type[User]:
        return User

    async def get_user_by_email(self, email: str) -> User | None:
        query = select(User).options(joinedload(User.roles)).filter(User.email == email)
        result = await self.session.execute(query)
        return result.scalars().first()

    async def assign_role(self, user_id: str, role_id: str) -> None:
        stmt = insert(user_role).values(user_id=user_id, role_id=role_id)
        await self.session.execute(stmt)
        await self.session.commit()

    async def get_social_account(self, provider: str, provider_user_id: str) -> SocialAccount | None:
        query = select(SocialAccount).options(joinedload(SocialAccount.user)).filter(
            SocialAccount.provider == provider,
            SocialAccount.provider_user_id == provider_user_id
        )
        result = await self.session.execute(query)
        return result.scalars().first()

    async def create_social_account(self, user: User, provider: str, provider_user_id: str, extra_data: dict) -> None:
        existing_account = await self.session.execute(
            select(SocialAccount).where(
                SocialAccount.provider == provider,
                SocialAccount.provider_user_id == provider_user_id
            )
        )
        if existing_account.scalar_one_or_none():
            return

        new_account = SocialAccount(
            user_id=user.id,
            provider=provider,
            provider_user_id=provider_user_id,
            extra_data=extra_data
        )
        self.session.add(new_account)
        await self.session.commit()

    async def create_user(self, email: str, first_name: str, last_name: str, password_hash: str) -> User:
        user = User(
            email=email,
            first_name=first_name,
            last_name=last_name,
            password_hash=password_hash
        )
        self.session.add(user)
        await self.session.commit()
        await self.session.refresh(user)
        return user


@lru_cache()
def get_user_repository(
        session: AsyncSession = Depends(get_session)
) -> UserRepository:
    return UserRepository(session)
