import uuid
from sqlalchemy import select
from app.models.company import Company, UserCompanyRole
from app.repositories.base import BaseRepository


class CompanyRepository(BaseRepository[Company]):
    model = Company


class UserCompanyRoleRepository(BaseRepository[UserCompanyRole]):
    model = UserCompanyRole

    async def get_by_user_and_company(
        self, user_id: uuid.UUID, company_id: uuid.UUID
    ) -> UserCompanyRole | None:
        result = await self.db.execute(
            select(UserCompanyRole).where(
                UserCompanyRole.user_id == user_id,
                UserCompanyRole.company_id == company_id,
            )
        )
        return result.scalar_one_or_none()
