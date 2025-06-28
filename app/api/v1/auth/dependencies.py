from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from jose import JWTError, jwt
from db.session import get_db
from api.v1.auth.models import User
from api.v1.auth.user import user_crud
from core.config import settings

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db)
) -> User:
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise HTTPException(status_code=401, detail="Invalid token")
    except JWTError:
        raise HTTPException(status_code=401, detail="Could not validate credentials")

    user = await user_crud.get_by_email(db, email)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user
    

async def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

def admin_required(current_user: User = Depends(get_current_user)) -> User:
    if not current_user.is_admin():
        raise HTTPException(status_code=403, detail="Admin access required")
    return current_user

class RequireRole:
    def __init__(self, allowed_roles: list[str]):
        self.allowed_roles = allowed_roles

    async def __call__(self, current_user: User = Depends(get_current_active_user)) -> User:
        if current_user.role not in self.allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied. Required role(s): {self.allowed_roles}"
            )
        return current_user
## In editor-role
# def editor_required(current_user: User = Depends(get_current_active_user)) -> User:
#     if current_user.role not in ["admin", "editor"]:
#         raise HTTPException(status_code=403, detail="Editor access required")
#     return current_user