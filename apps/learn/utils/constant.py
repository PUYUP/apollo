from django.utils.translation import ugettext_lazy as _

IDLE = 'idle'
REVIEW = 'review'
REJECT = 'reject'
ACCEPT = 'accept'
SIGNER_STATUS = (
    (IDLE, _(u"Idle")),
    (REVIEW, _(u"Review")),
    (REJECT, _(u"Reject")),
    (ACCEPT, _(u"Accept")),
)


DRAFT = 'draft'
PUBLISH = 'publish'
PUBLIC_STATUS = (
    (DRAFT, _(u"Draft")),
    (PUBLISH, _(u"Publish")),
)


PUBLIC = 'public'
PRIVATE = 'private'
ACCESS_TYPE = (
    (PUBLIC, _(u"Public")),
    (PRIVATE, _(u"Private")),
)


id_ID = 'id-ID'
en_GB = 'en-GB'
LANGUAGE_PREFERENCE = (
    (id_ID, _(u"Indonesian (Indonesia)")),
    (en_GB, _(u"English (United Kingdom)")),
)


PAID = 'paid'
FREE = 'free'
PRINCING_TYPE = (
    (PAID, _(u"Paid")),
    (FREE, _(u"Free")),
)


ARTICLE = 'article'
VIDEO = 'video'
DOCUMENT = 'document'
MATERIAL_TYPE = (
    (ARTICLE, _(u"Article")),
    (VIDEO, _(u"Video")),
    (DOCUMENT, _(u"Document")),
)
