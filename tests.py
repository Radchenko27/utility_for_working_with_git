from main import Graph
import git
import networkx as nx
import unittest
from unittest.mock import MagicMock, patch


class TestGraph(unittest.TestCase):
    """
                                              g --- k
                                             /       \
модель графа для тестирования: a -- b -- f ----- l -- j
                                    \           /
                                     c -- d -- e
    """

    def setUp(self):
        # Создаем фиктивные объекты коммитов
        self.mock_commit_a = MagicMock()
        self.mock_commit_a.hexsha = "a"
        self.mock_commit_a.parents = []

        self.mock_commit_b = MagicMock()
        self.mock_commit_b.hexsha = "b"
        self.mock_commit_b.parents = [self.mock_commit_a]

        self.mock_commit_c = MagicMock()
        self.mock_commit_c.hexsha = "c"
        self.mock_commit_c.parents = [self.mock_commit_b]

        self.mock_commit_d = MagicMock()
        self.mock_commit_d.hexsha = "d"
        self.mock_commit_d.parents = [self.mock_commit_c]

        self.mock_commit_e = MagicMock()
        self.mock_commit_e.hexsha = "e"
        self.mock_commit_e.parents = [self.mock_commit_d]

        self.mock_commit_f = MagicMock()
        self.mock_commit_f.hexsha = "f"
        self.mock_commit_f.parents = [self.mock_commit_b]

        self.mock_commit_g = MagicMock()
        self.mock_commit_g.hexsha = "g"
        self.mock_commit_g.parents = [self.mock_commit_f]

        self.mock_commit_k = MagicMock()
        self.mock_commit_k.hexsha = "k"
        self.mock_commit_k.parents = [self.mock_commit_g]

        self.mock_commit_l = MagicMock()
        self.mock_commit_l.hexsha = "l"
        self.mock_commit_l.parents = [self.mock_commit_f, self.mock_commit_e]

        self.mock_commit_j = MagicMock()
        self.mock_commit_j.hexsha = "j"
        self.mock_commit_j.parents = [self.mock_commit_l, self.mock_commit_k]

        # Создаем фиктивные ветки и связываем их с коммитами
        self.mock_branch_main = MagicMock()
        self.mock_branch_main.name = "main"

        self.mock_branch_Release = MagicMock()
        self.mock_branch_Release.name = "Release"

        self.mock_branch_Release_2 = MagicMock()
        self.mock_branch_Release_2.name = "Release_2"

        # Создаем фиктивный репозиторий и возвращаем фиктивные коммиты
        self.mock_repo = MagicMock()
        self.mock_repo.commit.side_effect = lambda x: {
            "a": self.mock_commit_a,
            "b": self.mock_commit_b,
            "c": self.mock_commit_c,
            "d": self.mock_commit_d,
            "e": self.mock_commit_e,
            "f": self.mock_commit_f,
            "g": self.mock_commit_g,
            "k": self.mock_commit_k,
            "l": self.mock_commit_l,
            "j": self.mock_commit_j,
        }[x]

        # Добавляем ветки в репозиторий
        self.mock_repo.branches = [self.mock_branch_main, self.mock_branch_Release, self.mock_branch_Release_2]

        # Связываем коммиты с ветками
        self.mock_repo.iter_commits.side_effect = lambda branch_name: {
            "main": [self.mock_commit_a, self.mock_commit_b, self.mock_commit_c, self.mock_commit_d, self.mock_commit_e,
                     self.mock_commit_f, self.mock_commit_l, self.mock_commit_j],
            "Release": [self.mock_commit_d, self.mock_commit_b, self.mock_commit_c, self.mock_commit_a],
            "Release_2": [self.mock_commit_d, self.mock_commit_b, self.mock_commit_c, self.mock_commit_a]
        }[branch_name]
        self.graph = Graph(self.mock_repo, "a", "b")

    def test_init(self):
        self.assertEqual(self.graph.repository, self.mock_repo)
        self.assertEqual(self.graph.start_commit, self.mock_commit_a)
        self.assertEqual(self.graph.end_commit, self.mock_commit_b)
        self.assertIsInstance(self.graph.graph, nx.Graph)
        self.assertIsInstance(self.graph.visited, set)

    def test_add_edges(self):
        Graph.add_edges(self.graph.graph, self.mock_commit_b, self.graph.visited, self.graph.hash_branches)
        self.assertIn("b", self.graph.graph.nodes)
        self.assertIn("a", self.graph.graph.nodes)
        self.assertIn(("b", "a"), self.graph.graph.edges)

    """
                                                g -- k
                                               /       \
  модель графа для тестирования: a -- b -- f ----- l -- j
                                      \           /
                                       c -- d -- e
      """

    def test_get_unique_commits_сase_1(self):  # построение пути между двумя коммитами из разных веток
        graph = Graph(self.mock_repo, "d", "g")
        path = graph.get_unique_commits()
        self.assertEqual(sorted(path), sorted({'d', 'c',  'f', 'g'}))

    def test_get_unique_commits_сase_2(self):  # построение пути между двумя коммитами (один из main  другой из Release)
        graph = Graph(self.mock_repo, "f", "e")
        path = graph.get_unique_commits()
        self.assertEqual(sorted(path), sorted({'f', 'c', 'd', 'e'}))

    def test_get_unique_commits_сase_3(self):  # построение пути между двумя коммитами (один из main  другой из Release)
        graph = Graph(self.mock_repo, "k", "l")
        path = graph.get_unique_commits()# определяет f как общего прородителя
        self.assertEqual(sorted(path), sorted({'k', 'g', 'c', 'd', 'e', 'l'}))

    def test_get_unique_commits_сase_4(self):  # построение пути между двумя merge-коммитами
        graph = Graph(self.mock_repo, "j", "l")
        path = graph.get_unique_commits()
        self.assertEqual(sorted(path), sorted({'g', 'k', 'j'}))

    def test_get_unique_commits_no_path(self):
        with self.assertRaises(ValueError):
            graph = Graph(self.mock_repo, "a", "z")

    # def test_get_unique_commits_single_node(self):
    #     graph = Graph(self.mock_repo, "a", "a")
    #     path = graph.get_unique_commits()
    #     self.assertEqual(path, ["a"])

    def test_find_lowest_common_ancestor(self):
        # Проверяем, что метод find_lowest_common_ancestor находит правильного предка
        lca_commit = self.graph.find_lowest_common_ancestor(self.mock_commit_a, self.mock_commit_b)
        self.assertEqual(lca_commit.hexsha, "a")



if __name__ == '__main__':
    unittest.main()
