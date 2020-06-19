import uuid

from django.conf import settings
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.core.exceptions import ValidationError
from django.contrib.contenttypes.fields import GenericRelation

from utils.files import material_upload_path
from utils.validators import non_python_keyword, IDENTIFIER_VALIDATOR
from apps.learn.utils.constant import (
    DRAFT, IDLE, SIGNER_STATUS, PUBLIC_STATUS, ACCESS_TYPE, PUBLIC,
    id_ID, LANGUAGE_PREFERENCE, PAID, PRINCING_TYPE, ARTICLE, VIDEO,
    DOCUMENT, MATERIAL_TYPE
)


class AbstractSubject(models.Model):
    _UPLOAD_TO = 'images/icon'

    uuid = models.UUIDField(default=uuid.uuid4, editable=False)
    date_created = models.DateTimeField(auto_now_add=True, editable=False)
    date_updated = models.DateTimeField(auto_now=True, editable=False)

    parent = models.ForeignKey('self', on_delete=models.SET_NULL, null=True,
                               blank=True, related_name='subject_parents',
                               related_query_name='subject_parent')
    label = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    sort_order = models.IntegerField(default=1)
    icon = models.ImageField(upload_to=_UPLOAD_TO, blank=True, max_length=500)
    is_active = models.BooleanField(default=True)

    class Meta:
        abstract = True
        verbose_name = _(u"Subject")
        verbose_name_plural = _(u"subjects")

    def __str__(self):
        return self.label


class AbstractCourse(models.Model):
    """Description below
    :signer_status is change by staff
    :public_status is change by creator
    """
    uuid = models.UUIDField(default=uuid.uuid4, editable=False)
    date_created = models.DateTimeField(auto_now_add=True, null=True)
    date_updated = models.DateTimeField(auto_now=True, null=True)

    # linked
    creator = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                                related_name='courses', related_query_name='course')
    updated_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
                                   null=True, related_name='+')
    subject = models.ForeignKey('learn.Subject', on_delete=models.SET_NULL, null=True,
                                related_name='courses', related_query_name='course')

    # basic info
    label = models.CharField(max_length=255, help_text=_(u"Course name."))
    excerpt = models.TextField(max_length=500, help_text=_(u"Short description."))
    description = models.TextField(help_text=_(u"Tell more details."))
    learned = models.TextField(help_text=_(u"What's learner got."))
    requirement = models.TextField(help_text=_(u"What's learner must prepare."))
    signer_status = models.SlugField(choices=SIGNER_STATUS, default=IDLE, max_length=255,
                                     validators=[IDENTIFIER_VALIDATOR, non_python_keyword])
    public_status = models.SlugField(choices=PUBLIC_STATUS, default=DRAFT, max_length=255,
                                     validators=[IDENTIFIER_VALIDATOR, non_python_keyword])
    access_type = models.CharField(choices=ACCESS_TYPE, default=PUBLIC, max_length=255,
                                   validators=[IDENTIFIER_VALIDATOR, non_python_keyword])
    language = models.CharField(choices=LANGUAGE_PREFERENCE, default=id_ID, max_length=255,
                                validators=[IDENTIFIER_VALIDATOR, non_python_keyword])
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    is_delete = models.BooleanField(default=False)

    # tails...
    attachments = GenericRelation('learn.Attachment', related_query_name='course')

    class Meta:
        abstract = True
        verbose_name = _(u"Course")
        verbose_name_plural = _(u"Courses")

    def __str__(self):
        return self.label


class AbstractChapter(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4, editable=False)
    date_created = models.DateTimeField(auto_now_add=True, null=True)
    date_updated = models.DateTimeField(auto_now=True, null=True)

    # linked
    creator = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                                related_name='chapters', related_query_name='chapter')
    updated_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
                                   null=True, related_name='+')
    subject = models.ForeignKey('learn.Subject', on_delete=models.SET_NULL, null=True,
                                editable=False, related_name='chapters', related_query_name='chapter')
    course = models.ForeignKey('learn.Course', on_delete=models.CASCADE,
                               related_name='chapters', related_query_name='chapter')

    label = models.CharField(max_length=255)
    description = models.TextField(max_length=500, blank=True)
    princing_type = models.CharField(choices=PRINCING_TYPE, default=PAID, max_length=255,
                                     validators=[IDENTIFIER_VALIDATOR, non_python_keyword])
    is_delete = models.BooleanField(default=False)

    class Meta:
        abstract = True
        verbose_name = _(u"Chapter")
        verbose_name_plural = _(u"Chapters")

    def __str__(self):
        return self.label

    def save(self, *args, **kwargs):
        subject = self.course.subject
        if subject:
            self.subject = subject
        super().save(*args, **kwargs)


class AbstractLecture(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4, editable=False)
    date_created = models.DateTimeField(auto_now_add=True, null=True)
    date_updated = models.DateTimeField(auto_now=True, null=True)

    creator = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                                related_name='lectures', related_query_name='lecture')
    updated_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
                                   null=True, related_name='+')
    subject = models.ForeignKey('learn.Subject', on_delete=models.SET_NULL, null=True,
                                editable=False, related_name='lectures',
                                related_query_name='lecture')
    course = models.ForeignKey('learn.Course', on_delete=models.CASCADE,
                               related_name='lectures', related_query_name='lecture',
                               editable=False)
    chapter = models.ForeignKey('learn.Chapter', on_delete=models.CASCADE,
                                related_name='lectures', related_query_name='lecture')

    label = models.CharField(max_length=255)
    description = models.TextField(max_length=500, blank=True)
    material_type = models.CharField(choices=MATERIAL_TYPE, default=ARTICLE, max_length=255,
                                     validators=[IDENTIFIER_VALIDATOR, non_python_keyword])
    is_delete = models.BooleanField(default=False)

    class Meta:
        abstract = True
        verbose_name = _(u"Lecture")
        verbose_name_plural = _(u"Lectures")

    def __str__(self):
        return self.label

    def save(self, *args, **kwargs):
        subject = self.chapter.subject
        course = self.chapter.course

        if subject:
            self.subject = subject

        if course:
            self.course = course
        super().save(*args, **kwargs)


class AbstractMaterial(models.Model):
    """Some information
    :value_article for material_type = ARTICLE
    :value_file for material_type = VIDEO, DOCUMENT (image, word, ect.)

    value_* required depend on material_type
    """
    uuid = models.UUIDField(default=uuid.uuid4, editable=False)
    date_created = models.DateTimeField(auto_now_add=True, null=True)
    date_updated = models.DateTimeField(auto_now=True, null=True)

    # linked
    creator = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                                related_name='materials', related_query_name='material')
    updated_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
                                   null=True, related_name='+')
    subject = models.ForeignKey('learn.Subject', on_delete=models.SET_NULL, null=True,
                                related_name='materials', related_query_name='material',
                                editable=False)
    course = models.ForeignKey('learn.Course', on_delete=models.CASCADE,
                               related_name='materials', related_query_name='material',
                               editable=False)
    chapter = models.ForeignKey('learn.Chapter', on_delete=models.CASCADE,
                                related_name='materials', related_query_name='material',
                                editable=False)
    lecture = models.OneToOneField('learn.Lecture', on_delete=models.CASCADE,
                                   related_name='materials', related_query_name='material')

    # tails...
    snippets = GenericRelation('learn.Snippet', related_query_name='material')
    attachments = GenericRelation('learn.Attachment', related_query_name='material')

    # content
    value_article = models.TextField(blank=True)
    value_file = models.FileField(upload_to=material_upload_path, max_length=500,
                                  blank=True)
    is_delete = models.BooleanField(default=False)

    class Meta:
        abstract = True
        verbose_name = _(u"Material")
        verbose_name_plural = _(u"Materials")

    def clean(self):
        material_type = self.lecture.material_type

        if material_type == ARTICLE:
            if not self.value_article:
                raise ValidationError(_(u"Article must provided."))

        if material_type == VIDEO:
            if not self.value_file:
                raise ValidationError(_(u"Video must provided."))

        if material_type == DOCUMENT:
            if not self.value_file:
                raise ValidationError(_(u"Document must provided."))

    def __str__(self):
        return self.lecture.label

    def save(self, *args, **kwargs):
        subject = self.lecture.subject
        course = self.lecture.course
        chapter = self.lecture.chapter

        if subject:
            self.subject = subject

        if course:
            self.course = course

        if chapter:
            self.chapter = chapter
        super().save(*args, **kwargs)


class AbstractInstructor(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4, editable=False)
    date_created = models.DateTimeField(auto_now_add=True, null=True)
    date_updated = models.DateTimeField(auto_now=True, null=True)

    course = models.ForeignKey('learn.Course', on_delete=models.CASCADE,
                               related_name='instructors', related_query_name='instructor')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
                             null=True, related_name='instructors',
                             related_query_name='instructor')
    is_creator = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    class Meta:
        abstract = True
        verbose_name = _(u"Instructors")
        verbose_name_plural = _(u"Instructor")

    def __str__(self):
        return self.user.username

    def save(self, *args, **kwargs):
        if self.course.creator == self.user:
            self.is_creator = True
        super().save(*args, **kwargs)
