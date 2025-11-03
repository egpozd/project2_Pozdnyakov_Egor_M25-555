import shlex

import prompt

from .core import create_table, drop_table, list_tables
from .utils import load_metadata, save_metadata


def print_help():
    """Печатает справочную информацию."""
    print("\n***База данных***")
    print("Функции:")
    print("<command> create_table <имя_таблицы> <столбец1:тип> .. - создать таблицу")
    print("<command> list_tables - показать список всех таблиц")
    print("<command> drop_table <имя_таблицы> - удалить таблицу")
    print("<command> exit - выход из программы")
    print("<command> help - справочная информация\n")


def run():
    """Основной цикл программы."""
    print("***База данных***")
    print_help()
    
    while True:
        try:
            user_input = prompt.string("Введите команду: ")
            if not user_input.strip():
                continue
                
            # Разбиваем ввод на команду и аргументы
            parts = shlex.split(user_input)
            command = parts[0].lower()
            args = parts[1:]
            
            # Загружаем актуальные метаданные
            metadata = load_metadata()
            
            if command == 'exit':
                print("Выход из программы.")
                break
                
            elif command == 'help':
                print_help()
                
            elif command == 'create_table':
                if len(args) < 1:
                    error_msg = (
                        "Ошибка: Недостаточно аргументов. "
                        "Использование: create_table <имя_таблицы> [столбцы...]"
                    )
                    print(error_msg)
                    continue
                
                table_name = args[0]
                columns = args[1:]
                
                success, message = create_table(metadata, table_name, columns)
                print(message)
                
                if success:
                    save_metadata(metadata)
                    
            elif command == 'drop_table':
                if len(args) != 1:
                    error_msg = (
                        "Ошибка: Неверное количество аргументов. "
                        "Использование: drop_table <имя_таблицы>"
                    )
                    print(error_msg)
                    continue
                
                table_name = args[0]
                success, message = drop_table(metadata, table_name)
                print(message)
                
                if success:
                    save_metadata(metadata)
                    
            elif command == 'list_tables':
                result = list_tables(metadata)
                print(result)
                
            else:
                print(f"Функции '{command}' нет. Попробуйте снова.")
                
        except Exception as e:
            print(f"Произошла ошибка: {e}")
            print("Попробуйте снова.")


def welcome():
    """Старая функция приветствия - оставляем для обратной совместимости"""
    run()