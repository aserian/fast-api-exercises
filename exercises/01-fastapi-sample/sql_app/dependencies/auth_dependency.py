
from fastapi import Depends, HTTPException, Request, status
from fastapi.security import APIKeyHeader

from sqlalchemy.orm import Session
from ..database import get_db
from .. import crud, schemas
from ..utils.auth import AuthenticatedUser, UnauthenticatedUser

from ..schemas import User
from .. import models


api_key_header = APIKeyHeader(name="X-API-TOKEN", auto_error=True)


def verify_active_user(request: Request, db: Session = Depends(get_db), api_key: str = Depends(api_key_header)) -> models.User:
    # 認証済みか確認
    if not request.user.is_authenticated:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
    # アクティブユーザーか確認
    db_user = crud.get_active_user(db, user_id=request.user.id)
    if not db_user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
    return db_user
