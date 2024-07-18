from main import Graph
import git
import networkx as nx
import unittest
from unittest.mock import MagicMock


class TestGraph(unittest.TestCase):

    def setUp(self):
        self.repository = MagicMock(spec=git.Repo)
        self.commit1 = MagicMock(spec=git.Commit)
        self.commit2 = MagicMock(spec=git.Commit)
        self.commit1.hexsha = 'a1b2c3d4'
        self.commit2.hexsha = 'e5f6g7h8'
        self.commit1.parents = []
        self.commit2.parents = [self.commit1]
        self.repository.commit.side_effect = lambda x: self.commit1 if x == 'a1b2c3d4' else self.commit2

    def test_init(self):
        g = Graph(self.repository, 'a1b2c3d4', 'e5f6g7h8')
        self.assertEqual(g.start_commit, self.commit1)
        self.assertEqual(g.end_commit, self.commit2)

    def test_init_type_error(self):
        with self.assertRaises(TypeError):
            Graph("не репозиторий ", 'a1b2c3d4', 'e5f6g7h8')

    def test_add_edges(self):
        graph = nx.Graph()
        visited = set()
        Graph.add_edges(graph, self.commit2, visited)
        self.assertIn(self.commit1.hexsha, visited)
        self.assertIn(self.commit2.hexsha, visited)
        self.assertTrue(graph.has_edge(self.commit2.hexsha, self.commit1.hexsha))

    def test_initialization_of_general_graph(self):
        g = Graph(self.repository, 'a1b2c3d4', 'e5f6g7h8')
        g.initialization_of_general_graph()
        self.assertIsNotNone(g.graph)
        self.assertIn(g.start_commit.hexsha, g.visited)
        self.assertIn(g.end_commit.hexsha, g.visited)

    def test_get_shortest_path(self):
        g = Graph(self.repository, 'a1b2c3d4', 'e5f6g7h8')
        g.initialization_of_general_graph()
        path = g.get_shortest_path()
        self.assertIsNotNone(path)
        self.assertEqual(path, ['a1b2c3d4', 'e5f6g7h8'])

    def test_get_history_diff(self):
        g = Graph(self.repository, 'a1b2c3d4', 'e5f6g7h8')
        g.initialization_of_general_graph()
        g.get_shortest_path()
        g.repository.git.diff = MagicMock(return_value="diff content")
        with self.assertLogs() as log:
            g.get_history_diff()
            self.assertIn('diff content', log.output[0])

    def test_model_graph(self):
        g = Graph(self.repository, 'a1b2c3d4', 'e5f6g7h8')
        g.initialization_of_general_graph()
        g.get_shortest_path()
        self.assertIsNotNone(g.graph)
        self.assertIsNotNone(g.path)


if __name__ == '__main__':
    unittest.main()
