import uuid
from fastapi import APIRouter, Depends, Query, UploadFile, File
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.core.deps import get_current_user, require_company
from app.models.user import User
from app.services.sed import SEDService
from app.schemas.sed import (
    ChainCreate, ChainUpdate, ChainOut,
    LetterCreate, LetterUpdate, LetterOut, LetterDetail, LetterThread, LetterFileOut,
)
from app.schemas.common import Paginated

router = APIRouter(prefix="/api/sed", tags=["sed"])


# ─── Chains ──────────────────────────────────────────────────────────────────

@router.get("/chains", response_model=Paginated[ChainOut])
async def list_chains(
    project_id: uuid.UUID | None = Query(None),
    company_id: uuid.UUID | None = Query(None),
    direction: str | None = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    current_company_id: uuid.UUID = Depends(require_company),
):
    service = SEDService(db)
    offset = (page - 1) * page_size
    items, total = await service.list_chains(
        current_company_id,
        project_id=project_id,
        company_id=company_id,
        direction=direction,
        offset=offset,
        limit=page_size,
    )
    return Paginated(
        items=items, total=total, page=page, page_size=page_size,
        pages=(total + page_size - 1) // page_size,
    )


@router.post("/chains", response_model=ChainOut)
async def create_chain(
    data: ChainCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    current_company_id: uuid.UUID = Depends(require_company),
):
    service = SEDService(db)
    return await service.create_chain(data, current_company_id)


@router.patch("/chains/{chain_id}", response_model=ChainOut)
async def update_chain(
    chain_id: uuid.UUID,
    data: ChainUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    current_company_id: uuid.UUID = Depends(require_company),
):
    service = SEDService(db)
    return await service.update_chain(chain_id, data, current_company_id)


# ─── Letters ─────────────────────────────────────────────────────────────────

@router.get("/letters/incoming", response_model=Paginated[LetterOut])
async def incoming_letters(
    project_id: uuid.UUID | None = Query(None),
    chain_id: uuid.UUID | None = Query(None),
    status: str | None = Query(None),
    from_company_id: uuid.UUID | None = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    current_company_id: uuid.UUID = Depends(require_company),
):
    service = SEDService(db)
    offset = (page - 1) * page_size
    items, total = await service.list_letters(
        current_company_id,
        letter_type="incoming",
        project_id=project_id,
        chain_id=chain_id,
        status=status,
        from_company_id=from_company_id,
        offset=offset,
        limit=page_size,
    )
    return Paginated(
        items=items, total=total, page=page, page_size=page_size,
        pages=(total + page_size - 1) // page_size,
    )


@router.get("/letters/outgoing", response_model=Paginated[LetterOut])
async def outgoing_letters(
    project_id: uuid.UUID | None = Query(None),
    chain_id: uuid.UUID | None = Query(None),
    status: str | None = Query(None),
    to_company_id: uuid.UUID | None = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    current_company_id: uuid.UUID = Depends(require_company),
):
    service = SEDService(db)
    offset = (page - 1) * page_size
    items, total = await service.list_letters(
        current_company_id,
        letter_type="outgoing",
        project_id=project_id,
        chain_id=chain_id,
        status=status,
        to_company_id=to_company_id,
        offset=offset,
        limit=page_size,
    )
    return Paginated(
        items=items, total=total, page=page, page_size=page_size,
        pages=(total + page_size - 1) // page_size,
    )


@router.post("/letters", response_model=LetterOut)
async def create_letter(
    data: LetterCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    current_company_id: uuid.UUID = Depends(require_company),
):
    service = SEDService(db)
    return await service.create_letter(data, current_user, current_company_id)


@router.get("/letters/{letter_id}", response_model=LetterDetail)
async def get_letter(
    letter_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    current_company_id: uuid.UUID = Depends(require_company),
):
    service = SEDService(db)
    return await service.get_letter_detail(letter_id, current_company_id)


@router.patch("/letters/{letter_id}", response_model=LetterOut)
async def update_letter(
    letter_id: uuid.UUID,
    data: LetterUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    current_company_id: uuid.UUID = Depends(require_company),
):
    service = SEDService(db)
    return await service.update_letter(letter_id, data, current_company_id)


@router.get("/letters/{letter_id}/thread", response_model=LetterThread)
async def letter_thread(
    letter_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    current_company_id: uuid.UUID = Depends(require_company),
):
    service = SEDService(db)
    return await service.get_thread(letter_id, current_company_id)


@router.post("/letters/{letter_id}/files", response_model=LetterFileOut)
async def upload_letter_file(
    letter_id: uuid.UUID,
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    current_company_id: uuid.UUID = Depends(require_company),
):
    service = SEDService(db)
    return await service.upload_file(letter_id, file, current_user, current_company_id)


@router.get("/letters/{letter_id}/files/{file_id}")
async def download_letter_file(
    letter_id: uuid.UUID,
    file_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    current_company_id: uuid.UUID = Depends(require_company),
):
    service = SEDService(db)
    letter_file = await service.get_file(letter_id, file_id, current_company_id)
    return FileResponse(
        path=letter_file.storage_path,
        filename=letter_file.original_name,
        media_type=letter_file.content_type,
    )
