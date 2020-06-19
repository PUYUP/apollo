import uuid
import datetime

from django.conf import settings
from django.db import models
from django.db.models import Q
from django.utils.translation import ugettext_lazy as _
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType

from utils.files import directory_file_path, directory_image_path
from utils.validators import IDENTIFIER_VALIDATOR, non_python_keyword
from apps.learn.utils.constant import ACCESS_TYPE, PUBLIC


class AbstractSnippet(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4, editable=False)
    date_created = models.DateTimeField(auto_now_add=True, null=True)
    date_updated = models.DateTimeField(auto_now=True, null=True)

    # linked
    creator = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
                                null=True, related_name='snippets',
                                related_query_name='snippet')

    # value
    label = models.CharField(max_length=255, help_text=_(
        "Name with extension: django.py"))
    description = models.TextField(max_length=500, blank=True)
    code = models.TextField(help_text=_(u"Line of sample code"))
    access_type = models.CharField(choices=ACCESS_TYPE, default=PUBLIC, max_length=255,
                                   validators=[IDENTIFIER_VALIDATOR, non_python_keyword])
    is_delete = models.BooleanField(default=False)

    # Generic relations
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE,
                                     related_name='snippets',
                                     related_query_name='snippet',
                                     limit_choices_to=Q(app_label='learn'),
                                     null=True, blank=True)
    object_id = models.PositiveIntegerField(blank=True)
    content_object = GenericForeignKey('content_type', 'object_id')

    class Meta:
        abstract = True
        ordering = ['-date_updated']
        verbose_name = _(u"Snippet")
        verbose_name_plural = _(u"Snippets")

    def __str__(self):
        return self.label


class AbstractAttachment(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4, editable=False)
    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)

    # linked
    uploader = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
                                 null=True, related_name='attachments',
                                 related_query_name='attachment')

    # value
    value_image = models.ImageField(upload_to=directory_image_path, max_length=500,
                                    blank=True)
    value_file = models.FileField(upload_to=directory_file_path, max_length=500,
                                  blank=True)
    identifier = models.CharField(max_length=255, blank=True,
                                  validators=[IDENTIFIER_VALIDATOR, non_python_keyword])
    caption = models.TextField(max_length=500, blank=True)
    access_type = models.CharField(choices=ACCESS_TYPE, default=PUBLIC, max_length=255,
                                   validators=[IDENTIFIER_VALIDATOR, non_python_keyword])
    is_delete = models.BooleanField(default=False)

    # Generic relations
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE,
                                     related_name='attachments',
                                     related_query_name='attachment',
                                     limit_choices_to=Q(app_label='learn'),
                                     blank=True)
    object_id = models.PositiveIntegerField(blank=True)
    content_object = GenericForeignKey('content_type', 'object_id')

    class Meta:
        abstract = True
        ordering = ['-date_updated']
        verbose_name = _(u"Attachment")
        verbose_name_plural = _(u"Attachments")

    def __str__(self):
        value = ''
        if self.value_image:
            value = self.value_image.url

        if self.value_file:
            value = self.value_file.url
        return value
