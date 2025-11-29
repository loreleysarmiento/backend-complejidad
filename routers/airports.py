from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from db.session import get_db
from core.security import get_current_user
from models.user import User
from models.airport import Airport
from schemas.airport import AirportRead

router = APIRouter(
    prefix="/airports",
    tags=["airports"],
    dependencies=[Depends(get_current_user)],
)


@router.get("/", response_model=list[AirportRead])
def list_airports(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Devuelve la lista de aeropuertos 
    """
    return (
        db.query(Airport)
        .order_by(Airport.id)
        .offset(skip)
        .limit(limit)
        .all()
    )


@router.get("/{airport_id}", response_model=AirportRead)
def get_airport_by_id(
    airport_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Devuelve un aeropuerto por ID 
    """
    airport = db.query(Airport).filter(Airport.id == airport_id).first()
    if not airport:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Airport not found",
        )
    return airport
