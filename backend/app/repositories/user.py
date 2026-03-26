import uuid
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.models.user import User
from app.models.company import UserCompanyRole
from app.repositories.base import BaseRepository


class UserRepository(BaseRepository[User]):
    model = User

    async def get_by_email(self, email: str) -> User | None:
        result = await self.db.execute(select(User).where(User.email == email))
        return result.scalar_one_or_none()

    async def get_by_username(self, username: str) -> User | None:
        result = await self.db.execute(select(User).where(User.username == username))
        return result.scalar_one_or_none()

    async def get_user_companies(self, user_id: uuid.UUID) -> list[UserCompanyRole]:
        result = await self.db.execute(
            select(UserCompanyRole)
            .options(selectinload(UserCompanyRole.company))
            .where(UserCompanyRole.user_id == user_id, UserCompanyRole.is_active == True)
        )
        return list(result.scalars().all())

    async def has_company_access(self, user_id: uuid.UUID, company_id: uuid.UUID) -> bool:
        result = await self.db.execute(
            select(UserCompanyRole).where(
                UserCompanyRole.user_id == user_id,
                UserCompanyRole.company_id == company_id,
                UserCompanyRole.is_active == True,
            )
        )
        return result.scalar_one_or_none() is not None
