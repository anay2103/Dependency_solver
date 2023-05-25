## DEPENDENCY SOLVER

Веб-приложение Fastapi, которое делает топологическую сортировку зависимостей. Сортировка использует алгоритм Кана. Список задач и их зависимостей загружается из файлов при старте приложения.

Пример запроса:
```
$ curl -X 'POST' \
  'http://0.0.0.0:8000/get_tasks' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "build": "forward_interest"
}'
```
В ответе содержится отсортированный список зависимостей задачи:
```
[
  "design_green_ogres",
  "create_maroon_ogres",
  ...
  "coloring_aqua_centaurs",
  "build_teal_leprechauns"
]
```

## Запуск

Запуск тестов в контейнере:

```
$ docker run -d --name container_name $(docker build -q . --build-arg="PIPENV_FLAGS=--dev")
$ docker exec -it container_name pytest
```

Запуск веб-приложения:
```
$ docker run -p 8000:8000 -it  $(docker build -q .)
```