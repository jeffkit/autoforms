# Create your views here.
from models import Form,FormInstance
from autoforms.forms import AutoForm
from django.shortcuts import render_to_response,get_object_or_404
from django.contrib import admin
from django.template import RequestContext

def jsi18n(request):
    return admin.site.i18n_javascript(request)

def index(request):
    return render_to_response('autoforms/index.html',context_instance=RequestContext(request))

def preview(request,id=None,template='autoforms/preview.html'):
    if request.method == 'GET':
        pk = id or request.GET.get('id',None)
        if not pk:
            forms = Form.objects.all()
            return render_to_response(template,{'forms':forms},context_instance=RequestContext(request))
        else:
            dform = get_object_or_404(Form,pk=pk)
            form = dform.as_form()
            return render_to_response(template,{'form':form,'dform':dform,'edit':True,'id':pk},context_instance=RequestContext(request))
    else:
        dform = get_object_or_404(Form,pk=id)
        form = AutoForm(fields=dform.field_set.all().order_by('order'),data=request.POST)
        if form.is_valid():
            return render_to_response(template,{'form':form,'dform':dform},context_instance=RequestContext(request))
        else:
            return render_to_response(template,{'form':form,'dform':dform,'edit':True},context_instance=RequestContext(request))


def fill(request,id,template='autoforms/fill.html',success_template='autoforms/fill_done.html'):
    dform = get_object_or_404(Form,pk=id)
    if request.method == 'GET':
        form = dform.as_form()
        return render_to_response(template,{'form':form,'dform':dform},context_instance=RequestContext(request))
    else:
        form = AutoForm(fields=dform.sorted_fields(),data=request.POST)
        if form.is_valid():
            fi = FormInstance(_form=dform,_name=dform.name)
            fi.save(data=form.cleaned_data)
            return render_to_response(success_template,{'form':form,'dform':dform},context_instance=RequestContext(request))
        else:
            return render_to_response(template,{'form':form,'dform':dform},context_instance=RequestContext(request))

def overview(request,id,template='autoforms/overview.html'):
    dform = get_object_or_404(Form,pk=id)
    return render_to_response(template,{'dform':dform},context_instance=RequestContext(request))


