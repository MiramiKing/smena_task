from django.db import models

PRINTER_CHOICES = [('kitchen', 'kitchen'), ('client', 'client')]

CHECK_CHOICES = [('new', 'new'), ('rendered', 'rendered'), ('printed', 'printed')]


class Printer(models.Model):
    name = models.CharField(max_length=100)
    api_key = models.CharField(max_length=50)
    check_type = models.CharField(max_length=100, choices=PRINTER_CHOICES)
    point_id = models.IntegerField()

    class Meta:
        verbose_name = 'Принтер'
        verbose_name_plural = 'Принтеры'


class Check(models.Model):
    printer_id = models.ForeignKey(Printer, on_delete=models.CASCADE, null=False)
    type = models.CharField(max_length=100, choices=PRINTER_CHOICES)
    order = models.JSONField()
    status = models.CharField(max_length=100, choices=CHECK_CHOICES)
    pdf_file = models.FileField(upload_to='media/pdf/')

    class Meta:
        verbose_name = 'Чек'
        verbose_name_plural = 'Чеки'
