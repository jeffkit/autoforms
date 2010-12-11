#encoding=utf-8
from django.db import models
from django import forms
from django.contrib.contenttypes.models import ContentType
from autoforms.forms import *
from django.db.models.query import QuerySet
from django.utils import simplejson

field_types = (
    ('boolean',u'布尔值'),
    ('char',u'文本'),
    ('choice',u'选项值'),
    ('date',u'日期'),
    ('datetime',u'日期时间'),
    ('decimal',u'小数'),
    ('email',u'Email'),
    ('file',u'文件'),
    ('float',u'浮点数'),
    ('filepath',u'文件路径'),
    ('image',u'图片'),
    ('integer',u'整数'),
    ('ipadress',u'IP地址'),
    ('multipleChoice',u'多选值'),
    #('nullBoolean',u''),
    ('regex',u'正则表达式'),
    #('slug',u''),
    ('time',u'时间'),
    ('url',u'URL'),
    ('modelChoice',u'数据表纪录'),
    ('modelMultipleChoice',u'数据表纪录（多选）'),
)

widget_types = (
    ('text',u'文本框'),
    ('password',u'密码输入框'),
    ('hidden',u'隐藏域'),
    ('multipleHidden',u'多个隐藏域'),
    ('file',u'文件浏览器'),
    ('date',u'日期选择器'),
    ('datetime',u'日期时间选择器'),
    ('time',u'时间选择器'),
    ('textarea',u'文本域'),
    ('checkbox',u'勾选框'),
    ('select',u'下拉框'),
    #('nullBoolean',u''),
    ('selectMultiple',u'多选下拉框'),
    ('radio',u'单选框'),
    ('checkboxMultiple',u'复选框'),
)

# Form Definition

class Form(models.Model):
    """
    Present a Django Form subClass
    """
    name = models.CharField(u'表单名',max_length=50)
    base = models.ForeignKey('self',verbose_name=u'继承自',blank=True,null=True)
    fields = models.TextField(u'字段',help_text=u'在此可定义显示表单的字段及排列顺序，使用逗号隔开字段名即可',blank=True,null=True)
    description = models.TextField(u'说明')


    def sorted_fields(self):
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

        if self.fields:
            real_fields = []
            order_field = self.fields.split(',')
            for f in order_field:
                real_fields.append(field_dict[f])
        return real_fields

    def as_form(self):
        return AutoForm(fields=self.sorted_fields())

    class Meta:
        verbose_name = u'表单'
        verbose_name_plural = u'表单'

    def __unicode__(self):
        return self.name

class Field(models.Model):
    """
    Present a Form Field Class
    """
    form = models.ForeignKey(Form,verbose_name=u'表单')
    name = models.CharField(u'名称',max_length=50,help_text=u'请使用英文填写表单域名')
    label = models.CharField(u'标签',max_length=50,blank=True,null=True,help_text=u'对用户友好的表单域名称')
    required = models.BooleanField(u'必填',help_text=u'该域是否必填')
    type = models.CharField(u'类型',max_length=50,choices=field_types)
    help_text = models.CharField(u'帮助文本',max_length=200,blank=True,null=True,help_text=u'如这段文字一样，向用户解释该字段，方便用户理解')
    widget = models.CharField(u'表单组件',max_length=50,blank=True,null=True,help_text=u'如果您不是特别熟悉HTML表单组件，保持系统默认即可。',choices=widget_types)
    initial = models.CharField(u'初始值',max_length=200,blank=True,null=True)
    validators = models.CharField(u'校验器',max_length=200,help_text=u'输入字段校验器的名称，以空格隔开',blank=True,null=True)
    localize = models.BooleanField(u'本地化',default=False)
    order = models.IntegerField(u'排列顺序',default=0)
    description = models.TextField(u'说明',blank=True,null=True)
    datasource = models.ForeignKey(ContentType,verbose_name=u'数据源',help_text=u'选择数据源，仅当表单域类型为"数据表纪录"时有效',null=True,blank=True)
    extends = models.TextField(u'扩展',help_text=u'其他参数或下拉列表选项等，请使用json格式的数据填充',blank=True,null=True)
    enable = models.BooleanField(u'可用',default=True)

    class Meta:
        verbose_name = u'表单域'
        verbose_name_plural = u'表单域'

    def __unicode__(self):
        return self.name

class ErrorMessage(models.Model):
    """
    Custom Error Messages
    """
    field = models.ForeignKey(Field,verbose_name='表单域')
    type = models.CharField(u'校验类型',max_length=20)
    message = models.CharField(u'错误信息',max_length=100)

    class Meta:
        verbose_name = u'错误信息'
        verbose_name_plural = u'错误信息'

    def __unicode__(self):
        return self.type

# Form Runtime

class FormInstance(models.Model):
    """
    A Form Instance
    """
    form = models.ForeignKey(Form,verbose_name=u'表单')
    name = models.CharField(u'名称',max_length=100)
    create_at = models.DateTimeField(u'创建时间')

    def save(self,*args,**kwargs):
        super(FormInstance,self).save(*args,**kwargs)
        if kwargs.get('data',None):
            for key in data.keys():
                if data[key] is not None:
                    if type(data[key]) in(list,QuerySet,tuple):
                        value = [str(item) for item in data[key]]
                        value = simplejson.dumps(value)
                    else:
                        value = str(data[key])
                field_value = FieldValue(form=self,name=key,value=value)
                field_value.save()


    class Meta:
        verbose_name = u'表单实例'
        verbose_name_plural = u'表单实例'

    def __unicode__(self):
        return self.name


class FieldValue(models.Model):
    form = models.ForeignKey(FormInstance,verbose_name=u'表单')
    name = models.CharField(u'字段名',max_length=100)
    value = models.TextField(u'字段值')

    class Meta:
        verbose_name = u'字段值'
        verbose_name_plural = u'字段值'

