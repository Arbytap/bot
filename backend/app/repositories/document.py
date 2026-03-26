import uuid
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload

from app.models.document import ProjectDocument, ProjectDocumentFile
from app.models.project import ProjectCompany
from app.repositories.base import BaseRepository


class DocumentRepository(BaseRepository[ProjectDocument]):
    model = ProjectDocument

    async def get_detail(self, doc_id: uuid.UUID) -> ProjectDocument | None:
        result = await self.db.execute(
            select(ProjectDocument)
            .options(
                selectinload(ProjectDocument.owner_company),
                selectinload(ProjectDocument.files),
            )
            .where(ProjectDocument.id == doc_id)
        )
        return result.scalar_one_or_none()

    async def get_accessible(
        self,
        current_company_id: uuid.UUID,
        project_id: uuid.UUID | None = None,
        doc_type: str | None = None,
        status: str | None = None,
        offset: int = 0,
        limit: int = 50,
    ) -> tuple[list[ProjectDocument], int]:
        accessible_projects = select(ProjectCompany.project_id).where(
            ProjectCompany.company_id == current_company_id
        )
        filters = [ProjectDocument.project_id.in_(accessible_projects)]
        if project_id:
            filters.append(ProjectDocument.project_id == project_id)
        if doc_type:
            filters.append(ProjectDocument.doc_type == doc_type)
        if status:
            filters.append(ProjectDocument.status == status)
        return await self.get_many(
            filters=filters, order_by=ProjectDocument.created_at.desc(), offset=offset, limit=limit
        )


class DocumentFileRepository(BaseRepository[ProjectDocumentFile]):
    model = ProjectDocumentFile

    async def get_by_document(self, document_id: uuid.UUID) -> list[ProjectDocumentFile]:
        result = await self.db.execute(
            select(ProjectDocumentFile).where(
                ProjectDocumentFile.document_id == document_id
            )
        )
        return list(result.scalars().all())
