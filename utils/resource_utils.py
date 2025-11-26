import sys
import os

def get_resource_path(relative_path):
    """
    Получает абсолютный путь к ресурсу (иконки, переводы).
    Работает и для dev-режима, и для PyInstaller (--onefile).
    """
    try:
        # PyInstaller создает временную папку и хранит путь в _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        # Если запускаем как обычный скрипт
        base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    return os.path.join(base_path, relative_path)

def get_external_path(filename):
    """
    Получает путь к файлу, который должен лежать РЯДОМ с исполняемым файлом
    (config.ini, logs).
    """
    # sys.argv[0] указывает на запущенный скрипт или exe файл
    base_path = os.path.dirname(os.path.abspath(sys.argv[0]))
    return os.path.join(base_path, filename)