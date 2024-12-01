import yaml
import networkx as nx
import subprocess
import xml.etree.ElementTree as ET
import os
import zipfile
import shutil

def load_config(config_path):
    with open(config_path, 'r') as file:
        config = yaml.safe_load(file)
    return config

def get_dependencies_from_nupkg(nupkg_path):
    # Создаем временную директорию для распаковки
    temp_dir = 'temp'
    os.makedirs(temp_dir, exist_ok=True)

    # Распаковываем .nupkg файл
    with zipfile.ZipFile(nupkg_path, 'r') as zip_ref:
        zip_ref.extractall(temp_dir)

    # Поиск .nuspec файла в распакованной директории
    nuspec_path = None
    for file in os.listdir(temp_dir):
        if file.endswith('.nuspec'):
            nuspec_path = os.path.join(temp_dir, file)
            break

    # Проверка существования .nuspec файла
    if not nuspec_path or not os.path.isfile(nuspec_path):
        print(f"Файл .nuspec не найден в {temp_dir}")
        shutil.rmtree(temp_dir)  # Удаляем временные файлы
        return []

    # Парсинг .nuspec файла для извлечения зависимостей
    dependencies = []
    try:
        # Вывод содержимого .nuspec файла для отладки
        with open(nuspec_path, 'r', encoding='utf-8') as file:
            nuspec_content = file.read()
            print("Содержимое .nuspec файла:")
            print(nuspec_content)

        tree = ET.parse(nuspec_path)
        root = tree.getroot()

        # Найдите секцию <dependencies>
        dependencies_section = root.find('.//dependencies')
        if dependencies_section is not None:
            for dependency in dependencies_section.findall('dependency'):
                package_id = dependency.attrib.get('id')
                version = dependency.attrib.get('version')
                # Игнорируем атрибут exclude
                if package_id:
                    dependencies.append((package_id, version))
        else:
            print("Секция <dependencies> не найдена.")

    except ET.ParseError as e:
        print(f"Ошибка парсинга .nuspec файла: {e}")
    finally:
        # Удаляем временные файлы и директорию
        shutil.rmtree(temp_dir)

    if not dependencies:
        print("Зависимости не найдены.")

    return dependencies

def build_graph(dependencies):
    G = nx.DiGraph()
    for package, version in dependencies:
        G.add_node(package, version=version)
        # Здесь можно добавить логику для добавления ребер, если у вас есть другие зависимости
        # Например, если у вас есть зависимости от других пакетов, вы можете добавить их
    return G

def generate_mermaid_graph(G):
    mermaid_str = "graph TD;\n"
    for u, v in G.edges():
        mermaid_str += f"    {u} --> {v};\n"
    return mermaid_str

def save_mermaid_to_file(mermaid_str, filename):
    with open(filename, 'w') as file:
        file.write(mermaid_str)

def render_graph(mermaid_file, visualizer_path, output_image_path):
    command = [visualizer_path, '-i', mermaid_file, '-o', output_image_path]
    print(f"Executing command: {' '.join(command)}")  # Выводим команду для отладки
    try:
        subprocess.run(command, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Ошибка при визуализации графа: {e}")

def main(config_path):
    config = load_config(config_path)

    # Получаем зависимости из .nupkg файла
    dependencies = get_dependencies_from_nupkg(config['nupkg_path'])
    print("Зависимости пакета:")
    for package, version in dependencies:
        print(f"{package}: {version}")

    G = build_graph(dependencies)

    mermaid_str = generate_mermaid_graph(G)
    print("Сгенерированный Mermaid граф:")
    print(mermaid_str)

    mermaid_file = 'graph.mmd'
    save_mermaid_to_file(mermaid_str, mermaid_file)

    render_graph(mermaid_file, config['visualizer_path'], config['output_image_path'])

    print("Граф зависимостей успешно визуализирован и сохранен в", config['output_image_path'])

if __name__ == "__main__":
    main('config.yaml')
