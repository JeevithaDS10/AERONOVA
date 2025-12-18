from app.db import get_connection
from collections import defaultdict

def build_graph():
    """
    Builds an adjacency list graph from routes table
    Graph format:
    {
      'BLR': [('MAA', 290), ('HYD', 570)],
      'MYQ': [('BLR', 150)]
    }
    """
    graph = defaultdict(list)
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT source_airport, destination_airport, distance_km
        FROM routes
    """)

    routes = cursor.fetchall()

    for r in routes:
        src = r["source_airport"]
        dest = r["destination_airport"]
        dist = r["distance_km"]

        graph[src].append((dest, dist))
        graph[dest].append((src, dist))  # bidirectional

    cursor.close()
    conn.close()
    return graph
