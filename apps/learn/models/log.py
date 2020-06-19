import json

from django.conf import settings
from django.contrib.admin.utils import quote
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.urls import NoReverseMatch, reverse
from django.utils import timezone
from django.utils.text import get_text_list
from django.utils.translation import gettext, gettext_lazy as _

from utils.generals import get_model

ADDITION = 1
CHANGE = 2
DELETION = 3

ACTION_FLAG_CHOICES = (
    (ADDITION, _(u"ddition")),
    (CHANGE, _(u"Change")),
    (DELETION, _(u"Deletion")),
)


class ActivityLogManager(models.Manager):
    use_in_migrations = True

    def log_action(self, user_id, content_type_id, object_id, object_repr, action_flag, change_message=''):
        if isinstance(change_message, list):
            change_message = json.dumps(change_message)
        return self.model.objects.create(
            user_id=user_id,
            content_type_id=content_type_id,
            object_id=str(object_id),
            object_repr=object_repr[:200],
            action_flag=action_flag,
            change_message=change_message,
        )


class AbstractActivityLog(models.Model):
    action_time = models.DateTimeField(
        _(u"action time"),
        default=timezone.now,
        editable=False,
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        models.CASCADE,
        verbose_name=_(u"user"),
    )
    content_type = models.ForeignKey(
        ContentType,
        models.SET_NULL,
        verbose_name=_(u"content type"),
        blank=True, null=True,
    )
    object_id = models.TextField(_(u"object id"), blank=True, null=True)
    # Translators: 'repr' means representation (https://docs.python.org/library/functions.html#repr)
    object_repr = models.CharField(_(u"object repr"), max_length=200)
    action_flag = models.PositiveSmallIntegerField(_(u"action flag"), choices=ACTION_FLAG_CHOICES)
    # change_message is either a string or a JSON structure
    change_message = models.TextField(_(u"change message"), blank=True)

    objects = ActivityLogManager()

    class Meta:
        abstract = True
        verbose_name = _(u"Log Entry")
        verbose_name_plural = _(u"Log Entries")
        ordering = ['-action_time']

    def __repr__(self):
        return str(self.action_time)

    def __str__(self):
        if self.is_addition():
            return gettext('Added “%(object)s”.') % {'object': self.object_repr}
        elif self.is_change():
            return gettext('Changed “%(object)s” — %(changes)s') % {
                'object': self.object_repr,
                'changes': self.get_change_message(),
            }
        elif self.is_deletion():
            return gettext('Deleted “%(object)s.”') % {'object': self.object_repr}

        return gettext('LogEntry Object')

    def is_addition(self):
        return self.action_flag == ADDITION

    def is_change(self):
        return self.action_flag == CHANGE

    def is_deletion(self):
        return self.action_flag == DELETION

    def get_change_message(self):
        """
        If self.change_message is a JSON structure, interpret it as a change
        string, properly translated.
        """
        if self.change_message and self.change_message[0] == '[':
            try:
                change_message = json.loads(self.change_message)
            except json.JSONDecodeError:
                return self.change_message
            messages = []
            for sub_message in change_message:
                if 'added' in sub_message:
                    if sub_message['added']:
                        sub_message['added']['name'] = gettext(sub_message['added']['name'])
                        messages.append(gettext('Added {name} “{object}”.').format(**sub_message['added']))
                    else:
                        messages.append(gettext('Added.'))

                elif 'changed' in sub_message:
                    sub_message['changed']['fields'] = get_text_list(
                        [gettext(field_name) for field_name in sub_message['changed']['fields']], gettext('and')
                    )
                    if 'name' in sub_message['changed']:
                        sub_message['changed']['name'] = gettext(sub_message['changed']['name'])
                        messages.append(gettext('Changed {fields} for {name} “{object}”.').format(
                            **sub_message['changed']
                        ))
                    else:
                        messages.append(gettext('Changed {fields}.').format(**sub_message['changed']))

                elif 'deleted' in sub_message:
                    sub_message['deleted']['name'] = gettext(sub_message['deleted']['name'])
                    messages.append(gettext('Deleted {name} “{object}”.').format(**sub_message['deleted']))

            change_message = ' '.join(msg[0].upper() + msg[1:] for msg in messages)
            return change_message or gettext('No fields changed.')
        else:
            return self.change_message

    def get_edited_object(self):
        """Return the edited object represented by this log entry."""
        return self.content_type.get_object_for_this_type(pk=self.object_id)

    def get_learn_url(self):
        """
        Return the learn URL to edit the object represented by this log entry.
        """
        if self.content_type and self.object_id:
            url_name = 'learn:%s_%s_change' % (self.content_type.app_label, self.content_type.model)
            try:
                return reverse(url_name, args=(quote(self.object_id),))
            except NoReverseMatch:
                pass
        return None


def get_content_type_for_model(obj):
    # Since this module gets imported in the application's root package,
    # it cannot import models from other applications at the module level.
    from django.contrib.contenttypes.models import ContentType
    return ContentType.objects.get_for_model(obj, for_concrete_model=False)


def log_addition(self, request, object, message):
    """
    Log that an object has been successfully added.

    The default implementation creates an admin ActivityLog object.
    """
    from django.contrib.admin.models import ADDITION
    ActivityLog = get_model('learn', 'ActivityLog')

    return ActivityLog.objects.log_action(
        user_id=request.user.pk,
        content_type_id=get_content_type_for_model(object).pk,
        object_id=object.pk,
        object_repr=str(object),
        action_flag=ADDITION,
        change_message=message,
    )


def log_change(self, request, object, message):
    """
    Log that an object has been successfully changed.

    The default implementation creates an admin ActivityLog object.
    """
    from django.contrib.admin.models import CHANGE
    ActivityLog = get_model('learn', 'ActivityLog')

    return ActivityLog.objects.log_action(
        user_id=request.user.pk,
        content_type_id=get_content_type_for_model(object).pk,
        object_id=object.pk,
        object_repr=str(object),
        action_flag=CHANGE,
        change_message=message,
    )


def log_deletion(self, request, object, object_repr):
    """
    Log that an object will be deleted. Note that this method must be
    called before the deletion.

    The default implementation creates an admin ActivityLog object.
    """
    from django.contrib.admin.models import DELETION
    ActivityLog = get_model('learn', 'ActivityLog')

    return ActivityLog.objects.log_action(
        user_id=request.user.pk,
        content_type_id=get_content_type_for_model(object).pk,
        object_id=object.pk,
        object_repr=object_repr,
        action_flag=DELETION,
    )
