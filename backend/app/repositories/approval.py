import uuid
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.models.approval import ApprovalRoute, ApprovalStep, ApprovalTask
from app.repositories.base import BaseRepository


class ApprovalRouteRepository(BaseRepository[ApprovalRoute]):
    model = ApprovalRoute

    async def get_with_steps(self, route_id: uuid.UUID) -> ApprovalRoute | None:
        result = await self.db.execute(
            select(ApprovalRoute)
            .options(selectinload(ApprovalRoute.steps))
            .where(ApprovalRoute.id == route_id)
        )
        return result.scalar_one_or_none()


class ApprovalStepRepository(BaseRepository[ApprovalStep]):
    model = ApprovalStep


class ApprovalTaskRepository(BaseRepository[ApprovalTask]):
    model = ApprovalTask

    async def get_by_project(
        self,
        project_id: uuid.UUID,
        assignee_id: uuid.UUID | None = None,
        status: str | None = None,
        offset: int = 0,
        limit: int = 50,
    ) -> tuple[list[ApprovalTask], int]:
        filters = [ApprovalTask.project_id == project_id]
        if assignee_id:
            filters.append(ApprovalTask.assignee_id == assignee_id)
        if status:
            filters.append(ApprovalTask.status == status)
        return await self.get_many(
            filters=filters, order_by=ApprovalTask.created_at.desc(), offset=offset, limit=limit
        )
