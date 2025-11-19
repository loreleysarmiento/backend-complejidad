# app/services/route_service.py
from sqlalchemy.orm import Session
from decimal import Decimal, ROUND_HALF_UP
from models.route import RouteCalculated, RouteDetail, RouteCriteriaEnum
from services.graph_service import build_graph, calculate_shortest_path
from models.user import User


def round_money(value: float) -> Decimal:
    return Decimal(value).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def create_route_for_user(
    db: Session,
    user: User,
    origin_id: int,
    destiny_id: int,
    criteria: RouteCriteriaEnum,
) -> RouteCalculated:
    G = build_graph(db)
    path, total_distance, total_cost = calculate_shortest_path(
        G, origin_id, destiny_id, criteria.value
    )

    route = RouteCalculated(
        user_id=user.id,
        origin_id=origin_id,
        destiny_id=destiny_id,
        total_distance=total_distance,
        total_cost=round_money(total_cost),
        criteria=criteria.value,
        total_stops=max(len(path) - 2, 0),
        algorithm="dijkstra",
    )
    db.add(route)
    db.flush()  # para tener route.id

    for order, airport_id in enumerate(path):
        detail = RouteDetail(
            route_id=route.id,
            route_order=order,
            airport_id=airport_id,
        )
        db.add(detail)

    db.commit()
    db.refresh(route)
    return route
