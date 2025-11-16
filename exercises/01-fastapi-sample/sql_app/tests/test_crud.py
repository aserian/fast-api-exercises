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

# ユーザーのアイテム取得のテスト
def test_get_user_items_success(test_db):
    user_id = 1
    test_db.execute(
        "INSERT INTO users (id, email, hashed_password, is_active) VALUES "
        f"({user_id}, 'user@example.com', 'hashed_password', True)"
    )
    test_db.execute(
        "INSERT INTO items (id, title, description, owner_id) VALUES "
        "(1, 'Item 1', 'Description 1', 1), "
        "(2, 'Item 2', 'Description 2', 1), "
        "(3, 'Item 3', 'Description 3', 1)"
    )
    test_db.commit()

    items = crud.get_user_items(test_db, user_id=user_id)
    assert len(items) == 3
    assert items[0].title == 'Item 1'
    assert items[1].title == 'Item 2'
    assert items[2].title == 'Item 3'
    assert all(item.owner_id == user_id for item in items)

# ユーザーのアイテム取得でskipとlimitを使用するテスト
def test_get_user_items_with_skip_limit(test_db):
    user_id = 1
    test_db.execute(
        "INSERT INTO users (id, email, hashed_password, is_active) VALUES "
        f"({user_id}, 'user@example.com', 'hashed_password', True)"
    )
    test_db.execute(
        "INSERT INTO items (id, title, description, owner_id) VALUES "
        "(1, 'Item 1', 'Description 1', 1), "
        "(2, 'Item 2', 'Description 2', 1), "
        "(3, 'Item 3', 'Description 3', 1), "
        "(4, 'Item 4', 'Description 4', 1), "
        "(5, 'Item 5', 'Description 5', 1)"
    )
    test_db.commit()

    items = crud.get_user_items(test_db, user_id=user_id, skip=1, limit=2)
    assert len(items) == 2
    assert items[0].title == 'Item 2'
    assert items[1].title == 'Item 3'

# ユーザーのアイテム取得でアイテムが存在しない場合のテスト
def test_get_user_items_no_items(test_db):
    user_id = 1
    test_db.execute(
        "INSERT INTO users (id, email, hashed_password, is_active) VALUES "
        f"({user_id}, 'user@example.com', 'hashed_password', True)"
    )
    test_db.commit()

    items = crud.get_user_items(test_db, user_id=user_id)
    assert len(items) == 0
    assert items == []

# ユーザーのアイテム取得で他のユーザーのアイテムが混入しないことを確認するテスト
def test_get_user_items_different_owners(test_db):
    test_db.execute(
        "INSERT INTO users (id, email, hashed_password, is_active) VALUES "
        "(1, 'user1@example.com', 'hashed_password', True), "
        "(2, 'user2@example.com', 'hashed_password', True)"
    )
    test_db.execute(
        "INSERT INTO items (id, title, description, owner_id) VALUES "
        "(1, 'Item 1', 'Description 1', 1), "
        "(2, 'Item 2', 'Description 2', 2), "
        "(3, 'Item 3', 'Description 3', 1)"
    )
    test_db.commit()

    items = crud.get_user_items(test_db, user_id=1)
    assert len(items) == 2
    assert all(item.owner_id == 1 for item in items)
    assert items[0].title == 'Item 1'
    assert items[1].title == 'Item 3'
