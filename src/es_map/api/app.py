from fastapi import FastAPI

from es_map.graph.api.models import Graph


def create_app(graph: Graph):
    app = FastAPI()

    app.state.graph = graph

    @app.get("/graph", response_model=Graph)
    def get_graph() -> Graph:
        return app.state.graph.model_dump()

    return app
