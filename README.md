## Постановка задачи
Разработать инструмент командной строки для визуализации графа 
зависимостей, включая транзитивные зависимости. Сторонние средства для 
получения зависимостей использовать нельзя. 
 
Зависимости определяются по имени пакета платформы .NET (nupkg). Для 
описания 
графа зависимостей используется представление Mermaid. 
Визуализатор должен выводить результат в виде сообщения об успешном 
выполнении и сохранять граф в файле формата png. 

Конфигурационный файл имеет формат yaml и содержит: 

• Путь к программе для визуализации графов. 

• Имя анализируемого пакета. 

• Путь к файлу с изображением графа зависимостей. 

Все функции визуализатора зависимостей должны быть покрыты тестами.
## Описание основных функций
**1. load_config(config_path)**

```
def load_config(config_path):
    with open(config_path, 'r') as file:
        config = yaml.safe_load(file)
    return config
```

*Описание:*

Функция загружает конфигурационный файл в формате YAML и возвращает его содержимое в виде словаря.

**2. get_dependencies_from_nupkg(nupkg_path)**
```
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
```

*Описание:*

Функция извлекает зависимости из nupkg пакета, парсит файл .nuspec и возвращает список зависимостей в формате (package, version).

**3. build_graph(dependencies, config)**
```
def build_graph(dependencies, config):
    G = nx.DiGraph()
    root_package = config['nupkg_path'][config['nupkg_path'].rfind("\\") + 1:]
    G.add_node(root_package)

    for package, version in dependencies:
        G.add_node(package, version=version)
        G.add_edge(root_package, package)
    return G
```

*Описание:*

Функция создает граф зависимостей на основе списка зависимостей и корневого пакета из конфигурации.

**4. generate_mermaid_graph(G)**
```
def generate_mermaid_graph(G):
    mermaid_str = "graph TD;\n"
    for u, v in G.edges():
        mermaid_str += f"    {u} --> {v};\n"
    return mermaid_str
```

*Описание:*

Функция генерирует строку в формате Mermaid для отображения графа.

**5. save_mermaid_to_file(mermaid_str, filename)**
```
def save_mermaid_to_file(mermaid_str, filename):
    with open(filename, 'w') as file:
        file.write(mermaid_str)
```

*Описание:*

Функция сохраняет строку в формате Mermaid в файл.

**6. render_graph(mermaid_file, visualizer_path, output_image_path)**
```
def render_graph(mermaid_file, visualizer_path, output_image_path):
    command = [visualizer_path, '-i', mermaid_file, '-o', output_image_path]
    try:
        subprocess.run(command, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Ошибка при визуализации графа: {e}")
```

*Описание:*

Функция отрисовывает граф с помощью визуализатора

**7. main(config_path)**
```
def main(config_path):
    config = load_config(config_path)

    dependencies = get_dependencies_from_nupkg(config['nupkg_path'])

    G = build_graph(dependencies, config)

    mermaid_str = generate_mermaid_graph(G)

    mermaid_file = 'graph.mmd'
    save_mermaid_to_file(mermaid_str, mermaid_file)

    render_graph(mermaid_file, config['visualizer_path'], config['output_image_path'])

    print("Граф зависимостей успешно визуализирован и сохранен в", config['output_image_path'])
```

*Описание:*

Основная функция, объединяющая все шаги выполнения программы. Загружает конфигурацию, извлекает зависимости, строит граф, генерирует Mermaid код, сохраняет в файл, визуализирует и сохраняет результат.

**8. name == "main"**
```
if __name__ == "__main__":
    main('config.yaml')
```

*Описание:*

Проверка, чтобы код выполнялся только как самостоятельный скрипт, а не импортировался как модуль.
## Сборка проекта

Для сборки проекта необходимо установить Mermaid.

*Комманда для запуска эмулятора для языка оболочки ОС:*
```
python visualizer.py config.yaml
```
*Комманда для установки тестирующей библиотеки pytest:*
```
pip install pytest
```
*Комманда для запуска тестов:*
```
python -m pytest
```

## Примеры использования

![примеры использования](https://github.com/user-attachments/assets/9c79ccae-668c-4d14-b8ef-7d0b2d1339d8)

## Результаты прогона тестов

![результаты прогона тестов](https://github.com/user-attachments/assets/67289c94-d58b-48b4-92a3-7150ff77d099)
