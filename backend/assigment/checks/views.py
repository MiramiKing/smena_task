from django.http import JsonResponse, FileResponse
from .models import Check, Printer
import json
import django_rq
from . import tasks
from django.views.decorators.csrf import ensure_csrf_cookie


# Create your views here.

@ensure_csrf_cookie
def new_checks(request):
    api_key = request.GET['api_key']
    printers = Printer.objects.filter(api_key=api_key)
    if len(printers) == 0:
        return JsonResponse({
            "error": "Ошибка авторизации"
        }, status=401)
    printer = printers[0]
    checks = Check.objects.filter(printer_id=printer.pk, status='rendered')
    result = {'checks': []}
    for check in checks:
        result['checks'].append({'id': check.pk})
    return JsonResponse(result)


def create_checks(request):
    data_dict = json.loads(request.body)
    point_id = int(data_dict['point_id'])
    printers = Printer.objects.filter(point_id=point_id)
    if len(printers) == 0:
        return JsonResponse({
            "error": "Для данной точки не настроено ни одного принтера"
        }, status=400)
    else:
        existing_checks = Check.objects.filter(order__id=data_dict['id'])
        if len(existing_checks) > 0:
            return JsonResponse({
                "error": "Для данного заказа уже созданы чеки"
            }, status=400)
        for printer in printers:
            check = Check(printer_id=printer, type=printer.check_type, order=data_dict, status='new')
            check.save()
            queue = django_rq.get_queue('default')
            queue.enqueue(tasks.generator, check.id)
        return JsonResponse({"ok": "Чеки успешно созданы"})
