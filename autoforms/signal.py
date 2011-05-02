#encoding=utf-8

from django.dispatch import Signal

form_filled = Signal(providing_args=['form','instance'])
