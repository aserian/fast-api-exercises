# memo: 全体的にfactory botを使ってテストデータを生成したいが、今回は演習のため直接SQLを実行してテストデータを作成する
import pytest

from ..dependencies.auth_dependency import verify_active_user
from ..main import app

def test_create_user(test_db, client):
    response = client.post(
        "/users/",
        json={"email": "deadpool@example.com", "password": "chimichangas4life"},
    )
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["user"]["email"] == "deadpool@example.com"
    assert "id" in data["user"]
    assert "x_api_token" in data
    user_id = data["user"]["id"]

    response = client.get(f"/users/{user_id}")
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["email"] == "deadpool@example.com"
    assert data["id"] == user_id


# 認証が必要なAPIでトークンがない場合のテスト
def test_auth_endpoints_missing_token(test_db, client):
    app.dependency_overrides.pop(verify_active_user, None)
    endpoints = [
        {"method": "get", "path": "/users/"},
        {"method": "get", "path": "/users/1"},
        {"method": "post", "path": "/users/1/items/", "json": {"title": "test", "description": "test"}},
        {"method": "get", "path": "/items/"},
        {"method": "get", "path": "/me/items/"}
    ]

    # 各エンドポイントの認証テスト
    for endpoint_data in endpoints:
        method = endpoint_data["method"]
        endpoint = endpoint_data["path"]
        json_data = endpoint_data.get("json")

        client_method = getattr(client, method)
        if json_data:
            response = client_method(endpoint, json=json_data)
        else:
            response = client_method(endpoint)

        assert response.status_code == 403
        assert response.json()["detail"] == "Not authenticated"


# 認証が必要なAPIでトークンが無効な場合のテスト
def test_auth_endpoints_without_token(test_db, client):
    app.dependency_overrides.pop(verify_active_user, None)
    endpoints = [
        {"method": "get", "path": "/users/"},
        {"method": "get", "path": "/users/1"},
        {"method": "post", "path": "/users/1/items/", "json": {"title": "test", "description": "test"}},
        {"method": "get", "path": "/items/"},
        {"method": "get", "path": "/me/items/"}
    ]


    # 無効なトークンを設定した場合は401が返ることを確認
    headers = {"X-API-TOKEN": "invalid_token"}
    for endpoint_data in endpoints:
        method = endpoint_data["method"]
        endpoint = endpoint_data["path"]
        json_data = endpoint_data.get("json")
        client_method = getattr(client, method)
        if json_data:
            response = client_method(endpoint, headers=headers, json=json_data)
        else:
            response = client_method(endpoint, headers=headers)

        assert response.status_code == 401
        assert response.json()["detail"] == "Not authenticated"


# 認証が必要なAPIでトークンが有効な場合のテスト
def test_auth_endpoints_with_valid_token(test_db, client):
    app.dependency_overrides.pop(verify_active_user, None)
    endpoints = [
        {"method": "get", "path": "/users/"},
        {"method": "get", "path": "/users/1"},
        {"method": "post", "path": "/users/1/items/", "json": {"title": "test", "description": "test"}},
        {"method": "get", "path": "/items/"},
        {"method": "get", "path": "/me/items/"}
    ]

    # 最低一人は、アクティブユーザーがいる想定なので事前に用意
    test_db.execute(
        "INSERT INTO users (id, email, hashed_password, is_active) VALUES "
        "(1, 'deadpool@example.com', 'hashed_chimichangas4life', True)"
    )
    test_db.commit()

    # ユーザ作成をしてapiトークンを取得
    response = client.post(
        "/users/",
        json={"email": "deadpool5@example.com", "password": "chimichangas4life"},
    )
    data = response.json()
    x_api_token = data["x_api_token"]

    headers = {"X-API-TOKEN": x_api_token}
    for endpoint_data in endpoints:
        method = endpoint_data["method"]
        endpoint = endpoint_data["path"]
        json_data = endpoint_data.get("json")

        client_method = getattr(client, method)
        if json_data:
            response = client_method(endpoint, headers=headers, json=json_data)
        else:
            response = client_method(endpoint, headers=headers)

        assert response.status_code == 200


# 認証が不要なAPIで、トークンがない場合のテスト
def test_no_auth_endpoints_without_token(test_db, client):
    app.dependency_overrides.pop(verify_active_user, None)
    endpoints = [
        {"method": "get", "path": "/health-check"},
        {"method": "post", "path": "/users/", "json": {"email": "test@example.com", "password": "testpassword"}},
    ]

    for endpoint_data in endpoints:
        method = endpoint_data["method"]
        endpoint = endpoint_data["path"]
        json_data = endpoint_data.get("json")

        client_method = getattr(client, method)
        if json_data:
            response = client_method(endpoint, json=json_data)
        else:
            response = client_method(endpoint)
        assert response.status_code == 200


# 認証が不要なAPIで、無効なトークンがある場合のテスト
def test_no_auth_endpoints_with_token(test_db, client):
    app.dependency_overrides.pop(verify_active_user, None)
    endpoints = [
        {"method": "get", "path": "/health-check"},
        {"method": "post", "path": "/users/", "json": {"email": "test@example.com", "password": "testpassword"}},
    ]

    headers = {"X-API-TOKEN": "invalid_token"}
    for endpoint_data in endpoints:
        method = endpoint_data["method"]
        endpoint = endpoint_data["path"]
        json_data = endpoint_data.get("json")

        client_method = getattr(client, method)
        if json_data:
            response = client_method(endpoint, json=json_data, headers=headers)
        else:
            response = client_method(endpoint, headers=headers)
        assert response.status_code == 200


# 認証が不要なAPIで、有効なトークンがある場合のテスト
def test_no_auth_endpoints_with_valid_token(test_db, client):
    app.dependency_overrides.pop(verify_active_user, None)
    endpoints = [
        {"method": "get", "path": "/health-check"},
        {"method": "post", "path": "/users/", "json": {"email": "test@example.com", "password": "testpassword"}},
    ]

    # ユーザ作成をしてapiトークンを取得
    response = client.post(
        "/users/",
        json={"email": "deadpool2@example.com", "password": "chimichangas4life"},
    )
    data = response.json()
    x_api_token = data["x_api_token"]

    headers = {"X-API-TOKEN": x_api_token}
    for endpoint_data in endpoints:
        method = endpoint_data["method"]
        endpoint = endpoint_data["path"]
        json_data = endpoint_data.get("json")

        client_method = getattr(client, method)
        if json_data:
            response = client_method(endpoint, json=json_data, headers=headers)
        else:
            response = client_method(endpoint, headers=headers)
        assert response.status_code == 200


# 認証されたユーザーのアイテム取得APIのテスト
def test_read_items_for_authenticated_user(test_db, client):
    app.dependency_overrides.pop(verify_active_user, None)
    # ユーザ作成をしてapiトークンを取得
    response = client.post(
        "/users/",
        json={"email": "deadpool@example.com", "password": "chimichangas4life"},
    )
    data = response.json()
    x_api_token = data["x_api_token"]

    # 事前にアイテムを作成
    test_db.execute(
        "INSERT INTO items (id, title, description, owner_id) VALUES"
        "(1, 'Item 1', 'Description 1', 1),"
        "(2, 'Item 2', 'Description 2', 1),"
        "(3, 'Item 3', 'Description 3', 1),"
        "(4, 'Item 4', 'Description 4', 1)"
    )
    test_db.commit()

    # 認証されたユーザーのアイテムを取得して全て返ることを確認
    response = client.get("/me/items/", headers={"x-api-token": x_api_token})
    assert response.status_code == 200, response.text
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 4

    # skip, limit パラメータの動作確認
    response = client.get("/me/items/?skip=1&limit=2", headers={"x-api-token": x_api_token})
    assert response.status_code == 200, response.text
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 2
    assert data[0]["title"] == "Item 2"
    assert data[1]["title"] == "Item 3"
