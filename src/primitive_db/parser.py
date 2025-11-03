import shlex


def parse_where_condition(where_clause):
    """
    Парсит условие WHERE в формате "столбец = значение".
    Возвращает словарь {column: value}.
    """
    if not where_clause:
        return None
    
    try:
        # Разбиваем на части
        parts = shlex.split(where_clause)
        if len(parts) != 3 or parts[1] != '=':
            raise ValueError("Некорректный формат условия WHERE")
        
        column = parts[0]
        value_str = parts[2]
        
        # Пробуем преобразовать значение
        value = parse_value(value_str)
        
        return {column: value}
    except Exception as e:
        raise ValueError(f"Ошибка парсинга условия WHERE: {e}")


def parse_set_clause(set_clause):
    """
    Парсит условие SET в формате "столбец1 = значение1, столбец2 = значение2".
    Возвращает словарь {column: value}.
    """
    if not set_clause:
        return {}
    
    try:
        result = {}
        # Разбиваем по запятым, но учитываем кавычки
        parts = shlex.split(set_clause)
        
        i = 0
        while i < len(parts):
            if i + 2 < len(parts) and parts[i + 1] == '=':
                column = parts[i]
                value_str = parts[i + 2]
                value = parse_value(value_str)
                result[column] = value
                i += 3
            else:
                raise ValueError("Некорректный формат условия SET")
            
            # Пропускаем запятую, если есть
            if i < len(parts) and parts[i] == ',':
                i += 1
        
        return result
    except Exception as e:
        raise ValueError(f"Ошибка парсинга условия SET: {e}")


def parse_value(value_str):
    """
    Парсит строковое значение в соответствующий тип.
    """
    # Удаляем кавычки если есть
    if (value_str.startswith('"') and value_str.endswith('"')) or \
       (value_str.startswith("'") and value_str.endswith("'")):
        return value_str[1:-1]
    
    # Булевы значения
    if value_str.lower() == 'true':
        return True
    elif value_str.lower() == 'false':
        return False
    
    # Числовые значения
    try:
        return int(value_str)
    except ValueError:
        pass
    
    # Если не число и не булево, возвращаем как строку
    return value_str


def parse_values_list(values_str):
    """
    Парсит список значений в формате "(значение1, значение2, ...)".
    """
    # Удаляем скобки если есть
    if values_str.startswith('(') and values_str.endswith(')'):
        values_str = values_str[1:-1]
    
    try:
        # Разбиваем с учетом кавычек
        parts = shlex.split(values_str.replace(',', ' '))
        return [parse_value(part) for part in parts]
    except Exception as e:
        raise ValueError(f"Ошибка парсинга списка значений: {e}")