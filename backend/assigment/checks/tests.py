from django.test import TestCase
from .models import Check, Printer
from django.urls import reverse
import django_rq


def get_example_check_data():
    return {
        "id": 123456,
        "price": 780,
        "items": [
            {
                "name": "Вкусная пицца",
                "quantity": 2,
                "unit_price": 250
            },
            {
                "name": "Не менее вкусные роллы",
                "quantity": 1,
                "unit_price": 280
            }
        ],
        "address": "г. Уфа, ул. Ленина, д. 42",
        "client": {
            "name": "Иван",
            "phone": 9173332222
        },
        "point_id": 1
    }


def create_printers_one_point(point_id=1):
    Printer.objects.create(name='Chernyaga Power kitchen',
                           api_key='1',
                           check_type='kitchen',
                           point_id=point_id)
    Printer.objects.create(name='Chernyaga Power client',
                           api_key='2',
                           check_type='client',
                           point_id=point_id)


def empty_rq_queue():
    queue = django_rq.get_queue('default')
    queue.empty()


class NewCheckTest(TestCase):

    @classmethod
    def setUp(cls):
        create_printers_one_point()

    def test_new_checks_wrong_api_key(self):
        """
        Если передаётся неверный API ключ, ожидается ошибка 401
        """

        response = self.client.get(reverse('checks:new_checks'), {'api_key': 'nope'})

        self.assertEqual(response.status_code, 401)
        self.assertJSONEqual(
            str(response.content, encoding='utf-8'),
            {"error": "Ошибка авторизации"}
        )

    def test_new_checks_empty_result(self):
        """
        Если передается правильный API ключ и не было вызова create_checks, ожидается код 200 и пустой результат
        """

        response = self.client.get(reverse('checks:new_checks'), {'api_key': '1'})

        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(
            str(response.content, encoding='utf-8'),
            {'checks': []}
        )

    def test_new_checks_after_create_checks(self):
        """
        Если передается правильный API ключ и не было вызова create_checks, ожидается код 200 и непустой результат
        """

        queue = django_rq.get_queue('default')
        queue.empty()

        self.client.post(reverse('checks:create_checks'), data=get_example_check_data(),
                         content_type='application/json')

        django_rq.get_worker().work(burst=True)

        response = self.client.get(reverse('checks:new_checks'), {'api_key': '1'})

        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(
            str(response.content, encoding='utf-8'),
            {'checks': []}
        )


class CheckTests(TestCase):

    @classmethod
    def setUp(cls):
        create_printers_one_point()

    def test_new_checks_wrong_api_key(self):
        """
        Если передан неверный API ключ, ожидается код 401
        """

        response = self.client.get(reverse('checks:check'), {'api_key': 'no_such_key', 'check_id': 1})

        self.assertEqual(response.status_code, 401)
        self.assertJSONEqual(
            str(response.content, encoding='utf-8'),
            {"error": "Не существует принтера с таким api_key"}
        )

    def test_new_check_without_existing_check(self):
        """
        Если передан верный API ключ и check_id, которого нет, код 400 ошибка
        """

        response = self.client.get(reverse('checks:check'), {'api_key': '1', 'check_id': 1})

        self.assertEqual(response.status_code, 400)
        self.assertJSONEqual(
            str(response.content, encoding='utf8'),
            {"error": "Данного чека не существует"}
        )

    def test_check_status_new(self):
        """
        Если передан верный API ключ и check_id, для которого ешё не сгенерировался PDF файл, ожидается 400 код
        """

        empty_rq_queue()
        self.client.post(reverse('checks:create_checks'), data=get_example_check_data(),
                         content_type='application/json')

        response = self.client.get(reverse('checks:check'),
                                   {'api_key': '1', 'check_id': Check.objects.last().pk})

        self.assertEqual(response.status_code, 400)
        self.assertJSONEqual(
            str(response.content, encoding='utf8'),
            {"error": "Для данного чека не сгенерирован PDF-файл"}
        )

    def test_check_status_rendered(self):
        """
        Если передан верный API ключ и check_id, для которого сгенерировался PDF файл, ожидается 200 код
        и application/pdf
        """

        empty_rq_queue()
        self.client.post(reverse('checks:create_checks'), data=get_example_check_data(),
                         content_type='application/json')

        django_rq.get_worker().work(burst=True)

        response = self.client.get(reverse('checks:check'),
                                   {'api_key': '1', 'check_id': Check.objects.last().pk})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['content-type'], 'application/pdf')


class CreateChecksTests(TestCase):

    def test_create_checks_no_printers_for_point(self):
        """
        Если создаются чеки для точки без принтеров, ожидается код 400
        """

        create_printers_one_point(point_id=2)

        create_checks_response = self.client.post(reverse('checks:create_checks'), data=get_example_check_data(),
                                                  content_type='application/json')

        self.assertEqual(create_checks_response.status_code, 400)
        self.assertJSONEqual(
            str(create_checks_response.content, encoding='utf8'),
            {"error": "Для данной точки не настроено ни одного принтера"}
        )

    def test_create_checks_two_times(self):
        """
        Если создаются чеки для заказа, для которого уже созданы чеки, ожидается код 400
        """

        create_printers_one_point(point_id=1)

        self.client.post(reverse('checks:create_checks'), data=get_example_check_data(),
                         content_type='application/json')
        create_checks_response = self.client.post(reverse('checks:create_checks'), data=get_example_check_data(),
                                                  content_type='application/json')

        self.assertEqual(create_checks_response.status_code, 400)
        self.assertJSONEqual(
            str(create_checks_response.content, encoding='utf8'),
            {"error": "Для данного заказа уже созданы чеки"}
        )

    def test_create_checks_already_created(self):
        """
        Если создаются чеки для заказа и у точки есть принтеры, ожидается код 200
        """

        create_printers_one_point(point_id=1)

        create_checks_response = self.client.post(reverse('checks:create_checks'), data=get_example_check_data(),
                                                  content_type='application/json')

        # Assert
        self.assertEqual(create_checks_response.status_code, 200)
        self.assertJSONEqual(
            str(create_checks_response.content, encoding='utf8'),
            {"ok": "Чеки успешно созданы"}
        )
