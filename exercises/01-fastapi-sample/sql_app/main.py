from typing import List

from fastapi import Depends, FastAPI, APIRouter, HTTPException, Request
from sqlalchemy.orm import Session

from . import crud, models, schemas
from .database import SessionLocal, engine, get_db

from .utils.jwt import jwt_claims,jwt_encode

from starlette.middleware.authentication import AuthenticationMiddleware
from .middlewares import AuthenticationBackend

from .dependencies.auth_dependency import verify_active_user

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

# memo: 認証済みのユーザーID取得用に認証ミドルウェアを追加
app.add_middleware(AuthenticationMiddleware, backend=AuthenticationBackend())

db_session = Depends(get_db)

public_router = APIRouter()
authentication_router = APIRouter(dependencies=[Depends(verify_active_user)])


# memo: ヘルスチェックようなので、認証は不要なためpublicルーターに追加
@public_router.get("/health-check")
def health_check(db: Session = db_session):
    return {"status": "ok"}


@public_router.post("/users/", response_model=schemas.UserCreateResponse)
def create_user(user: schemas.UserCreate, db: Session = db_session):
    db_user = crud.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    user = crud.create_user(db=db, user=user)
    claim_set = jwt_claims(user)
    return schemas.UserCreateResponse(
        user=user,
        x_api_token=jwt_encode(claim_set)
    )


@authentication_router.get("/users/", response_model=List[schemas.User])
def read_users(skip: int = 0, limit: int = 100, db: Session = db_session):
    users = crud.get_users(db, skip=skip, limit=limit)
    return users


@authentication_router.get("/users/{user_id}", response_model=schemas.User)
def read_user(user_id: int, db: Session = db_session):
    db_user = crud.get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user


@authentication_router.delete("/users/{user_id}", response_model=schemas.UserDeactivateResponse)
def deactivate_user(user_id: int, db: Session = db_session):
    db_user = crud.get_active_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")

    # activeなユーザーが最低1人は必要なので、指定されたユーザー以外で最小IDのactiveユーザーを取得してチェック
    min_user = crud.get_active_user_with_min_id_excluding(db, exclude_user_id=user_id)
    if not min_user:
        raise HTTPException(status_code=400, detail="Cannot deactivate the only active user")

    if not crud.deactivate_user(db, user_id=user_id, transfer_user_id=min_user.id):
        raise HTTPException(status_code=500, detail="Failed to deactivate user")
    return schemas.UserDeactivateResponse(detail="User deactivated successfully")


@authentication_router.post("/users/{user_id}/items/", response_model=schemas.Item)
def create_item_for_user(
    user_id: int, item: schemas.ItemCreate, db: Session = db_session
):
    return crud.create_user_item(db=db, item=item, user_id=user_id)


@authentication_router.get("/items/", response_model=List[schemas.Item])
def read_items(skip: int = 0, limit: int = 100, db: Session = db_session):
    items = crud.get_items(db, skip=skip, limit=limit)
    return items


@authentication_router.get("/me/items/", response_model=List[schemas.Item])
def read_items_for_authenticated_user(request: Request, skip: int = 0, limit: int = 100, db: Session = db_session):
    items = crud.get_user_items(db, user_id=request.user.id, skip=skip, limit=limit)
    return items


app.include_router(public_router)
app.include_router(authentication_router)
