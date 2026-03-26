import uuid
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.core.deps import get_current_user, require_superuser
from app.models.user import User
from app.services.company import CompanyService
from app.schemas.company import CompanyCreate, CompanyUpdate, CompanyOut, UserCompanyRoleCreate, UserCompanyRoleOut
from app.schemas.common import Paginated

router = APIRouter(prefix="/api/companies", tags=["companies"])


@router.get("", response_model=Paginated[CompanyOut])
async def list_companies(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = CompanyService(db)
    offset = (page - 1) * page_size
    items, total = await service.list_companies(offset=offset, limit=page_size)
    return Paginated(
        items=items, total=total, page=page, page_size=page_size,
        pages=(total + page_size - 1) // page_size
    )


@router.post("", response_model=CompanyOut)
async def create_company(
    data: CompanyCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_superuser),
):
    service = CompanyService(db)
    return await service.create(data)


@router.get("/{company_id}", response_model=CompanyOut)
async def get_company(
    company_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = CompanyService(db)
    return await service.get_or_404(company_id)


@router.patch("/{company_id}", response_model=CompanyOut)
async def update_company(
    company_id: uuid.UUID,
    data: CompanyUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_superuser),
):
    service = CompanyService(db)
    return await service.update(company_id, data)


@router.post("/users/assign", response_model=UserCompanyRoleOut)
async def assign_user(
    data: UserCompanyRoleCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_superuser),
):
    service = CompanyService(db)
    return await service.add_user_to_company(data)
