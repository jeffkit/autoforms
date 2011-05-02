#encoding=utf-8
from django.contrib.admin import widgets
from django import forms
try:
    import simplejson
except:
    from django.utils import simplejson
from models import Field

field_types = {
    'boolean':forms.BooleanField,
    'char':forms.CharField,
    'choice':forms.ChoiceField,
    'date':forms.DateField,
    'datetime':forms.DateTimeField,
    'decimal':forms.DecimalField,
    'email':forms.EmailField,
    'file':forms.FileField,
    'float':forms.FloatField,
    'filepath':forms.FilePathField,
    'image':forms.ImageField,
    'integer':forms.IntegerField,
    'ipadress':forms.IPAddressField,
    'multipleChoice':forms.MultipleChoiceField,
    'nullBoolean':forms.NullBooleanField,
    'regex':forms.RegexField,
    'slug':forms.SlugField,
    'time':forms.TimeField,
    'url':forms.URLField,
    'modelChoice':forms.ModelChoiceField,
    'modelMultipleChoice':forms.ModelMultipleChoiceField,
}

widget_types = {
    'text':forms.TextInput,
    'password':forms.PasswordInput,
    'hidden':forms.HiddenInput,
    'multipleHidden':forms.MultipleHiddenInput,
    'file':forms.FileInput,
    'date':widgets.AdminDateWidget,
    'datetime':widgets.AdminSplitDateTime,
    'time':widgets.AdminTimeWidget,
    'textarea':forms.Textarea,
    'checkbox':forms.CheckboxInput,
    'select':forms.Select,
    'nullBoolean':forms.NullBooleanSelect,
    'selectMultiple':forms.SelectMultiple,
    'radio':forms.RadioSelect,
    'checkboxMultiple':forms.CheckboxSelectMultiple,
}

field_required_arguments = {
    'choice':'choices',
    'multipleChoice':'choices',
    'regex':'regex',
    'combo':'fields',
    'multiValue':'fields',
    'modelChoice':'queryset',
    'modelMultipleChoice':'queryset',
}

class AutoForm(forms.Form):
    """
    usage：
    1. create an empty AutoForm:
    form = AutoForm(fields=form.sorted_fields()))
    2. create an AutoForm with datas:
    form = AutoForm(fields=form.sorted_fields()),data=datas)
    """
    def __init__(self,fields,data=None,*args,**kwargs1):
        super(AutoForm,self).__init__(data,*args,**kwargs1)
        # fields is a set of sorted fields
        for field in fields:
            field_type = field_types[field.type]
            kwargs = {'required':field.required,'label':field.label,'help_text':field.help_text,'localize':field.localize}
            if field.widget:
                kwargs['widget'] = widget_types[field.widget]()
            if field.initial:
                kwargs['initial'] = field.initial

            # turn extends from json to dict
            if field.extends:
                other_args = simplejson.loads(field.extends)
                for item in other_args.items():
                    kwargs[str(item[0])] = item[1]

            # ModelChioce field，need a queryset parameter.
            if field.type in ['modelChoice','modelMultipleChoice']:
                if field.datasource:
                    kwargs['queryset'] = field.datasource.model_class().objects.all()
                else:
                    raise ValueError,u'%s need a datasource!'%field.name

            if field.type in ['choice','multipleChoice']:
                choices = []
                if kwargs.get('choices',None):
                    choices += kwargs['choices']
                for option in field.option_set.all():
                    choices.append((option.value,option.label))

                kwargs['choices'] = choices

            else:
                required_arguments = field_required_arguments.get(field.type,None)
                if required_arguments:
                    required_arguments = required_arguments.split(',')
                    for arg in required_arguments:
                        if arg not in kwargs:
                            raise ValueError,u'argument "%s" for %s is required'%(arg,field.name)

                if field.widget in ['select','selectMultiple','radio','checkboxMultiple']:
                    if 'choices' not in kwargs:
                        raise ValueError,'widget select,radio,checkbox need a choices parameters'

            # custome error message
            error_messages = {}
            for error_msg in field.errormessage_set.all():
                error_messages[error_msg.type] =  error_msg.message

            if error_messages:
                kwargs['error_messages'] = error_messages

            self.fields[field.name] = field_type(**kwargs)


class FieldForm(forms.ModelForm):
    class Meta:
        model = Field
        fields = ('type','required','name','label','help_text','order','widget')

