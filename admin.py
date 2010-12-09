#encoding=utf-8

from django.contrib import admin

from autoforms import models
from autoforms import forms

class FieldInline(admin.TabularInline):
    model = models.Field
    form = forms.FieldForm



class FormAdmin(admin.ModelAdmin):
    list_display = ['name','description']
    search_fields = ['name','description']
    inlines = [FieldInline]

admin.site.register(models.Form,FormAdmin)

class ErrorMessageInline(admin.TabularInline):
    model = models.ErrorMessage
    template = 'field_tabular.html'

class FieldAdmin(admin.ModelAdmin):
    list_display = ['name','label','type','required','order','form']
    list_filter = ['form']
    search_fields = ['name','label','description','help_text']
    inlines = [ErrorMessageInline]
    list_editable = ['order']

    fieldsets = (
        (u'基础信息',{
            'fields':('form','type','required','order','name','label','help_text')
        }),
        (u'高级设置',{
            'classes': ('collapse',),
            'fields':('localize','initial','widget','validators','datasource','extends','description')
        })
        )

admin.site.register(models.Field,FieldAdmin)
