from django.contrib import admin

from utils.generals import get_model

Subject = get_model('learn', 'Subject')
Course = get_model('learn', 'Course')
Chapter = get_model('learn', 'Chapter')
Lecture = get_model('learn', 'Lecture')
Material = get_model('learn', 'Material')
Instructor = get_model('learn', 'Instructor')
Attachment = get_model('learn', 'Attachment')
Snippet = get_model('learn', 'Snippet')

# Register your models here.
