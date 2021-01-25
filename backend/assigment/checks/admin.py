from django.contrib import admin
from .models import Printer, Check


# Register your models here.

class AdminPrinter(admin.ModelAdmin):
    fields = ['name', 'api_key', 'check_type', 'point_id']

class AdminCheck(admin.ModelAdmin):
    list_display = ('pk', 'printer_id', 'type', 'status')
    list_filter = ('printer_id', 'type', 'status')

admin.site.register(Printer, AdminPrinter)
admin.site.register(Check,AdminCheck)
