import uuid
import os
import aiofiles
from pathlib import Path
from fastapi import HTTPException, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.models.sed import Chain, Letter, LetterFile
from app.models.user import User
from app.repositories.sed import ChainRepository, LetterRepository, LetterFileRepository
from app.repositories.project import ProjectCompanyRepository
from app.schemas.sed import ChainCreate, ChainUpdate, LetterCreate, LetterUpdate


class SEDService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.chain_repo = ChainRepository(db)
        self.letter_repo = LetterRepository(db)
        self.file_repo = LetterFileRepository(db)
        self.pc_repo = ProjectCompanyRepository(db)

    # ─── Chains ──────────────────────────────────────────────────────────────

    async def create_chain(self, data: ChainCreate, current_company_id: uuid.UUID) -> Chain:
        await self._check_project_access(data.project_id, current_company_id)
        chain = await self.chain_repo.create(**data.model_dump())
        await self.db.commit()
        return chain

    async def update_chain(
        self, chain_id: uuid.UUID, data: ChainUpdate, current_company_id: uuid.UUID
    ) -> Chain:
        chain = await self._get_chain_or_404(chain_id)
        await self._check_project_access(chain.project_id, current_company_id)
        updated = await self.chain_repo.update(
            chain_id, **{k: v for k, v in data.model_dump().items() if v is not None}
        )
        await self.db.commit()
        return updated

    async def list_chains(
        self,
        current_company_id: uuid.UUID,
        project_id: uuid.UUID | None = None,
        company_id: uuid.UUID | None = None,
        direction: str | None = None,
        offset: int = 0,
        limit: int = 50,
    ):
        return await self.chain_repo.get_accessible_chains(
            current_company_id,
            project_id=project_id,
            direction=direction,
            offset=offset,
            limit=limit,
        )

    # ─── Letters ─────────────────────────────────────────────────────────────

    async def create_letter(
        self, data: LetterCreate, current_user: User, current_company_id: uuid.UUID
    ) -> Letter:
        await self._check_project_access(data.project_id, current_company_id)
        letter = await self.letter_repo.create(
            owner_company_id=current_company_id,
            **data.model_dump(),
        )
        await self.db.commit()
        return letter

    async def update_letter(
        self, letter_id: uuid.UUID, data: LetterUpdate, current_company_id: uuid.UUID
    ) -> Letter:
        letter = await self._get_letter_or_404(letter_id)
        if letter.owner_company_id != current_company_id:
            raise HTTPException(status_code=403, detail="Only owner company can edit this letter")
        updated = await self.letter_repo.update(
            letter_id, **{k: v for k, v in data.model_dump().items() if v is not None}
        )
        await self.db.commit()
        return updated

    async def get_letter_detail(self, letter_id: uuid.UUID, current_company_id: uuid.UUID) -> Letter:
        letter = await self.letter_repo.get_detail(letter_id)
        if not letter:
            raise HTTPException(status_code=404, detail="Letter not found")
        await self._check_project_access(letter.project_id, current_company_id)
        return letter

    async def get_thread(self, letter_id: uuid.UUID, current_company_id: uuid.UUID) -> dict:
        thread = await self.letter_repo.get_thread(letter_id)
        if not thread:
            raise HTTPException(status_code=404, detail="Letter not found")
        await self._check_project_access(thread["letter"].project_id, current_company_id)
        return thread

    async def list_letters(
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
    ):
        return await self.letter_repo.get_accessible(
            current_company_id,
            letter_type=letter_type,
            project_id=project_id,
            chain_id=chain_id,
            status=status,
            from_company_id=from_company_id,
            to_company_id=to_company_id,
            offset=offset,
            limit=limit,
        )

    # ─── Files ───────────────────────────────────────────────────────────────

    async def upload_file(
        self, letter_id: uuid.UUID, file: UploadFile, current_user: User, current_company_id: uuid.UUID
    ) -> LetterFile:
        letter = await self._get_letter_or_404(letter_id)
        await self._check_project_access(letter.project_id, current_company_id)

        upload_dir = Path(settings.UPLOAD_DIR) / "letters" / str(letter_id)
        upload_dir.mkdir(parents=True, exist_ok=True)

        safe_name = f"{uuid.uuid4()}_{Path(file.filename).name}"
        dest = upload_dir / safe_name

        content = await file.read()
        if len(content) > settings.MAX_UPLOAD_SIZE:
            raise HTTPException(status_code=413, detail="File too large")

        async with aiofiles.open(dest, "wb") as f:
            await f.write(content)

        letter_file = await self.file_repo.create(
            letter_id=letter_id,
            filename=safe_name,
            original_name=file.filename,
            content_type=file.content_type or "application/octet-stream",
            size=len(content),
            storage_path=str(dest),
            uploaded_by_id=current_user.id,
        )
        await self.db.commit()
        return letter_file

    async def get_file(self, letter_id: uuid.UUID, file_id: uuid.UUID, current_company_id: uuid.UUID) -> LetterFile:
        letter = await self._get_letter_or_404(letter_id)
        await self._check_project_access(letter.project_id, current_company_id)
        file = await self.file_repo.get(file_id)
        if not file or file.letter_id != letter_id:
            raise HTTPException(status_code=404, detail="File not found")
        return file

    # ─── Helpers ─────────────────────────────────────────────────────────────

    async def _check_project_access(self, project_id: uuid.UUID, company_id: uuid.UUID) -> None:
        if not await self.pc_repo.company_in_project(project_id, company_id):
            raise HTTPException(status_code=403, detail="Company has no access to this project")

    async def _get_chain_or_404(self, chain_id: uuid.UUID) -> Chain:
        chain = await self.chain_repo.get(chain_id)
        if not chain:
            raise HTTPException(status_code=404, detail="Chain not found")
        return chain

    async def _get_letter_or_404(self, letter_id: uuid.UUID) -> Letter:
        letter = await self.letter_repo.get(letter_id)
        if not letter:
            raise HTTPException(status_code=404, detail="Letter not found")
        return letter
