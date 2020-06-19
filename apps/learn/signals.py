from utils.generals import get_model

Course = get_model('learn', 'Course')


def course_pre_save_handler(sender, instance, raw, using, update_fields, **kwargs):
    pass


def course_pre_delete_handler(sender, instance, using, **kwargs):
    pass
