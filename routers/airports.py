from fastapi import APIRouter, Depends
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
    Devuelve la lista de aeropuertos (solo visibles si estás logueado).
    """
    return db.query(Airport).order_by(Airport.airport_id).offset(skip).limit(limit).all()
