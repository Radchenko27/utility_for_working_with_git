#Первый запуск Утилиты

##Шаг №1
Скачайте удаленный репозиторий  на локальную машину.
```
git clone https://github.com/Radchenko27/utility_for_working_with_git
```

##Шаг №2
Установите виртуальное окружение для проекта
```
python -m venv venv
```

##Шаг №3
Активируйте его
```
.\venv\Scripts\activate
```

##Шаг №4
Скачайте необходимые библиотеки из файла requirements.txt
```
pip install -r requiremets.txt
```

##Шаг №5
Предполагается, что у вас на локальной машине уже есть репозиторий, для которого применима данная утилита. Запуск происходит при помощи команды:
```
python main.py <путь к репозиторию> <хеш коммита №1> <хеш коммита №2>
```

