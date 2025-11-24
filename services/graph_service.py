
import math
import random
import networkx as nx
from sqlalchemy.orm import Session

from models.airport import Airport
from models.connection import Connection

COST_PER_KM = 5.0


def haversine(lat1, lon1, lat2, lon2) -> float:
    """Distancia aproximada en km entre dos puntos (lat, lon)."""
    R = 6371.0
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dl = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c


def _classify_concurrency(degree: int) -> int:
    """
    - <=3  -> 3  (baja)
    - <=5  -> 5  (media)
    - >5   -> 7  (alta)
    """
    if degree <= 3:
        return 3
    elif degree <= 5:
        return 5
    else:
        return 7


def _congestion_factor_for_edge(deg_a: int, deg_b: int) -> float:
    """
    Factor de congestión en base a cuántas rutas pasan por los extremos.
    """
    degree_sum = deg_a + deg_b

    if degree_sum <= 6:
        return 1.0
    elif degree_sum <= 10:
        return 1.3
    else:
        return 1.6


def _ensure_connections_for_subset(
    db: Session,
    subset_ids: set[int],
) -> None:
  

    if len(subset_ids) < 2:
        return

    airports = (
        db.query(Airport)
        .filter(Airport.id.in_(subset_ids))
        .all()
    )
    airport_by_id = {a.id: a for a in airports}

    existing_conns = (
        db.query(Connection)
        .filter(
            Connection.airport_a_id.in_(subset_ids),
            Connection.airport_b_id.in_(subset_ids),
        )
        .all()
    )

    current_degree: dict[int, int] = {aid: 0 for aid in subset_ids}
    edge_set: set[frozenset[int]] = set()

    for c in existing_conns:
        a = c.airport_a_id
        b = c.airport_b_id
        if a in subset_ids:
            current_degree[a] += 1
        if b in subset_ids:
            current_degree[b] += 1
        edge_set.add(frozenset({a, b}))

    # Target aleatorio 3/5/7, pero nunca menor al grado actual y máximo 7
    target_degree: dict[int, int] = {}
    for aid in subset_ids:
        rnd = random.choice([3, 5, 7])
        target = max(current_degree[aid], rnd)
        target = min(target, 7)  # límite superior
        target_degree[aid] = target

    # Coords solo del subconjunto
    coords = [
        (a.id, a.lat, a.lon)
        for a in airports
    ]

    new_edges: list[tuple[int, int, float]] = []

    for id1, lat1, lon1 in coords:
        if current_degree[id1] >= target_degree[id1]:
            continue

        dists = []
        for id2, lat2, lon2 in coords:
            if id1 == id2:
                continue
            dist_km = haversine(lat1, lon1, lat2, lon2)
            dists.append((id2, dist_km))
        dists.sort(key=lambda x: x[1])

        for id2, dist in dists:
            if current_degree[id1] >= target_degree[id1]:
                break
            if current_degree[id2] >= target_degree[id2]:
                continue

            edge_key = frozenset({id1, id2})
            if edge_key in edge_set:
                continue

            edge_set.add(edge_key)
            new_edges.append((id1, id2, dist))
            current_degree[id1] += 1
            current_degree[id2] += 1

    for aid, deg in current_degree.items():
        airport = airport_by_id.get(aid)
        if not airport:
            continue
        airport.concurrency = _classify_concurrency(deg)

    for id1, id2, dist in new_edges:
        deg_a = current_degree[id1]
        deg_b = current_degree[id2]
        congestion_factor = _congestion_factor_for_edge(deg_a, deg_b)
        cost = dist * COST_PER_KM * congestion_factor

        conn = Connection(
            airport_a_id=id1,
            airport_b_id=id2,
            distance=dist,
            congestion_factor=congestion_factor,
            cost=cost,
        )
        db.add(conn)

    db.commit()


def build_graph_for_route(
    db: Session,
    origin_id: int,
    destiny_id: int,
    max_nodes: int = 300,
) -> nx.Graph:
  

    airports = db.query(Airport).all()
    if len(airports) < 2:
        raise ValueError("No hay suficientes aeropuertos en la base de datos.")

    airport_by_id = {a.id: a for a in airports}
    origin = airport_by_id.get(origin_id)
    destiny = airport_by_id.get(destiny_id)

    if origin is None or destiny is None:
        raise ValueError("Origen o destino no existen en la tabla Aeropuertos.")

    distances = []
    for a in airports:
        d = haversine(origin.lat, origin.lon, a.lat, a.lon)
        distances.append((a.id, d))

    distances.sort(key=lambda x: x[1])

    subset_ids: set[int] = {aid for aid, _ in distances[:max_nodes]}
    subset_ids.add(destiny_id)  # asegurar destino

    _ensure_connections_for_subset(db, subset_ids)

    G = nx.Graph()

    subset_airports = (
        db.query(Airport)
        .filter(Airport.id.in_(subset_ids))
        .all()
    )
    for a in subset_airports:
        G.add_node(
            a.id,
            name=a.name,
            city=a.city,
            country=a.country,
            lat=a.lat,
            lon=a.lon,
            concurrency=a.concurrency,
        )

    subset_connections = (
        db.query(Connection)
        .filter(
            Connection.airport_a_id.in_(subset_ids),
            Connection.airport_b_id.in_(subset_ids),
        )
        .all()
    )
    for c in subset_connections:
        G.add_edge(
            c.airport_a_id,
            c.airport_b_id,
            distance=float(c.distance),
            cost=float(c.cost),
            congestion_factor=float(c.congestion_factor),
        )

    return G


def calculate_shortest_path(
    G: nx.Graph,
    origin_id: int,
    destiny_id: int,
    criteria: str,
):
    """
    Calcula el camino más corto según criteria:
    - 'distance'  -> Dijkstra sobre atributo 'distance'
    - 'cost'      -> Bellman-Ford sobre atributo 'cost'
    Devuelve: path, total_distance, total_cost
    """

    if criteria == "distance":
       
        path = nx.dijkstra_path(
            G,
            source=origin_id,
            target=destiny_id,
            weight="distance",
        )
    elif criteria == "cost":
       
        path = nx.bellman_ford_path(
            G,
            source=origin_id,
            target=destiny_id,
            weight="cost",
        )
    else:
        
        path = nx.dijkstra_path(
            G,
            source=origin_id,
            target=destiny_id,
            weight="distance",
        )

    total_distance = 0.0
    total_cost = 0.0

    for i in range(len(path) - 1):
        data = G.get_edge_data(path[i], path[i + 1])
        total_distance += float(data["distance"])
        total_cost += float(data["cost"])

    return path, total_distance, total_cost

