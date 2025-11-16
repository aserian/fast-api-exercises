import pytest
from .. import crud

# アクティブユーザー取得のテスト
def test_get_active_user_success(test_db):
    user_id = 1
    test_db.execute(
        "INSERT INTO users (id, email, hashed_password, is_active) VALUES "
        f"({user_id}, 'active@example.com', 'hashed_password', True)"
    )
    test_db.commit()

    user = crud.get_active_user(test_db, user_id=user_id)
    assert user is not None
    assert user.id == user_id
    assert user.email == 'active@example.com'
    assert user.is_active is True

# アクティブでないユーザーを取得しようとした場合のテスト
def test_get_active_user_inactive_user(test_db):
    user_id = 1
    test_db.execute(
        "INSERT INTO users (id, email, hashed_password, is_active) VALUES "
        f"({user_id}, 'inactive@example.com', 'hashed_password', False)"
    )
    test_db.commit()

    user = crud.get_active_user(test_db, user_id=user_id)
    assert user is None

# 存在しないユーザーを取得しようとした場合のテスト
def test_get_active_user_nonexistent(test_db):
    nonexistent_user_id = 999
    user = crud.get_active_user(test_db, user_id=nonexistent_user_id)
    assert user is None
