# Create your views here.
from models import Form
from autoforms.forms import AutoForm
from django.shortcuts import render_to_response
from django.contrib import admin

def jsi18n(request):
    return admin.site.i18n_javascript(request)

def preview(request,id=None,template='autoforms/preview.html'):
    if request.method == 'GET':
        pk = id or request.GET.get('id',None)
        if not pk:
            forms = Form.objects.all()
            return render_to_response(template,{'forms':forms})
        else:
            dform = Form.objects.get(pk=pk)
            form = AutoForm(fields=dform.field_set.all(),data=None)
            return render_to_response(template,{'form':form,'dform':dform,'edit':True,'id':pk})
    else:
        dform = Form.objects.get(pk=id)
        form = AutoForm(fields=dform.field_set.all().order_by('order'),data=request.POST)
        if form.is_valid():
            return render_to_response(template,{'form':form,'dform':dform})
        else:
            return render_to_response(template,{'form':form,'dform':dform,'edit':True})


def fill(request,id,template='autoforms/fill.html'):
    dform = Form.objects.get(pk=id)
    if request.method == 'GET':
        form = dform.as_form()
        return render_to_response(template,{'form':form,'dform':dform})
    else:
        form = AutoForm(fields=dform.sorted_fields(),data=request.POST)
        if form.is_valid():
            fi = FormInstance(form=dform,name=dform.name)
            fi.save(data=form.cleaned_data)
            return render_to_response(template,{'form':form,'dform':dform})
        else:
            return render_to_response(template,{'form':form,'dform':dform})


