from django.contrib import admin
from .models import College, Program, Thesis, Tag

@admin.register(College)
@admin.register(Program)
@admin.register(Thesis)
@admin.register(Tag)

# Register your models here.
