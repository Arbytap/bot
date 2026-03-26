import uuid
from fastapi import APIRouter, Depends, Query, UploadFile, File
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.core.deps import get_current_user, require_company
from app.models.user import User
from app.services.document import DocumentService
from app.schemas.document import (
    DocumentCreate, DocumentUpdate, DocumentOut, DocumentDetail, DocumentFileOut
)
from app.schemas.common import Paginated

router = APIRouter(prefix="/api/documents", tags=["documents"])


@router.get("", response_model=Paginated[DocumentOut])
async def list_documents(
    project_id: uuid.UUID | None = Query(None),
    doc_type: str | None = Query(None),
    status: str | None = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    current_company_id: uuid.UUID = Depends(require_company),
):
    service = DocumentService(db)
    offset = (page - 1) * page_size
    items, total = await service.list_documents(
        current_company_id,
        project_id=project_id,
        doc_type=doc_type,
        status=status,
        offset=offset,
        limit=page_size,
    )
    return Paginated(
        items=items, total=total, page=page, page_size=page_size,
        pages=(total + page_size - 1) // page_size,
    )


@router.post("", response_model=DocumentOut)
async def create_document(
    data: DocumentCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    current_company_id: uuid.UUID = Depends(require_company),
):
    service = DocumentService(db)
    return await service.create(data, current_user, current_company_id)


@router.get("/{doc_id}", response_model=DocumentDetail)
async def get_document(
    doc_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    current_company_id: uuid.UUID = Depends(require_company),
):
    service = DocumentService(db)
    return await service.get_detail(doc_id, current_company_id)


@router.patch("/{doc_id}", response_model=DocumentOut)
async def update_document(
    doc_id: uuid.UUID,
    data: DocumentUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    current_company_id: uuid.UUID = Depends(require_company),
):
    service = DocumentService(db)
    return await service.update(doc_id, data, current_company_id)


@router.post("/{doc_id}/files", response_model=DocumentFileOut)
async def upload_document_file(
    doc_id: uuid.UUID,
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    current_company_id: uuid.UUID = Depends(require_company),
):
    service = DocumentService(db)
    return await service.upload_file(doc_id, file, current_user, current_company_id)


@router.get("/{doc_id}/files/{file_id}")
async def download_document_file(
    doc_id: uuid.UUID,
    file_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    current_company_id: uuid.UUID = Depends(require_company),
):
    service = DocumentService(db)
    doc_file = await service.get_file(doc_id, file_id, current_company_id)
    return FileResponse(
        path=doc_file.storage_path,
        filename=doc_file.original_name,
        media_type=doc_file.content_type,
    )


@router.post("/{doc_id}/link-letter", response_model=DocumentOut)
async def link_letter(
    doc_id: uuid.UUID,
    letter_id: uuid.UUID = Query(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    current_company_id: uuid.UUID = Depends(require_company),
):
    service = DocumentService(db)
    return await service.link_letter(doc_id, letter_id, current_company_id)
