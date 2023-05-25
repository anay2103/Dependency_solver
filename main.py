"""Main app."""
from contextlib import asynccontextmanager
from typing import Any, List

from fastapi import FastAPI, status
from fastapi.exceptions import HTTPException
from pydantic import BaseModel

import topology


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Построение списка зависимостей перед стартом проекта.

    Args:
        app: приложение, в state которого сохраняется граф зависимостей
    """
    app.state.graph = topology.Graph()
    app.state.graph.process()
    yield
    app.state.graph.adj_list.clear()
    app.state.graph.sorted.clear()


app = FastAPI(title='Build system', lifespan=lifespan)


class Build(BaseModel):
    """Схема запроса POST /get_tasks."""
    build: str


@app.post('/get_tasks', name='Get tasks by build name', response_model=List[Any])
def get_tasks(build: Build) -> List[Any]:
    """Эндпоинт принимает название билда и возвращает список отсортированных зависимостей."""
    try:
        sorted_tasks = app.state.graph.sorted[build.build]
    except KeyError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Build not found')
    except Exception as exc:
        detail = {'exception': exc.__class__.__name__}
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, detail)
    return sorted_tasks
