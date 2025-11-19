from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from db.session import get_db
from core.security import get_current_user, get_password_hash
from models.user import User
from schemas.user import UserRead, UserUpdate

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/logout")
def logout(current_user: User = Depends(get_current_user)):
    """
    Logout 'lógico'. Con JWT stateless en realidad el front solo
    tiene que borrar el token. Este endpoint existe para la integración.
    """
    return {"message": "Logged out successfully"}

@router.get("/profile", response_model=UserRead)
def read_profile(current_user: User = Depends(get_current_user)):
    return current_user

@router.put("/profile", response_model=UserRead)
def update_profile(
    user_update: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if user_update.username is not None:
        current_user.username = user_update.username

    if user_update.password is not None:
        current_user.hashed_password = get_password_hash(user_update.password)

    db.add(current_user)
    db.commit()
    db.refresh(current_user)
    return current_user
