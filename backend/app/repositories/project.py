import uuid
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload

from app.models.project import Project, ProjectCompany
from app.models.sed import Letter, Chain
from app.models.document import ProjectDocument
from app.models.approval import ApprovalTask
from app.repositories.base import BaseRepository


class ProjectRepository(BaseRepository[Project]):
    model = Project

    async def get_detail(self, project_id: uuid.UUID) -> Project | None:
        result = await self.db.execute(
            select(Project)
            .options(
                selectinload(Project.owner_company),
                selectinload(Project.project_companies).selectinload(ProjectCompany.company),
            )
            .where(Project.id == project_id)
        )
        return result.scalar_one_or_none()

    async def get_by_company(
        self,
        company_id: uuid.UUID,
        status: str | None = None,
        offset: int = 0,
        limit: int = 50,
    ) -> tuple[list[Project], int]:
        """Get projects where company participates (via project_companies)."""
        subq = select(ProjectCompany.project_id).where(
            ProjectCompany.company_id == company_id
        )
        filters = [Project.id.in_(subq)]
        if status:
            filters.append(Project.status == status)
        return await self.get_many(filters=filters, order_by=Project.created_at.desc(), offset=offset, limit=limit)

    async def get_summary(self, project_id: uuid.UUID) -> dict:
        letters_count = (
            await self.db.execute(
                select(func.count()).select_from(Letter).where(Letter.project_id == project_id)
            )
        ).scalar_one()
        incoming = (
            await self.db.execute(
                select(func.count()).select_from(Letter).where(
                    Letter.project_id == project_id, Letter.letter_type == "incoming"
                )
            )
        ).scalar_one()
        outgoing = (
            await self.db.execute(
                select(func.count()).select_from(Letter).where(
                    Letter.project_id == project_id, Letter.letter_type == "outgoing"
                )
            )
        ).scalar_one()
        docs = (
            await self.db.execute(
                select(func.count()).select_from(ProjectDocument).where(
                    ProjectDocument.project_id == project_id
                )
            )
        ).scalar_one()
        tasks = (
            await self.db.execute(
                select(func.count()).select_from(ApprovalTask).where(
                    ApprovalTask.project_id == project_id
                )
            )
        ).scalar_one()
        chains = (
            await self.db.execute(
                select(func.count()).select_from(Chain).where(Chain.project_id == project_id)
            )
        ).scalar_one()
        return {
            "project_id": project_id,
            "letters_count": letters_count,
            "incoming_count": incoming,
            "outgoing_count": outgoing,
            "documents_count": docs,
            "approval_tasks_count": tasks,
            "chains_count": chains,
        }


class ProjectCompanyRepository(BaseRepository[ProjectCompany]):
    model = ProjectCompany

    async def get_by_project(self, project_id: uuid.UUID) -> list[ProjectCompany]:
        result = await self.db.execute(
            select(ProjectCompany)
            .options(selectinload(ProjectCompany.company))
            .where(ProjectCompany.project_id == project_id)
        )
        return list(result.scalars().all())

    async def get_by_project_and_company(
        self, project_id: uuid.UUID, company_id: uuid.UUID
    ) -> ProjectCompany | None:
        result = await self.db.execute(
            select(ProjectCompany).where(
                ProjectCompany.project_id == project_id,
                ProjectCompany.company_id == company_id,
            )
        )
        return result.scalar_one_or_none()

    async def company_in_project(self, project_id: uuid.UUID, company_id: uuid.UUID) -> bool:
        return (await self.get_by_project_and_company(project_id, company_id)) is not None
