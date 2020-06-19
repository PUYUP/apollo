import uuid
import keyword

from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _
from django.utils.html import strip_tags, escape


IDENTIFIER_VALIDATOR = RegexValidator(
    regex=r'^[a-zA-Z_][a-zA-Z_]*$',
    message=_(u"Can only contain the letters a-z and underscores."))


def non_python_keyword(value):
    if keyword.iskeyword(value):
        raise ValidationError(
            _(u"This field is invalid as its value is forbidden.")
        )
    return value


def check_uuid(uid=None):
    if not uid:
        raise ValidationError(_(u"UUID not provided."))

    if uid and type(uid) is not uuid.UUID:
        try:
            uid = uuid.UUID(uid)
        except ValueError:
            raise ValidationError(_(u"UUID invalid."))
        return uid
    return uid


def make_safe_string(data):
    # clear unsafe html string
    for key in data:
        string = data.get(key, None)
        if string and isinstance(string, str):
            string = escape(strip_tags(string))
            data[key] = string
    return data
