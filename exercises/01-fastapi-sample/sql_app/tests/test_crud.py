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


# アクティブユーザーの中で指定したユーザーIDを除外して最小IDのユーザーを取得するテスト
def test_get_active_user_with_min_id_excluding_success(test_db):
    exclude_user_id = 2
    test_db.execute(
        "INSERT INTO users (id, email, hashed_password, is_active) VALUES "
        "(1, 'user1@example.com', 'hashed_password', True), "
        f"({exclude_user_id}, 'user2@example.com', 'hashed_password', True), "
        "(3, 'user3@example.com', 'hashed_password', True)"
    )
    test_db.commit()

    user = crud.get_active_user_with_min_id_excluding(test_db, exclude_user_id=exclude_user_id)
    assert user is not None
    assert user.id == 1


# アクティブユーザーの中で指定したユーザーIDを除外して最小IDのユーザーを取得するテスト（最初のユーザーを除外）
def test_get_active_user_with_min_id_excluding_first_user(test_db):
    exclude_user_id = 1
    test_db.execute(
        "INSERT INTO users (id, email, hashed_password, is_active) VALUES "
        f"({exclude_user_id}, 'user1@example.com', 'hashed_password', True), "
        "(2, 'user2@example.com', 'hashed_password', True), "
        "(3, 'user3@example.com', 'hashed_password', True)"
    )
    test_db.commit()

    user = crud.get_active_user_with_min_id_excluding(test_db, exclude_user_id=exclude_user_id)
    assert user is not None
    assert user.id == 2


# アクティブユーザーの中で指定したユーザーIDを除外して最小IDのユーザーを取得するテスト（除外したユーザー以外が非アクティブ）
def test_get_active_user_with_min_id_excluding_with_inactive(test_db):
    exclude_user_id = 2
    test_db.execute(
        "INSERT INTO users (id, email, hashed_password, is_active) VALUES "
        "(1, 'user1@example.com', 'hashed_password', False), "
        f"({exclude_user_id}, 'user2@example.com', 'hashed_password', True), "
        "(3, 'user3@example.com', 'hashed_password', True)"
    )
    test_db.commit()

    user = crud.get_active_user_with_min_id_excluding(test_db, exclude_user_id=exclude_user_id)
    assert user is not None
    assert user.id == 3


# アクティブユーザーの中で指定したユーザーIDを除外して最小IDのユーザーを取得するテスト（他にアクティブユーザーがいない場合）
def test_get_active_user_with_min_id_excluding_no_other_users(test_db):
    exclude_user_id = 1
    test_db.execute(
        "INSERT INTO users (id, email, hashed_password, is_active) VALUES "
        f"({exclude_user_id}, 'user1@example.com', 'hashed_password', True)"
    )
    test_db.commit()

    user = crud.get_active_user_with_min_id_excluding(test_db, exclude_user_id=exclude_user_id)
    assert user is None


# ユーザーの非アクティブ化のテスト
def test_deactivate_user_success(test_db):
    deactivate_user_id = 1
    transfer_user_id = 2
    test_db.execute(
        "INSERT INTO users (id, email, hashed_password, is_active) VALUES "
        f"({deactivate_user_id}, 'user1@example.com', 'hashed_password', True), "
        f"({transfer_user_id}, 'user2@example.com', 'hashed_password', True)"
    )
    test_db.execute(
        "INSERT INTO items (id, title, description, owner_id) VALUES "
        f"(1, 'Item 1', 'Description 1', {deactivate_user_id}), "
        f"(2, 'Item 2', 'Description 2', {deactivate_user_id})"
    )
    test_db.commit()

    result = crud.deactivate_user(test_db, user_id=deactivate_user_id, transfer_user_id=transfer_user_id)
    assert result is True

    cursor = test_db.execute(f"SELECT is_active FROM users WHERE id = {deactivate_user_id}")
    user_status = cursor.fetchone()
    assert user_status[0] == 0  # False

    cursor = test_db.execute("SELECT owner_id FROM items")
    items_owners = cursor.fetchall()
    assert all(owner[0] == 2 for owner in items_owners)


# ユーザーの非アクティブ化でアイテムがない場合のテスト
def test_deactivate_user_no_items(test_db):
    deactivate_user_id = 1
    transfer_user_id = 2
    test_db.execute(
        "INSERT INTO users (id, email, hashed_password, is_active) VALUES "
        f"({deactivate_user_id}, 'user1@example.com', 'hashed_password', True), "
        f"({transfer_user_id}, 'user2@example.com', 'hashed_password', True)"
    )
    test_db.commit()

    result = crud.deactivate_user(test_db, user_id=deactivate_user_id, transfer_user_id=transfer_user_id)
    assert result is True

    cursor = test_db.execute(f"SELECT is_active FROM users WHERE id = {deactivate_user_id}")
    user_status = cursor.fetchone()
    assert user_status[0] == 0
