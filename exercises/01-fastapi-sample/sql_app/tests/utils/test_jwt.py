from ...utils.jwt import jwt_claims, jwt_encode, jwt_decode
from ... import models

# jwt_claimsのテスト
def test_jwt_claims_user():
    user = models.User(id=1, email="test@example.com")
    assert jwt_claims(user) == {"user_id": 1}
