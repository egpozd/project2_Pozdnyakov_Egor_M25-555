import json


def load_metadata(filepath="db_meta.json"):
    """
    Загружает метаданные из JSON-файла.
    Если файл не найден, возвращает пустой словарь.
    """
    try:
        with open(filepath, 'r', encoding='utf-8') as file:
            return json.load(file)
    except FileNotFoundError:
        return {}


def save_metadata(data, filepath="db_meta.json"):
    """
    Сохраняет метаданные в JSON-файл.
    """
    with open(filepath, 'w', encoding='utf-8') as file:
        json.dump(data, file, ensure_ascii=False, indent=2)