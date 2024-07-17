import git
import networkx as nx
import matplotlib.pyplot as plt

import sys
from typing import Type, Optional, List, Set


class Graph:
    visited: Set[str] = None
    graph: Optional[nx.Graph] = None
    path: List[str] = None

    def __init__(self, repository: Type[git.Repo], start_hash: str, end_hash: str):
        if isinstance(repository, git.Repo):
            self.repository = repository
            self.start_commit = repository.commit(start_hash)
            self.end_commit = repository.commit(end_hash)
        else:
            raise TypeError(
                "Ошибка типа данных, в качестве аргументов обьекта класса Graph подайте объекты класса git.Repo")

    @staticmethod
    def add_edges(graph, commit, visited):
        if commit.hexsha in visited:
            return
        visited.add(commit.hexsha)
        for parent in commit.parents:
            graph.add_edge(commit.hexsha, parent.hexsha)
            Graph.add_edges(graph, parent, visited)

    def initialization_of_general_graph(self):
        self.graph = nx.Graph()
        self.visited = set()
        self.add_edges(self.graph, self.start_commit, self.visited)
        self.add_edges(self.graph, self.end_commit, self.visited)

    def get_shortest_path(self):
        if self.graph is None:
            print("Вызовите метод initialization_of_general_graph . Граф пустой!")
            return
        try:
            self.path = nx.shortest_path(self.graph, source=self.start_commit.hexsha, target=self.end_commit.hexsha)
            return self.path
        except nx.NetworkXNoPath:
            print("Нет пути между коммитами.")

    def get_history_diff(self):
        if self.path is None:
            print("Вызовите метод get_shortest_path. Поле path данного обЪекта равно None")
            return
        else:
            for first_value, second_value in zip(self.path, self.path[1:]):
                diff = self.repository.git.diff(first_value, second_value)
                print(diff)
                print('=' * 140)

    def model_graph(self):
        if self.graph is None:
            print("Вызовите метод initialization_of_general_graph . Граф пустой!")
            return
        if self.path is None:
            print("Вызовите метод get_shortest_path. Поле path данного обЪекта равно None")
            return
        pos = nx.spring_layout(self.graph)
        plt.figure(figsize=(12, 8))
        nx.draw(self.graph, pos, with_labels=True, node_size=500, node_color='skyblue', font_size=10,
                font_weight='bold')
        path_edges = list(zip(self.path, self.path[1:]))
        nx.draw_networkx_edges(self.graph, pos, edgelist=path_edges, edge_color='r', width=2)
        plt.title('Git Commit Graph with Shortest Path')
        plt.show()


def main():
    if len(sys.argv) != 4:
        print(
            'Ошибка.Формат введенных данных должен соответствовать примеру: python example.py <repo_path> <commit1> <commit2>')
        sys.exit(1)
    #         # Открываем существующий репозиторий
    repository = git.Repo(f'{sys.argv[1]}')
    our_graph = Graph(repository, f'{sys.argv[2]}', f'{sys.argv[3]}')
    our_graph.initialization_of_general_graph()
    our_graph.get_shortest_path()
    our_graph.get_history_diff()
    our_graph.model_graph()


if __name__ == '__main__':
    main()
