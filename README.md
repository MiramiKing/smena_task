# Тестовое задание на позицию backend разработчика

Как развернуть:
1. Для докера `docker-compose up`
2. Для создания окружения введите поселдовательно:<br/>
`cd backend`<br/>
`python3 -m venv env`<br/> 
`source env/bin/activate`<br/> 
`pip install -r requirements.txt`
3. `cd assignment`
4. Для django проведите миграции `python manage.py migrate`
5. Если необходимо, заполните БД начальными данными `python manage.py loaddata checks/fixtures/initial.yaml`
6. Запустите сервер `python manage.py runserver`
7. Запустите очередь задач `python manage.py rqworker`
8. Для доступа к панели администратора создайте пользователя `python manage.py createsuperuser`
