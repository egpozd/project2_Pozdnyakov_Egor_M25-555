import time
from functools import wraps


def handle_db_errors(func):
    """
    Декоратор для обработки ошибок базы данных.
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except FileNotFoundError:
            return False, (
                "Ошибка: Файл данных не найден. "
                "Возможно, база данных не инициализирована."
            )
        except KeyError as e:
            return False, f"Ошибка: Таблица или столбец {e} не найден."
        except ValueError as e:
            return False, f"Ошибка валидации: {e}"
        except Exception as e:
            return False, f"Произошла непредвиденная ошибка: {e}"
    return wrapper


def confirm_action(action_name):
    """
    Декоратор для подтверждения опасных операций.
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Для функций в core.py, первый аргумент - metadata, второй - table_name
            table_name = args[1] if len(args) > 1 else "неизвестная таблица"
            
            response = input(
                f'Вы уверены, что хотите выполнить "{action_name}" '
                f'для таблицы "{table_name}"? [y/N]: '
            )
            if response.lower() not in ['y', 'yes', 'д', 'да']:
                return False, "Операция отменена пользователем."
            
            return func(*args, **kwargs)
        return wrapper
    return decorator


def log_time(func):
    """
    Декоратор для замера времени выполнения функции.
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.monotonic()
        result = func(*args, **kwargs)
        end_time = time.monotonic()
        execution_time = end_time - start_time
        
        print(f"Функция {func.__name__} выполнилась за {execution_time:.3f} секунд")
        return result
    return wrapper


def create_cacher():
    """
    Фабрика для создания замыкания с кэшем.
    """
    cache = {}
    
    def cache_result(key, value_func):
        """
        Внутренняя функция для кэширования результатов.
        """
        if key in cache:
            return cache[key]
        
        result = value_func()
        cache[key] = result
        return result
    
    return cache_result