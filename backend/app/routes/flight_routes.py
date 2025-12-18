from fastapi import APIRouter, HTTPException
from app.services.graph_builder import build_graph
from app.services.path_finder import dijkstra
from app.services.airport_resolver import resolve_airport_code


router = APIRouter(prefix="/flights", tags=["Flights"])
@router.get("/search")
def search_flights(source: str, destination: str, date: str):

    source_code = resolve_airport_code(source)
    destination_code = resolve_airport_code(destination)

    if not source_code or not destination_code:
        raise HTTPException(
            status_code=400,
            detail="Invalid source or destination airport"
        )

    graph = build_graph()
    cost, path = dijkstra(graph, source_code, destination_code)

    if not path:
        raise HTTPException(status_code=404, detail="No route found")

    return {
        "source": source,
        "destination": destination,
        "source_code": source_code,
        "destination_code": destination_code,
        "date": date,
        "total_distance": cost,
        "route": path
    }
