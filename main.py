import git
import networkx as nx
import matplotlib.pyplot as plt


def add_edges(graph, commit, visited):
    if commit.hexsha in visited:
        return
    visited.add(commit.hexsha)
    for parent in commit.parents:
        graph.add_edge(commit.hexsha, parent.hexsha)
        add_edges(graph, parent, visited)


def track_changes(first_value, second_value):
    first = repo.commit(first_value)
    second = repo.commit(second_value)
    diff = first.diff(second)
    for change in diff:
        print(f"Статус изменения: {change.change_type}")
        print(f"Из файла: {change.a_path}")
        print(f"В файл: {change.b_path}")
        if change.change_type != 'D':  # D - deleted file, no content to show
            print("Diff content:")
            # print(change.diff.decode('utf-8'))
        print("=" * 80)
# Открываем существующий репозиторий
repo = git.Repo(r'C:\Users\dimar\OneDrive\Рабочий стол\Портфолио\Стажировка_работа_с_Git')

# Определяем начальный и конечный коммиты
start_commit = repo.commit('26faf85')
end_commit = repo.commit('9ac62ae')

# Создаем граф
graph = nx.Graph()


# Добавляем ребра для начального и конечного коммитов
visited = set()
add_edges(graph, start_commit, visited)
add_edges(graph, end_commit, visited)

path = []
# Находим кратчайший путь
try:
    path = nx.shortest_path(graph, source=start_commit.hexsha, target=end_commit.hexsha)
    print("Shortest path:")
    for first_value, second_value in zip(path, path[1:]):
        track_changes(first_value, second_value)
# print(commit)
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
