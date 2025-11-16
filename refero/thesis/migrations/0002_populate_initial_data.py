from django.db import migrations


def create_initial_data(apps, schema_editor):
    College = apps.get_model('thesis', 'College')
    Program = apps.get_model('thesis', 'Program')

    cos, _ = College.objects.get_or_create(college_name="College of Science")
    Program.objects.get_or_create(prog_name="BS Information Technology", college=cos)
    Program.objects.get_or_create(prog_name="BS Computer Science", college=cos)


def remove_initial_data(apps, schema_editor):
    Program = apps.get_model('thesis', 'Program')
    College = apps.get_model('thesis', 'College')

    Program.objects.filter(prog_name__in=[
        "BS Information Technology",
        "BS Computer Science",
    ]).delete()
    College.objects.filter(college_name="College of Science").delete()


class Migration(migrations.Migration):

    dependencies = [
        ('thesis', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(create_initial_data, remove_initial_data),
    ]
