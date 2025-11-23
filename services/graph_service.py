# services/graph_service.py

import networkx as nx
from sqlalchemy.orm import Session
from models.connection import Connection

COST_PER_KM = 5.0
STOP_FEE = 30.0  # opcional


def build_graph(db: Session) -> nx.Graph:
    G = nx.Graph()

    connections = db.query(Connection).all()
    for c in connections:
        G.add_edge(
            c.airport_a_id,
            c.airport_b_id,
            distance=c.distance,
            cost=float(c.cost),
        )
    return G


def calculate_shortest_path(
    G: nx.Graph,
    origin_id: int,
    destiny_id: int,
    criteria: str,
):
    if criteria == "distance":
        weight_attr = "distance"
    else:
        weight_attr = "cost"

    path = nx.shortest_path(
        G,
        source=origin_id,
        target=destiny_id,
        weight=weight_attr,
    )

    total_distance = 0.0
    total_cost = 0.0

    for i in range(len(path) - 1):
        data = G.get_edge_data(path[i], path[i + 1])
        total_distance += data["distance"]
        total_cost += data["cost"]

    total_stops = max(0, len(path) - 2)
    algorithm = "dijkstra_shortest_path"

    return path, total_distance, total_cost, total_stops, algorithm
