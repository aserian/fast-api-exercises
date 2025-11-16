from sqlalchemy.orm import Session

from . import models, schemas


def get_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()


def get_active_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id, models.User.is_active == True).first()


def get_active_user_with_min_id_excluding(db: Session, exclude_user_id: int):
    return db.query(models.User).filter(models.User.is_active == True, models.User.id != exclude_user_id).order_by(models.User.id.asc()).first()


def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()


def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.User).offset(skip).limit(limit).all()


def create_user(db: Session, user: schemas.UserCreate):
    fake_hashed_password = user.password + "notreallyhashed"
    db_user = models.User(email=user.email, hashed_password=fake_hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def deactivate_user(db: Session, user_id: int, transfer_user_id: int) -> bool:
    try:
        # タスクの所有者を移管
        # memo: 数が多い場合はバッチ処理にするなど検討が必要だが、今回は演習のため単純化
        db.query(models.Item).filter(models.Item.owner_id == user_id).update({"owner_id": transfer_user_id})
        # ユーザーを非アクティブ化
        db.query(models.User).filter(models.User.id == user_id).update({"is_active": False})
        db.commit()
        return True
    except Exception:
        db.rollback()
        return False


def get_items(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Item).offset(skip).limit(limit).all()


def get_user_items(db: Session, user_id: int, skip: int = 0, limit: int = 100):
    return db.query(models.Item).filter(models.Item.owner_id == user_id).offset(skip).limit(limit).all()


def create_user_item(db: Session, item: schemas.ItemCreate, user_id: int):
    db_item = models.Item(**item.dict(), owner_id=user_id)
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item
