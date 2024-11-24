import subprocess
import yaml
import networkx as nx
import os
import xml.etree.ElementTree as ET

def load_config(config_path):
    with open(config_path, 'r') as file:
        config = yaml.safe_load(file)
    return config

def parse_csproj(file_path):
    dependencies = {}
    tree = ET.parse(file_path)
    root = tree.getroot()
    
    # Пространство имен для XML
    namespace = {'ns': 'http://schemas.microsoft.com/developer/msbuild/2003'}

    # Ищем все PackageReference
    for package_ref in root.findall('ns:ItemGroup/ns:PackageReference', namespace):
        package_name = package_ref.get('Include')
        dependencies[package_name] = []

    # Ищем все ProjectReference (если нужно)
    for project_ref in root.findall('ns:ItemGroup/ns:ProjectReference', namespace):
        project_path = project_ref.get('Include')
        # Рекурсивно получаем зависимости из других проектов, если нужно
        dependencies[project_path] = parse_csproj(os.path.join(os.path.dirname(file_path), project_path))

    return dependencies

def get_dependencies(package_name):
    # Предполагаем, что package_name - это путь к .csproj файлу
    if not os.path.isfile(package_name):
        print(f"Файл {package_name} не найден.")
        return {}

    dependencies = parse_csproj(package_name)
    return dependencies

def build_graph(dependencies):
    G = nx.DiGraph()
    for package, deps in dependencies.items():
        for dep in deps:
            G.add_edge(package, dep)
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
    command = [visualizer_path, mermaid_file, output_image_path]
    subprocess.run(command, check=True)

def main(config_path):
    config = load_config(config_path)

    dependencies = get_dependencies(config['package_name'])
    G = build_graph(dependencies)

    mermaid_str = generate_mermaid_graph(G)
    mermaid_file = 'graph.mmd'
    save_mermaid_to_file(mermaid_str, mermaid_file)

    render_graph(mermaid_file, config['visualizer_path'], config['output_image_path'])

    print("Граф зависимостей успешно визуализирован и сохранен в", config['output_image_path'])

if __name__ == "__main__":
    main('config.yaml')
