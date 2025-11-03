from prettytable import PrettyTable

from .decorators import confirm_action, create_cacher, handle_db_errors, log_time
from .utils import load_table_data, save_table_data

# Создаем кэшер для результатов запросов
cache_result = create_cacher()

# Поддерживаемые типы данных
SUPPORTED_TYPES = {'int', 'str', 'bool'}


def validate_column_definition(column_def):
    """
    Проверяет корректность определения столбца.
    Формат: "название:тип"
    """
    if ':' not in column_def:
        return False, f"Некорректный формат столбца: {column_def}"
    
    name, col_type = column_def.split(':', 1)
    if not name.strip():
        return False, "Имя столбца не может быть пустым"
    
    if col_type not in SUPPORTED_TYPES:
        error_msg = (
            f"Неподдерживаемый тип данных: {col_type}. "
            f"Поддерживаемые типы: {', '.join(SUPPORTED_TYPES)}"
        )
        return False, error_msg
    
    return True, (name.strip(), col_type)


@handle_db_errors
def create_table(metadata, table_name, columns):
    """
    Создает новую таблицу в метаданных.
    Автоматически добавляет столбец ID:int.
    """
    # Проверяем, существует ли таблица
    if table_name in metadata:
        return False, f'Таблица "{table_name}" уже существует.'
    
    # Проверяем корректность имени таблицы
    if not table_name or not table_name.strip():
        return False, "Имя таблицы не может быть пустым"
    
    # Автоматически добавляем столбец ID
    table_columns = ['ID:int']
    
    # Обрабатываем пользовательские столбцы
    for column_def in columns:
        is_valid, result = validate_column_definition(column_def)
        if not is_valid:
            return False, result
        column_name, column_type = result
        table_columns.append(f"{column_name}:{column_type}")
    
    # Добавляем таблицу в метаданные
    metadata[table_name] = {
        'columns': table_columns
    }
    
    # Создаем пустой файл данных для таблицы
    save_table_data(table_name, [])
    
    success_msg = (
        f'Таблица "{table_name}" успешно создана '
        f'со столбцами: {", ".join(table_columns)}'
    )
    return True, success_msg


@handle_db_errors
@confirm_action("удаление таблицы")
def drop_table(metadata, table_name):
    """
    Удаляет таблицу из метаданных.
    """
    if table_name not in metadata:
        return False, f'Таблица "{table_name}" не существует.'
    
    del metadata[table_name]
    return True, f'Таблица "{table_name}" успешно удалена.'


@handle_db_errors
def list_tables(metadata):
    """
    Возвращает список всех таблиц.
    """
    if not metadata:
        return "Нет созданных таблиц."
    
    tables = list(metadata.keys())
    if len(tables) == 1:
        return f"- {tables[0]}"
    else:
        return "\n".join([f"- {table}" for table in tables])


@handle_db_errors
def validate_data_types(metadata, table_name, values):
    """
    Проверяет соответствие типов данных значениям.
    """
    table_meta = metadata[table_name]
    columns = table_meta['columns']
    
    # Пропускаем ID столбец (он первый)
    data_columns = columns[1:]
    
    if len(values) != len(data_columns):
        return False, (
            f"Неверное количество значений. Ожидается {len(data_columns)}, "
            f"получено {len(values)}"
        )
    
    for i, (column_def, value) in enumerate(zip(data_columns, values)):
        col_name, col_type = column_def.split(':')
        
        # Проверяем тип
        if col_type == 'int' and not isinstance(value, int):
            return False, f"Столбец '{col_name}' должен быть типа int"
        elif col_type == 'str' and not isinstance(value, str):
            return False, f"Столбец '{col_name}' должен быть типа str"
        elif col_type == 'bool' and not isinstance(value, bool):
            return False, f"Столбец '{col_name}' должен быть типа bool"
    
    return True, "OK"


@handle_db_errors
@log_time
def insert(metadata, table_name, values):
    """
    Вставляет новую запись в таблицу.
    """
    if table_name not in metadata:
        return False, f'Таблица "{table_name}" не существует.'
    
    # Загружаем данные таблицы
    table_data = load_table_data(table_name)
    
    # Валидируем типы данных
    is_valid, message = validate_data_types(metadata, table_name, values)
    if not is_valid:
        return False, message
    
    # Генерируем ID
    if table_data:
        new_id = max(record['ID'] for record in table_data) + 1
    else:
        new_id = 1
    
    # Создаем запись
    record = {'ID': new_id}
    columns = metadata[table_name]['columns'][1:]  # Пропускаем ID
    
    for i, column_def in enumerate(columns):
        col_name = column_def.split(':')[0]
        record[col_name] = values[i]
    
    # Добавляем запись
    table_data.append(record)
    
    # Сохраняем данные
    save_table_data(table_name, table_data)
    
    return True, (
        f'Запись с ID={new_id} успешно добавлена в таблицу "{table_name}".'
    )


@handle_db_errors
@log_time
def select(metadata, table_name, where_clause=None):
    """
    Выбирает записи из таблицы.
    """
    if table_name not in metadata:
        return False, f'Таблица "{table_name}" не существует.'
    
    # Создаем ключ для кэша
    cache_key = f"select_{table_name}_{str(where_clause)}"
    
    def _select_data():
        # Загружаем данные таблицы
        table_data = load_table_data(table_name)
        
        if not table_data:
            return True, "Таблица пуста."
        
        # Фильтруем данные если есть условие
        if where_clause:
            filtered_data = []
            for record in table_data:
                match = True
                for column, value in where_clause.items():
                    if record.get(column) != value:
                        match = False
                        break
                if match:
                    filtered_data.append(record)
            
            if not filtered_data:
                return True, "Записей, удовлетворяющих условию, не найдено."
            table_data = filtered_data
        
        # Создаем красивую таблицу для вывода
        columns = [col.split(':')[0] for col in metadata[table_name]['columns']]
        table = PrettyTable()
        table.field_names = columns
        
        for record in table_data:
            row = [record.get(col, '') for col in columns]
            table.add_row(row)
        
        return True, table
    
    # Используем кэш для одинаковых запросов
    return cache_result(cache_key, _select_data)


@handle_db_errors
def update(metadata, table_name, set_clause, where_clause):
    """
    Обновляет записи в таблице.
    """
    if table_name not in metadata:
        return False, f'Таблица "{table_name}" не существует.'
    
    # Загружаем данные таблицы
    table_data = load_table_data(table_name)
    
    if not table_data:
        return False, "Таблица пуста."
    
    # Проверяем, что столбцы из SET существуют
    table_columns = [col.split(':')[0] for col in metadata[table_name]['columns']]
    for column in set_clause.keys():
        if column not in table_columns:
            return False, (
                f'Столбец "{column}" не существует в таблице "{table_name}".'
            )
    
    # Находим и обновляем записи
    updated_count = 0
    for record in table_data:
        match = True
        if where_clause:
            for column, value in where_clause.items():
                if record.get(column) != value:
                    match = False
                    break
        
        if match:
            updated_count += 1
            for column, new_value in set_clause.items():
                record[column] = new_value
    
    if updated_count == 0:
        return False, "Записей, удовлетворяющих условию, не найдено."
    
    # Сохраняем данные
    save_table_data(table_name, table_data)
    
    return True, (
        f'{updated_count} запись(ей) успешно обновлено в таблице "{table_name}".'
    )


@handle_db_errors
@confirm_action("удаление записей")
def delete(metadata, table_name, where_clause):
    """
    Удаляет записи из таблицы.
    """
    if table_name not in metadata:
        return False, f'Таблица "{table_name}" не существует.'
    
    # Загружаем данные таблицы
    table_data = load_table_data(table_name)
    
    if not table_data:
        return False, "Таблица пуста."
    
    # Фильтруем записи для удаления
    if where_clause:
        filtered_data = []
        deleted_count = 0
        
        for record in table_data:
            match = True
            for column, value in where_clause.items():
                if record.get(column) != value:
                    match = False
                    break
            
            if not match:
                filtered_data.append(record)
            else:
                deleted_count += 1
        
        if deleted_count == 0:
            return False, "Записей, удовлетворяющих условию, не найдено."
        
        table_data = filtered_data
    else:
        # Если нет условия, удаляем все
        deleted_count = len(table_data)
        table_data = []
    
    # Сохраняем данные
    save_table_data(table_name, table_data)
    
    return True, (
        f'{deleted_count} запись(ей) успешно удалено из таблице "{table_name}".'
    )


@handle_db_errors
def info_table(metadata, table_name):
    """
    Выводит информацию о таблице.
    """
    if table_name not in metadata:
        return False, f'Таблица "{table_name}" не существует.'
    
    # Загружаем данные таблицы для подсчета записей
    table_data = load_table_data(table_name)
    record_count = len(table_data)
    
    table_meta = metadata[table_name]
    columns_str = ", ".join(table_meta['columns'])
    
    info_msg = (
        f"Таблица: {table_name}\n"
        f"Столбцы: {columns_str}\n"
        f"Количество записей: {record_count}"
    )
    
    return True, info_msg