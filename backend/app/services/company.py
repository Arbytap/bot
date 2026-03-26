import uuid
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.company import Company, UserCompanyRole
from app.repositories.company import CompanyRepository, UserCompanyRoleRepository
from app.schemas.company import CompanyCreate, CompanyUpdate, UserCompanyRoleCreate


class CompanyService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = CompanyRepository(db)
        self.ucr_repo = UserCompanyRoleRepository(db)

    async def create(self, data: CompanyCreate) -> Company:
        company = await self.repo.create(**data.model_dump())
        await self.db.commit()
        await self.db.refresh(company)
        return company

    async def update(self, company_id: uuid.UUID, data: CompanyUpdate) -> Company:
        company = await self.repo.update(
            company_id, **{k: v for k, v in data.model_dump().items() if v is not None}
        )
        if not company:
            raise HTTPException(status_code=404, detail="Company not found")
        await self.db.commit()
        return company

    async def get_or_404(self, company_id: uuid.UUID) -> Company:
        company = await self.repo.get(company_id)
        if not company:
            raise HTTPException(status_code=404, detail="Company not found")
        return company

    async def list_companies(self, offset: int = 0, limit: int = 50):
        return await self.repo.get_many(offset=offset, limit=limit)

    async def add_user_to_company(self, data: UserCompanyRoleCreate) -> UserCompanyRole:
        existing = await self.ucr_repo.get_by_user_and_company(data.user_id, data.company_id)
        if existing:
            raise HTTPException(status_code=400, detail="User already in company")
        role = await self.ucr_repo.create(**data.model_dump())
        await self.db.commit()
        return role
