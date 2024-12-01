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
**1. __init__(self, hostname, tar_path, startup_script)**

```
def __init__(self, hostname, tar_path, startup_script):
    self.hostname = hostname
    self.tar_path = tar_path
    self.current_path = '/'
    self.filesystem = {}
    self.load_filesystem(tar_path)
    self.setup_gui()
    self.execute_startup_script(startup_script)
```

*Описание:*

Конструктор класса, который инициализирует основные параметры, загружает файловую систему из tar-архива, настраивает графический интерфейс и выполняет стартовый скрипт.

**2. load_filesystem(self, tar_path)**
```
def load_filesystem(self, tar_path):
    with tarfile.open(tar_path, 'r') as tar:
        for member in tar.getmembers():
            self.filesystem[member.name] = member
```

*Описание:*

Загружает содержимое tar-архива в словарь filesystem, где ключами являются имена файлов и директорий.

**3. setup_gui(self)**
```
def setup_gui(self):
    self.root = tk.Tk()
    self.root.title(f"{self.hostname} Shell Emulator")
    
    self.text_area = scrolledtext.ScrolledText(self.root, wrap=tk.WORD)
    self.text_area.pack(expand=True, fill='both')
    
    self.entry = tk.Entry(self.root)
    self.entry.bind("<Return>", self.process_command)
    self.entry.pack(fill='x')
    
    self.prompt()
```

*Описание:*

Настраивает графический интерфейс приложения, включая текстовое поле для вывода и поле ввода для команд.

**4. prompt(self)**
```
def prompt(self):
    self.entry.delete(0, tk.END)
    self.entry.insert(0, f"{self.hostname}:{self.current_path}$ ")
```

*Описание:*

Устанавливает текст приглашения в поле ввода, показывая имя хоста и текущий путь.

**5. process_command(self, event)**
```
def process_command(self, event):
    command = self.entry.get()
    self.text_area.insert(tk.END, f"{command}\n")
    self.entry.delete(0, tk.END)
    if (command.find("$")):
        command = command[command.find(" ") + 1:]
        
    if command.startswith("ls"):
        self.ls()
    elif command.startswith("cd"):
        self.cd(command)
    elif command.startswith("head"):
        self.head(command)
    elif command.startswith("find"):
        self.find(command)
    elif command == "exit":
        self.root.quit()
    else:
        self.text_area.insert(tk.END, "Command not found\n")
    
    self.prompt()
```

*Описание:*

Обрабатывает введенные пользователем команды, определяет, какую команду выполнять, и вызывает соответствующий метод.

**6. ls(self)**
```
def ls(self):
    if (self.current_path == '/'):
        files1 = [name for name in self.filesystem if name.startswith("")]
        files = []
        for f in files1:
            if(f.find("/") == -1):
                files.append(f)
                continue
            if (not(f[:f.find("/")] in files)):
                files.append(f[:f.find("/")])
    else:
        files = [name for name in self.filesystem if name.startswith(self.current_path)]
        files1 = []
        for f in files:
            if (f != self.current_path):
                files1.append(f[len(self.current_path) + 1:])
        files.clear()
        for f in files1:
            if(f.find("/") == -1):
                files.append(f)
    self.text_area.insert(tk.END, "\n".join(files) + "\n")
```

*Описание:*

Выводит список файлов и директорий в текущем каталоге.

**7. cd(self, command)**
```
def cd(self, command):
    if (command.count(" ") == 1):
        _, path = command.split()
        if path in self.filesystem:
            self.current_path = path
        elif self.current_path + "/" + path in self.filesystem:
            self.current_path += "/" + path
        elif path == "../":
            self.current_path = self.current_path[:len(self.current_path) - 1 - self.current_path.rfind('/')]
        else:
            flag = False
            for f in self.filesystem:
                if path == f[:f.find("/")]:
                    self.current_path = path
                    flag = True
            if flag == False:
                self.text_area.insert(tk.END, "No such directory\n")
    else:
        self.current_path = '/'
```

*Описание:*

Изменяет текущий каталог на указанный пользователем.

**8. head(self, command)**
```
def head(self, command):
    _, file_name = command.split()
    if file_name in self.filesystem:
        member = self.filesystem[file_name]
        with tarfile.open(self.tar_path, 'r') as tar:
            f = tar.extractfile(member)
            lines = f.readlines()[:10]
            self.text_area.insert(tk.END, ''.join([line.decode() for line in lines]))
    elif self.current_path + "/" + file_name in self.filesystem:
        member = self.filesystem[self.current_path + "/" + file_name]
        with tarfile.open(self.tar_path, 'r') as tar:
            f = tar.extractfile(member)
            lines = f.readlines()[:10]
            self.text_area.insert(tk.END, ''.join([line.decode() for line in lines]))
    else:
        self.text_area.insert(tk.END, "No such file\n")
```

*Описание:*

Выводит первые 10 строк указанного файла.

**9. find(self, command)**
```
def find(self, command):
    _, search_term = command.split()
    found_files = [name for name in self.filesystem.keys() if (search_term in name and not(search_term + "/" in name))]
    self.text_area.insert(tk.END, "\n".join(found_files) + "\n")
```

*Описание:*

Ищет файлы по заданной строке и выводит их имена.

**10. execute_startup_script(self, startup_script)**
```
def execute_startup_script(self, startup_script):
    if os.path.exists(startup_script):
        with open(startup_script, 'r') as file:
            for line in file:
                self.entry.insert(len(self.current_path) + len(self.hostname) + 5, line.strip())
                self.process_command(line.strip())
```

*Описание:*

Выполняет команды из стартового скрипта, если он существует.

**11. run(self)**
```
def run(self):
    self.root.mainloop()
Описание: Запускает главный цикл приложения Tkinter.
Ссылки: Вызывается в if __name__ == "__main__": для запуска эмулятора.
12. if __name__ == "__main__":
if __name__ == "__main__":
    import sys
    if len(sys.argv) != 4:
        print("Usage: python shell_emulator.py <hostname> <tar_path> <startup_script>")
        sys.exit(1)

    hostname = sys.argv[1]
    tar_path = sys.argv[2]
    startup_script = sys.argv[3]
    emulator = ShellEmulator(hostname, tar_path, startup_script)
    emulator.run()
```
*Описание:*

Проверяет, что скрипт запущен с правильным количеством аргументов, и инициализирует экземпляр ShellEmulator.

## Сборка проекта

*Комманда для запуска эмулятора для языка оболочки ОС:*
```
python shell_emulator.py hostname my_filesystem.tar startup_script.txt
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

![примеры использования](https://github.com/user-attachments/assets/7339ae38-9202-489f-8f8c-7a4a0d868b72)

## Результаты прогона тестов

![результаты прогона тестов](https://github.com/user-attachments/assets/37941382-b04e-4edb-8c4d-b9e1911016ba)
