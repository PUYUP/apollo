from .course import *
from .log import *
from .general import *

# PROJECT UTILS
from utils.generals import is_model_registered

__all__ = list()

# 1
if not is_model_registered('learn', 'Subject'):
    class Subject(AbstractSubject):
        class Meta(AbstractSubject.Meta):
            db_table = 'learn_subject'

    __all__.append('Subject')


# 2
if not is_model_registered('learn', 'Course'):
    class Course(AbstractCourse):
        class Meta(AbstractCourse.Meta):
            db_table = 'learn_course'

    __all__.append('Course')


# 3
if not is_model_registered('learn', 'Chapter'):
    class Chapter(AbstractChapter):
        class Meta(AbstractChapter.Meta):
            db_table = 'learn_chapter'

    __all__.append('Chapter')


# 4
if not is_model_registered('learn', 'Lecture'):
    class Lecture(AbstractLecture):
        class Meta(AbstractLecture.Meta):
            db_table = 'learn_lecture'

    __all__.append('Lecture')


# 5
if not is_model_registered('learn', 'Material'):
    class Material(AbstractMaterial):
        class Meta(AbstractMaterial.Meta):
            db_table = 'learn_material'

    __all__.append('Material')


# 6
if not is_model_registered('learn', 'Instructor'):
    class Instructor(AbstractInstructor):
        class Meta(AbstractInstructor.Meta):
            db_table = 'learn_instructor'

    __all__.append('Instructor')


# 7
if not is_model_registered('learn', 'Snippet'):
    class Snippet(AbstractSnippet):
        class Meta(AbstractSnippet.Meta):
            db_table = 'learn_snippet'

    __all__.append('Snippet')


# 8
if not is_model_registered('learn', 'Attachment'):
    class Attachment(AbstractAttachment):
        class Meta(AbstractAttachment.Meta):
            db_table = 'learn_attachment'

    __all__.append('Attachment')


# 9
if not is_model_registered('learn', 'ActivityLog'):
    class ActivityLog(AbstractActivityLog):
        class Meta(AbstractActivityLog.Meta):
            db_table = 'learn_log'

    __all__.append('ActivityLog')