from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from api.v1.auth.models import User
from api.v1.auth.security import get_password_hash, verify_password

class UserCRUD:
    async def get_by_email(self, db: AsyncSession, email: str) -> User | None:
        result = await db.execute(select(User).where(User.email == email))
        return result.scalar_one_or_none()

    async def get_by_id(self, db: AsyncSession, user_id: int) -> User | None:
        result = await db.execute(select(User).where(User.id == user_id))
        return result.scalar_one_or_none()

    async def create_user(self, db: AsyncSession, user_data) -> User:
        hashed_password = get_password_hash(user_data.password)
        db_user = User(
            first_name=user_data.first_name,
            last_name=user_data.last_name,
            email=user_data.email,
            password=hashed_password,
            role=user_data.role
        )
        db.add(db_user)
        await db.commit()
        await db.refresh(db_user)
        return db_user

    async def update_password(self, db: AsyncSession, user_id: int, new_password: str) -> User | None:
        user = await self.get_by_id(db, user_id)
        if not user:
            return None
        user.password = get_password_hash(new_password)
        await db.commit()
        await db.refresh(user)
        return user

    async def authenticate(self, db: AsyncSession, email: str, password: str) -> User | None:
        user = await self.get_by_email(db, email)
        if not user or not verify_password(password, user.password):
            return None
        return user

    async def get_all_users(self, db: AsyncSession) -> list[User]:
        result = await db.execute(select(User))
        return result.scalars().all() 
    
    async def delete_user(self, db: AsyncSession, user_id: int) -> None | str:
        user = await self.get_by_id(db, user_id)
        if user.role == "admin":   #ask admin to delete admin ? 
            return "Cannot delete an admin user"
        if user:
            await db.delete(user)
            await db.commit()   
    
user_crud = UserCRUD()