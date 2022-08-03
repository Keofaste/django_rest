# Тестовое задание на позицию 'Backend developer (Python)'

## Задание
Написать сервис на Python, который имеет 3 REST ендпоинта:

* получает по HTTP имя CSV-файла (пример файла во вложении) в хранилище 
и суммирует каждый 10й столбец
* показывает количество задач на вычисление, которые на текущий момент в работе
* принимает ID задачи из п.1 и отображает результат в JSON-формате

Сервис должен поддерживать обработку нескольких задач от одного клиента
одновременно.

Сервис должен иметь возможность горизонтально масштабироваться и загружать
данные из AWS S3 и/или с локального диска.

Количество строк в csv может достигать 3*10^6.

Подключение к хранилищу может работать нестабильно.


## Описание API

* PUT /tasks/ - создание задачи на вычисление
* GET /tasks/active_tasks_count - получение количества активных задач
* GET /tasks/{task_id}/results - получение результата вычислений


## Как запустить

1. `make build`
2. `make run`
3. `docker cp <localfile> dj_rest:/home/app/data/csv/`
   1. [тестовый файл](data/test.csv)
4. Создать пользователя:
   1. `docker exec -it dj_rest bash`
   2. `poetry run python manage.py createsuperuser`
5. войти через [админку](http://127.0.0.1/admin/)
6. подёргать API можно [тут](http://127.0.0.1/tasks)


## Заметки 

1. В первую очередь я бы уточнил что значит каждый десятый столбец, ведь это 
можно понять по-разному. Но было сказано, что всё на моё усмотрение. 
Поэтому решил суммировать колонки, а не строки, к примеру. 
На выходе список сумм по каждому 10-му столбцу.
2. Достаточно странный формат в примере файла с разделителем в виде '","'. 
3. Добавить поддержку S3 не успел
