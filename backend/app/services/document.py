import uuid
from pathlib import Path
from fastapi import HTTPException, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

import aiofiles

from app.config import settings
from app.models.document import ProjectDocument, ProjectDocumentFile
from app.models.user import User
from app.repositories.document import DocumentRepository, DocumentFileRepository
from app.repositories.project import ProjectCompanyRepository
from app.schemas.document import DocumentCreate, DocumentUpdate


class DocumentService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = DocumentRepository(db)
        self.file_repo = DocumentFileRepository(db)
        self.pc_repo = ProjectCompanyRepository(db)

    async def create(self, data: DocumentCreate, current_user: User, current_company_id: uuid.UUID) -> ProjectDocument:
        await self._check_access(data.project_id, current_company_id)
        doc = await self.repo.create(owner_company_id=current_company_id, **data.model_dump())
        await self.db.commit()
        return doc

    async def update(
        self, doc_id: uuid.UUID, data: DocumentUpdate, current_company_id: uuid.UUID
    ) -> ProjectDocument:
        doc = await self._get_or_404(doc_id)
        if doc.owner_company_id != current_company_id:
            raise HTTPException(status_code=403, detail="Only owner company can edit this document")
        updated = await self.repo.update(
            doc_id, **{k: v for k, v in data.model_dump().items() if v is not None}
        )
        await self.db.commit()
        return updated

    async def get_detail(self, doc_id: uuid.UUID, current_company_id: uuid.UUID) -> ProjectDocument:
        doc = await self.repo.get_detail(doc_id)
        if not doc:
            raise HTTPException(status_code=404, detail="Document not found")
        await self._check_access(doc.project_id, current_company_id)
        return doc

    async def list_documents(
        self,
        current_company_id: uuid.UUID,
        project_id: uuid.UUID | None = None,
        doc_type: str | None = None,
        status: str | None = None,
        offset: int = 0,
        limit: int = 50,
    ):
        return await self.repo.get_accessible(
            current_company_id,
            project_id=project_id,
            doc_type=doc_type,
            status=status,
            offset=offset,
            limit=limit,
        )

    async def upload_file(
        self, doc_id: uuid.UUID, file: UploadFile, current_user: User, current_company_id: uuid.UUID
    ) -> ProjectDocumentFile:
        doc = await self._get_or_404(doc_id)
        await self._check_access(doc.project_id, current_company_id)

        upload_dir = Path(settings.UPLOAD_DIR) / "documents" / str(doc_id)
        upload_dir.mkdir(parents=True, exist_ok=True)

        safe_name = f"{uuid.uuid4()}_{Path(file.filename).name}"
        dest = upload_dir / safe_name

        content = await file.read()
        if len(content) > settings.MAX_UPLOAD_SIZE:
            raise HTTPException(status_code=413, detail="File too large")

        async with aiofiles.open(dest, "wb") as f:
            await f.write(content)

        doc_file = await self.file_repo.create(
            document_id=doc_id,
            filename=safe_name,
            original_name=file.filename,
            content_type=file.content_type or "application/octet-stream",
            size=len(content),
            storage_path=str(dest),
            version=doc.version,
            uploaded_by_id=current_user.id,
        )
        await self.db.commit()
        return doc_file

    async def get_file(self, doc_id: uuid.UUID, file_id: uuid.UUID, current_company_id: uuid.UUID) -> ProjectDocumentFile:
        doc = await self._get_or_404(doc_id)
        await self._check_access(doc.project_id, current_company_id)
        file = await self.file_repo.get(file_id)
        if not file or file.document_id != doc_id:
            raise HTTPException(status_code=404, detail="File not found")
        return file

    async def link_letter(self, doc_id: uuid.UUID, letter_id: uuid.UUID, current_company_id: uuid.UUID) -> ProjectDocument:
        doc = await self._get_or_404(doc_id)
        if doc.owner_company_id != current_company_id:
            raise HTTPException(status_code=403, detail="Only owner company can link letters")
        updated = await self.repo.update(doc_id, linked_letter_id=letter_id)
        await self.db.commit()
        return updated

    async def _check_access(self, project_id: uuid.UUID, company_id: uuid.UUID) -> None:
        if not await self.pc_repo.company_in_project(project_id, company_id):
            raise HTTPException(status_code=403, detail="Company has no access to this project")

    async def _get_or_404(self, doc_id: uuid.UUID) -> ProjectDocument:
        doc = await self.repo.get(doc_id)
        if not doc:
            raise HTTPException(status_code=404, detail="Document not found")
        return doc
