"""Топологическая сортировка зависимостей."""
from collections import defaultdict
from queue import Queue
from typing import Any, Dict, List

import yaml


class Graph:

    BUILDS_PATH = 'builds/builds.yaml'
    TASKS_PATH = 'builds/tasks.yaml'

    def __init__(self) -> None:
        """Инициализация.

        Attributes:
            self.adj_list: словарь, где ключ - название задачи, значение - список прямых зависимостей
            self.sorted: словарь, где ключ - название задачи, значение - список отсортированных зависимостей
        """
        self.adj_list: Dict[Any, List[Any]] = {}
        self.sorted: Dict[Any, List[Any]] = {}

    def process(self) -> None:
        """Чтение файлов, сортировка зависимостей  по алгоритму Кана.

        https://en.wikipedia.org/wiki/Topological_sorting#CITEREFKahn1962
        """
        with open(self.TASKS_PATH) as tasksfile:
            tasks_data = yaml.safe_load(tasksfile)
            for task in tasks_data.get('tasks', []):
                name, subtasks = task['name'], task['dependencies']
                self.adj_list[name] = subtasks

        with open(self.BUILDS_PATH) as buildfile:
            build_data = yaml.safe_load(buildfile)
            for build in build_data.get('builds', []):
                name, root_tasks = build['name'], build['tasks']
                self.adj_list[name] = root_tasks
                dep_count = self.count_deps(name)
                self.sort_tasks(name, dep_count)

    def count_deps(self, build: Any) -> Dict[Any, int]:
        """Подсчет зависимых задач для билда.

        Args:
            build: билд, для которого считаются зависимые задачи.

        Returns:
            Dict[Any, int]: словарь где ключ название задач, значение - количество зависимых от нее задач
        """
        stack = [*self.adj_list[build]]
        dep_count: Dict[Any, int] = defaultdict(int)
        seen = set()
        while stack:
            task = stack.pop()
            seen.add(task)
            for subtask in self.adj_list[task]:
                dep_count[subtask] += 1
                if subtask not in seen:
                    stack.append(subtask)
        return dep_count

    def sort_tasks(self, build: Any, dep_count: Dict[Any, int]) -> None:
        """Сортировка зависимостей.

        Args:
            build: название билда, чьи зависимости нужно отсортировать
            dep_count: словарь с подсчетом зависимых задач
        """
        queue: Queue[Any] = Queue()
        result: List[Any] = []

        for dep in self.adj_list[build]:
            if dep_count[dep] == 0:
                queue.put(dep)

        while not queue.empty():
            task = queue.get()
            result.append(task)
            for dep in self.adj_list[task]:
                dep_count[dep] -= 1
                if dep_count[dep] == 0:
                    queue.put(dep)

        self.sorted[build] = result[::-1]
