from fastapi import FastAPI

from es_map.graph.api.models import Graph


def create_app(graph: Graph):
    app = FastAPI()

    app.state.graph = graph

    @app.get("/graph")
    def get_graph():
        return app.state.graph.model_dump()

    return app
