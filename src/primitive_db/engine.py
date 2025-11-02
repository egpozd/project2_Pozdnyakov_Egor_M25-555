import prompt

def welcome():
    print("Добро пожаловать в Primitive DB!")
    
    # Запрашиваем имя пользователя
    name = prompt.string('May I have your name? ')
    print(f"Привет, {name}!")
    
    print("\n***")
    print("<command> exit - выйти из программы")
    print("<command> help - справочная информация")
    
    while True:
        command = prompt.string("Введите команду: ")
        if command == "exit":
            print(f"До свидания, {name}!")
            break
        elif command == "help":
            print("<command> exit - выйти из программы")
            print("<command> help - справочная информация")
        else:
            print(f"Неизвестная команда: {command}")