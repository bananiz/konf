import os
import tarfile
import sys
import tkinter as tk
from tkinter import scrolledtext


class ShellEmulator:
    def __init__(self, username, fs_path, init_script):
        self.username = username
        self.cwd = "/tmp/virtual_fs"  # Установим начальную директорию
        self.fs_path = fs_path
        self.init_script = init_script
        self.check_or_create_filesystem()
        self.run_script(init_script)

    def check_or_create_filesystem(self):
        """Проверяет существование файловой системы и создаёт её, если не существует."""
        if not os.path.exists(self.fs_path):
            print(f"Файловая система не найдена. Создание {self.fs_path}...")
            self.create_filesystem()
        else:
            self.load_filesystem(self.fs_path)

    def create_filesystem(self):
        """Создаёт виртуальную файловую систему и сохраняет её в tar-файл."""
        # Пример создания файловой структуры
        os.makedirs("/tmp/virtual_fs/some_directory", exist_ok=True)
        os.makedirs("/tmp/virtual_fs/another_directory", exist_ok=True)

        with open("/tmp/virtual_fs/some_directory/some_file.txt", "w") as f:
            f.write("Это тестовый файл.")

        with open("/tmp/virtual_fs/some_directory/another_file.txt", "w") as f:
            f.write("Это еще один тестовый файл.")

        with open("/tmp/virtual_fs/another_directory/file_in_another_directory.txt", "w") as f:
            f.write("Это файл в другой директории.")

        # Создание tar-файла
        with tarfile.open(self.fs_path, "w") as tar:
            tar.add("/tmp/virtual_fs", arcname=os.path.basename("/tmp/virtual_fs"))

        print(f"Файловая система успешно создана в {self.fs_path}")

    def load_filesystem(self, fs_path):
        """Загружает виртуальную файловую систему из tar-файла."""
        with tarfile.open(fs_path) as tar:
            tar.extractall("/tmp/virtual_fs")
        print(f"Файловая система загружена из {fs_path}")

    def run_script(self, script_path):
        """Запускает начальный скрипт."""
        if not os.path.exists(script_path):
            print(f"Скрипт {script_path} не найден. Пропуск выполнения.")
            return

        with open(script_path, 'r') as f:
            commands = f.readlines()
        for command in commands:
            command = command.strip()
            if command.startswith("#") or not command:
                continue  # Игнорируем комментарии и пустые строки
            self.run_command(command)

    def run_command(self, command):
        """Выполняет команды."""
        if command.startswith("ls"):
            return self.ls()
        elif command.startswith("cd"):
            return self.cd(command.split()[1])
        elif command.startswith("exit"):
            sys.exit()
        elif command.startswith("find"):
            return self.find(command.split()[1])
        elif command.startswith("chown"):
            return self.chown(command.split()[1], command.split()[2])
        else:
            return f"Команда {command} не поддерживается"

    def ls(self):
        """Реализация команды ls."""
        return "\n".join(os.listdir(self.cwd))

    def cd(self, path):
        """Реализация команды cd."""
        new_path = os.path.join(self.cwd, path)
        if os.path.exists(new_path):
            self.cwd = new_path
            return f"Перемещено в {self.cwd}"
        else:
            return f"Путь {new_path} не найден"

    def find(self, name):
        """Реализация команды find."""
        results = []
        for root, dirs, files in os.walk(self.cwd):
            if name in files or name in dirs:
                results.append(os.path.join(root, name))
        return "\n".join(results) if results else "Файл или каталог не найден."

    def chown(self, owner, path):
        """Реализация команды chown."""
        full_path = os.path.join(self.cwd, path)
        if os.path.exists(full_path):
            return f"Изменен владелец {full_path} на {owner}"
        else:
            return f"Файл или каталог {full_path} не найден"


class GUI:
    def __init__(self, emulator):
        self.emulator = emulator
        self.window = tk.Tk()
        self.window.title("Shell Emulator")

        self.output_area = scrolledtext.ScrolledText(self.window, width=80, height=20)
        self.output_area.pack()

        self.input_area = tk.Entry(self.window, width=80)
        self.input_area.pack()
        self.input_area.bind("<Return>", self.process_command)

        self.output_area.insert(tk.END, f"{self.emulator.username}@emulator:~$ ")
        self.output_area.see(tk.END)

    def process_command(self, event):
        command = self.input_area.get()
        self.input_area.delete(0, tk.END)
        if command.strip():  # Игнорируем пустые команды
            output = self.emulator.run_command(command)
            self.output_area.insert(tk.END, f"{command}\n{output}\n")
            self.output_area.insert(tk.END, f"{self.emulator.username}@emulator:~$ ")
            self.output_area.see(tk.END)

    def run(self):
        self.window.mainloop()


def main():
    import csv
    # Чтение конфигурации из CSV
    with open('config.csv', newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            emulator = ShellEmulator(row['username'], row['virtual_fs'], row['initial_script'])
            gui = GUI(emulator)
            gui.run()


if __name__ == "__main__":
    main()
