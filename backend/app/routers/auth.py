from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Account
from app.schemas import SignupRequest, LoginRequest, TokenResponse
from app.security import hash_password, verify_password, create_access_token
from app.rate_limit import is_locked_out, record_failed_attempt, clear_attempts

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/signup", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
def signup(payload: SignupRequest, db: Session = Depends(get_db)):
    existing = db.query(Account).filter(Account.email == payload.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="An account with that email already exists.")

    account = Account(
        shop_name=payload.shop_name,
        email=payload.email,
        password_hash=hash_password(payload.password),
    )
    db.add(account)
    db.commit()
    db.refresh(account)

    token = create_access_token(account.id)
    return TokenResponse(access_token=token, shop_name=account.shop_name, currency=account.currency)


@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    if is_locked_out(payload.email):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many failed login attempts. Please wait 15 minutes and try again.",
        )

    account = db.query(Account).filter(Account.email == payload.email).first()
    # Deliberately identical error for "no such email" and "wrong password" -
    # telling an attacker which one was wrong makes it easier to enumerate
    # valid emails on the system.
    invalid = HTTPException(status_code=401, detail="Incorrect email or password.")
    if not account or not verify_password(payload.password, account.password_hash):
        record_failed_attempt(payload.email)
        raise invalid

    clear_attempts(payload.email)
    token = create_access_token(account.id)
    return TokenResponse(access_token=token, shop_name=account.shop_name, currency=account.currency)
