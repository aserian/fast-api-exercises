from datetime import datetime, timedelta
from typing import Any, Dict
from jose import jwt
from .. import models

ALGORITHM = "HS256"
# 秘密鍵（今回は演習のため、テスト用の固定値を使用）
SECRET_KEY = "testsecretkeyforapi"


# memo：セキュリティリスクはあるが、今回はユーザ作成時のみ発行する仕様のためリフレッシュトークンは無しで実装
def jwt_claims(user: models.User) -> Dict[str, Any]:
    claim_set = {"user_id": user.id}

    return claim_set


def jwt_encode(claim_set: Dict[str, Any]) -> str:
    return jwt.encode(claim_set, SECRET_KEY, algorithm=ALGORITHM)


def jwt_decode(token: str) -> Dict[str, Any]:
    return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
