# Тестовое задание на позицию backend разработчика

Как запустить:
1. docker-compose up
2. cd backend
3. python3 -m venv env
4. source env/bin/activate
5. pip install -r requirements.txt
6. cd assignment
7. python manage.py migrate
8. python manage.py loaddata checks/fixtures/initial.yaml
9. python manage.py runserver
10. python manage.py rqworker
