from fastapi.testclient import TestClient

from app.main import app


class FakeGraph:
    async def ainvoke(self, state, config):
        return {
            "answer": "Respuesta de prueba.",
            "thread_id": config["configurable"]["thread_id"],
            "agent": "research",
            "sources": [],
        }


async def fake_execute_graph(state, config):
    return await app.state.graph.ainvoke(state, config)


def test_health_endpoint():
    with TestClient(app) as client:
        response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_query_endpoint_returns_valid_response():
    with TestClient(app) as client:
        client.app.state.graph = FakeGraph()
        client.app.state.execute_graph = fake_execute_graph

        response = client.post(
            "/query",
            json={
                "question": "Pregunta de prueba",
                "mode": "research",
                "thread_id": "api-test-001",
            },
        )

    assert response.status_code == 200
    assert response.json()["answer"] == "Respuesta de prueba."
    assert response.json()["thread_id"] == "api-test-001"


def test_query_endpoint_validates_input():
    with TestClient(app) as client:
        response = client.post(
            "/query",
            json={
                "question": "a",
                "mode": "research",
            },
        )

    assert response.status_code == 422
