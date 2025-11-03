# Primitive Database

Простая консольная база данных на Python.

## Демонстрация

[![asciicast](https://asciinema.org/a/0D6zKWmoHuScLwMi956ZBcBwI.svg)](https://asciinema.org/a/0D6zKWmoHuScLwMi956ZBcBwI)

*Посмотрите демонстрацию работы всех функций базы данных*

## Пример использования

```bash
# Создание таблицы
create_table users name:str age:int is_active:bool

# Добавление записей  
insert into users values ("Алексей", 28, true)

# Выборка данных
select from users
select from users where age = 28

# Обновление записей
update users set age = 29 where name = "Алексей"

# Удаление записей
delete from users where is_active = false

# Информация о таблице
info users