import shlex

import prompt

from .core import (
    create_table,
    drop_table,
    info_table,
    insert,
    list_tables,
    select,
    update,
    delete,
)
from .parser import parse_set_clause, parse_where_condition, parse_values_list
from .utils import load_metadata, save_metadata


def print_help():
    """Печатает справочную информацию."""
    print("\n***Операции с данными***")
    print("Функции:")
    print("<command> insert into <имя_таблицы> values (<значение1>, ...) - создать запись")
    print("<command> select from <имя_таблицы> [where <условие>] - прочитать записи")
    print("<command> update <имя_таблицы> set <столбец=значение> [where <условие>] - обновить запись")
    print("<command> delete from <имя_таблицы> [where <условие>] - удалить запись")
    print("<command> info <имя_таблицы> - вывести информацию о таблице")
    print("<command> create_table <имя_таблицы> <столбец1:тип> .. - создать таблицу")
    print("<command> list_tables - показать список всех таблиц")
    print("<command> drop_table <имя_таблицы> - удалить таблицу")
    print("<command> exit - выход из программы")
    print("<command> help - справочная информация\n")


def run():
    """Основной цикл программы."""
    print("***Операции с данными***")
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
                
            elif command == 'insert':
                if len(args) < 4 or args[0].lower() != 'into' or args[2].lower() != 'values':
                    print("Ошибка: Неверный формат команды INSERT")
                    print("Использование: insert into <таблица> values (<значение1>, <значение2>, ...)")
                    continue
                
                table_name = args[1]
                values_str = ' '.join(args[3:])
                
                try:
                    values = parse_values_list(values_str)
                    success, message = insert(metadata, table_name, values)
                    print(message)
                except Exception as e:
                    print(f"Ошибка: {e}")
                    
            elif command == 'select':
                if len(args) < 2 or args[0].lower() != 'from':
                    print("Ошибка: Неверный формат команды SELECT")
                    print("Использование: select from <таблица> [where <условие>]")
                    continue
                
                table_name = args[1]
                where_clause = None
                
                # Обрабатываем условие WHERE если есть
                if len(args) > 3 and args[2].lower() == 'where':
                    where_str = ' '.join(args[3:])
                    try:
                        where_clause = parse_where_condition(where_str)
                    except Exception as e:
                        print(f"Ошибка в условии WHERE: {e}")
                        continue
                
                success, result = select(metadata, table_name, where_clause)
                if success:
                    if isinstance(result, str):
                        print(result)
                    else:
                        print(result)
                else:
                    print(result)
                    
            elif command == 'update':
                if len(args) < 4 or args[1].lower() != 'set':
                    print("Ошибка: Неверный формат команды UPDATE")
                    print("Использование: update <таблица> set <столбец=значение> [where <условие>]")
                    continue
                
                table_name = args[0]
                set_str = ' '.join(args[2:])
                
                # Разделяем SET и WHERE части
                where_index = set_str.lower().find(' where ')
                if where_index != -1:
                    set_clause_str = set_str[:where_index]
                    where_str = set_str[where_index + 7:]
                else:
                    set_clause_str = set_str
                    where_str = None
                
                try:
                    set_clause = parse_set_clause(set_clause_str)
                    where_clause = parse_where_condition(where_str) if where_str else None
                    
                    success, message = update(metadata, table_name, set_clause, where_clause)
                    print(message)
                except Exception as e:
                    print(f"Ошибка: {e}")
                    
            elif command == 'delete':
                if len(args) < 2 or args[0].lower() != 'from':
                    print("Ошибка: Неверный формат команды DELETE")
                    print("Использование: delete from <таблица> [where <условие>]")
                    continue
                
                table_name = args[1]
                where_clause = None
                
                # Обрабатываем условие WHERE если есть
                if len(args) > 3 and args[2].lower() == 'where':
                    where_str = ' '.join(args[3:])
                    try:
                        where_clause = parse_where_condition(where_str)
                    except Exception as e:
                        print(f"Ошибка в условии WHERE: {e}")
                        continue
                
                success, message = delete(metadata, table_name, where_clause)
                print(message)
                
            elif command == 'info':
                if len(args) != 1:
                    print("Ошибка: Неверное количество аргументов")
                    print("Использование: info <имя_таблицы>")
                    continue
                
                table_name = args[0]
                success, message = info_table(metadata, table_name)
                print(message)
                
            else:
                print(f"Функции '{command}' нет. Попробуйте снова.")
                
        except Exception as e:
            print(f"Произошла ошибка: {e}")
            print("Попробуйте снова.")


def welcome():
    """Старая функция приветствия - оставляем для обратной совместимости"""
    run()