from django.db import models
from django.contrib.auth.models import User

class BaseModel(models.Model):
    date_added = models.DateTimeField(auto_now_add=True, db_index=True)
    date_modified = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

class College(BaseModel):
    college_name = models.CharField(max_length=150)

    def __str__(self):
        return self.college_name

class Program(BaseModel):
    prog_name = models.CharField(max_length=150)
    college = models.ForeignKey('College', on_delete=models.CASCADE, related_name='programs')

    def __str__(self):
        return self.prog_name

class Tag(BaseModel):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name

class Thesis(BaseModel):
    title = models.CharField(max_length=255)
    abstract = models.TextField()
    authors = models.CharField(max_length=255, help_text="Comma-separated list of authors")
    adviser = models.CharField(max_length=255, blank=True, null=True)
    year_submitted = models.IntegerField()
    uploaded_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='uploaded_theses')
    college = models.ForeignKey('College', on_delete=models.CASCADE, related_name='theses')
    program = models.ForeignKey('Program', on_delete=models.CASCADE, related_name='theses')
    panel_score = models.FloatField(blank=True, null=True)
    tags = models.ManyToManyField('Tag', blank=True, related_name='theses')
    pdf_file = models.FileField(upload_to='theses_pdf/', verbose_name="Thesis PDF File", blank=True)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "Thesis"
        verbose_name_plural = "Theses"
