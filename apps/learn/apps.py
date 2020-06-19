from django.apps import AppConfig
from django.db.models.signals import pre_save, pre_delete


class LearnConfig(AppConfig):
    name = 'apps.learn'

    def ready(self):
        from utils.generals import get_model
        from apps.learn.signals import course_pre_save_handler, course_pre_delete_handler

        Course = get_model('learn', 'Subject')

        pre_save.connect(course_pre_save_handler, sender=Course, dispatch_uid='course_pre_save_signal')
        pre_delete.connect(course_pre_delete_handler, sender=Course, dispatch_uid='course_pre_delete_signal')
