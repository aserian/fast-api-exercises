from typing import Optional, Tuple

from fastapi import Request
from fastapi.security.utils import get_authorization_scheme_param

from jose.jwt import ExpiredSignatureError, JWTError

from starlette.authentication import AuthCredentials, BaseUser
from starlette.middleware import authentication

from ..utils import AuthenticatedUser, UnauthenticatedUser, jwt_decode


class AuthenticationBackend(authentication.AuthenticationBackend):
    async def authenticate(self, request: Request) -> Optional[Tuple[AuthCredentials, BaseUser]]:
        # X-API-TOKENヘッダーからトークンを取得
        auth_header = request.headers.get("X-API-TOKEN")
        if not auth_header:
            return (AuthCredentials(["unauthenticated"]), UnauthenticatedUser())

        try:
            payload = jwt_decode(auth_header)
        except ExpiredSignatureError:
            return (AuthCredentials(["unauthenticated"]), UnauthenticatedUser())
        except JWTError:
            return (AuthCredentials(["unauthenticated"]), UnauthenticatedUser())
        except Exception:
            return (AuthCredentials(["unauthenticated"]), UnauthenticatedUser())

        user_id: int = payload.get("user_id")
        if user_id is None:
            return (AuthCredentials(["unauthenticated"]), UnauthenticatedUser())

        return (AuthCredentials(["authenticated"]), AuthenticatedUser(user_id=user_id))
