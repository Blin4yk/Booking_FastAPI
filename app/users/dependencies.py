from datetime import datetime, timezone
from fastapi import Depends, Request
from jose import jwt, JWTError
from app.config import settings
from app.exceptions import IncorrectTokenFormatException, TokenAbsentException, TokenExpiredException, UserIsNotPresent
from app.users.models import Users
from app.users.service import UsersService


def get_token(request: Request):
    token = request.cookies.get("booking_access_token")
    if not token:
        raise TokenAbsentException
    return token

async def get_current_user(token: str = Depends(get_token)):
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, settings.ALGORITHM 
        )
    except JWTError:
        raise IncorrectTokenFormatException
    expire: str = payload.get("exp")
    if (not expire) or (int(expire) < datetime.now(timezone.utc).timestamp()):
        raise TokenExpiredException
    user_id: str = payload.get("sub")
    if not user_id:
        raise UserIsNotPresent
    user = await UsersService.find_by_id(int(user_id))

    if not user:
        raise UserIsNotPresent
    
    return user


async def get_current_admin_user(current_user: Users = Depends(get_current_user)):
    # if current_user.role != "admin": грубо говоря это уже разделение на роли
    #     raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED) 
    return current_user

