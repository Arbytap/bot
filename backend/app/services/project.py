import uuid
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.project import Project, ProjectCompany
from app.models.user import User
from app.repositories.project import ProjectRepository, ProjectCompanyRepository
from app.schemas.project import ProjectCreate, ProjectUpdate, ProjectCompanyAdd


class ProjectService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = ProjectRepository(db)
        self.pc_repo = ProjectCompanyRepository(db)

    async def create(self, data: ProjectCreate, current_user: User) -> Project:
        existing = await self.db.execute(
            __import__("sqlalchemy").select(Project).where(Project.code == data.code)
        )
        if existing.scalar_one_or_none():
            raise HTTPException(status_code=400, detail="Project code already exists")
        project = await self.repo.create(**data.model_dump())
        # auto-add owner_company to project
        await self.pc_repo.create(
            project_id=project.id,
            company_id=data.owner_company_id,
            role="customer",
        )
        await self.db.commit()
        return await self.repo.get_detail(project.id)

    async def update(self, project_id: uuid.UUID, data: ProjectUpdate, current_company_id: uuid.UUID) -> Project:
        await self._check_access(project_id, current_company_id)
        updated = await self.repo.update(
            project_id, **{k: v for k, v in data.model_dump().items() if v is not None}
        )
        await self.db.commit()
        return await self.repo.get_detail(project_id)

    async def get_detail(self, project_id: uuid.UUID, current_company_id: uuid.UUID) -> Project:
        await self._check_access(project_id, current_company_id)
        project = await self.repo.get_detail(project_id)
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
        return project

    async def get_summary(self, project_id: uuid.UUID, current_company_id: uuid.UUID) -> dict:
        await self._check_access(project_id, current_company_id)
        return await self.repo.get_summary(project_id)

    async def list_projects(
        self,
        current_company_id: uuid.UUID,
        status: str | None = None,
        offset: int = 0,
        limit: int = 50,
    ):
        return await self.repo.get_by_company(
            current_company_id, status=status, offset=offset, limit=limit
        )

    async def add_company(
        self, project_id: uuid.UUID, data: ProjectCompanyAdd, current_company_id: uuid.UUID
    ) -> ProjectCompany:
        await self._check_access(project_id, current_company_id)
        existing = await self.pc_repo.get_by_project_and_company(project_id, data.company_id)
        if existing:
            raise HTTPException(status_code=400, detail="Company already in project")
        pc = await self.pc_repo.create(
            project_id=project_id, company_id=data.company_id, role=data.role
        )
        await self.db.commit()
        return pc

    async def remove_company(
        self, project_id: uuid.UUID, company_id: uuid.UUID, current_company_id: uuid.UUID
    ) -> None:
        await self._check_access(project_id, current_company_id)
        pc = await self.pc_repo.get_by_project_and_company(project_id, company_id)
        if not pc:
            raise HTTPException(status_code=404, detail="Company not in project")
        await self.pc_repo.delete(pc.id)
        await self.db.commit()

    async def _check_access(self, project_id: uuid.UUID, company_id: uuid.UUID) -> None:
        if not await self.pc_repo.company_in_project(project_id, company_id):
            raise HTTPException(status_code=403, detail="Company has no access to this project")
