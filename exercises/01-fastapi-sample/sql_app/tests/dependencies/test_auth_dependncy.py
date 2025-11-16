import pytest

from unittest.mock import Mock
from fastapi import HTTPException, Request

from ...dependencies.auth_dependency import verify_active_user
from ...utils.auth import AuthenticatedUser, UnauthenticatedUser
from ... import crud


# 有効な認証情報がある場合のテスト
def test_verify_active_user_success(test_db):
    user_id = 1
    test_db.execute(
        "INSERT INTO users (id, email, hashed_password, is_active) VALUES "
        f"({user_id}, 'test@example.com', 'hashed_testpassword', True)"
    )
    test_db.commit()

    mock_request = Mock(spec=Request)
    mock_request.user = AuthenticatedUser(user_id=user_id)

    user = verify_active_user(mock_request, test_db, "X-API-TOKEN")

    assert user.id == user_id
    assert user.is_active is True

# 認証されていない場合のテスト
def test_verify_active_user_not_authenticated(test_db):
    mock_request = Mock(spec=Request)
    mock_request.user = UnauthenticatedUser()

    with pytest.raises(HTTPException) as exc_info:
        verify_active_user(mock_request, test_db, "X-API-TOKEN")

    assert exc_info.value.status_code == 401

# 非アクティブなユーザーの場合のテスト
def test_verify_active_user_inactive_user(test_db, client):
    user_id = 1
    test_db.execute(
        "INSERT INTO users (id, email, hashed_password, is_active) VALUES "
        f"({user_id}, 'test@example.com', 'hashed_testpassword', False)"
    )
    test_db.commit()

    # 認証済みだが非アクティブなユーザーのRequestオブジェクトをモック
    mock_request = Mock(spec=Request)
    mock_request.user = AuthenticatedUser(user_id=user_id)

    with pytest.raises(HTTPException) as exc_info:
        verify_active_user(mock_request, test_db, "dummy_api_key")

    assert exc_info.value.status_code == 401
    assert exc_info.value.detail == "Not authenticated"

# 存在しないユーザーの場合のテスト
def test_verify_active_user_nonexistent_user(test_db):
    user_id = 99999
    mock_request = Mock(spec=Request)
    mock_request.user = AuthenticatedUser(user_id=user_id)

    with pytest.raises(HTTPException) as exc_info:
        verify_active_user(mock_request, test_db, "dummy_api_key")

    assert exc_info.value.status_code == 401
    assert exc_info.value.detail == "Not authenticated"
