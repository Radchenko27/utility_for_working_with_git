import git
import networkx as nx
import matplotlib.pyplot as plt
import logging
import sys
from typing import Type, Optional, List, Set, Any, Dict
from git.exc import BadName
from collections import defaultdict
import gzip

logging.basicConfig(level=logging.INFO)


class Graph:
    repository: object
    visited: Set[str] = None
    graph: Optional[nx.DiGraph] = None
    path: List[str] = None
    hash_branches: Dict = defaultdict(list)

    def __init__(self, repository: object, start_hash: str, end_hash: str):
        if not isinstance(repository, object):
            raise TypeError(
                "Ошибка типа данных: в качестве аргумента 'repository' ожидается объект любого класса"
            )
        self.repository = repository
        if self.is_commit_in_repo(repository, start_hash) and self.is_commit_in_repo(repository, end_hash):
            self.start_commit = repository.commit(start_hash)
            self.end_commit = repository.commit(end_hash)
        else:
            raise ValueError(
                'Ошибка значения данных: проверьте подаваемые хеши в аргументы. Хотя бы один из них не принадлежит данному репозиторию'
            )
        self.hash_branches = self.add_hash_branches(self.repository)
        self.graph = nx.DiGraph()
        self.visited = set()
        self.add_edges(self.graph, self.start_commit, self.visited, self.hash_branches)
        self.add_edges(self.graph, self.end_commit, self.visited, self.hash_branches)

    @staticmethod
    def add_hash_branches(repository):
        hash_branches = {}
        for branch in repository.branches:
            for commit in repository.iter_commits(branch.name):
                if commit.hexsha in hash_branches:
                    hash_branches[commit.hexsha].append(branch.name)
                else:
                    hash_branches[commit.hexsha] = [branch.name]
        return hash_branches

    @staticmethod
    def add_edges(graph, commit, visited, hash_branches):

        if commit.hexsha in visited or len(commit.parents) == 0:
            return
        visited.add(commit.hexsha)

        branch = hash_branches.get(commit.hexsha, "unknown")
        graph.add_node(commit.hexsha, branch=branch)

        if len(commit.parents) > 1 and branch[0] == 'main':
            parent = commit.parents[1]
        else:
            parent = commit.parents[0]
        graph.add_edge(commit.hexsha, parent.hexsha)
        Graph.add_edges(graph, parent, visited, hash_branches)

    @staticmethod
    def is_commit_in_repo(repo: object, commit_hash: str) -> bool:
        try:
            repo.commit(commit_hash)
            return True
        except (BadName, KeyError):
            return False

    def get_shortest_path(self):

        lca_commit = self.find_lowest_common_ancestor(self.start_commit, self.end_commit)
        if lca_commit is None:
            raise ValueError("Нет общего предка между коммитами.")

        # Находим путь от начального коммита до общего предка
        path_to_lca = nx.shortest_path(self.graph, source=self.start_commit.hexsha, target=lca_commit.hexsha)
        # Находим путь от конечного коммита до общего предка
        path_from_lca = nx.shortest_path(self.graph, source=self.end_commit.hexsha, target=lca_commit.hexsha)
        # Объединяем пути, убирая дублирование общего предка
        self.path = path_to_lca + path_from_lca[::-1][1:]
        return self.path

    def find_lowest_common_ancestor(self, commit1, commit2):
        try:
            ancestors1 = set(nx.single_source_shortest_path_length(self.graph, commit1.hexsha).keys())
            ancestors2 = set(nx.single_source_shortest_path_length(self.graph, commit2.hexsha).keys())
            common_ancestors = ancestors1 & ancestors2
            if not common_ancestors:
                return None
            return self.repository.commit(
                min(common_ancestors, key=lambda x: nx.shortest_path_length(self.graph, commit1.hexsha, x)))
        except ValueError as e:
            # Обработка отсутствия пути
            logging.warning(f"Нет пути между : {e}")
            return None

    def get_history_diff(self):
        if self.path is None:
            raise TypeError("Вызовите метод get_shortest_path. Поле path данного обЪекта равно None")
        else:
            for first_value, second_value in zip(self.path, self.path[1:]):
                diff = self.repository.git.diff(first_value, second_value)
                logging.info(diff)
                logging.info('=' * 140)

    def model_graph(self):
        if self.path is None:
            raise TypeError("Вызовите метод get_shortest_path. Поле path данного объекта равно None")

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
        logging.warning(
            'Ошибка.Формат введенных данных должен соответствовать примеру: python example.py <repo_path> <commit1> <commit2>')
        sys.exit(1)
    #         # Открываем существующий репозиторий
    repository = git.Repo(f'{sys.argv[1]}')
    our_graph = Graph(repository, f'{sys.argv[2]}', f'{sys.argv[3]}')
    # repository = git.Repo(r"C:\Users\dimar\OneDrive\Рабочий стол\Портфолио\ContentAI\Стажировка_работа_с_Git")
    # our_graph = Graph(repository, "9480afa", "ef3404f")
    our_graph.get_shortest_path()
    our_graph.get_history_diff()
    our_graph.model_graph()


if __name__ == '__main__':
    main()
