#encoding=utf-8
from django import template

register = template.Library()

def form_value(value):
  if not value:
	return ''
  if type(value) == list:
	return ','.join(value)
  return value

register.filter('formvalue',form_value)
