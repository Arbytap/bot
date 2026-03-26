import uuid
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.core.deps import get_current_user, require_company
from app.models.user import User
from app.services.project import ProjectService
from app.schemas.project import (
    ProjectCreate, ProjectUpdate, ProjectOut, ProjectDetail,
    ProjectCompanyAdd, ProjectCompanyOut, ProjectSummary,
)
from app.schemas.common import Paginated

router = APIRouter(prefix="/api/projects", tags=["projects"])


@router.get("", response_model=Paginated[ProjectOut])
async def list_projects(
    status: str | None = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    current_company_id: uuid.UUID = Depends(require_company),
):
    service = ProjectService(db)
    offset = (page - 1) * page_size
    items, total = await service.list_projects(
        current_company_id, status=status, offset=offset, limit=page_size
    )
    return Paginated(
        items=items, total=total, page=page, page_size=page_size,
        pages=(total + page_size - 1) // page_size
    )


@router.post("", response_model=ProjectDetail)
async def create_project(
    data: ProjectCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    current_company_id: uuid.UUID = Depends(require_company),
):
    service = ProjectService(db)
    return await service.create(data, current_user)


@router.get("/{project_id}", response_model=ProjectDetail)
async def get_project(
    project_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    current_company_id: uuid.UUID = Depends(require_company),
):
    service = ProjectService(db)
    return await service.get_detail(project_id, current_company_id)


@router.patch("/{project_id}", response_model=ProjectDetail)
async def update_project(
    project_id: uuid.UUID,
    data: ProjectUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    current_company_id: uuid.UUID = Depends(require_company),
):
    service = ProjectService(db)
    return await service.update(project_id, data, current_company_id)


@router.get("/{project_id}/summary", response_model=ProjectSummary)
async def project_summary(
    project_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    current_company_id: uuid.UUID = Depends(require_company),
):
    service = ProjectService(db)
    return await service.get_summary(project_id, current_company_id)


@router.post("/{project_id}/companies", response_model=ProjectCompanyOut)
async def add_company_to_project(
    project_id: uuid.UUID,
    data: ProjectCompanyAdd,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    current_company_id: uuid.UUID = Depends(require_company),
):
    service = ProjectService(db)
    return await service.add_company(project_id, data, current_company_id)


@router.delete("/{project_id}/companies/{company_id}", status_code=204)
async def remove_company_from_project(
    project_id: uuid.UUID,
    company_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    current_company_id: uuid.UUID = Depends(require_company),
):
    service = ProjectService(db)
    await service.remove_company(project_id, company_id, current_company_id)
