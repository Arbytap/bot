import uuid
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload

from app.models.sed import Chain, Letter, LetterFile
from app.models.project import ProjectCompany
from app.repositories.base import BaseRepository


class ChainRepository(BaseRepository[Chain]):
    model = Chain

    async def get_by_project(
        self,
        project_id: uuid.UUID,
        company_id: uuid.UUID | None = None,
        direction: str | None = None,
        offset: int = 0,
        limit: int = 50,
    ) -> tuple[list[Chain], int]:
        filters = [Chain.project_id == project_id]
        if company_id:
            filters.append(Chain.main_company_id == company_id)
        if direction:
            filters.append(Chain.direction == direction)
        return await self.get_many(
            filters=filters, order_by=Chain.created_at.desc(), offset=offset, limit=limit
        )

    async def get_accessible_chains(
        self,
        current_company_id: uuid.UUID,
        project_id: uuid.UUID | None = None,
        direction: str | None = None,
        offset: int = 0,
        limit: int = 50,
    ) -> tuple[list[Chain], int]:
        """Chains accessible to current company (via project membership)."""
        accessible_projects = select(ProjectCompany.project_id).where(
            ProjectCompany.company_id == current_company_id
        )
        filters = [Chain.project_id.in_(accessible_projects)]
        if project_id:
            filters.append(Chain.project_id == project_id)
        if direction:
            filters.append(Chain.direction == direction)
        return await self.get_many(
            filters=filters, order_by=Chain.created_at.desc(), offset=offset, limit=limit
        )


class LetterRepository(BaseRepository[Letter]):
    model = Letter

    async def get_detail(self, letter_id: uuid.UUID) -> Letter | None:
        result = await self.db.execute(
            select(Letter)
            .options(
                selectinload(Letter.owner_company),
                selectinload(Letter.from_company),
                selectinload(Letter.to_company),
                selectinload(Letter.files),
            )
            .where(Letter.id == letter_id)
        )
        return result.scalar_one_or_none()

    async def get_accessible(
        self,
        current_company_id: uuid.UUID,
        letter_type: str | None = None,
        project_id: uuid.UUID | None = None,
        chain_id: uuid.UUID | None = None,
        status: str | None = None,
        from_company_id: uuid.UUID | None = None,
        to_company_id: uuid.UUID | None = None,
        offset: int = 0,
        limit: int = 50,
    ) -> tuple[list[Letter], int]:
        accessible_projects = select(ProjectCompany.project_id).where(
            ProjectCompany.company_id == current_company_id
        )
        filters = [Letter.project_id.in_(accessible_projects)]
        if letter_type:
            filters.append(Letter.letter_type == letter_type)
        if project_id:
            filters.append(Letter.project_id == project_id)
        if chain_id:
            filters.append(Letter.chain_id == chain_id)
        if status:
            filters.append(Letter.status == status)
        if from_company_id:
            filters.append(Letter.from_company_id == from_company_id)
        if to_company_id:
            filters.append(Letter.to_company_id == to_company_id)
        return await self.get_many(
            filters=filters, order_by=Letter.letter_date.desc(), offset=offset, limit=limit
        )

    async def get_thread(self, letter_id: uuid.UUID) -> dict:
        """Get letter with its reply_to, replies, and chain siblings."""
        letter_result = await self.db.execute(
            select(Letter)
            .options(
                selectinload(Letter.owner_company),
                selectinload(Letter.from_company),
                selectinload(Letter.to_company),
                selectinload(Letter.files),
            )
            .where(Letter.id == letter_id)
        )
        letter = letter_result.scalar_one_or_none()
        if not letter:
            return {}

        reply_to = None
        if letter.reply_to_id:
            rt_result = await self.db.execute(
                select(Letter).where(Letter.id == letter.reply_to_id)
            )
            reply_to = rt_result.scalar_one_or_none()

        replies_result = await self.db.execute(
            select(Letter).where(Letter.reply_to_id == letter_id)
        )
        replies = list(replies_result.scalars().all())

        chain_result = await self.db.execute(
            select(Letter)
            .where(Letter.chain_id == letter.chain_id, Letter.id != letter_id)
            .order_by(Letter.letter_date)
        )
        chain_letters = list(chain_result.scalars().all())

        return {
            "letter": letter,
            "reply_to": reply_to,
            "replies": replies,
            "chain_letters": chain_letters,
        }

    async def count_files(self, letter_id: uuid.UUID) -> int:
        result = await self.db.execute(
            select(func.count()).select_from(LetterFile).where(LetterFile.letter_id == letter_id)
        )
        return result.scalar_one()

    async def count_replies(self, letter_id: uuid.UUID) -> int:
        result = await self.db.execute(
            select(func.count()).select_from(Letter).where(Letter.reply_to_id == letter_id)
        )
        return result.scalar_one()


class LetterFileRepository(BaseRepository[LetterFile]):
    model = LetterFile

    async def get_by_letter(self, letter_id: uuid.UUID) -> list[LetterFile]:
        result = await self.db.execute(
            select(LetterFile).where(LetterFile.letter_id == letter_id)
        )
        return list(result.scalars().all())
