#encoding=utf-8
from django.db import models
from django import forms
from django.contrib.contenttypes.models import ContentType
from django.db.models.query import QuerySet
from django.utils import simplejson
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.conf import settings
from django.core.mail import send_mail
from signal import form_filled

field_types = (
    ('char',_('char')),
    ('boolean',_('boolean')),
    ('choice',_('choice')),
    ('multipleChoice',_('mulitpleChoice')),
    ('date',_('date')),
    ('datetime',_('datetime')),
    ('decimal',_('decimal')),
    ('email',_('email')),
    #('file',_('file')),
    ('float',_('float')),
    #('filepath',_('filepath')),
    #('image',_('image')),
    ('integer',_('integer')),
    ('ipadress',_('ipaddress')),
    #('nullBoolean',_('nullBoolean')),
    #('regex',_('regex')),
    ('slug',_('slug')),
    ('time',_('time')),
    ('url',_('url')),
    #('modelChoice',_('modelChoice')),
    #('modelMultipleChoice',_('modelMultipleChoice')),
)

widget_types = (
    ('text',_('text')),
    ('textarea',_('textarea')),
    ('password',_('password')),
    ('hidden',_('hidden')),
    ('multipleHidden',_('multipleHidden')),
    #('file',_('file')),
    ('date',_('date')),
    ('datetime',_('datetime')),
    ('time',_('time')),
    ('radio',_('radio')),
    ('select',_('select')),
    #('nullBoolean',_('nullBoolean')),
    ('selectMultiple',_('selectMultiple')),
    ('checkbox',_('checkbox')),
    ('checkboxMultiple',_('checkboxMultiple')),
)

# Form Definition

class Form(models.Model):
    """
    Present a Django Form subClass
    """
    name = models.CharField(_('Form.name'),max_length=50)
    slug = models.SlugField(_('Form.slug'),unique=True,help_text=_('a easy to remember slug,letters,digits,underlines are allowed.'))
    base = models.ForeignKey('self',verbose_name=_('Form.base'),blank=True,null=True)
    fields = models.TextField(_('Form.fields'),help_text=_('set the display fields,separate with comma'),blank=True,null=True)
    description = models.TextField(_('Form.description'))
    enable = models.BooleanField(_('Form.enable'),default=True)
    user = models.ForeignKey(User,verbose_name=_('user'),blank=True,null=True)

    def short_desc(self):
        if self.description and len(self.description) > 70:
            return self.description[:70] + '...'
        return self.description

    short_desc.short_description = _('description')

    @models.permalink
    def get_absolute_url(self):
        return ('autoforms.views.fill_with_slug',[self.user.username,self.slug])

    def persist(self,data):
        """
        usage:
        data = request.POST
        form.persist(data)
        """
        form = self.as_form(data)
        if form.is_valid():
            fi = FormInstance(_form=self,_name=self.name)
            fi.save(form.cleaned_data)
            return fi
        else:
            return None

    def sorted_fields(self,fields=None):
        """
        return sorted fields
        """
        real_fields = []
        field_dict = {}
        if self.base: # add parent's field first
            field_set_base = self.base.sorted_fields()
            real_fields += field_set_base
            for field in field_set_base:
                field_dict[field.name] = field

        field_set = self.field_set.filter(enable=True).order_by('order')
        for field in field_set:
            if field_dict.has_key(field.name):
                index = real_fields.index(field_dict[field.name])
                real_fields.remove(field_dict[field.name])
                real_fields.insert(index,field)
            else:
                real_fields.append(field)
            field_dict[field.name] = field # local field will override the parent's same field

        if self.fields or fields:
            real_fields = []
            order_field = self.fields.split(',')
            for f in order_field:
                real_fields.append(field_dict[f])
        return real_fields

    def as_form(self,data=None):
        """
        usage:
        form = Form.objects.get(pk=1)
        fobj = form.as_form() # fobj is a Django Form obj
        """
        from autoforms.forms import AutoForm
        return AutoForm(fields=self.sorted_fields(),data=data)

    def search(self,page=1,pagesize=0,*args,**kwargs):
        """
        search form instance data
        """
        if pagesize:
            start = (page - 1) * pagesize
            fis = FormInstance.objects.filter(_form=self)[start:start + pagesize]
        else:
            fis = FormInstance.objects.filter(_form=self)


        fvs = FieldValue.objects.filter(form__in=fis).order_by('form')

        datas = []
        current_instance = None
        current_data = {}

        def find_instance(id):
            for fi in fis:
                if fi.pk == id:return fi

        def update_current():
            current_instance.apply_form_data(self.as_form(current_data))
            datas.append(current_instance)

        for item in fvs:
            if current_instance:
                # same as last row
                if item.form.pk != current_instance.pk:
                    update_current()
                    # setup new instace for current
                    current_instance = find_instance(item.form.pk)
                    current_data = {}
            else:
                # the first row
                current_instance = find_instance(item.form.pk)
            current_data[item.name] = item.value
            setattr(current_instance,item.name,item.value)
        if current_instance:
            update_current()
        return datas


    class Meta:
        verbose_name = _('form')
        verbose_name_plural = _('forms')

    def __unicode__(self):
        return self.name

class Field(models.Model):
    """
    Present a Form Field Class
    """
    form = models.ForeignKey(Form,verbose_name=_('Field.form'))
    name = models.SlugField(_('Field.name'),help_text=_('leters,digits,underline are allowed.'))
    label = models.CharField(_('Field.label'),max_length=50,blank=True,null=True,help_text=_('a friendly field label'))
    required = models.BooleanField(_('Field.required'),help_text=_('is it required?'))
    type = models.CharField(_('Field.type'),max_length=50,choices=field_types)
    help_text = models.CharField(_('Field.help_text'),max_length=200,blank=True,null=True)
    widget = models.CharField(_('Field.widget'),max_length=50,blank=True,null=True,choices=widget_types)
    initial = models.CharField(_('Field.initial'),max_length=200,blank=True,null=True)
    validators = models.CharField(_('Field.validators'),max_length=200,help_text=_('validator names,separate with space'),blank=True,null=True)
    localize = models.BooleanField(_('Field.localize'),default=False)
    order = models.IntegerField(_('Field.order'),default=0)
    description = models.TextField(_('Field.description'),blank=True,null=True)
    datasource = models.ForeignKey(ContentType,verbose_name=_('Field.datasource'),help_text=_('select a datasource for the choice field'),null=True,blank=True)
    extends = models.TextField(_('Field.extends'),help_text=_('other parameters,such as widget parameters,use a json dictionary'),blank=True,null=True)
    enable = models.BooleanField(_('Field.enable'),default=True)

    class Meta:
        verbose_name = _('Field')
        verbose_name_plural = _('Fields')

    def __unicode__(self):
        return self.name

class Option(models.Model):
    """
    Options for Choice.
    """
    field = models.ForeignKey(Field,verbose_name=_('Option.field'))
    value = models.CharField(_('Option.value'),max_length=100)
    label = models.CharField(_('Option.label'),max_length=100)

    def __unicode__(self):
        return self.label

    class Meta:
        verbose_name = _('Option')
        verbose_name_plural = _('Options')


class ErrorMessage(models.Model):
    """
    Custom Error Messages
    """
    field = models.ForeignKey(Field,verbose_name=_('ErrorMessage.field'))
    type = models.CharField(_('ErrorMessage.type'),max_length=20)
    message = models.CharField(_('ErrorMessage.message'),max_length=100)

    class Meta:
        verbose_name = _('ErrorMessage')
        verbose_name_plural = _('ErrorMessages')

    def __unicode__(self):
        return self.type

# Form Runtime

class FormInstance(models.Model):
    """
    A Form Instance
    """
    _id = models.AutoField(primary_key=True)
    _form = models.ForeignKey(Form,verbose_name=_('FormInstance.form'))
    _name = models.CharField(_('FormInstance.name'),max_length=100)
    _create_at = models.DateTimeField(_('FormInstance.create_at'),auto_now_add=True)

    def apply_form_data(self,form):
        self.formobj = form
        if form.is_valid():
            self.cleaned_data = form.cleaned_data

    def save(self,*args,**kwargs):
        data = None
        if kwargs.get('data',None):
           data = kwargs['data']
           del kwargs['data']
        super(FormInstance,self).save(*args,**kwargs)
        if data:
            for key in data.keys():
                if data[key] is not None:
                    if type(data[key]) in(list,QuerySet,tuple):
                        value = [unicode(item) for item in data[key]]
                        value = simplejson.dumps(value)
                    else:
                        value = unicode(data[key])
                    field_value = FieldValue(form=self,name=key,value=value)
                    field_value.save()
        form_filled.send(sender=self.__class__,form=self._form,instance=self)


    class Meta:
        verbose_name = _('FormInstance')
        verbose_name_plural = _('FormInstances')

    def __unicode__(self):
        return self._name

    def summary(self):
        result = ''
        for value in self.fieldvalue_set.all():
            result = result + '%s : %s \n'%(value.name,value.value)
        return result


class FieldValue(models.Model):
    form = models.ForeignKey(FormInstance,verbose_name=_('FieldValue.form'))
    name = models.CharField(_('FieldValue.name'),max_length=100)
    value = models.TextField(_('FieldValue.value'))

    class Meta:
        verbose_name = _('FieldValue')
        verbose_name_plural = _('FieldValues')

    def __unicode__(self):
        return "%s: %s" % (self.name, self.value)

############ signals ############

def form_fill_notify(sender,form,instance,**kwargs):
    if getattr(settings,'NOTIFY_FORM_CHANGE',False):
        msg = 'New commit for form "%s":\n%s' %(form.name,instance.summary())
        send_mail('New commit for form %s'%form.name,msg,
                'notfiy@jeffkit.info',[form.user.email],fail_silently=True)


form_filled.connect(form_fill_notify,sender=FormInstance,dispatch_uid='form_fill_notify')


