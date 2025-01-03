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
    temp_dir = 'temp'
    os.makedirs(temp_dir, exist_ok=True)

    with zipfile.ZipFile(nupkg_path, 'r') as zip_ref:
        zip_ref.extractall(temp_dir)

    nuspec_path = None
    for file in os.listdir(temp_dir):
        if file.endswith('.nuspec'):
            nuspec_path = os.path.join(temp_dir, file)
            break

    if not nuspec_path or not os.path.isfile(nuspec_path):
        print(f"Файл .nuspec не найден в {temp_dir}")
        return []

    dependencies = []
    try:
        tree = ET.parse(nuspec_path)
        root = tree.getroot()

        namespace = {'ns': 'http://schemas.microsoft.com/packaging/2013/05/nuspec.xsd'}

        dependencies_element = root.find('.//ns:dependencies', namespace)
        if dependencies_element is not None:
            for dependency in dependencies_element.findall('ns:dependency', namespace):
                dep_id = dependency.get('id')
                dep_version = dependency.get('version')
                dependencies.append((dep_id, dep_version))

    except ET.ParseError as e:
        print(f"Ошибка при парсинге .nuspec файла: {e}")

    shutil.rmtree(temp_dir)

    return dependencies

def build_graph(dependencies, config):
    G = nx.DiGraph()
    root_package = config['nupkg_path'][config['nupkg_path'].rfind("\\") + 1:]
    G.add_node(root_package)

    for package, version in dependencies:
        G.add_node(package, version=version)
        G.add_edge(root_package, package)
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
    command = [visualizer_path, '-i', mermaid_file, '-o', output_image_path, '-w', '3840', '-H', '2160']
    try:
        subprocess.run(command, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Ошибка при визуализации графа: {e}")

def main(config_path):
    config = load_config(config_path)

    dependencies = get_dependencies_from_nupkg(config['nupkg_path'])

    G = build_graph(dependencies, config)

    mermaid_str = generate_mermaid_graph(G)

    mermaid_file = 'graph.mmd'
    save_mermaid_to_file(mermaid_str, mermaid_file)

    render_graph(mermaid_file, config['visualizer_path'], config['output_image_path'])

    print("Граф зависимостей успешно визуализирован и сохранен в", config['output_image_path'])

if __name__ == "__main__":
    main('config.yaml')
