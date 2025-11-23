
import math
import random
import networkx as nx
from sqlalchemy.orm import Session

from models.connection import Connection
from models.airport import Airport

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
    Factor de congestión en base a cuántas rutas pasan por los aeropuertos
    extremos .

    """
    degree_sum = deg_a + deg_b

    if degree_sum <= 6:
        return 1.0      
    elif degree_sum <= 10:
        return 1.3     
    else:
        return 1.6      


def generate_connections_if_empty(db: Session) -> None:

    existing = db.query(Connection).count()
    if existing > 0:
        
        return

    airports = db.query(Airport).all()
    if len(airports) < 2:
        return  

    airport_by_id = {a.id: a for a in airports}
    coords = [(a.id, a.lat, a.lon) for a in airports]

   
    target_degree = {
        a.id: random.choice([3, 5, 7])
        for a in airports
    }

  
    current_degree = {a.id: 0 for a in airports}

    
    edge_set = set()
    edges_temp = []  

   
    for id1, lat1, lon1 in coords:
        
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
            edges_temp.append((id1, id2, dist))
            current_degree[id1] += 1
            current_degree[id2] += 1

    
    for airport_id, deg in current_degree.items():
        airport = airport_by_id[airport_id]
        airport.concurrency = _classify_concurrency(deg)

   
    for id1, id2, dist in edges_temp:
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


def build_graph(db: Session) -> nx.Graph:
    """
    Construye el grafo a partir de la tabla Conexiones.
    Si está vacía, genera conexiones automáticamente primero.
    """
    generate_connections_if_empty(db)

    G = nx.Graph()

    connections = db.query(Connection).all()
    for c in connections:
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
    Calcula el camino más corto según criteria: 'distance' o 'cost'.
    Devuelve: path, total_distance, total_cost
    """
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
        total_distance += float(data["distance"])
        total_cost += float(data["cost"])

    return path, total_distance, total_cost
