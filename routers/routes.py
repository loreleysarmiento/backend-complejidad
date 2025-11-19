# routers/routes.py

import networkx as nx
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from db.session import get_db
from core.security import get_current_user
from models.user import User
from models.route import RouteCalculated, RouteDetail
from schemas.route import RouteCalculateRequest, RouteHistoryItem
from services.graph_service import build_graph, calculate_shortest_path  

router = APIRouter(
    prefix="/routes",
    tags=["routes"],
    dependencies=[Depends(get_current_user)],
)


@router.post("/calculate", response_model=RouteHistoryItem)
def calculate_route_endpoint(
    body: RouteCalculateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # 1) Construir el grafo desde la BD
    G = build_graph(db)

    # 2) Calcular ruta con tu función
    try:
        (
            path_nodes,
            total_distance,
            total_cost,
            total_stops,
            algorithm,
        ) = calculate_shortest_path(
            G,
            origin_id=body.origin_id,
            destiny_id=body.destiny_id,
            criteria=body.criteria.value,
        )
    except nx.NetworkXNoPath:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No se encontró ruta entre los aeropuertos indicados",
        )

    # 3) Guardar cabecera en routes_calculated
    route = RouteCalculated(
        user_id=current_user.id,
        origin_id=body.origin_id,
        destiny_id=body.destiny_id,
        total_distance=total_distance,
        total_cost=total_cost,
        criteria=body.criteria.value,
        total_stops=total_stops,
        algorithm=algorithm,
    )
    db.add(route)
    db.flush()  # consigue route.id sin hacer commit todavía

    # 4) Guardar detalle de la ruta
    for order, airport_id in enumerate(path_nodes):
        detail = RouteDetail(
            route_id=route.id,
            route_order=order,
            airport_id=airport_id,
        )
        db.add(detail)

    db.commit()
    db.refresh(route)
    return route


@router.get("/history", response_model=list[RouteHistoryItem])
def get_history(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    routes = (
        db.query(RouteCalculated)
        .filter(RouteCalculated.user_id == current_user.id)
        .order_by(RouteCalculated.query_date.desc())
        .all()
    )
    return routes


@router.delete("/history/{route_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_history_item(
    route_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    route = (
        db.query(RouteCalculated)
        .filter(
            RouteCalculated.id == route_id,
            RouteCalculated.user_id == current_user.id,
        )
        .first()
    )
    if not route:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ruta no encontrada en el historial del usuario",
        )

    db.query(RouteDetail).filter(RouteDetail.route_id == route.id).delete()
    db.delete(route)
    db.commit()
    return
