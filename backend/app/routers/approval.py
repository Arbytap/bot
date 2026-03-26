import uuid
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.core.deps import get_current_user, require_company
from app.models.user import User
from app.services.approval import ApprovalService
from app.schemas.approval import (
    ApprovalRouteCreate, ApprovalStepCreate, ApprovalStartRequest,
    ApprovalTaskUpdate, ApprovalTaskOut,
)
from app.schemas.common import Paginated

router = APIRouter(prefix="/api/approval", tags=["approval"])


@router.post("/routes")
async def create_route(
    data: ApprovalRouteCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = ApprovalService(db)
    return await service.create_route(data, current_user)


@router.post("/routes/{route_id}/steps", status_code=201)
async def add_step(
    route_id: uuid.UUID,
    data: ApprovalStepCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = ApprovalService(db)
    await service.add_step(route_id, data)
    return {"status": "ok"}


@router.post("/start", response_model=ApprovalTaskOut)
async def start_approval(
    data: ApprovalStartRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    current_company_id: uuid.UUID = Depends(require_company),
):
    service = ApprovalService(db)
    return await service.start_approval(data, current_user, current_company_id)


@router.get("/tasks", response_model=Paginated[ApprovalTaskOut])
async def list_tasks(
    project_id: uuid.UUID = Query(...),
    assignee: uuid.UUID | None = Query(None),
    status: str | None = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    current_company_id: uuid.UUID = Depends(require_company),
):
    service = ApprovalService(db)
    offset = (page - 1) * page_size
    items, total = await service.list_tasks(
        project_id, current_company_id,
        assignee_id=assignee, status=status,
        offset=offset, limit=page_size,
    )
    return Paginated(
        items=items, total=total, page=page, page_size=page_size,
        pages=(total + page_size - 1) // page_size,
    )


@router.patch("/tasks/{task_id}", response_model=ApprovalTaskOut)
async def update_task(
    task_id: uuid.UUID,
    data: ApprovalTaskUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = ApprovalService(db)
    return await service.update_task(task_id, data, current_user)
