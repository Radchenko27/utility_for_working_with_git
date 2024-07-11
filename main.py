import git
import networkx as nx
import matplotlib.pyplot as plt
import subprocess
import sys


def add_edges(graph, commit, visited):
    if commit.hexsha in visited:
        return
    visited.add(commit.hexsha)
    for parent in commit.parents:
        graph.add_edge(commit.hexsha, parent.hexsha)
        add_edges(graph, parent, visited)


def run_git_diff(repo_path, commit1, commit2):
    try:
        # Формируем команду git diff
        command = ['git', '-C', repo_path, 'diff', commit1, commit2]

        # Выполняем команду
        result = subprocess.run(command, capture_output=True, text=True)

        # Проверяем, если команда выполнена успешно
        if result.returncode == 0:
            print(result.stdout)  # Выводим результат diff
        else:
            print(f"Error: {result.stderr}")

    except Exception as e:
        print(f"An error occurred: {e}")


def main():
    if len(sys.argv) != 4:
        print(
            'Ошибка.Формат введенных данных должен соответствовать примеру: python example.py <repo_path> <commit1> <commit2>')
        sys.exit(1)
        # Открываем существующий репозиторий
    repo = git.Repo(f'{sys.argv[1]}')
    # repo_path = r'C:\Users\dimar\OneDrive\Рабочий стол\Портфолио\Стажировка_работа_с_Git'
    # Определяем начальный и конечный коммиты
    start_commit = repo.commit(f'{sys.argv[2]}')
    end_commit = repo.commit(f'{sys.argv[3]}')

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
        # print("Shortest path:")
        for first_value, second_value in zip(path, path[1:]):
            # run_git_diff(repo_path, first_value, second_value)
            diff = repo.git.diff(first_value, second_value)
            print(diff)
            print('=' * 140)
    # print(commit)
    except nx.NetworkXNoPath:
        print("No path found between the specified commits.")

    # Построение графа с выделением кратчайшего пути
    pos = nx.spring_layout(graph)
    plt.figure(figsize=(12, 8))
    nx.draw(graph, pos, with_labels=True, node_size=500, node_color='skyblue', font_size=10, font_weight='bold')
    path_edges = list(zip(path, path[1:]))
    nx.draw_networkx_edges(graph, pos, edgelist=path_edges, edge_color='r', width=2)
    plt.title('Git Commit Graph with Shortest Path')
    plt.show()


if __name__ == '__main__':
    main()

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
