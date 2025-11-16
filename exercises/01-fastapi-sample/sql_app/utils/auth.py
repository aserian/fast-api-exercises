from typing import Any,Optional
from starlette import authentication

from fastapi import HTTPException, Request, security, status
from fastapi.security.utils import get_authorization_scheme_param

from .. import schemas


class AuthenticatedUser(authentication.SimpleUser):
    def __init__(self, user_id: int) -> None:
	    self.id = user_id


class UnauthenticatedUser(authentication.UnauthenticatedUser):
	pass
