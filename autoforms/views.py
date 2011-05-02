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

def fill_with_id(request,id,template='autoforms/fill.html',success_template='autoforms/fill_done.html'):
    form = get_object_or_404(Form,pk=id)
    return fill(request,form,template,success_template)

def fill_with_slug(request,user,slug,template='autoforms/fill.html',success_template='autoforms/fill_done.html'):
    form = get_object_or_404(Form,user__username=user,slug=slug)
    return fill(request,form,template,success_template)

def fill(request,form,template='autoforms/fill.html',success_template='autoforms/fill_done.html'):
    data = request.GET or request.POST
    #is_popup = data.get('is_popup',None)
    is_popup = True
    if request.method == 'GET':
        dform = form.as_form()
        return render_to_response(template,{'title':form.name,'is_popup':is_popup,'form':form,'dform':dform},context_instance=RequestContext(request))
    else:
        dform = AutoForm(fields=form.sorted_fields(),data=request.POST)
        if dform.is_valid():
            if form.enable:
                # save the data only form is enable
                fi = FormInstance(_form=form,_name=form.name)
                fi.save(data=dform.cleaned_data)
            return render_to_response(success_template,{'title':form.name,'is_popup':is_popup,'form':form,'dform':dform},context_instance=RequestContext(request))
        else:
            return render_to_response(template,{'title':form.name,'is_popup':is_popup,'form':form,'dform':dform},context_instance=RequestContext(request))



