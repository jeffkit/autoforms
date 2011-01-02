#encoding=utf-8

from django.conf.urls.defaults import *
from django.contrib import admin
from django.http import HttpResponse
from django.shortcuts import render_to_response,get_object_or_404
from django.template import RequestContext
from django.utils.translation import ugettext_lazy as _
from django.template import loader, Context

from autoforms import models
from autoforms import forms


class FieldInline(admin.TabularInline):
    model = models.Field
    form = forms.FieldForm

class FormAdmin(admin.ModelAdmin):
    list_display = ['name','slug','short_desc']
    search_fields = ['name','description']
    inlines = [FieldInline]

    def preview(self,request,id):
        form = models.Form.objects.get(pk=id)
        return render_to_response('autoforms/admin/form_preview.html',{'form':form,'dform':form.as_form(),'title':_('Preview form : %(form_name)s')%{'form_name':form.name}},context_instance = RequestContext(request))

    def data(self,request,id):
        form = models.Form.objects.get(pk=id)
        return render_to_response('autoforms/admin/form_data.html',{'form':form,'title':_('Data of form : %(form_name)s')%{'form_name':form.name}},context_instance = RequestContext(request))

    def embed(self,request,id):
        return HttpResponse('get embed code')

    def export(self,request,id,format='csv'):
        form = models.Form.objects.get(pk=id)
        if format == 'csv':
            response = HttpResponse(mimetype='text/csv')
            response['Content-Disposition'] = 'attachment; filename=%s.csv'%id
            template = loader.get_template('autoforms/admin/form_export.csv')
            context = Context({'datalist':form.search(),'fields':form.sorted_fields()})
            response.write(template.render(context))
            return response
        else:
            return HttpResponse('format not support yet')

    def get_urls(self):
        urls = super(FormAdmin,self).get_urls()
        form_urls = patterns('',
            (r'^(?P<id>\d+)/preview/$',self.admin_site.admin_view(self.preview)),
            (r'^(?P<id>\d+)/data/$',self.admin_site.admin_view(self.data)),
            (r'^(?P<id>\d+)/embed/$',self.admin_site.admin_view(self.embed)),
            (r'^(?P<id>\d+)/data/export/(?P<format>\w+)/$',self.admin_site.admin_view(self.export)),
        )
        return form_urls + urls

admin.site.register(models.Form,FormAdmin)

class ErrorMessageInline(admin.TabularInline):
    model = models.ErrorMessage
    template = 'autoforms/field_tabular.html'

class FieldAdmin(admin.ModelAdmin):
    list_display = ['form','name','label','type','required','order',]
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
