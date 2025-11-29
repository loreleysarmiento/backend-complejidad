# routers/routes.py

import networkx as nx
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from db.session import get_db
from core.security import get_current_user
from models.user import User
from models.route import RouteCalculated, RouteDetail, RouteCriteriaEnum
from schemas.route import RouteCalculateRequest, RouteHistoryItem
from services.graph_service import build_graph_for_route, calculate_shortest_path  

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
    try:
        G = build_graph_for_route(
            db,
            origin_id=body.origin_id,
            destiny_id=body.destiny_id,
            max_nodes=300,
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )

    try:
        path_nodes, total_distance, total_cost = calculate_shortest_path(
            G,
            origin_id=body.origin_id,
            destiny_id=body.destiny_id,
            criteria=body.criteria.value,
            max_stops=body.max_stops,
            max_concurrency=body.max_concurrency,
        )
    except nx.NetworkXNoPath as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
    except nx.NodeNotFound:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Alguno de los aeropuertos indicados no existe en el grafo.",
        )

    total_stops = max(len(path_nodes) - 2, 0)

    avg_concurrency = None
    if path_nodes:
        sum_conc = 0
        for node_id in path_nodes:
            node_data = G.nodes[node_id]
            conc = int(node_data.get("concurrency", 0) or 0)
            sum_conc += conc
        avg_concurrency = sum_conc / len(path_nodes)

    if body.criteria == RouteCriteriaEnum.DISTANCE:
        algorithm = "dijkstra"
    elif body.criteria == RouteCriteriaEnum.COST:
        algorithm = "bellman_ford"
    else:
        algorithm = "dijkstra"

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
    db.flush()

    for order, airport_id in enumerate(path_nodes):
        detail = RouteDetail(
            route_id=route.id,
            route_order=order,
            airport_id=airport_id,
        )
        db.add(detail)

    db.commit()
    db.refresh(route)

    route.max_stops = body.max_stops
    route.avg_concurrency = avg_concurrency

    return route


@router.get("/history", response_model=list[RouteHistoryItem])
def get_history(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Devuelve el historial de rutas calculadas por el usuario actual,
    ordenadas de la más reciente a la más antigua.
    """
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
