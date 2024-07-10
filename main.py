import git
import networkx as nx
import matplotlib.pyplot as plt

# Открываем существующий репозиторий
repo = git.Repo(r'C:\Users\dimar\OneDrive\Рабочий стол\Портфолио\Стажировка_работа_с_Git')

# Определяем начальный и конечный коммиты
start_commit = repo.commit('5f6c93f')
end_commit = repo.commit('9435574')

# Создаем граф
graph = nx.DiGraph()


def add_edges(graph, commit, visited):
    if commit.hexsha in visited:
        return
    visited.add(commit.hexsha)
    for parent in commit.parents:
        graph.add_edge(commit.hexsha, parent.hexsha)
        add_edges(graph, parent, visited)


# Добавляем ребра для начального и конечного коммитов
visited = set()
add_edges(graph, start_commit, visited)
add_edges(graph, end_commit, visited)

path = []
# Находим кратчайший путь
try:
    path = nx.shortest_path(graph, source=start_commit.hexsha, target=end_commit.hexsha)
    print("Shortest path:")
    for commit in path:
        print(commit)
except nx.NetworkXNoPath:
    print("No path found between the specified commits.")

# Построение графа с выделением кратчайшего пути
pos = nx.spring_layout(graph)
plt.figure(figsize=(12, 8))
nx.draw(graph, pos, with_labels=True, node_size=500, node_color='skyblue', font_size=10, font_weight='bold')
path_edges = list(zip(path, path[1:]))
print(path_edges)
nx.draw_networkx_edges(graph, pos, edgelist=path_edges, edge_color='r', width=2)
plt.title('Git Commit Graph with Shortest Path')
plt.show()
# if __name__ == '__main__':


# See PyCharm help at https://www.jetbrains.com/help/pycharm/
