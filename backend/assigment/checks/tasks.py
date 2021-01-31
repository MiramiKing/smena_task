from .models import Check
from django.conf import settings
from django.template.loader import render_to_string
from django.apps import apps
import json
import requests
import os
import base64


def generator(num):
    check = Check.objects.get(id=num)

    check_template = check.type + '_check.html'
    check_html_filename = apps.get_app_config('checks').path + '/templates/' + str(
        check.order['id']) + '_' + check.type + '.html'

    print(check_html_filename)
    context = check.order
    content = render_to_string(check_template, context)

    pdf_filename = str(settings.MEDIA_ROOT) + '/pdf/' + str(check.order['id']) + '_' + check.type + '.pdf'

    with open(check_html_filename, 'w') as file:
        file.write(content)

    url = 'http://127.0.0.1:80/'
    data = {
        'contents': base64.b64encode(open(check_html_filename, 'rb').read()).decode('ascii'),
    }
    headers = {
        'Content-Type': 'application/json',
    }
    response = requests.post(url, data=json.dumps(data), headers=headers)

    with open(pdf_filename, 'wb') as file:
        file.write(response.content)

    os.remove(check_html_filename)

    check.status = 'rendered'
    check.pdf_file = pdf_filename
    check.save()
