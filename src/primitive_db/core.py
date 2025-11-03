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
    
    success_msg = (
        f'Таблица "{table_name}" успешно создана '
        f'со столбцами: {", ".join(table_columns)}'
    )
    return True, success_msg


def drop_table(metadata, table_name):
    """
    Удаляет таблицу из метаданных.
    """
    if table_name not in metadata:
        return False, f'Таблица "{table_name}" не существует.'
    
    del metadata[table_name]
    return True, f'Таблица "{table_name}" успешно удалена.'


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