import uuid
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.approval import ApprovalRoute, ApprovalTask
from app.models.user import User
from app.repositories.approval import ApprovalRouteRepository, ApprovalTaskRepository, ApprovalStepRepository
from app.repositories.project import ProjectCompanyRepository
from app.schemas.approval import ApprovalRouteCreate, ApprovalStepCreate, ApprovalStartRequest, ApprovalTaskUpdate


class ApprovalService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.route_repo = ApprovalRouteRepository(db)
        self.step_repo = ApprovalStepRepository(db)
        self.task_repo = ApprovalTaskRepository(db)
        self.pc_repo = ProjectCompanyRepository(db)

    async def create_route(self, data: ApprovalRouteCreate, current_user: User) -> ApprovalRoute:
        route = await self.route_repo.create(**data.model_dump())
        await self.db.commit()
        return route

    async def add_step(self, route_id: uuid.UUID, data: ApprovalStepCreate) -> None:
        route = await self.route_repo.get(route_id)
        if not route:
            raise HTTPException(status_code=404, detail="Route not found")
        await self.step_repo.create(route_id=route_id, **data.model_dump())
        await self.db.commit()

    async def start_approval(
        self, data: ApprovalStartRequest, current_user: User, current_company_id: uuid.UUID
    ) -> ApprovalTask:
        await self._check_project_access(data.project_id, current_company_id)
        task = await self.task_repo.create(
            created_by_id=current_user.id,
            **data.model_dump(),
        )
        await self.db.commit()
        return task

    async def update_task(
        self, task_id: uuid.UUID, data: ApprovalTaskUpdate, current_user: User
    ) -> ApprovalTask:
        task = await self.task_repo.get(task_id)
        if not task:
            raise HTTPException(status_code=404, detail="Task not found")
        updated = await self.task_repo.update(
            task_id, **{k: v for k, v in data.model_dump().items() if v is not None}
        )
        await self.db.commit()
        return updated

    async def list_tasks(
        self,
        project_id: uuid.UUID,
        current_company_id: uuid.UUID,
        assignee_id: uuid.UUID | None = None,
        status: str | None = None,
        offset: int = 0,
        limit: int = 50,
    ):
        await self._check_project_access(project_id, current_company_id)
        return await self.task_repo.get_by_project(
            project_id, assignee_id=assignee_id, status=status, offset=offset, limit=limit
        )

    async def _check_project_access(self, project_id: uuid.UUID, company_id: uuid.UUID) -> None:
        if not await self.pc_repo.company_in_project(project_id, company_id):
            raise HTTPException(status_code=403, detail="Company has no access to this project")
