from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError
from sqlalchemy.orm import Session

from .database import get_db
from .models import Inspector, RoleEnum
from .security import decode_access_token

oauth2_scheme = OAuth2PasswordBearer(tokenUrl='/auth/login')

def get_current_user(db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)) -> Inspector:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail='Не удалось подтвердить учетные данные',
        headers={'WWW-Authenticate': 'Bearer'},
    )
    try:
        payload = decode_access_token(token)
        user_id = int(payload.get('sub'))
    except (JWTError, TypeError, ValueError):
        raise credentials_exception

    user = db.get(Inspector, user_id)
    if not user:
        raise credentials_exception
    return user

def require_roles(*roles: RoleEnum):
    def checker(current_user: Inspector = Depends(get_current_user)) -> Inspector:
        if current_user.role not in roles:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Недостаточно прав доступа')
        return current_user

    return checker
