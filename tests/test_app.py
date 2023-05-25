import pytest
from fastapi import FastAPI, status
from fastapi.testclient import TestClient

import topology


@pytest.fixture
def test_paths(monkeypatch: pytest.MonkeyPatch) -> None:
    """Замена исходных файлов на тестовые."""
    monkeypatch.setattr(topology.Graph, 'BUILDS_PATH', 'tests/fixtures/builds.yaml')
    monkeypatch.setattr(topology.Graph, 'TASKS_PATH', 'tests/fixtures/tasks.yaml')


@pytest.fixture
def test_graph(test_paths) -> topology.Graph:
    """Тестовый граф зависимостей."""
    graph = topology.Graph()
    graph.process()
    test_adj_list = {
        9: [10, 11], 10: [1, 2, 3], 11: [4, 5], 1: [4], 2: [7],  3: [11], 7: [],
        4: [6], 6: [5], 5: [], 8: [13, 14], 13: [2, 6], 14: [11]
    }
    assert graph.adj_list == test_adj_list
    return graph


@pytest.fixture
def app() -> FastAPI:
    """Тестовое веб-приложение."""
    from main import app as testapp

    testapp.state.graph = topology.Graph()
    testapp.state.graph.sorted = {
        'one': [5, 6, 4, 11, 7, 3, 2, 1, 10],
        'two': [5, 6, 4, 7, 11, 2, 14, 13],
    }
    return testapp


@pytest.fixture
def client(app: FastAPI) -> TestClient:
    """Тестовый клиент."""
    return TestClient(app)


def test_sort(test_graph: topology.Graph) -> None:
    """Тест сортировки зависимостей."""
    result = test_graph.sorted[9]
    assert result == [5, 6, 4, 11, 7, 3, 2, 1, 10]
    result = test_graph.sorted[8]
    assert result == [5, 6, 4, 7, 11, 2, 14, 13]


def test_post_ok(client: TestClient) -> None:
    """Тест POST /get_tasks ответ OK."""
    resp = client.post('/get_tasks', json={'build': 'one'})
    assert resp.status_code == status.HTTP_200_OK
    respdata = resp.json()
    assert respdata == [5, 6, 4, 11, 7, 3, 2, 1, 10]


async def test_post_not_found(client: TestClient) -> None:
    """Тест POST /get_tasks ответ 400."""
    resp = client.post('/get_tasks', json={'build': 'three'})
    assert resp.status_code == status.HTTP_400_BAD_REQUEST
    respdata = resp.json()
    assert respdata['detail'] == 'Build not found'
