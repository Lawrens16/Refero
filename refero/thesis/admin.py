from django.contrib import admin

from .models import College, Program, Tag, Thesis


@admin.register(College)
class CollegeAdmin(admin.ModelAdmin):
    list_display = ("college_name", "date_added", "date_modified")
    search_fields = ("college_name",)
    list_filter = ("date_added",)


@admin.register(Program)
class ProgramAdmin(admin.ModelAdmin):
    list_display = ("prog_name", "college", "date_added", "date_modified")
    search_fields = ("prog_name", "college__college_name")
    list_filter = ("college",)


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ("name", "date_added", "date_modified")
    search_fields = ("name",)


@admin.register(Thesis)
class ThesisAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "year_submitted",
        "college",
        "program",
        "uploaded_by",
        "panel_score",
    )
    search_fields = ("title", "authors", "adviser", "uploaded_by__username")
    list_filter = ("year_submitted", "college", "program", "tags")
    filter_horizontal = ("tags",)

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.select_related("college", "program", "uploaded_by").prefetch_related("tags")
