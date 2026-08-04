from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.database import get_db
from app.security import decode_access_token
from app.models import Account

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def get_current_account(
    token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)
) -> Account:
    """
    Every protected endpoint depends on this. It's the single choke point
    that turns 'a request came in with this token' into 'this specific
    shop's data'. Every router function below uses account.id to filter
    every query - that filter is what keeps shops isolated from each other.
    """
    credentials_error = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    account_id = decode_access_token(token)
    if account_id is None:
        raise credentials_error

    account = db.query(Account).filter(Account.id == account_id).first()
    if account is None:
        raise credentials_error
    return account
