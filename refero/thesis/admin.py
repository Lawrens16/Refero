from django.contrib import admin
from .models import College, Program, Thesis, Tag

admin.site.register(College)
admin.site.register(Program)
admin.site.register(Thesis)
admin.site.register(Tag)
