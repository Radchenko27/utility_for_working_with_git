import git
import networkx as nx
import sys
from typing import Optional, Set, Dict
from git.exc import BadName
from collections import defaultdict



class Graph:
    repository: object
    visited: Set[str] = None
    graph: Optional[nx.DiGraph] = None
    unique_commits: Set[str] = None
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
                "Ошибка значения данных: проверьте подаваемые хеши в аргументы. Хотя бы один из них не принадлежит данному репозиторию"
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

        if commit.hexsha in visited:  # or len(commit.parents) == 0
            return
        visited.add(commit.hexsha)

        branch = hash_branches.get(commit.hexsha, "unknown")
        graph.add_node(commit.hexsha, branch=branch)

        for parent in commit.parents:
            graph.add_edge(commit.hexsha, parent.hexsha)
            Graph.add_edges(graph, parent, visited, hash_branches)

    @staticmethod
    def is_commit_in_repo(repo: object, commit_hash: str) -> bool:
        try:
            repo.commit(commit_hash)
            return True
        except (BadName, KeyError):
            return False

    def get_unique_commits(self):

        lca_commit = self.find_lowest_common_ancestor(self.start_commit, self.end_commit)
        if lca_commit is None:
            raise ValueError("Нет общего предка между коммитами.")

        # Находим путь от начального коммита до общего предка
        path_to_lca = list(nx.all_simple_paths(self.graph, source=self.start_commit.hexsha, target=lca_commit.hexsha))
        # Находим путь от конечного коммита до общего предка
        path_from_lca = list(nx.all_simple_paths(self.graph, source=self.end_commit.hexsha, target=lca_commit.hexsha))

        path_to_lca_set = set()
        path_from_lca_set = set()
        for path in path_to_lca:
            path_to_lca_set.update(path)

        for path in path_from_lca:
            path_from_lca_set.update(path)

        self.unique_commits = path_to_lca_set.symmetric_difference(path_from_lca_set)
        # Объединяем пути, убирая дублирование общего предка
        return self.unique_commits

    def find_lowest_common_ancestor(self, commit1, commit2):
        global paths_head_ancestor1, paths_head_ancestor2
        try:
            roots = [node for node in self.graph if self.graph.out_degree(node) == 0]

            for root in roots:
                paths_head_ancestor1 = list(nx.all_simple_paths(self.graph, source=commit1.hexsha, target=root))
                paths_head_ancestor2 = list(nx.all_simple_paths(self.graph, source=commit2.hexsha, target=root))

            paths_head_ancestor = paths_head_ancestor1 + paths_head_ancestor2
            paths_head_ancestor_set = [set(path) for path in paths_head_ancestor]
            common_ancestors = set.intersection(*paths_head_ancestor_set)
            if not common_ancestors:
                return None
            return self.repository.commit(
                min(common_ancestors, key=lambda x: nx.shortest_path_length(self.graph, commit1.hexsha, x)))
        except ValueError:
            # Обработка отсутствия пути
            return None


def main():
    if len(sys.argv) != 4:
        sys.exit(1)
    repository = git.Repo(f'{sys.argv[1]}')
    our_graph = Graph(repository, f'{sys.argv[2]}', f'{sys.argv[3]}')
    # repository = git.Repo(r"C:\Users\dimar\OneDrive\Рабочий стол\Портфолио\ContentAI\Стажировка_работа_с_Git")
    # our_graph = Graph(repository, "9480afa", "ef3404f")
    our_graph.get_unique_commits()


if __name__ == '__main__':
    main()
