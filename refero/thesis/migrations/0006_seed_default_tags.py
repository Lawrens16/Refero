from django.db import migrations

DEFAULT_TAGS = [
    "AI",
    "Agriculture",
    "Algorithms",
    "Blockchain",
    "Cloud Computing",
    "Computer Vision",
    "Cybersecurity",
    "Data Science",
    "Deep Learning",
    "E-Commerce",
    "Education Technology",
    "Game Development",
    "Health",
    "Human-Computer Interaction",
    "Image Processing",
    "Machine Learning",
    "Mobile Development",
    "NLP",
    "Network Security",
    "Neural Networks",
    "Operating Systems",
    "Reinforcement Learning",
    "Robotics",
    "Software Engineering",
    "Web Development",
]


def seed_tags(apps, schema_editor):
    Tag = apps.get_model('thesis', 'Tag')
    for name in DEFAULT_TAGS:
        Tag.objects.get_or_create(name=name)


def remove_seeded_tags(apps, schema_editor):
    Tag = apps.get_model('thesis', 'Tag')
    Tag.objects.filter(name__in=DEFAULT_TAGS).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('thesis', '0005_thesis_ss_paper_id'),
    ]

    operations = [
        migrations.RunPython(seed_tags, remove_seeded_tags),
    ]
