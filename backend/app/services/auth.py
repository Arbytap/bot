import uuid
from datetime import datetime
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import hash_password, verify_password, create_access_token
from app.models.user import User
from app.repositories.user import UserRepository
from app.repositories.company import UserCompanyRoleRepository
from app.schemas.auth import UserRegister


class AuthService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.user_repo = UserRepository(db)
        self.ucr_repo = UserCompanyRoleRepository(db)

    async def register(self, data: UserRegister) -> User:
        if await self.user_repo.get_by_email(data.email):
            raise HTTPException(status_code=400, detail="Email already registered")
        if await self.user_repo.get_by_username(data.username):
            raise HTTPException(status_code=400, detail="Username already taken")
        user = await self.user_repo.create(
            email=data.email,
            username=data.username,
            full_name=data.full_name,
            hashed_password=hash_password(data.password),
        )
        await self.db.commit()
        return user

    async def authenticate(self, username_or_email: str, password: str) -> str:
        user = await self.user_repo.get_by_email(username_or_email)
        if not user:
            user = await self.user_repo.get_by_username(username_or_email)
        if not user or not verify_password(password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect credentials",
            )
        if not user.is_active:
            raise HTTPException(status_code=403, detail="User is inactive")
        await self.user_repo.update(user.id, last_login=datetime.utcnow())
        await self.db.commit()
        return create_access_token(user.id)

    async def switch_company(self, user: User, company_id: uuid.UUID) -> User:
        has_access = await self.user_repo.has_company_access(user.id, company_id)
        if not has_access and not user.is_superuser:
            raise HTTPException(status_code=403, detail="No access to this company")
        updated = await self.user_repo.update(user.id, current_company_id=company_id)
        await self.db.commit()
        return updated
